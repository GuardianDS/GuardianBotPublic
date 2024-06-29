import json
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
from stats.membership_data import MembershipData


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

BOT_ID = 1223643497144516618
APPROVAL_CHANNEL_ID = 1217086803425759252
REJECTION_CHANNEL_ID = 1227213063573471232
WALL_OF_SHAME_CHANNEL_ID = 1217087859857817600
ICEBREAKER_CHANNEL_ID = 1214760927841222666
T_OR_D_CHANNEL_ID = 1206114770122707015

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
TEAM_RED = 1244889487117385770
TEAM_RED_PAINT = 1225079527726649405

TEAM_BLUE = 1244889570445889558
TEAM_BLUE_PAINT = 1225080523563466825

TEAM_YELLOW = 1244889641904246854
TEAM_YELLOW_PAINT = 1225079856681844837

TEAM_GREEN = 1244889720312434779
TEAM_GREEN_PAINT = 1225080339068878950

TEAM_PURPLE = 1244889799156826133
TEAM_PURPLE_PAINT = 1225080060311244921

TEAM_ORANGE = 1244893424960671784
TEAM_ORANGE_PAINT = 1225079692797673562

TEAM_NONE = 0000000000000000000

COLORWAR_TEAMS  = [1244889487117385770,1244889570445889558,1244889641904246854,1244889720312434779,1244889799156826133,1244893424960671784]
COLORWAR_PAINTS = [1225079527726649405,1225080523563466825,1225079856681844837,1225080339068878950,1225080060311244921,1225079692797673562]
COLORWAR_TEAM_PAINT_DICT = {
    1244889487117385770: 1225079527726649405, #RED
    1244889570445889558: 1225080523563466825, #BLUE
    1244889641904246854: 1225079856681844837, #YELLOW
    1244889720312434779: 1225080339068878950, #GREEN
    1244889799156826133: 1225080060311244921, #PURPLE
    1244893424960671784: 1225079692797673562  #ORANGE
}
COLORWAR_TEAM_EMOJI_DICT = {
    1244889487117385770: "🔴", #RED
    1244889570445889558: "🔵", #BLUE
    1244889641904246854: "🟡", #YELLOW
    1244889720312434779: "🟢", #GREEN
    1244889799156826133: "🟣", #PURPLE
    1244893424960671784: "🟠"  #ORANGE
}

COLORWAR_BASE_CHANNEL_NAME = {
    1204074109492002868: "💬general",
    1205893763772452976: "🙈nsfw-general",
    1206321967502852196: "🧩hobby-lobby",
    1214760927841222666: "🧊icebreakers",
    1206110669305286666: "😂memeology"
}

COLORWAR_PAINTBALL_CD_MINS = 15
COLORWAR_CHANNEL_CD_MINS = 60

EMOJI_PAINTBALL = 1245181909785514038
EMOJI_GRENADE = 1245182187670601818
MODE_COLOR_WAR = True

CHANNEL_CW_LOG = 1245628559553462294
CW_STATS_MESSAGE_ID = 1246106979316011121
CHANNEL_CW_STATS = 1245628410479247423

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
        )
        self.logger = logger
        self.config = config
        self.database = None
        BOT_REF = self

    @tasks.loop(minutes=15)
    async def colorwar_scheduled_job(self):
        print('[CW] RUNNING colorwar_scheduled_job')
        await bot.wait_until_ready()
        if MODE_COLOR_WAR:
            channel = await bot.fetch_channel(CHANNEL_CW_LOG)
            await bot.database.colorwar_channel_refresh()
            await bot.refresh_colorwar_stats()
            await channel.send('🔃Team Paintball Stores Have Been Refreshed')

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
        #await self.load_cogs()
        #self.status_task.start()
        self.database = DatabaseManager(
            connection=await aiosqlite.connect(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
            )
        )
        # https://stackoverflow.com/questions/74989101/discord-py-tasks-loop-sending-runtime-error-no-running-event-loop
        if MODE_COLOR_WAR:
            self.colorwar_scheduled_job.start()
            print("START")
            #https://stackoverflow.com/questions/22715086/scheduling-python-script-to-run-every-hour-accurately
            #self.scheduler = BlockingScheduler()
            #self.scheduler.add_job(colorwar_scheduled_job, 'interval', minutes=15)
            #self.scheduler.start()
            #https://github.com/agronholm/apscheduler/blob/3.x/examples/schedulers/asyncio_.py
            #self.scheduler = AsyncIOScheduler()
            #https://stackoverflow.com/questions/61366148/python-discord-py-bot-interval-message-send

