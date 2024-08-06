import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import gw_constants
from discord import Webhook
import aiohttp
import random

class Fun(commands.Cog, name="fun"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # ==============================================================================
    # CONSTANTS
    # ==============================================================================
    GAG_LIST = ["mmn", "glr", "ffmph", "gah", "hlur", "oog", "mrrrr", "shlur"]
    PET_LIST = ["woof", "bark", "yip", "ruff", "grrr", "arf"]
    NAUGHTY_MOD_LIST = ["Make yourself at home. Use my face as your throne. I'll patiently worship while you play with your phone",
                        "I'm a dirty little slut, I like it up my butt. Now I'll bend over so you can give me your hot nut!",
                        "I ain't just a tinderella, I'll drop to my knees for a fella. I've been quite a baddie, now punish me daddy!",
                        "Glug glug glug. Please give me your milk to chug. Make me a sight, my belly is too light!",
                        "Take off your belt, I want to earn my stripes. Make it hurt so I can show off my pipes!",
                        "I have a huge dildo collection. But no, I won't share, I'm just flexin'",
                        "Big white cock is my religion. It came to me in a vision. Get bleach in my eyes. Spread my thighs. My ass is ready for that collision.",
                        "I have a tight butt. I need it loosened up. So spin me around, and dick me down. I'll even back it up."]
    
    # Technically these two aren't constants but w/e
    HOOKS_CACHE = {}
    JIGSAW_PASSWORD = "im sorry"

    # ==============================================================================
    # CUSTOM CHECKS
    # https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#checks
    # ==============================================================================

    # ==============================================================================
    # HELPERS
    # ==============================================================================

    # See if we have the id cached => return the webhook
    # otherwise lazy load it into the cache
    async def get_channel_hook(self, message: discord.Message, session):
        hook = None

        if message.channel.id in self.HOOKS_CACHE:
            hook = self.HOOKS_CACHE.get(message.channel.id)
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
            self.HOOKS_CACHE[message.channel.id] = hook

        webhook = Webhook.from_url(hook.url, session=session)
        return webhook

    async def garble_message(self, message: discord.Message, type: str, word_list: list, chance: float) -> None:
        msg = ""
        author = message.author.display_name
        avatar = message.author.display_avatar.url
        self.bot.logger.info(f"[{type}] {author}: {message.content}")
        for word in message.content.split(" "):
            if "<@" in word or word.startswith(":"):
                msg += word
            else:
                if random.random() > chance:
                    msg += random.choice(word_list)
                    if word.endswith("!"):
                        msg += "!"
                    if word.endswith("."):
                        msg += "."
                else:
                    msg += word
            msg += " "
        async with aiohttp.ClientSession() as session:
            webhook = await self.get_channel_hook(message, session)
            await message.delete()
            await webhook.send(content=msg, username=author, avatar_url=avatar)

    # ==============================================================================
    # COMMANDS
    # ==============================================================================

    # ~~~~~~~~~~~~~~~~
    # GAG
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="gag", description="[User] [Quiet (default: false)] => gags target user"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR, gw_constants.ROLE_BOOSTER)
    async def gag(self, context: Context, user: discord.User, quiet: bool = False) -> None:
        user = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        if user.id != gw_constants.UID_GUARDIAN:
            gagged = context.guild.get_role(gw_constants.ROLE_GAGGED)
            await user.add_roles(gagged)
            if quiet:
                await context.send(f"✅ Successfully Gagged {user.display_name}.", ephemeral=True, delete_after=5.0)
            else:
                await context.send(f"<:ballgag:1209745312965591040> Gagged {user.display_name}.", ephemeral=False)
        else:
            await context.send(f"❌ SMH you think I'd let you animals gag me?", ephemeral=True, delete_after=5.0)

    @commands.hybrid_command(
        name="ungag", description="[User] [Quiet (default: false)] => ungags target user"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR, gw_constants.ROLE_BOOSTER)
    async def ungag(self, context: Context, user: discord.User, quiet: bool = False) -> None:
        user = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        if user.get_role(gw_constants.ROLE_GAGGED) != None:
            gagged = context.guild.get_role(gw_constants.ROLE_GAGGED)
            await user.remove_roles(gagged)
            if quiet:
                await context.send(f"✅ Successfully Ungagged {user.display_name}.", ephemeral=True, delete_after=5.0)
            else:
                await context.send(f"😮 Ungagged {user.display_name}.", ephemeral=False)
        else:
            await context.send(f"❌ {user.display_name} did not have the Gagged role", ephemeral=True, delete_after=5.0)

    # ~~~~~~~~~~~~~~~~
    # HEEL
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="heel", description="[User] [Quiet (false)] => heels target (doesn't work on Doms and those w/o a Pet Play kink role)"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR, gw_constants.ROLE_BOOSTER)
    async def heel(self, context: Context, user: discord.User, quiet: bool = False) -> None:
        user = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        if (user.id != gw_constants.UID_GUARDIAN) and (user.get_role(gw_constants.ROLE_DOM) == None and user.get_role(gw_constants.ROLE_PET_PLAY) != None):
            heel = context.guild.get_role(gw_constants.ROLE_HEEL)
            await user.add_roles(heel)
            if quiet:
                await context.send(f"✅ Successfully Heeled {user.display_name}.", ephemeral=True, delete_after=5.0)
            else:
                await context.send(f"<:collar:1209736715124871250> Heeled {user.display_name}.", ephemeral=False)
        else:
            await context.send("❌ User cannot be heeled (does not work on Doms and those without a Pet Play kink role)", ephemeral=True, delete_after=5.0)


    @commands.hybrid_command(
        name="good", description="[User] [Quiet (default: false)] => releases target user from heel"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR, gw_constants.ROLE_BOOSTER)
    async def good(self, context: Context, user: discord.User, quiet: bool = False) -> None:
        user = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        if user.get_role(gw_constants.ROLE_HEEL) != None:
            gagged = context.guild.get_role(gw_constants.ROLE_HEEL)
            await user.remove_roles(gagged)
            if quiet:
                await context.send(f"✅ Successfully released {user.display_name} from heel.", ephemeral=True, delete_after=5.0)
            else:
                await context.send(f"#<:headpat:1210213136263675986> Good {user.display_name}", ephemeral=False)
        else:
            await context.send(f"❌ {user.display_name} did not have the Heel role", ephemeral=True, delete_after=5.0)

    # ~~~~~~~~~~~~~~~~
    # JIGSAW
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="jigsaw", description="[User] [OPT: PW] => Jigsaws a user and sets their escape password if given"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def jigsaw(self, context: Context, user: discord.User, password: str = None) -> None:
        user = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        #global JIGSAW_PASSWORD
        if user.id != gw_constants.UID_GUARDIAN:
            jigsaw = context.guild.get_role(gw_constants.ROLE_JIGSAW)
            await user.add_roles(jigsaw)
            pw_msg = ""
            if password is not None:
                self.JIGSAW_PASSWORD = password
                pw_msg = f", and updated the jigsaw password to '{password}'"
            else:
                pw_msg = f", and jigsaw password remains '{self.JIGSAW_PASSWORD}'"
                self.bot.logger.info(f"[JIGSAW] {author}: Updated password to \"{password}\"")
            await context.send(f"✅ Successfully Jigsawed {user.display_name}{pw_msg}.", ephemeral=True, delete_after=5.0)
        else:
            await context.send("❌ Keep Dreaming", ephemeral=True, delete_after=5.0)

    @commands.hybrid_command(
        name="changepw", description="[NEW PASS] => updates the jigsaw room password to the given"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def changepw(self, context: Context, password: str) -> None:
        #global JIGSAW_PASSWORD
        if len(password.strip()) > 0:
            self.JIGSAW_PASSWORD = password
            author = message.author.display_name
            self.bot.logger.info(f"[JIGSAW] {author}: Updated password to \"{password}\"")
            await context.send(f"✅ successfully updated jigsaw password to '{password}'", ephemeral=True, delete_after=5.0)
        else:
            await context.send("❌ No Password Provided", ephemeral=True, delete_after=5.0)

    @commands.hybrid_command(
        name="free", description="[User] => Frees user from jigsaw room"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def free(self, context: Context, user: discord.User) -> None:
        user = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        if user.get_role(gw_constants.ROLE_JIGSAW) != None:
            jigsaw = context.guild.get_role(gw_constants.ROLE_JIGSAW)
            await user.remove_roles(jigsaw)
            await context.send(f"✅ Successfully released {user.display_name} from the jigsaw room.", ephemeral=True, delete_after=5.0)
        else:
            await context.send(f"❌ {user.display_name} did not have the Jigsaw role", ephemeral=True, delete_after=5.0)


    @commands.hybrid_command(
        name="dye", description="[User] => Frees user from jigsaw room"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_PAINTBUCKET)
    async def dye(self, context: Context, user: discord.Member, color: str) -> None:
        color = color.strip().lower() #sanitize
        color = "pastel " + color
        # remove current color role
        for clr in COLORS_ID_DICT.values():
            await user.remove_roles(self.bot.get_role(clr, context.channel.guild))
        await target.add_roles(self.get_role(COLORS_ID_DICT[color], message.channel.guild))

    # ==============================================================================
    # EVENT LISTENERS
    # https://stackoverflow.com/questions/76279755/how-can-i-use-cogs-discord-py
    # ==============================================================================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        global JIGSAW_PASSWORD
        if message.author == self.bot.user or message.author.bot:
            return

        user_roles_ids = []
        for role in message.author.roles:
            user_roles_ids.append(role.id)

        if (gw_constants.ROLE_GAGGED in user_roles_ids) and message.author.id != gw_constants.UID_GUARDIAN:
            await self.garble_message(message, "Gagged", self.GAG_LIST, 0.2)
        elif (gw_constants.ROLE_HEEL in user_roles_ids) and message.author.id != gw_constants.UID_GUARDIAN:
            await self.garble_message(message, "Heel", self.PET_LIST, 0.2)
        elif (gw_constants.ROLE_JIGSAW in user_roles_ids) and message.author.id != gw_constants.UID_GUARDIAN:
            if message.channel.id != CHANNEL_JIGSAW:
                author = message.author.display_name
                avatar = message.author.display_avatar.url
                self.bot.logger.info(f"[JIGSAW] {author}: {message.content}")
                jigsaw_msg = f"I wanted to play games. Now I have to guess the magic words in <#{CHANNEL_JIGSAW}> to talk again."
                async with aiohttp.ClientSession() as session:
                    webhook = await self.get_channel_hook(message, session)
                    await message.delete()
                    await webhook.send(content=jigsaw_msg, username=author, avatar_url=avatar)
            elif message.content.lower().replace(",", "").replace("!","").replace(".", "") == JIGSAW_PASSWORD.lower().replace(",", "").replace("!","").replace(".", ""):
                jigsaw = message.channel.guild.get_role(ROLE_JIGSAW)
                await user.remove_roles(jigsaw)
        elif ((gw_constants.ROLE_NAUGHTY_MOD in user_roles_ids) #or message.author.id == 1066107260272640121)
                and message.author.id != gw_constants.UID_GUARDIAN
                and message.channel.category_id != gw_constants.CATEGORY_ADMIN 
                and message.channel.category_id != gw_constants.CATEGORY_WELCOME 
                and message.channel.category_id != gw_constants.CATEGORY_APPROVAL_TICKETS
                and message.channel.category_id != gw_constants.CATEGORY_REPORT_TICKETS
                and message.channel.category_id != gw_constants.CATEGORY_ADMIN_TICKETS):
            author = message.author.display_name
            avatar = message.author.display_avatar.url
            self.bot.logger.info(f"[NAUGHTY] {author}: {message.content}")
            naughty_msg = random.choice(self.NAUGHTY_MOD_LIST)
            async with aiohttp.ClientSession() as session:
                webhook = await self.get_channel_hook(message, session)
                await message.delete()
                await webhook.send(content=naughty_msg, username=author, avatar_url=avatar)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.emoji.name == '📌':
            admin_bot_commands = payload.member.guild.get_channel(1205994621658996746)
            post = "Test 📌"
            await admin_bot_commands.send(post)
        elif payload.emoji.id == gw_constants.EMOJI_NUT_BUTTON:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            # make sure this isn't in places people can't see or for non-members
            if (    message.author.id != payload.user_id
                and message.channel.category_id != gw_constants.CATEGORY_ADMIN 
                and message.channel.category_id != gw_constants.CATEGORY_WELCOME 
                and message.channel.category_id != gw_constants.CATEGORY_APPROVAL_TICKETS
                and message.channel.category_id != gw_constants.CATEGORY_REPORT_TICKETS
                and message.channel.category_id != gw_constants.CATEGORY_ADMIN_TICKETS):
                    await message.clear_reaction(payload.emoji)
                    self.bot.logger.info(f"[REACT] {payload.emoji.name} ({payload.emoji.id}) used on {message.id} by {payload.member.display_name}")
                    content_type = "text"
                    if message.attachments:
                        msg_content = message.attachments[0].content_type
                        content_type = msg_content[:msg_content.index("/")]
                    if message.embeds and message.embeds[0].url:
                        content_type = "link"
                    
                    add_success = await self.bot.database.add_nut(payload.user_id, payload.guild_id, payload.channel_id, payload.message_id, message.author.id, content_type)
                    if add_success:
                        nut_channel = payload.member.guild.get_channel(gw_constants.CHANNEL_NUT)
                        nut_count_author = await self.bot.database.get_nut_count_author(message.author.id)
                        nut_count_content = await self.bot.database.get_nut_count_message(payload.guild_id, payload.channel_id, payload.message_id)
                        post = f"Someone Just NUTTED to {message.jump_url}!\n{message.author.display_name}'s ({message.author.name}) Content Nut Count: `{nut_count_author[0]}`\nThis Message's Nut Count: `{nut_count_content[0]}`\nContent Type: `{content_type}`"
                        await nut_channel.send(post, suppress_embeds=True)



async def setup(bot) -> None:
    await bot.add_cog(Fun(bot))