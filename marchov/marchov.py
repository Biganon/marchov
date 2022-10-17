import pydle
from .secrets import *


class Marchov(pydle.Client):
    async def on_connect(self):
        await self.join(CHANNEL)

    async def on_message(self, target, source, message):
        if not message or message[0] != "?" or source == self.nickname:
            return

        # await self.message(target, message)
