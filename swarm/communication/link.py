import inspect
import threading
import time
import queue
from abc import ABC, abstractmethod

# TODO: create malformed data exception


class Packet(ABC):
    """
    data to be sent over a Link
    """

    code = None
    kwargs = {}  # passed to write as kwargs
    data = []

    def __init__(self, *args, **kwargs):
        self.data = args
        self.kwargs = kwargs

    @abstractmethod
    def pack(self):
        """
        return data to be sent in form expected by the Link
        """

    @abstractmethod
    def unpack(self, *data, **kwargs):
        """
        take data from the Link and construct a Packet
        """


class Cycle:
    def __init__(self, delay, func):
        self.delay = delay
        self.func = func
        self.thread = threading.Thread()

    def start(self, link):
        self.func(link)
        time.sleep(self.delay)

    def cancel(self):
        self.task.cancel()


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
    packet = Packet

    @abstractmethod
    async def read(self, *args, **kwargs):
        """
        This method should return data when it is received from the network. It should block until it gets data.
        The data returned should be expected be the defined Packet.
        """

    @abstractmethod
    async def write(self, *data, **kwargs):
        """
        This method should write on the network. It should block until it is done.
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
            self.recv_queue.put(self.read())

    def send_loop(self):
        while self.running:
            try:
                packet = self.send_queue.get(block=True, timeout=5)
                self.write(packet)
            except queue.Empty:
                continue  # timeout every 5 seconds to check if the thread should join

    def ctrl_loop(self):
        while self.running:
            try:
                packet = self.recv_queue.get(block=True, timeout=5)
                # TODO: handle packet

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