# =======================================================
# UTILITY
# =======================================================

    # See if we have the id cached => return the webhook
    # otherwise lazy load it into the cache
    async def get_channel_hook(self, message: discord.Message, session):
        hook = None

        if message.channel.id in HOOKS_CACHE:
            hook = HOOKS_CACHE.get(message.channel.id)
        else:
            # see if a webhook exists
            hooks = await message.channel.webhooks()
            for wh in hooks:
                if wh.name == "GuardianBot":
                    hook = wh
            # if one doesn't then create one
            if hook == None:
                hook = await message.channel.create_webhook(name="GuardianBot")
            
            # cache it for later use
            HOOKS_CACHE[message.channel.id] = hook

        webhook = Webhook.from_url(hook.url, session=session)
        return webhook

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
        post = f"<@{target.id}>\n`{target.display_name}`\n`{target.name}`\n"
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

# =======================================================
# UTILITY - QUESTIONS
# =======================================================

    async def get_next_question(self, message: discord.Message, category: str, channel: int, prefix: str):
        # check to see if we hit the end of the list
        q_max = await self.database.get_shuffled_count(category)
        q_count = await self.database.get_counter(category)

        # regenerate if so
        if (q_count >= q_max) or q_max == 0:
            clear = await self.database.clear_shuffled_questions(category)
            questions = await self.database.get_questions(category)
            random.shuffle(questions) # shuffles in place
            count = 0
            for q in questions:
                q_id = q[0]
                q_ques = q[3]
                await self.database.add_shuffled_question(q_id, count, category, q_ques)
                count += 1
            await self.database.reset_counter(category)
            q_count = 0

        # fetch next question in sequence and progress counter
        result_question = f"**{prefix}:** "
        result_question += await self.database.get_shuffled_question(q_count, category)
        await self.database.progress_counter(category)
        await message.channel.guild.get_channel(channel).send(result_question)
    
    async def add_question(self, message: discord.Message, category: str):
        guid = await self.database.add_question(message.author.id, category, message.content[17:].strip())
        if guid:
            await message.channel.send("Added successfully and will be in rotation after the current shuffle is exhausted.")

# =======================================================
# STATS
# =======================================================

    async def collect_membership_stats(self, guild: discord.Guild) -> dict:

        role_count = {}
        pos_bot = guild.get_role(ROLE_SEPERATOR_BOT).position
        pos_mid = guild.get_role(ROLE_SEPERATOR_MID).position
        pos_top = guild.get_role(ROLE_SEPERATOR_TOP).position
        async for member in guild.fetch_members():
            print(f'Member: {member.display_name}')
            if member.get_role(ROLES_ID_DICT["member"]):
                for role in member.roles:
                    if role_count.get(role.id):
                        role_count[role.id].member_count = role_count[role.id].member_count + 1
                    else:
                        category = ''
                        if role.position > pos_bot and role.position < pos_mid:
                            category = "Kinks"
                        elif role.position > pos_mid and role.position < pos_top:
                            category = "Demographic"
                        elif role.position > pos_top and (("Member" in role.name) or ("Prestige" in role.name)):
                            category = "Membership"
                        role_count[role.id] = MembershipData(category, role.id, role.name, role.color.value, 1, datetime.now())

        return role_count

