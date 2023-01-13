import discord
from discord import app_commands
from discord.ext import commands
import requests
import re

from config import config

class Freela(commands.Cog):
  def __init__(self, client):
    self.client = client
    
  @app_commands.command(
    name="freela",
    description="Cadastrar um pedido de freela"
  )
  async def Freela(self, interaction: discord.Interaction):
    modal = generate_modal()
    await interaction.response.send_modal(modal)
    return

def generate_modal():
  modal = discord.ui.Modal(title='Registrar Freela')
  modal.add_item(discord.ui.TextInput(
    label='Titulo',
    style= discord.TextStyle.short,
    placeholder='Desenvolvimento de portifólio com React',
    required=True,
    min_length=15,
    max_length=70
  ))
  modal.add_item(discord.ui.TextInput(
    label='Descrição',
    style=discord.TextStyle.long,
    placeholder='# Olá, eu sou o VinniLv, e estou procurando um desenvolvedor para criar um site para mim.',
    required=True,
    min_length=80,
    max_length=3000,
  ))
  modal.add_item(discord.ui.TextInput(
    label='Preço',
    style=discord.TextStyle.short,
    placeholder='180',
    required=True,
    max_length=5,
  ))
  modal.add_item(discord.ui.TextInput(
    label='Tempo',
    style=discord.TextStyle.short,
    placeholder='1 semana',
    required=True,
    min_length=5,
    max_length=20
  ))
  modal.add_item(discord.ui.TextInput(
    label='Tecnologias',
    style=discord.TextStyle.long,
    placeholder='react,node,python',
    required=True,
    max_length=300
  ))
  
  async def on_submit(interaction: discord.Interaction):
    title        = interaction.data['components'][0]['components'][0]['value']
    description  = interaction.data['components'][1]['components'][0]['value']
    price        = interaction.data['components'][2]['components'][0]['value']
    deadline     = interaction.data['components'][3]['components'][0]['value']
    technologies = interaction.data['components'][4]['components'][0]['value']
    
    freela = {
      "title": title,
      "description": description,
      "price": price,
      "deadline": deadline,
      "technologies": technologies.lower().split(","),
      "user_id": str(interaction.user.id),
    }

    if price.isnumeric() == False:
      await interaction.response.send_message("Preço inválido!", ephemeral=True)
      return

    if not re.fullmatch(r'(\S{1,15})(,\S{1,15})*', technologies):
      await interaction.response.send_message("Formato de Technologias inválido!", ephemeral=True)
      return

    try:
      response = requests.post(f"{config['base_url']}/freela", json=freela)
    except:
      await interaction.response.send_message("Erro ao conectar com o servidor!", ephemeral=True)
      return

    if response.status_code == 401:
      await interaction.response.send_message(f"Número máximo de freelas ativos atingido!", ephemeral=True)
      return
    elif response.status_code != 201:
      await interaction.response.send_message(f"Erro ao cadastrar Freela! Erro {response.status_code} {response.content}", ephemeral=True)
      return

    await interaction.response.send_message("Ação concluida!", ephemeral=True)

  modal.on_submit = on_submit

  return modal

async def setup(client):
  await client.add_cog(Freela(client))