import logging
import traceback

import discord
from discord import app_commands
from discord.ext import commands

from settings import MAIN_COLOR, REROL_CHANNEL_ID, REROL_MESSAGE_ID, NEWS_CHANNEL_ID, RULES_CHANNEL_ID, RULES_MESSAGE_ID

import utils.loggingUtils
import utils.otherUtils

def CreateAnouncementEmbed(titulo:str, description:str, image_url:str, roles) -> discord.Embed: 
  em = discord.Embed(title=titulo, description=description, color=MAIN_COLOR)
  em.set_author(name="by Rooster Games", icon_url="")
  em.set_image(url=image_url)

  if roles:
    em.description += "\n"

    for rol in roles:
      em.description += f"{rol.mention}"
 
  return em

class AnouncementModal(discord.ui.Modal, title="Anuncio"):
  title_ = discord.ui.TextInput(label="Título", style=discord.TextStyle.short, placeholder="Viernes de Pizza!", required=True)
  description_ = discord.ui.TextInput(label="Descripción", style=discord.TextStyle.paragraph, placeholder="Va a ser peperoni con orilla de queso 🍕")
  image_ = discord.ui.TextInput(label="Imagen", style=discord.TextStyle.short, placeholder="url de la imagen", required=False)

  async def on_submit(self, interaction: discord.Interaction):
    em = CreateAnouncementEmbed(self.title_.value, self.description_.value, self.image_.value, None)

    # get the news channel
    channel = await interaction.guild.fetch_channel(NEWS_CHANNEL_ID)

    if not channel:
      channel = interaction.channel
      await channel.send("news channel not found...")

    message = await channel.send(embed=em)
    await interaction.response.send_message(f"[announcement]({message.jump_url}) publish on {channel.mention}")

  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

    # Make sure we know what the error actually is
    traceback.print_exception(type(error), error, error.__traceback__)

class AdminCog(commands.Cog, name="Admin"):
  def __init__(self, bot):
    self.bot = bot

    self.logger = logging.getLogger("bot.admin_cog") 

  async def cog_before_invoke(self, ctx):
    utils.loggingUtils.log_command_call(self.logger, ctx) 

  @app_commands.command(name="announcement", description="create a new anouncement embed that will be sent to the news channel")
  async def announcement_slash(self, interaction : discord.Interaction):
    utils.loggingUtils.log_slash_command_call(self.logger, interaction)
    
    author = interaction.user
    
    if not utils.otherUtils.isAdmin(interaction.guild, author):
      self.logger.log(logging.INFO, f"access denied for user {author.display_name} (member ID: {author.id}) when running anouncemnt (slash command) command")
      return

    await interaction.response.send_modal(AnouncementModal())

  @commands.command(brief="announce an event", description="send an announcement embed with the title and description specified")
  async def announcement(self, ctx:commands.context, title:str, description:str, image_url:str):
    author = ctx.author

    if not utils.otherUtils.isAdmin(ctx.guild, author):
      self.logger.log(logging.INFO, f"access denied for user {author.display_name} (member ID: {author.id}) when running anouncemnt (normal command) command")
      return

    em = CreateAnouncementEmbed(title, description, image_url, None)

    channel = await ctx.guild.fetch_channel(NEWS_CHANNEL_ID)

    if not channel:
      channel = ctx.channel
      await channel.send("news channel not found...")

    message = await channel.send(embed=em)
    await ctx.send(f"[anouncement]({message.jump_url}) publish on {channel.mention}")

  @commands.command(hidden=True)
  async def genrerol(self, ctx : commands.Context):

    if not utils.otherUtils.isAdmin(ctx.guild, ctx.message.author):
      return

    description_ = "Reacciona con el emoji adecuado para obtener tu rol"
    description_ += "\n\n**---------- Intereses ----------**\n"
    description_ += "\n> 🎲 para **Game Design**"
    description_ += "\n> ⚙️ para **Programming**"
    description_ += "\n> 🎨 para **Graphics** o **Animation**"
    description_ += "\n> 🎵 para **Music**"
    description_ += "\n> 🔊 para **Sound Design** o **Voice Acting**"
    description_ += "\n> 📚 para **Writing** o **Narrative Design**"
    description_ += "\n\n**----------  Hobbies ----------**\n"
    description_ += "\n> 🕹️ para **Gaming**"

    em = discord.Embed(title="Obten tus roles", description=description_, color=MAIN_COLOR)
    
    channel = await self.bot.fetch_channel(REROL_CHANNEL_ID)

    # check if the message exists already, if it does we edit it, otherwise we create it for the first time
    message = await channel.fetch_message(REROL_MESSAGE_ID)

    if message: 
      await message.edit(embed=em)
    else:
      message = await channel.send(embed=em)

    await message.add_reaction("🎲")
    await message.add_reaction("⚙️")
    await message.add_reaction("🎨")
    await message.add_reaction("🎵")
    await message.add_reaction("🔊")
    await message.add_reaction("📚")
    await message.add_reaction("🕹️")

  @commands.command(hidden=True)
  async def genrules(self, ctx : commands.Context):
    
    if not utils.otherUtils.isAdmin(ctx.guild, ctx.message.author):
      return

    em = discord.Embed(title="Las reglas", color=MAIN_COLOR)

    rules = [
      "No faltar el respeto a los demás",
      "No difundir odio",
      "No xenofobia",
      "No homofobia",
      "No discriminación",
      "Ser creativo"
    ]

    description_ = ""

    for i in range(len(rules)):
      description_ += f"\n{i + 1}. {rules[i]}"

    em.description = description_

    channel = await self.bot.fetch_channel(RULES_CHANNEL_ID)

    message = await channel.fetch_message(RULES_MESSAGE_ID)

    if message: 
      await message.edit(embed=em)
    else:
      message = await channel.send(embed=em)

    await message.add_reaction("✅")