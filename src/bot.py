
import abc


class SubBot:
    @abc.abstractmethod
    async def get_msg(self, scheduled):
        pass