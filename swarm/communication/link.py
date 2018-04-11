import inspect
import threading
import time
import queue
import enum
from abc import ABC, abstractmethod


class OpCode(enum.Enum):
    """
    Descriptive names and values for OpCodes.
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
    data to be sent over a Link
    """

    code: OpCode = None
    kwargs = {}  # passed to write as kwargs
    data = []

    def __init__(self, *data, **kwargs):
        self.data = data
        self.kwargs = kwargs

    @classmethod
    @abstractmethod
    def from_data(cls):
        """
        stub
        """

    @abstractmethod
    def pack(self, *kwargs):
        """
        return data to be sent in form expected by the Link
        :raises MalformedData: if there is an error packing
        """

    @abstractmethod
    def unpack(self, *data, **kwargs):
        """
        Process a packet into it's data. Returns a tuple of valid data.
        :raises MalformedData: if there is an error unpacking
        """

threading.Thread()


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


class Recv:
    """
    Register a receive opcode in this Link. Usage:
    class Name(Link):
        @Recv.op(0)
        def func(self, packet):
            # respond to the data starting with opcode 0

    When opcode 0 is received, this function will be called and the data following the code is passed.
    Note that Send is callable, and will simply pass through to the function.
    """

    @staticmethod
    def op(code):
        def dec(func):
            return Recv(code, func)
        return dec

    def __init__(self, code, func):
        self.code = code
        self.func = func

    def __call__(self, packet: Packet):
        return self.func(packet)


class Send:
    """
    Register a send opcode in this Link. Usage:
    class Name(Link):
        @Send.op(0)
        def func(self, args...):
            # process args and return what is to be sent

    When Name.ping is called, adding the opcode and putting it in the sendqueue will be handled.
    Func should return a Packet
    """

    @staticmethod
    def op(code):
        def dec(func):
            return Send(code, func)
        return dec

    def __init__(self, code, func):
        self.code = code
        self.func = func
        try:
            self.link: Link = func.__self__
        except AttributeError:
            raise TypeError("func must be a bound method of a class")

    def __call__(self, *args, **kwargs):
        data: Packet = self.func(*args, **kwargs)
        try:
            data.code = self.code
        except AttributeError:
            raise TypeError("Send function should return a Packet")
        self.link.send_queue.put(data)


class Link(ABC):
    """
    abstract base class for basic shared communication code.
    """

    send_opcodes = {}
    recv_opcodes = {}
    cycles = []

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
        for name, member in inspect.getmembers(self):
            if isinstance(member, Recv):
                self.recv_opcodes[member.code] = member
            if isinstance(member, Send):
                self.send_opcodes[member.code] = member

    def recv_loop(self):
        while self.running:
            # wait for a new packet, add it to the queue
            try:
                self.recv_queue.put(self.read())
            except TimeoutError:
                continue  # timeout to check if the thread should join

    def send_loop(self):
        while self.running:
            try:
                # get a packet from the queue
                packet = self.send_queue.get(block=True, timeout=5)
                # send it
                self.write(packet)
            except queue.Empty:
                continue  # timeout every 5 seconds to check if the thread should join
            except TimeoutError:
                continue  # TODO: retry/log/etc, this happens when we fail to send data.

    def ctrl_loop(self):
        while self.running:
            try:
                # get and unpack a new packet
                packet = self.recv_queue.get(block=True, timeout=5)
            except queue.Empty:
                continue  # timeout every 5 seconds to check if the thread should join
            except MalformedData:
                continue  # we might want to log/debug/retry this eventually, for now ignore

            # run the requested command
            self.recv_opcodes[packet.code](packet)

    def start(self):
        self.running = True
        self.recv_thread.start()
        self.send_thread.start()
        self.ctrl_thread.start()

    def stop(self):
        self.running = False
        self.recv_thread.join()
        self.send_thread.join()
        self.ctrl_thread.join()
