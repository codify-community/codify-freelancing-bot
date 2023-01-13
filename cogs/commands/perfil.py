import json
import discord
from discord import app_commands
from discord.ext import commands
import requests
import re

from config import config

class Perfil(commands.Cog):
  def __init__(self, client):
    self.client = client
    
  @app_commands.command(
    name="perfil",
    description="Crie ou altere seu perfil no CodeFreelas"
  )
  async def Perfil(self, interaction: discord.Interaction):
    user = requests.get(f"{config['base_url']}/{interaction.user.id}")

    if user.status_code != 200:
      modal = generate_modal()  
    else:
      user = json.loads(user.content)
      modal = generate_modal(user)

    await interaction.response.send_modal(modal)
    return

def generate_modal(user=None):
  modal = discord.ui.Modal(title='Perfil CodeFreelas')
  modal.add_item(discord.ui.TextInput(
    default=user["name"] if user else None,
    label='Nome',
    style= discord.TextStyle.short,
    placeholder='Seu Nome Aqui',
    required=True,
    min_length=4,
    max_length=30
  ))
  modal.add_item(discord.ui.TextInput(
    default=user["description"] if user else None,
    label='Descrição',
    style=discord.TextStyle.long,
    placeholder='Eu não gosto de golfinhos, mas o mysql é muito bom',
    required=True,
    max_length=300,
  ))
  modal.add_item(discord.ui.TextInput(
    default=user["banner_url"] if user else None,
    label='Banner',
    style=discord.TextStyle.short,
    placeholder='Links do imgur! Dimenções recomendadas: 1660x533',
    required=False,
  ))
  modal.add_item(discord.ui.TextInput(
    default=user["whatsapp"] if user else None,
    label='Whatsapp',
    style=discord.TextStyle.short,
    placeholder='16997355525',
    required=False,
    min_length=11,
    max_length=11
  ))
  modal.add_item(discord.ui.TextInput(
    default=user["instagram"] if user else None,
    label='Instagram',
    style=discord.TextStyle.short,
    placeholder='viinilv',
    required=False,
    max_length=15
  ))

  async def on_submit(interaction: discord.Interaction):
    name        = interaction.data['components'][0]['components'][0]['value']
    description = interaction.data['components'][1]['components'][0]['value']
    banner_url  = interaction.data['components'][2]['components'][0]['value']
    whatsapp    = interaction.data['components'][3]['components'][0]['value']
    instagram   = interaction.data['components'][4]['components'][0]['value']

    user = {
      "_id": str(interaction.user.id),
      "name": name,
      "avatar_url": str(interaction.user.display_avatar),
      "description": description,
      "banner_url": banner_url,
      "whatsapp": whatsapp,
      "instagram": instagram
    }

    if user["banner_url"]:
      if not user["banner_url"].startswith("https://i.imgur.com/"):
        await interaction.response.send_message("Banner url inválido!", ephemeral=True)
        return

    if user["whatsapp"]:
      if not re.search(r'^\s*(\d{2}|\d{0})[-. ]?(\d{5}|\d{4})[-. ]?(\d{4})[-. ]?\s*$', user["whatsapp"]):
        await interaction.response.send_message("Numero de whatsapp inválido!", ephemeral=True)
        return

    try:
      response = requests.post(f"{config['base_url']}/", json=user)
    except:
      await interaction.response.send_message("Erro ao conectar com o servidor!", ephemeral=True)
      return

    if response.status_code != 201:
      await interaction.response.send_message(f"Erro ao modificar perfil! Erro {response.status_code} {response.content}", ephemeral=True)
      return

    await interaction.response.send_message("Ação concluida!", ephemeral=True)

  modal.on_submit = on_submit

  return modal

async def setup(client):
  await client.add_cog(Perfil(client))