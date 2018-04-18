import inspect
import threading
import time
import queue
import enum
from abc import ABC, abstractmethod
from collections import defaultdict


class OpCode(enum.Enum):
    """
    Descriptive names and values for OpCodes. Values should be Opinfo
    """

    @classmethod
    def _missing_(cls, value):
        """
        raise our more specific exception when an opcode is missing.
        """
        raise MalformedData("OpCode not found: {} in {}".format(value, cls.__name__))

    @classmethod
    def is_valid(cls, item):
        return any(item == e.value for e in cls)


class MalformedData(BaseException):
    """
    Signals that a packet couldn't be packed or unpacked properly.
    """


class Packet(ABC):
    """
    data to be sent over a Link. extract values using .values and data to be sent using .pack()
    """

    def __init__(self, *values, data=None, code=None, **options):
        self.options = defaultdict(lambda: None)
        self.options.update(options)

        # can be set later if needed
        self.code: OpCode = code
        self.data = data
        self.values = values

    @abstractmethod
    def get_code(self):
        """
        Get and store opcode from data.
        """

    @abstractmethod
    def pack(self, *kwargs):
        """
        Return data to be sent in form expected by the Link
        :raises MalformedData: if there is an error packing
        """

    @abstractmethod
    def unpack(self, **kwargs):
        """
        Process a packet into it's values from data. updates internal values and returns them. kwargs are options.
        :raises MalformedData: if there is an error unpacking
        """


class Cycle(threading.Thread):
    """
    Register a cycle in this Link. Usage:
    class Name(Link):
        @Cycle.register(10)
        def func(self):
            # send a message or something.

    In this example, every 10 seconds func will be run.
    This is useful for periodic tasks such as telemetry.
    Func should return a Packet.
    """

    @staticmethod
    def register(delay: int):
        def dec(func):
            return Cycle(delay, func)
        return dec

    def __init__(self, delay, func):
        self.delay = delay
        self.func = func
        try:
            self.link = func.__self__
            self.link.cycles.append(self)
            self.name = "{}: cycle {}".format(
                func.__self__.__class__.__name__,
                func.__name__
            )
        except AttributeError:
            raise TypeError("Cycle function must be a bound method of a class")
        super(Cycle, self).__init__(name=self.name)

    def run(self):
        while self.link.running:
            time.sleep(self.delay)
            self.link.send_queue.put(self.func())


def recv_op(code, **options):
    """
    Register a receive opcode in this Link. Usage:
    class Name(Link):
        @recv_op(OpCodes.EXAMPLE, example_option=1)
        def func(self, x, y, z):
            # respond to the data starting with opcode 0

    When opcode EXAMPLEE is received, this function will be called.
    The data interpreted according to the code is passed as arguments from Packet.unpack().
    kwargs/options passed will be updated in the packet.
    """
    def dec(func):
        def f(*args):
            args[1].options.update(options)
            return func(args[0], *args[1].unpack(), **args[1].options)
        f.code = code
        return f
    return dec


def send_op(code, **options):
    """
    Register a send opcode in this Link. Usage:
    class Name(Link):
        @send_op(OpCodes.EXAMPLE, example_option=1)
        def func(self, args...):
            # process args ...
            return Packet(blah, blah, blah)

    When Name.func is called, adding the opcode and putting it in the sendqueue will be handled.
    Func should return a Packet
    kwargs passed will be updated in the packet.
    """
    def dec(func):
        def f(*args, **kwargs):
            data: Packet = func(*args, **kwargs)
            data.options.update(options)
            try:
                data.code = code
            except AttributeError:
                raise TypeError("Send function should return a Packet")
            try:
                args[0].send_queue.put(data)
            except AttributeError:
                raise TypeError("Send function should be a method of a class")
        return f
    return dec


class Link(ABC):
    """
    Abstract Base Class for basic shared communication code.
    """

    cycles: [Cycle] = []
    recv_opcodes = {}

    @abstractmethod
    async def read(self):
        """
        This method should return data when it is received from the network. It should block until it gets data.
        The data returned should be the defined Packet.
        :raises TimeoutError: if blocking for too long. (important to terminate thread)
        """

    @abstractmethod
    async def write(self, packet: Packet):
        """
        This method should write on the network. It should block until it is done.
        :raises TimeoutError: if blocking for too long. (important to terminate thread)
        """

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()

        self.ready_to_send = True

        # threads
        self.running = False
        self.send_thread = threading.Thread(
            name='{}: send'.format(self.__class__.__name__),
            target=self.send_loop
        )
        self.recv_thread = threading.Thread(
            name='{}: recv'.format(self.__class__.__name__),
            target=self.recv_loop
        )
        self.ctrl_thread = threading.Thread(
            name='{}: ctrl'.format(self.__class__.__name__),
            target=self.ctrl_loop
        )

        super(Link, self).__init__()

        # register opcodes
        for name, member in inspect.getmembers(self):
            if hasattr(member, 'code'):
                self.recv_opcodes[member.code] = member

    def recv_loop(self):
        while self.running:
            # wait for a new packet, add it to the queue
            try:
                self.recv_queue.put(self.read())
            except TimeoutError:
                # print('{}: recv timeout'.format(self.__class__.__name__))
                continue  # timeout to check if the thread should join

    def send_loop(self):
        while self.running:
            # Delay between sends to give arduino a chance to process
            # This is important due to small buffer size and slower processor.
            while self.running and not self.ready_to_send:
                time.sleep(0.001)

            try:
                # get a packet from the queue
                packet = self.send_queue.get(block=True, timeout=5)
                # send it
                self.write(packet)
            except queue.Empty:
                continue  # timeout every 5 seconds to check if the thread should join
            except TimeoutError:
                print('{}: send timeout'.format(self.__class__.__name__))
                continue  # TODO: retry/log/etc, this happens when we fail to send data.

    def ctrl_loop(self):
        while self.running:
            try:
                # get and unpack a new packet
                packet = self.recv_queue.get(block=True, timeout=5)

                # run the requested command
                self.recv_opcodes[packet.get_code()](packet)
            except queue.Empty:
                continue  # timeout every 5 seconds to check if the thread should join
            except MalformedData as e:
                print('{}: ctrl malformed data: {}'.format(self.__class__.__name__, str(e)))
                continue  # we might want to log/debug/retry this eventually, for now ignore

    def start(self):
        self.running = True
        self.recv_thread.start()
        self.send_thread.start()
        self.ctrl_thread.start()
        for c in self.cycles:
            c.start()

    def stop(self):
        self.running = False
        self.recv_thread.join()
        self.send_thread.join()
        self.ctrl_thread.join()
        for c in self.cycles:
            c.join()
