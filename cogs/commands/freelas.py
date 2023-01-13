import discord
from discord import app_commands
from discord.ext import commands
import re
import requests
import json

from config import config

class Freelas(commands.Cog):
  def __init__(self, client):
    self.client = client
    
  @app_commands.command(
    name="freelas",
    description="Veja, altere e conclua seus freelas"
  )
  async def Freelas(self, interaction: discord.Interaction):
    select, isEmpty = generate_dropdown(interaction.user.id)

    if not isEmpty:
      await interaction.response.send_message("Você não tem nenhum freela cadastrado!", ephemeral=True)
      return

    await interaction.response.send_message(view=select, ephemeral=True)
    return
  
class Dropdown_(discord.ui.Select):
  def __init__(self, freela_id):
    self.freela_id=freela_id
    super().__init__(
      options=[
        discord.SelectOption(label='Editar Freela', value='edit'),
        discord.SelectOption(label='Concluir Freela', value='finish'),
      ],
      placeholder='Selecione uma ação',
      min_values=0,
      max_values=1
    )

  async def callback(self, interaction: discord.Interaction):
    try:
      action = interaction.data["values"][0]

      if action == 'finish':
        try:
          requests.put(f"{config['base_url']}/{interaction.user.id}/{self.freela_id}")
        except:
          await interaction.response.send_message('Erro ao concluir o freela', ephemeral=True)
          return
        
        await interaction.response.send_message('Freela concluido com sucesso', ephemeral=True)
      elif action == 'edit':
        modal = generate_modal(interaction.user.id, self.freela_id)
        await interaction.response.send_modal(modal)
    except:
      await interaction.response.send_message('Selecione uma ação', ephemeral=True)

class Dropdown(discord.ui.Select):
  def __init__(self, options):
    super().__init__(
      options=options,
      placeholder='Selecione um freela',
      min_values=0,
      max_values=1
    )

  async def callback(self, interaction: discord.Interaction):
    try:
      freela_id = interaction.data["values"][0]

      action = generate_dropdown_(freela_id)
      await interaction.response.send_message(view=action, ephemeral=True)
    except:
      await interaction.response.send_message('Selecione um freela', ephemeral=True)

def generate_dropdown_(freela_id: int):
  select = discord.ui.View()
  select.add_item(Dropdown_(freela_id))

  return select

def generate_dropdown(user_id: int):
  response = json.loads(requests.get(f"{config['base_url']}/{user_id}").content)

  options = []
  for i in response["freelas"]:
    options.append(discord.SelectOption(label=i["title"], value=i["id"]))

  select = discord.ui.View()
  select.add_item(Dropdown(options=options))

  return select, options

def generate_modal(user_id: int, freela_id: int):
  response = json.loads(requests.get(f"{config['base_url']}/{user_id}/{freela_id}").content)

  modal = discord.ui.Modal(title='Editar Freela')
  modal.add_item(discord.ui.TextInput(
    default=response["title"],
    label='Titulo',
    style= discord.TextStyle.short,
    placeholder='Desenvolvimento de portifólio com React',
    required=True,
    min_length=15,
    max_length=70
  ))
  modal.add_item(discord.ui.TextInput(
    default=response["description"],
    label='Descrição',
    style=discord.TextStyle.long,
    placeholder='# Olá, eu sou o VinniLv, e estou procurando um desenvolvedor para criar um site para mim.',
    required=True,
    min_length=80,
    max_length=3000,
  ))
  modal.add_item(discord.ui.TextInput(
    default=response["price"],
    label='Preço',
    style=discord.TextStyle.short,
    placeholder='180',
    required=True,
    max_length=5,
  ))
  modal.add_item(discord.ui.TextInput(
    default=response["deadline"],
    label='Tempo',
    style=discord.TextStyle.short,
    placeholder='1 semana',
    required=True,
    min_length=5,
    max_length=20
  ))
  modal.add_item(discord.ui.TextInput(
    default=",".join(response["technologies"]),
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
    }

    if price.isnumeric() == False:
      await interaction.response.send_message("Preço inválido!", ephemeral=True)
      return

    if not re.fullmatch(r'(\S{1,15})(,\S{1,15})*', technologies):
      await interaction.response.send_message("Formato de Technologias inválido!", ephemeral=True)
      return

    try:
      response = requests.post(f"{config['base_url']}/{user_id}/{freela_id}", json=freela)
      
    except:
      await interaction.response.send_message("Erro ao conectar com o servidor!", ephemeral=True)
      return

    if response.status_code != 200:
      await interaction.response.send_message(f"Erro ao editar Freela! Erro {response.status_code} {response.content}", ephemeral=True)
      return

    await interaction.response.send_message("Ação concluida!", ephemeral=True)

  modal.on_submit = on_submit

  return modal

async def setup(client):
  await client.add_cog(Freelas(client))