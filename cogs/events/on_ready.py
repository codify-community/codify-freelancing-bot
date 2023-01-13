import discord
from colorize import colorize_rainbow
from discord.ext import commands

class Ready(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_ready(self):
    for guild in self.client.guilds:
      print("sincronizando comandos em ", guild.name)
      self.client.tree.copy_global_to(guild=discord.Object(id=guild.id))
      await self.client.tree.sync(guild=discord.Object(id=guild.id))
      
    print(colorize_rainbow('@================@', mode_type='foreground'))
    print(colorize_rainbow('    BOT ONLINE    ', mode_type='foreground'))
    print(colorize_rainbow('@================@', mode_type='foreground'))
    
async def setup(client):
  await client.add_cog(Ready(client))