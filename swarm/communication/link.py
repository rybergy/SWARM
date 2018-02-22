import asyncio
from abc import ABC, abstractmethod


class Cycle:
    def __init__(self, delay, func):
        self.delay = delay
        self.func = func
        self.task: asyncio.Task = None

    def start(self, link):
        async def loop():
            await self.func(link)
            await asyncio.sleep(self.delay)
        self.task = asyncio.get_event_loop().create_task(loop())

    def cancel(self):
        self.task.cancel()


class Link(ABC):
    """
    abstract base class for basic shared communication code.
    """

    opcodes = {}
    cycles = []

    @abstractmethod
    def __wait_for_read(self, **kwargs):
        """
        This method should return data when it is received from the network. It can block until it gets data.
        The data returned should be a processed list of arguments/data starting with the opcode.
        """

    @abstractmethod
    def __wait_for_write(self, data, **kwargs):
        """
        This method should write on the network. It can block until it is done.
        """

    async def read(self, *args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(None, lambda: self.__wait_for_read(*args, **kwargs))

    async def write(self, *args, **kwargs):
        await asyncio.get_event_loop().run_in_executor(None, lambda: self.__wait_for_write(*args, **kwargs))

    @classmethod
    def recv_op(cls, code: int):
        """
        Decorator to add an opcode handler for incoming communication.
        code is the opcode, it is an int.
        arguments passed to this function are this link instance followed by the bytes in the payload.

        Example usage:
        @Link.op(0)
        async def function(data):
            ...
        """

        def decorator(func):
            cls.opcodes[code] = func

        return decorator

    @classmethod
    def cycle(cls, delay: int):
        """
        Decorator to add a repeated message to be sent on the network. Useful for telemetry etc.
        delay is the time between sending in seconds.
        this link instance is passed as an argument.

        Example usage:
        @Link.cycle(60)
        async def function():
            ...
        """

        def decorator(func):
            cls.cycles.append(Cycle(delay, func))

        return decorator

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.task = None
        super(Link, self).__init__()

    async def loop(self):
        data = await self.read()
        try:
            asyncio.get_event_loop().create_task(self.opcodes[data[0]](self, data[1:]))
        except KeyError:
            print("unrecognized opcode: {}".format(data[0]))

    def start(self):
        self.task = asyncio.get_event_loop().create_task(self.loop())
        for c in self.cycles:
            c.start(self)
