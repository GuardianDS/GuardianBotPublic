import json
import csv
import logging
import os
import shutil
import platform
import random
import sys
from datetime import datetime, timedelta
#from apscheduler.schedulers.blocking import BlockingScheduler
#from apscheduler.schedulers.asyncio import AsyncIOScheduler

import aiosqlite
import discord
from discord.ext.commands.context import Context
from discord.ext import commands, tasks
from discord import Intents
from dotenv import load_dotenv
from discord import Webhook
import aiohttp

from database import DatabaseManager


from translate import Translator
import requests


if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
        config = json.load(file)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

LOG_NAME = "discord.log"

BOT_ID = os.getenv("BOT_ID")
SERVER_ID = os.getenv("SERVER_ID")
APPROVAL_CHANNEL_ID = 1217086803425759252
REJECTION_CHANNEL_ID = 1227213063573471232
WALL_OF_SHAME_CHANNEL_ID = 1217087859857817600


ROLES_ID_DICT = {
    "prankster": 1224377043748130916,
    "heel": 1224376450367492128,
    "gagged": 1224376171769368646,
    "dom": 1204431046506975283,
    "sub": 1204431294331748372,
    "switch": 1204431226497269830,
    "pet play": 1206148592767868959,
    "brat": 1206147205535105045,
    "member": 1205129581791674388,
    "admin": 1204074468537008138,
    "paintbucket": 1225071141706661928,
    "moderator": 1204236484735934474,
    "booster": 1209731341244039208
}

ROLE_PRANKSTER = 1224377043748130916
ROLE_HEEL = 1224376450367492128
ROLE_GAGGED = 1224376171769368646
ROLE_DOM = 1204431046506975283
ROLE_SUB = 1204431294331748372
ROLE_SWITCH = 1204431226497269830
ROLE_PET_PLAY = 1206148592767868959
ROLE_BRAT = 1206147205535105045
ROLE_MEMBER = 1205129581791674388
ROLE_ADMIN = 1204074468537008138
ROLE_NAUGHTY_MOD = 1235590945244839936
ROLE_JIGSAW = 1235591378608586772
JIGSAW_PASSWORD = "im sorry"
CHANNEL_JIGSAW = 1235591892838645780
GAG_LIST = ["mmn", "glr", "ffmph", "gah", "hlur", "oog", "mrrrr", "shlur"]
PET_LIST = ["woof", "bark", "yip", "ruff", "grrr", "arf"]
#"I was a naughty mod and I'm suffering the consequences",
NAUGHTY_MOD_LIST = ["Make yourself at home. Use my face as your throne. I'll patiently worship while you play with your phone",
                    "I'm a dirty little slut, I like it up my butt. Now I'll bend over so you can give me your hot nut!",
                    "I ain't just a tinderella, I'll drop to my knees for a fella. I've been quite a baddie, now punish me daddy!",
                    "Glug glug glug. Please give me your milk to chug. Make me a sight, my belly is too light!",
                    "Take off your belt, I want to earn my stripes. Make it hurt so I can show off my pipes!",
                    "I have a huge dildo collection. But no, I won't share, I'm just flexin'",
                    "Big white cock is my religion. It came to me in a vision. Get bleach in my eyes. Spread my thighs. My ass is ready for that collision.",
                    "I have a tight butt. I need it loosened up. So spin me around, and dick me down. I'll even back it up."]

CAT_WELCOME = 1204074109492002866
CAT_ADMIN = 1204251584968785930
CAT_TICKET_APP = 1216160133831200958
CAT_TICKET_REP = 1216426772317601894
CAT_TICKET_ADM = 1227750292494221424

ROLE_SEPERATOR_TOP = 1206092856347857006
ROLE_SEPERATOR_MID = 1209883176789475339
ROLE_SEPERATOR_BOT = 1206608645136191578

UID_GUARDIAN = os.getenv("UID_GUARDIAN")
MODE_COLOR_WAR = False

COLORS_ID_DICT = {
    "pastel light blue": 1225078760424869888,
    "pastel periwinkle": 1225079039245549669,
    "pastel pink": 1225079356028751952,
    "pastel red": 1225079527726649405,
    "pastel orange": 1225079692797673562,
    "pastel yellow": 1225079856681844837,
    "pastel purple": 1225080060311244921,
    "pastel green": 1225080339068878950,
    "pastel blue": 1225080523563466825
}

