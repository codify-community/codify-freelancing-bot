import os

import discord
from discord.ext import commands

from config import config

class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(
          command_prefix='!',
          intents=discord.Intents.all(),
          application_id=1061357152033329163
        )

    async def setup_hook(self):
      for i in os.listdir('./cogs'):
        for e in os.listdir(f'./cogs/{i}'):
          if str(e).endswith('.py'):
            print('loaded ', e)
            await client.load_extension(f'cogs.{i}.{e[:-3]}')

client = MyClient()
client.run(config['token'])