# =======================================================
# COLOR WAR UTILITY
# =======================================================

    async def find_colorwar_team(self, roles: list) -> int:
        for role in roles:
            #print(f"CURR ROLE = {role}")
            if role.id in COLORWAR_TEAMS:
                #print("Found Role")
                return role.id
        return None

    async def find_colorwar_paint(self, roles: list) -> int:
        for role in roles:
            if role.id in COLORWAR_PAINTS:
                return role.id
        return None

    async def purge_colorwar_paints(self, member: discord.Member):
        for role_id in COLORWAR_PAINTS:
            paint_role = member.get_role(role_id)
            if paint_role != None:
                await member.remove_roles(paint_role)
        
    # async def remove_old_colors(self, member: discord.Member, new_paint: int):
    #     for role in member.roles:
    #         if role.id in COLORWAR_PAINTS:

    async def seed_colorwar(self, guild: discord.Guild):
        counter = 0
        async for member in guild.fetch_members():
            if member.get_role(ROLES_ID_DICT["member"]):
                already_on_team = False
                for team in COLORWAR_TEAMS:
                    if member.get_role(team) != None:
                        already_on_team = True

                if not already_on_team:
                    team_role = guild.get_role(COLORWAR_TEAMS[counter % 6])
                    await member.add_roles(team_role)
                    counter += 1


    async def refresh_colorwar_stats(self):
        print('[CW] REFRESHING STATS')
        edit_msg = await bot.get_channel(CHANNEL_CW_STATS).fetch_message(CW_STATS_MESSAGE_ID)
        score_dict = {
            TEAM_RED_PAINT: 0,
            TEAM_BLUE_PAINT: 0,
            TEAM_YELLOW_PAINT: 0,
            TEAM_GREEN_PAINT: 0,
            TEAM_PURPLE_PAINT: 0,
            TEAM_ORANGE_PAINT: 0
        }
        async for member in edit_msg.guild.fetch_members():
            for role in member.roles:
                if role.id in COLORWAR_PAINTS:
                    score_dict[role.id] = score_dict[role.id] + 1
                    break

        post = "# Scores\n```"
        post += f"🔴 RED SCORE:    {score_dict[TEAM_RED_PAINT]}\n"
        post += f"🔵 BLUE SCORE:   {score_dict[TEAM_BLUE_PAINT]}\n"
        post += f"🟡 YELLOW SCORE: {score_dict[TEAM_YELLOW_PAINT]}\n"
        post += f"🟢 GREEN SCORE:  {score_dict[TEAM_GREEN_PAINT]}\n"
        post += f"🟣 PURPLE SCORE: {score_dict[TEAM_PURPLE_PAINT]}\n"
        post += f"🟠 ORANGE SCORE: {score_dict[TEAM_ORANGE_PAINT]}\n"
        post += "```\n"

        channel_stats = await self.database.get_channel_ownership_stats()
        post += "# Channel Control\n"
        for row in channel_stats:
            print(row)
            channel = bot.get_channel(int(row[2]))
            post += f"- {channel.name}\n"
            owner = int(row[3])
            if owner in COLORWAR_TEAMS:
                owner_lookup = channel.guild.get_role(int(owner))
                post += f" - OWNER: {COLORWAR_TEAM_EMOJI_DICT[owner_lookup.id]} {owner_lookup.name}\n"
            else:
                post += " - OWNER: none\n"
            
            post += f" - SUPPLY: {row[6]}/{row[5]}\n"

        #post += "```\n"
        await edit_msg.edit(content=post)

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
            if message.content.lower().startswith("g! cw"):
                if ROLES_ID_DICT["admin"] in user_roles_ids:
                    if message.content.lower().startswith("g! cw init"):
                        await message.channel.send("init")
                    if message.content.lower().startswith("g! cw refresh"):
                        await self.refresh_colorwar_stats()
                    if message.content.lower().startswith("g! cw seed"):
                        await self.seed_colorwar(message.guild)
                    if message.content.lower().startswith("g! cw clear"):
                        roles = []
                        for role in COLORWAR_TEAMS:
                            roles.append(message.guild.get_role(role))
                        for role in COLORWAR_PAINTS:
                            roles.append(message.guild.get_role(role))
                        async for member in message.channel.guild.fetch_members():
                            for role in roles:
                                await member.remove_roles(role)
                if ROLES_ID_DICT["moderator"] in user_roles_ids:
                    if message.content.lower().startswith("g! cw set shield"):
                        if "<@" in message.content:
                            # get target user
                            target_uid = int(message.content[message.content.index("<@") + 2:message.content.index(">")])
                            user = message.channel.guild.get_member(target_uid)
                            count = int(message.content[message.content.index(">") + 1:].strip())
                            if count > 5:
                                count = 5
                            await self.database.set_shields(user, count)
                    elif message.content.lower().startswith("g! cw set grenade"):
                        if "<@" in message.content:
                            # get target user
                            target_uid = int(message.content[message.content.index("<@") + 2:message.content.index(">")])
                            user = message.channel.guild.get_member(target_uid)
                            count = int(message.content[message.content.index(">") + 1:].strip())
                            if count > 5:
                                count = 5
                            await self.database.set_grenades(user, count)
                    elif message.content.lower().startswith("g! cw spawn item shield"):
                        count = int(message.content.replace("g! cw spawn item shield", "").strip())
                        post = "🎈🎈\n📦\nA color war supply box has spawned! React with 🫳 to grab it."
                        channel = CHANNEL_GEN_CHAT # (temp mod chat - 1210574473619709983)
                        #if "<#" in message.content:
                        #    channel = int(message.content[message.content.index("<#") + 2:message.content.index(">")])
                        spawn_msg = await message.guild.get_channel(channel).send(post)
                        await self.database.create_spawn(spawn_msg, "SHIELD", count)
                    elif message.content.lower().startswith("g! cw spawn item grenade"):
                        count = int(message.content.replace("g! cw spawn item grenade", "").strip())
                        post = "🎈🎈\n📦\nA color war supply box has spawned! React with 🫳 to grab it."
                        channel = CHANNEL_GEN_CHAT
                        spawn_msg = await message.guild.get_channel(channel).send(post)
                        await self.database.create_spawn(spawn_msg, "GRENADE", count)

            if message.content.lower().startswith("g! test"):
                await message.channel.send("/top type:Text page:1")
            #     async with aiohttp.ClientSession() as session:
            #         webhook = await self.get_channel_hook(message, session)
            #         await webhook.send("Test", ephemeral=True)
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
            elif message.content.lower().startswith("g! gag") and ((ROLES_ID_DICT["moderator"] in user_roles_ids) or (ROLES_ID_DICT["booster"] in user_roles_ids)):
                if "<@" in message.content:
                        # get target user
                        target_uid = int(message.content[message.content.index("<@") + 2:message.content.index(">")])
                        user = message.channel.guild.get_member(target_uid)
                        # check to make sure they're not a Dom
                        #if user.get_role(ROLE_DOM) == None:
                        # make sure it's not me :D
                        if target_uid != UID_GUARDIAN:
                            gagged = message.channel.guild.get_role(ROLE_GAGGED)
                            await user.add_roles(gagged)
            elif message.content.lower().startswith("g! ungag") and ((ROLES_ID_DICT["moderator"] in user_roles_ids) or (ROLES_ID_DICT["booster"] in user_roles_ids)):
                    if "<@" in message.content:
                        # get target user
                        target_uid = int(message.content[message.content.index("<@") + 2:message.content.index(">")])
                        user = message.channel.guild.get_member(target_uid)
                        if user.get_role(ROLE_GAGGED) != None:
                            gagged = message.channel.guild.get_role(ROLE_GAGGED)
                            await user.remove_roles(gagged)
            elif message.content.lower().startswith("g! heel") and ((ROLES_ID_DICT["moderator"] in user_roles_ids) or (ROLES_ID_DICT["booster"] in user_roles_ids)):
                    if "<@" in message.content:
                        # get target user
                        target_uid = int(message.content[message.content.index("<@") + 2:message.content.index(">")])
                        user = message.channel.guild.get_member(target_uid)
                        # check to make sure they're not a Dom
                        if (target_uid != UID_GUARDIAN) and (user.get_role(ROLE_DOM) == None and user.get_role(ROLE_PET_PLAY) != None):
                            heel = message.channel.guild.get_role(ROLE_HEEL)
                            await user.add_roles(heel)
            elif message.content.lower().startswith("g! good") and ((ROLES_ID_DICT["moderator"] in user_roles_ids) or (ROLES_ID_DICT["booster"] in user_roles_ids)):
                if "<@" in message.content:
                    # get target user
                    target_uid = int(message.content[message.content.index("<@") + 2:message.content.index(">")])
                    user = message.channel.guild.get_member(target_uid)
                    if user.get_role(ROLE_HEEL) != None:
                        heel = message.channel.guild.get_role(ROLE_HEEL)
                        await user.remove_roles(heel)
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
            elif message.content.lower().startswith("g! approve") and (ROLES_ID_DICT["moderator"] in user_roles_ids):
                await self.ticket_collect(message, APPROVAL_CHANNEL_ID)
            elif message.content.lower().startswith("g! reject") and (ROLES_ID_DICT["moderator"] in user_roles_ids):
                await self.ticket_collect(message, REJECTION_CHANNEL_ID)
            elif message.content.lower().startswith("g! shame") and (ROLES_ID_DICT["moderator"] in user_roles_ids):
                await self.ticket_collect(message, WALL_OF_SHAME_CHANNEL_ID)
            elif message.content.lower().startswith("g! icebreaker"):
                await self.get_next_question(message, "icebreakers", ICEBREAKER_CHANNEL_ID, "ICEBREAKER")
            elif message.content.lower().startswith("g! truth"):
                await self.get_next_question(message, "truths", T_OR_D_CHANNEL_ID, "TRUTH")
            elif message.content.lower().startswith("g! dare"):
                await self.get_next_question(message, "dares", T_OR_D_CHANNEL_ID, "DARE")
            elif message.content.lower().startswith("g! add") and self.get_user_prestige(message.author) > QUESTION_ADD_PRESTIGE_REQ:
                if message.content.lower().startswith("g! add icebreaker"):
                    await self.add_question(message, "icebreakers")
                elif message.content.lower().startswith("g! add truth"):
                    await self.add_question(message, "truths")
                elif message.content.lower().startswith("g! add dare"):
                    await self.add_question(message, "dares")
            elif message.content.lower().startswith("g! jigsaw") and (ROLES_ID_DICT["moderator"] in user_roles_ids):
                if "<@" in message.content:
                    # get target user
                    target_uid = int(message.content[message.content.index("<@") + 2:message.content.index(">")])
                    user = message.channel.guild.get_member(target_uid)
                    if target_uid != UID_GUARDIAN:
                        jigsaw = message.channel.guild.get_role(ROLE_JIGSAW)
                        await user.add_roles(jigsaw)
                    password = message.content[message.content.index(">") + 2:].strip()
                    if len(password) > 0:
                        JIGSAW_PASSWORD = password
                        author = message.author.display_name
                        self.logger.info(f"[JIGSAW] {author}: Updated password to \"{password}\"")
            elif message.content.lower().startswith("g! free") and (ROLES_ID_DICT["moderator"] in user_roles_ids):
                if "<@" in message.content:
                    # get target user
                    target_uid = int(message.content[message.content.index("<@") + 2:message.content.index(">")])
                    user = message.channel.guild.get_member(target_uid)
                    if user.get_role(ROLE_JIGSAW) != None:
                        jigsaw = message.channel.guild.get_role(ROLE_JIGSAW)
                        await user.remove_roles(jigsaw)
            elif message.content.lower().startswith("g! changepw") and (ROLES_ID_DICT["moderator"] in user_roles_ids):
                password = message.content.replace("g! changepw", "").strip()
                if len(password) > 0:
                    JIGSAW_PASSWORD = password
                    author = message.author.display_name
                    self.logger.info(f"[JIGSAW] {author}: Updated password to \"{password}\"")
            elif message.content.lower().startswith("g! collect stats") and (ROLES_ID_DICT["moderator"] in user_roles_ids):
                stats = await self.collect_membership_stats(message.guild)
                pos_bot = message.guild.get_role(ROLE_SEPERATOR_BOT).position
                pos_mid = message.guild.get_role(ROLE_SEPERATOR_MID).position
                pos_top = message.guild.get_role(ROLE_SEPERATOR_TOP).position
                kink_roles = []
                info_roles = []
                member_roles = []
                print("Processing Roles....")
                print(f"Positions: {pos_bot} - {pos_mid} - {pos_top}")
                for key,val in stats.items():
                    role = message.guild.get_role(key)
                    print(f"{role.position} - {role.name} - {val.member_count}")
                    await self.database.add_membership_stat(val.category, val.role_id, val.name, val.color, val.member_count)
                    # kinks
                    if role.position > pos_bot and role.position < pos_mid:
                        #kink_roles.insert(role.position - pos_bot - 1, [role, val])
                        kink_roles.append([role, val.member_count])
                    elif role.position > pos_mid and role.position < pos_top:
                        #info_roles.insert(role.position - pos_bot - 1, [role, val])
                        info_roles.append([role, val.member_count])
                    elif role.position > pos_top and (("Member" in role.name) or ("Prestige" in role.name)):
                        member_roles.append([role, val.member_count])
                # sort
                #kink_roles.sort(key=lambda x: x[0].position, reverse=True)
                kink_roles.sort(key=lambda x: x[1], reverse=True)
                info_roles.sort(key=lambda x: x[0].position, reverse=True)

                # dump stats
                msg = ""
                f = open("stats.txt", "w")
                f.write("Member Roles\n")
                msg += "Member Roles\n"
                f.write("=================================================\n")
                msg += "=================================================\n"
                for item in member_roles:
                    msg += f"{item[0].name}: {item[1]}\n"
                    f.write(f"{item[0].name}: {item[1]}\n")
                f.write("Info Roles\n")
                msg += "Info Roles\n"
                f.write("=================================================\n")
                msg += "=================================================\n"
                for item in info_roles:
                    msg += f"{item[0].name}: {item[1]}\n"
                    f.write(f"{item[0].name}: {item[1]}\n")
                f.write("=================================================\n")
                msg += "=================================================\n"
                f.write("Kink Roles\n")
                msg += "Kink Roles\n"
                f.write("=================================================\n")
                msg += "=================================================\n"
                for item in kink_roles:
                    msg += f"{item[0].name}: {item[1]}\n"
                    f.write(f"{item[0].name}: {item[1]}\n")
                f.close()
                await message.channel.send("Collection Complete - Check Server Files")

        # Events
        if (ROLES_ID_DICT["gagged"] in user_roles_ids) and message.author.id != UID_GUARDIAN:
            gagged_msg = ""
            author = message.author.display_name
            avatar = message.author.display_avatar.url
            self.logger.info(f"[Gagged] {author}: {message.content}")
            for word in message.content.split(" "):
                if "<@" in word or word.startswith(":"):
                    gagged_msg += word
                else:
                    if random.random() > 0.2:
                        gagged_msg += random.choice(GAG_LIST)
                        if word.endswith("!"):
                            gagged_msg += "!"
                        if word.endswith("."):
                            gagged_msg += "."
                    else:
                        gagged_msg += word
                    
                gagged_msg += " "
            async with aiohttp.ClientSession() as session:
                webhook = await self.get_channel_hook(message, session)
                await message.delete()
                await webhook.send(content=gagged_msg, username=author, avatar_url=avatar)
        elif (ROLES_ID_DICT["heel"] in user_roles_ids) and message.author.id != UID_GUARDIAN:
            heel_msg = ""
            author = message.author.display_name
            avatar = message.author.display_avatar.url
            self.logger.info(f"[Heel] {author}: {message.content}")
            for word in message.content.split(" "):
                if "<@" in word or word.startswith(":"):
                    heel_msg += word
                else:
                    if random.random() > 0.2:
                        heel_msg += random.choice(PET_LIST)
                        if word.endswith("!"):
                            heel_msg += "!"
                        if word.endswith("."):
                            heel_msg += "."
                    else:
                        heel_msg += word
                    
                heel_msg += " "
            
            async with aiohttp.ClientSession() as session:
                webhook = await self.get_channel_hook(message, session)
                await message.delete()
                await webhook.send(content=heel_msg, username=author, avatar_url=avatar)
        elif (ROLE_JIGSAW in user_roles_ids) and message.author.id != UID_GUARDIAN:
            if message.channel.id != CHANNEL_JIGSAW:
                author = message.author.display_name
                avatar = message.author.display_avatar.url
                self.logger.info(f"[JIGSAW] {author}: {message.content}")
                jigsaw_msg = f"I wanted to play games. Now I have to guess the magic words in <#{CHANNEL_JIGSAW}> to talk again."
                async with aiohttp.ClientSession() as session:
                    webhook = await self.get_channel_hook(message, session)
                    await message.delete()
                    await webhook.send(content=jigsaw_msg, username=author, avatar_url=avatar)
            elif message.content.lower().replace(",", "").replace("!","").replace(".", "") == JIGSAW_PASSWORD:
                jigsaw = message.channel.guild.get_role(ROLE_JIGSAW)
                await user.remove_roles(jigsaw)
        elif ((ROLE_NAUGHTY_MOD in user_roles_ids) #or message.author.id == 1066107260272640121)
                and message.author.id != UID_GUARDIAN
                and message.channel.category_id != CAT_ADMIN 
                and message.channel.category_id != CAT_WELCOME 
                and message.channel.category_id != CAT_TICKET_APP
                and message.channel.category_id != CAT_TICKET_REP
                and message.channel.category_id != CAT_TICKET_ADM):
            author = message.author.display_name
            avatar = message.author.display_avatar.url
            self.logger.info(f"[NAUGHTY] {author}: {message.content}")
            naughty_msg = random.choice(NAUGHTY_MOD_LIST)
            async with aiohttp.ClientSession() as session:
                webhook = await self.get_channel_hook(message, session)
                await message.delete()
                await webhook.send(content=naughty_msg, username=author, avatar_url=avatar)

    #async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
    # channel_id
    # emoji
    # event_type
    # guild_id
    # member
    # message_id
    # user_id
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if MODE_COLOR_WAR:
            #print(f"{payload.emoji.name}")
            #print(f"{'🫳' == payload.emoji.name}")
            if payload.emoji.id == EMOJI_PAINTBALL:
                message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                # check if it's already been used
                reactions = message.reactions
                for reaction in reactions:
                    async for user in reaction.users():
                        if user.id == BOT_ID:
                            dm_post = "The message you selected has already been used for Color War"
                            print(f"[COLORWAR] Sending DM to {payload.member.name}: {dm_post}")
                            dm_channel = await payload.member.create_dm()
                            await dm_channel.send(dm_post, suppress_embeds=True)
                            return
                # can we paintball?
                # 1. is it off cooldown? / do we have a stockpile
                team_id = await self.find_colorwar_team(payload.member.roles)
                print(f"TEAMID = {team_id}")
                if team_id:
                    last_shot = await self.database.last_paintball_fired(payload.member, team_id)
                    if last_shot:
                        last_shot = datetime.strptime(last_shot, '%Y-%m-%d %H:%M:%S.%f')
                        minutes_diff = (datetime.now() - last_shot).total_seconds() / 60.0
                        #print(f"{minutes_diff} = {datetime.now()} - {last_shot}")
                    else:
                        minutes_diff = COLORWAR_PAINTBALL_CD_MINS + 1
                    print(f"MIN DIF = {minutes_diff}")
                    if (minutes_diff >= COLORWAR_PAINTBALL_CD_MINS) or (await self.database.try_use_channel_paintball_supply(team_id)):
                        # 2. is the target a different color?
                        target_team_id = await self.find_colorwar_team(message.author.roles)
                        target_paint_role = await self.find_colorwar_paint(message.author.roles)
                        user_team_paint = COLORWAR_TEAM_PAINT_DICT[team_id]
                        # if (target_team_id                      # do they have a team?
                        #     #and (target_team_id != team_id)     # is it different from your team?
                        #     and (target_paint_role != user_team_paint)  # can they be painted your color?
                        # ):
                        # Check if target can absorb the paintball attempt
                        shield_points = int(await self.database.get_shields(message.author))
                        if team_id != target_team_id and shield_points > 0:
                            await message.add_reaction("🛡️")
                            await self.database.update_last_paintball_fired(payload.member, team_id)
                            await self.database.update_colorwar_log(message, payload.member.id, message.author.id, "SHIELDED", "PLAYER")
                            post = f"🛡️ **{payload.member.display_name}** ({payload.member.name}) just paintballed (shield absorbed) **{message.author.display_name}** ({message.author.name})"
                            print(post)
                            cw_channel = payload.member.guild.get_channel(CHANNEL_CW_LOG)
                            await cw_channel.send(post, suppress_embeds=True)
                            await self.database.set_shields(payload.member, (shield_points - 1))
                        else:
                            # remove old paint if they have one
                            await self.purge_colorwar_paints(message.author)
                            # if target_paint_role:
                            #     obj_paint_role_curr = message.channel.guild.get_role(target_paint_role)
                            #     message.author.remove_roles(obj_paint_role_curr)
                            # Give them the color role
                            obj_paint_role_new = message.channel.guild.get_role(user_team_paint)
                            await message.author.add_roles(obj_paint_role_new)
                            # Update cooldown
                            await self.database.update_last_paintball_fired(payload.member, team_id)
                            # Write Log
                            await self.database.update_colorwar_log(message, payload.member.id, message.author.id, "PAINTBALLED", "PLAYER")
                            # Write to Log Channel
                            post = f"{COLORWAR_TEAM_EMOJI_DICT[team_id]} **{payload.member.display_name}** ({payload.member.name}) just paintballed **{message.author.display_name}** ({message.author.name})"
                            print(post)
                            cw_channel = payload.member.guild.get_channel(CHANNEL_CW_LOG)
                            await cw_channel.send(post, suppress_embeds=True)
                            await message.add_reaction(COLORWAR_TEAM_EMOJI_DICT[team_id])
                        # else:
                        #     dm_post = f"Your target is already marked by your team color"
                        #     print(f"[COLORWAR] Sending DM to {payload.member.name}: {dm_post}")
                        #     dm_channel = await payload.member.create_dm()
                        #     await dm_channel.send(dm_post, suppress_embeds=True)

                        # Check to see if this helped take the channel
                        channel_stats = await self.database.get_single_channel_ownership_stats(message.channel.id)
                        print(channel_stats)
                        # make sure this is an ownable channel
                        if len(channel_stats) > 0:
                            last_ownership = datetime.strptime(channel_stats[0][8], '%Y-%m-%d %H:%M:%S')
                            minutes_diff = (datetime.now() - last_ownership).total_seconds() / 60.0
                            if minutes_diff >= COLORWAR_CHANNEL_CD_MINS:
                                channel_hit_count = await self.database.hit_count_in_channel_after_timestamp(message.channel.id, team_id, (last_ownership + timedelta(hours=1)) )
                                print(f'Channel_hit_count = {channel_hit_count} | channel_hp = {channel_stats[0][4]}')
                                # see if we've reached the hitpoint threshold
                                if channel_hit_count >= channel_stats[0][4]:
                                    await self.database.update_channel_ownership(message.channel.id, team_id)
                                    await message.channel.edit(name=f"{COLORWAR_BASE_CHANNEL_NAME[message.channel.id]}{COLORWAR_TEAM_EMOJI_DICT[team_id]}")
                                    role = message.guild.get_role(team_id)
                                    post = f"👑 {COLORWAR_TEAM_EMOJI_DICT[team_id]} {role.name} have just taken control of {message.channel.name}"
                                    print(post)
                                    cw_channel = payload.member.guild.get_channel(CHANNEL_CW_LOG)
                                    await cw_channel.send(post, suppress_embeds=True)
                        await self.refresh_colorwar_stats()
                    else:
                        dm_post = f"Your paintball gun is still on cooldown for: {round(COLORWAR_PAINTBALL_CD_MINS - minutes_diff, 2)} minutes"
                        print(f"[COLORWAR] Sending DM to {payload.member.name}: {dm_post}")
                        dm_channel = await payload.member.create_dm()
                        await dm_channel.send(dm_post, suppress_embeds=True)
            elif payload.emoji.id == EMOJI_GRENADE:
                grenade_count = int(await self.database.get_grenades(payload.member))
                if grenade_count > 0:
                    team_id = await self.find_colorwar_team(payload.member.roles)
                    user_team_paint = COLORWAR_TEAM_PAINT_DICT[team_id]
                    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    obj_paint_role_new = message.channel.guild.get_role(user_team_paint)
                    await self.purge_colorwar_paints(message.author)
                    await message.author.add_roles(obj_paint_role_new)
                    await self.database.update_colorwar_log(message, payload.member.id, message.author.id, "GRENADED", "PLAYER")
                    post = f"{COLORWAR_TEAM_EMOJI_DICT[team_id]} <:Grenade:{EMOJI_GRENADE}> **{payload.member.display_name}** ({payload.member.name}) just grenaded **{message.author.display_name}** ({message.author.name})"
                    cw_channel = payload.member.guild.get_channel(CHANNEL_CW_LOG)
                    await cw_channel.send(post, suppress_embeds=True)
                    await message.add_reaction(COLORWAR_TEAM_EMOJI_DICT[team_id])
                    await self.database.set_grenades(payload.member, (grenade_count - 1))
                    messages = [msg async for msg in message.channel.history(limit=4, before=message.created_at)]
                    for m in messages:
                        await self.purge_colorwar_paints(m.author)
                        await m.author.add_roles(obj_paint_role_new)
                        await self.database.update_colorwar_log(m, payload.member.id, m.author.id, "GRENADE-SPLASH", "PLAYER")
                        post = f"{COLORWAR_TEAM_EMOJI_DICT[team_id]} 💥 **{payload.member.display_name}** ({payload.member.name}) grenade just splashed **{m.author.display_name}** ({m.author.name})"
                        await cw_channel.send(post, suppress_embeds=True)
                        await m.add_reaction("💥")
                        await m.add_reaction(COLORWAR_TEAM_EMOJI_DICT[team_id])
                else:
                    dm_post = "You do not have any grenades in your inventory"
                    print(f"[COLORWAR] Sending DM to {payload.member.name}: {dm_post}")
                    dm_channel = await payload.member.create_dm()
                    await dm_channel.send(dm_post, suppress_embeds=True)
            elif '🫳' == payload.emoji.name:
                message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                user_grabbed = await self.database.consume_spawn(message, payload.member.id)
                print(f"{payload.member.display_name} grabbed the item => {user_grabbed}")
                if user_grabbed:
                    spawn = await self.database.get_spawn(message)
                    item_type = spawn[4]
                    if item_type == "SHIELD":
                        curr_shields = await self.database.get_shields(payload.member)
                        spawn_shields = spawn[5]
                        print(f"Updating shields for member {payload.member.display_name} to {curr_shields + spawn_shields}")
                        await self.database.set_shields(payload.member, (curr_shields + spawn_shields))
                        dm_post = f"You've picked up {spawn_shields} 🛡️. It has been added to your inventory for a total of: {curr_shields + spawn_shields}"
                        print(f"[COLORWAR] Sending DM to {payload.member.name}: {dm_post}")
                        dm_channel = await payload.member.create_dm()
                        await dm_channel.send(dm_post, suppress_embeds=True)
                    elif item_type == "GRENADE":
                        curr_grenades = await self.database.get_shields(payload.member)
                        spawn_grenades = spawn[5]
                        print(f"Updating grenades for member {payload.member.display_name} to {curr_grenades + spawn_grenades}")
                        await self.database.set_shields(payload.member, (curr_grenades + spawn_grenades))
                        dm_post = f"You've picked up {spawn_grenades} <:Grenade:{EMOJI_GRENADE}>. It has been added to your inventory for a total of: {curr_grenades + spawn_grenades}"
                        print(f"[COLORWAR] Sending DM to {payload.member.name}: {dm_post}")
                        dm_channel = await payload.member.create_dm()
                        await dm_channel.send(dm_post, suppress_embeds=True)

        if payload.emoji.id == EMOJI_NUT_BUTTON:
            message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            # make sure this isn't in places people can't see or for non-members
            if (    message.author.id != payload.user_id
                and message.channel.category_id != CAT_ADMIN 
                and message.channel.category_id != CAT_WELCOME 
                and message.channel.category_id != CAT_TICKET_APP
                and message.channel.category_id != CAT_TICKET_REP
                and message.channel.category_id != CAT_TICKET_ADM):
                    await message.clear_reaction(payload.emoji)
                    self.logger.info(f"[REACT] {payload.emoji.name} ({payload.emoji.id}) used on {message.id} by {payload.member.display_name}")
                    content_type = "text"
                    if message.attachments:
                        msg_content = message.attachments[0].content_type
                        content_type = msg_content[:msg_content.index("/")]
                    if message.embeds and message.embeds[0].url:
                        content_type = "link"
                    
                    add_success = await self.database.add_nut(payload.user_id, payload.guild_id, payload.channel_id, payload.message_id, message.author.id, content_type)
                    if add_success:
                        nut_channel = payload.member.guild.get_channel(CHANNEL_NUT)
                        nut_count_author = await self.database.get_nut_count_author(message.author.id)
                        #nut_count_author = nut_count_author.replace("(", "").replace(")", "").replace(",", "")
                        nut_count_content = await self.database.get_nut_count_message(payload.guild_id, payload.channel_id, payload.message_id)
                        #nut_count_content = nut_count_content.replace("(", "").replace(")", "").replace(",", "")
                        #post = f"Someone Just NUTTED to {message.jump_url}!\n<@{message.author.id}>'s Content Nut Count: `{nut_count_author[0]}`\nThis Message's Nut Count: `{nut_count_content[0]}`\nContent Type: `{content_type}`"
                        post = f"Someone Just NUTTED to {message.jump_url}!\n{message.author.display_name}'s ({message.author.name}) Content Nut Count: `{nut_count_author[0]}`\nThis Message's Nut Count: `{nut_count_content[0]}`\nContent Type: `{content_type}`"
                        await nut_channel.send(post, suppress_embeds=True)

                


        


# =======================================================
# MAIN
# =======================================================

load_dotenv()
bot = GuardianBot()
#colorwar_scheduled_job.start()
bot.run(os.getenv("TOKEN"))