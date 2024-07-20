import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import gw_constants
import requests


class General(commands.Cog, name="general"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # ==============================================================================
    # COMMANDS
    # ==============================================================================

    @commands.hybrid_command(
        name="help", description="List all commands the bot has loaded."
    )
    #@app_commands.guilds(discord.Object(id=gw_constants.SERVER_ID))
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        print(f"{prefix}")
        embed = discord.Embed(
            title="Help", description="List of available commands:", color=0xBEBEFE
        )
        for i in self.bot.cogs:
            if i == "owner" and not (await self.bot.is_owner(context.author)):
                continue
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            data = []
            for command in commands:
                description = command.description.partition("\n")[0]
                data.append(f"{prefix}{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(
                name=i.capitalize(), value=f"```{help_text}```", inline=False
            )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    #@app_commands.guilds(discord.Object(id=gw_constants.SERVER_ID))
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="⏱️ Ping",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0xBEBEFE,
        )
        await context.send(embed=embed)

    # ==============================================================================
    # EVENT LISTENERS
    # https://stackoverflow.com/questions/76279755/how-can-i-use-cogs-discord-py
    # ==============================================================================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if message.author.id is not gw_constants.BOT_ID:
            if payload.emoji.name == '🇯🇵':
                
                r = requests.post(f"http://localhost:5000/detect?q={message.content}")
                r_det = r.json()
                print(r_det)
                lang = r_det[0]['language']
                r = requests.post(f"http://localhost:5000/translate?q={message.content}&source={lang}&target=ja")
                r_trans = r.json()
                print(r_trans)
                await message.channel.send(f"{message.jump_url}\n🔎**Translation**\nDetected Language: {lang} (Confidence: {r_det[0]['confidence']})\n```{r_trans['translatedText']}```")
            elif payload.emoji.name == '🔍' or payload.emoji.name =='🔎':
                #translator = Translator(to_lang="en")
                #message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                r = requests.post(f"http://localhost:5000/detect?q={message.content}")
                r_det = r.json()
                print(r_det)
                lang = r_det[0]['language']
                r = requests.post(f"http://localhost:5000/translate?q={message.content}&source={lang}&target=en")
                r_trans = r.json()
                print(r_trans)
                #translation = translator.translate(message.content)
                await message.channel.send(f"{message.jump_url}\n🔎**Translation**\nDetected Language: {lang} (Confidence: {r_det[0]['confidence']})\n```{r_trans['translatedText']}```")

async def setup(bot) -> None:
    await bot.add_cog(General(bot))