##########################################################
# COLOR WAR
##########################################################


##########################################################
##########################################################

CHANNEL_GEN_CHAT = 1204074109492002868
CHANNEL_NUT = 1240117878724890706
EMOJI_NUT_BUTTON = 1239968423178403840


ROLES_CACHE = {}
HOOKS_CACHE = {}
COLORS_CACHE = {}

QUESTION_ADD_PRESTIGE_REQ = 10

HELP_MSG = """
## Commands:
====================
- `g! icebreaker` ⇒ pull a new icebreaker question to be sent in the icebreaker channel

🔰 **Prestige 5+**
- `g! truth` ⇒ pull a new truth to be sent in the T or D channel
- `g! dare` ⇒ pull a new dare to be sent in the T or D channel

🔰 **Prestige 10+**
- `g! add icebreaker <question>` ⇒ adds a brand new question to the database that will be available after the next shuffle
- `g! add truth <question>` ⇒ adds a brand new truth to the database that will be available after the next shuffle
- `g! add dare <question>` ⇒ adds a brand new dare to the database that will be available after the next shuffle
"""


PAINT_MSG = """
🐰 **Easter Event Winner**
- `g! dye <user> <color>` ⇒ dye the username a color (light blue, periwinkle, pink, red, orange, yellow, purple, green, blue)
"""

ADMIN_MSG = """
👮 **Admin**
- `g! approve <user> <note>` ⇒ transfers all that user's comments into the approvals channel + admin note
- `g! reject <user> <note>` ⇒ transfers all that user's comments into the wall of shame channel + admin note
- `g! collect stats` ⇒ collects membership role stats
- `g! jigsaw <user> <passphrase>` ⇒ applies the jigsaw role to a user so they can only post in the <#1235591892838645780> channel and can only escape by saying the passphrase
- `g! free <user>` ⇒ removes the jigsaw role
- `g! changepw <passphrase>` ⇒ updates the jigsaw passphrase
"""

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)

logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# Check for previous log
if os.path.isfile(LOG_NAME):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    shutil.copy(LOG_NAME, f"logs/{LOG_NAME}_{timestamp}.log")
# File handler
file_handler = logging.FileHandler(filename=LOG_NAME, encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

BOT_REF = None

class GuardianBot(commands.Bot):
# =======================================================
# SETUP
# =======================================================
    def __init__(self) -> None:
        global BOT_REF
        super().__init__(
            command_prefix=commands.when_mentioned_or(config["prefix"]),
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.logger = logger
        self.config = config
        self.database = None
        BOT_REF = self

    @tasks.loop(minutes=15)
    async def colorwar_scheduled_job(self):
        print('[CW] RUNNING colorwar_scheduled_job')
        await bot.wait_until_ready()
        # if MODE_COLOR_WAR:
        #     channel = await bot.fetch_channel(CHANNEL_CW_LOG)
        #     await bot.database.colorwar_channel_refresh()
        #     await bot.refresh_colorwar_stats()
        #     await channel.send('🔃Team Paintball Stores Have Been Refreshed')

    # @colorwar_scheduled_job.before_loop
    # async def colorwar_scheduled_job_before_loop():
    #     await bot.wait_until_ready()

    async def init_db(self) -> None:
        async with aiosqlite.connect(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
        ) as db:
            with open(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
            ) as file:
                await db.executescript(file.read())
            await db.commit()

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            print(f"Inspecting Cogs: {file}")
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    async def setup_hook(self) -> None:
        """
        This will just be executed when the bot starts the first time.
        """
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        await self.init_db()
        await self.load_cogs()
        #self.status_task.start()
        self.database = DatabaseManager(
            connection=await aiosqlite.connect(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
            )
        )

# =======================================================
# UTILITY
# =======================================================


    def get_role(self, role_id, guild):
        if role_id not in ROLES_CACHE:
            ROLES_CACHE[role_id] = guild.get_role(role_id)
        return ROLES_CACHE[role_id]

    async def get_user_target(self, message: discord.Message):
        if "<@" in message.content:
            # get target user
            target_uid = int(message.content[message.content.index("<@") + 2:message.content.index(">")])
            user = message.channel.guild.get_member(target_uid)
            if user:
                return user
            else:
                return await bot.fetch_user(target_uid)
        else:
            return None
    
    def get_user_prestige(self, user: discord.Member) -> int:
        roles = user.roles
        for role in roles:
            if "prestige" in role.name.lower():
                num = role.name.lower().replace("prestige", "").strip()
                return int(num)
        
        return 0

    async def ticket_collect(self, message: discord.Message, target_channel_id: int):
        target = await self.get_user_target(message)
        post = f"<@{target.id}> (ID: `{target.id}`)\nDisplay Name: `{target.display_name}`\nUser Name: `{target.name}`\n"
        post += "\n```\n"

        history = ""
        # note: iterates in reverse
        async for msg in message.channel.history(limit=100):
            if msg.author.id == target.id:
                history = f"{msg.content}\n" + history
        
        post += history
        post += "```"
        comment = message.content[message.content.index(">") + 2:].strip()
        if comment:
            post += f"*NOTE: {comment}*"
        await message.channel.guild.get_channel(target_channel_id).send(post)

    async def add_question(self, message: discord.Message, category: str):
        guid = await self.database.add_question(message.author.id, category, message.content[17:].strip())
        if guid:
            await message.channel.send("Added successfully and will be in rotation after the current shuffle is exhausted.")



# =======================================================
# DISCORD API EVENTS
# =======================================================

    async def on_message(self, message: discord.Message) -> None:
        global JIGSAW_PASSWORD
        if message.author == self.user or message.author.bot:
            return

        user_roles_ids = []
        #print(f"GUILD: {message.guild}")
        for role in message.author.roles:
            user_roles_ids.append(role.id)

        # Commands
        if message.content.lower().startswith("g!"):
            # attempt to fix their case insensitivity issue


            if message.content.lower().startswith("g! sync") and (ROLES_ID_DICT["admin"] in user_roles_ids):
                MY_GUILD = discord.Object(id=SERVER_ID)
                self.tree.copy_global_to(guild=MY_GUILD)
                await self.tree.sync(guild=MY_GUILD)
                return
            if message.content.lower().startswith("g! help"):
                help_message = HELP_MSG
                if ROLES_ID_DICT["paintbucket"] in user_roles_ids:
                    help_message += PAINT_MSG
                if (message.content.lower().startswith("g! help admin")) and (ROLES_ID_DICT["moderator"] in user_roles_ids):
                    help_message += ADMIN_MSG
                await message.channel.send(help_message)
            elif message.content.lower().startswith("g! debug roles") and (ROLES_ID_DICT["admin"] in user_roles_ids):
                f = open('role_debug.txt', "w", encoding="utf-8")
                for role in message.channel.guild.roles:
                    f.write(f"{role.position} - {role.name}\n")
                f.close()
            elif message.content.lower().startswith("g! dye") and (ROLES_ID_DICT["paintbucket"] in user_roles_ids):
                target = await self.get_user_target(message)
                if target:
                    color = message.content[message.content.index(">") + 2:]
                    color = color.strip().lower() #sanitize
                    color = "pastel " + color
                    # remove current color role
                    for clr in COLORS_ID_DICT.values():
                        await target.remove_roles(self.get_role(clr, message.channel.guild))
                    await target.add_roles(self.get_role(COLORS_ID_DICT[color], message.channel.guild))
            elif message.content.lower().startswith("g! seed") and (ROLES_ID_DICT["admin"] in user_roles_ids):
                seed_target = message.content.replace("g! seed", "").strip()
                f = open(f"questions\{seed_target}.txt", 'r', encoding="utf-8")
                for line in f:
                    print(f"Adding: {seed_target} | {line}")
                    await self.database.add_question(BOT_ID, seed_target, line)
                f.close()
            elif message.content.lower().startswith("g! add") and self.get_user_prestige(message.author) > QUESTION_ADD_PRESTIGE_REQ:
                if message.content.lower().startswith("g! add icebreaker"):
                    await self.add_question(message, "icebreakers")
                elif message.content.lower().startswith("g! add truth"):
                    await self.add_question(message, "truths")
                elif message.content.lower().startswith("g! add dare"):
                    await self.add_question(message, "dares")
            #elif message.content.lower().startswith("g! collect stats") and (ROLES_ID_DICT["moderator"] in user_roles_ids):
                
        
            await self.process_commands(message)
                

                


        


# =======================================================
# MAIN
# =======================================================

load_dotenv()
bot = GuardianBot()
#colorwar_scheduled_job.start()
bot.run(os.getenv("TOKEN"))