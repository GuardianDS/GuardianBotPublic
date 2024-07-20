import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import gw_constants
import requests
import os

class Moderation(commands.Cog, name="moderation"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="approve", description="[User] [Note] [Quiet - Don't Announce in Gen Chat, defaults False] => Approve an applicant's ticket"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def approve(self, context: Context, user: discord.User, note: str = None, quiet: bool = False) -> None:
        await context.defer() # takes longer than 3 seconds so buy some extra time - https://stackoverflow.com/questions/73361556/error-discord-errors-notfound-404-not-found-error-code-10062-unknown-inter

        # Capture Ticket Responses (do this first in case we're trying to capture an old ticket where the user already had left)
        approved = await self.ticket_collect(context, user, gw_constants.CHANNEL_APPROVAL, note)

        user = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        # Remove Onboarding Roles
        await user.remove_roles(context.guild.get_role(gw_constants.ROLE_REGISTRATION_INIT),
                                context.guild.get_role(gw_constants.ROLE_REGISTRATION_1_ACCESS),
                                context.guild.get_role(gw_constants.ROLE_REGISTRATION_2_RULES),
                                context.guild.get_role(gw_constants.ROLE_REGISTRATION_3_ROLES),
                                context.guild.get_role(gw_constants.ROLE_REGISTRATION_COMPLETE),
                                context.guild.get_role(gw_constants.ROLE_REGISTRATION_HONEYPOT))
        # Grant Membership
        await user.add_roles(context.guild.get_role(gw_constants.ROLE_MEMBER))

        # Grant Optional Views
        if (user.get_role(gw_constants.ROLE_RACEPLAY) is not None):
            await user.add_roles(context.guild.get_role(gw_constants.ROLE_VIEW_RACEPLAY))
        if (user.get_role(gw_constants.ROLE_CNC) is not None):
            await user.add_roles(context.guild.get_role(gw_constants.ROLE_VIEW_CNC))
        if (user.get_role(gw_constants.ROLE_HIGH_PROTOCOL) is not None):
            await user.add_roles(context.guild.get_role(gw_constants.ROLE_VIEW_HIGH_PROTOCOL))
        if (user.get_role(gw_constants.ROLE_RIMMING) is not None):
            await user.add_roles(context.guild.get_role(gw_constants.ROLE_VIEW_RIMMING))

        # Make sure they have a DM Role / default to "DMs Ask"
        if (    user.get_role(gw_constants.ROLE_DM_OPEN) is None
            and user.get_role(gw_constants.ROLE_DM_REGULARS) is None
            and user.get_role(gw_constants.ROLE_DM_ASK) is None
            and user.get_role(gw_constants.ROLE_DM_CLOSED) is None):
            await user.add_roles(context.guild.get_role(gw_constants.ROLE_DM_ASK))

        if approved:
            # Send Message to Gen Chat
            if not quiet:
                join_message = f"Welcome our newest member <@{user.id}> <:hype:1209858652522024990>"
                await context.guild.get_channel(gw_constants.CHANNEL_GEN_CHAT).send(join_message)

            # Message so the command completes successfully
            await context.send(f"Member <@{user.id}> Approved")
        else:
            await context.send("❌ Error: Could Not Find Ticket Channel for Given User")

    @commands.hybrid_command(
        name="reject", description="[User] [Note] [Quiet - Don't Post Note] [Ban - defaults False] => Reject an applicant's ticket"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def reject(self, context: Context, user: discord.User, note: str = None, quiet: bool = False, ban: bool = False) -> None:
        await context.defer() # takes longer than 3 seconds so buy some extra time
        collect_success = True
        if not quiet:
            collect_success = await self.ticket_collect(context, user, gw_constants.CHANNEL_REJECTION, note)

        if collect_success:
            #TODO: Handle case where user has already left the server
            member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
            if not note or len(note) == 0:
                note = "Rejected Application"

            if ban:
                await member.ban(reason=note)
                await context.send("Member Rejected and Banned")
            else:
                await member.kick(reason=note)
                await context.send(f"Member <@{user.id}> Rejected and Kicked")
        else:
            await context.send("❌ Error: Could Not Find Ticket Channel for Given User")

    @commands.hybrid_command(
        name="shame", description="[User] [Note] [Quiet - Don't Post Note] => Reject an applicant's ticket w/ ban"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def shame(self, context: Context, user: discord.User, note: str = None, quiet: bool = False) -> None:
        await context.defer() # takes longer than 3 seconds so buy some extra time
        collect_success = True
        if not quiet:
            collect_success = await self.ticket_collect(context, user, gw_constants.CHANNEL_WALL_OF_SHAME, note)

        if collect_success:
            member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
            if not note or len(note) == 0:
                note = "Wall of Shame Application"

            await member.ban(reason=note)
            await context.send(f"Member <@{user.id}> Wall of Shamed and Banned")
        else:
            await context.send("❌ Error: Could Not Find Ticket Channel for Given User")

    @commands.hybrid_command(
        name="verify", description="[User] [Note] [Quiet - Don't Post Note] => Verifies a user (only JPG, JPEG, and PNG accepted)"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def verify(self, context: Context, user: discord.User, note: str = None, quiet: bool = False) -> None:
        await context.defer() # takes longer than 3 seconds so buy some extra time

        # Find Verification Ticket
        ticket_channel = await self.find_ticket(context, user, gw_constants.CATEGORY_VERIFY_TICKETS)

        images = []
        if ticket_channel is not None:
            async for msg in ticket_channel.history(limit=100):
                # find images
                if  (   msg.author.id == user.id
                    and len(msg.attachments) > 0):
                    for attachment in msg.attachments:
                        if (attachment.filename.endswith(".jpg")
                        or attachment.filename.endswith(".jpeg")
                        or attachment.filename.endswith(".png")):
                            img_data = requests.get(attachment.url).content
                            images.append(attachment.filename)
                            with open(f"verification\\{attachment.filename}", "wb") as handler:
                                handler.write(img_data)
            upload_files = []
            for image in images:
                upload_files.append(discord.File(f"verification\\{image}"))
            post = f"Verification for <@{user.id}> (UID: `{user.id}`)"
            await context.guild.get_channel(gw_constants.CHANNEL_VERIFY).send(post, files=upload_files)
            # Cleanup
            for image in images:
                os.remove(f"verification\\{image}")

            # Grant Role
            await user.add_roles(context.guild.get_role(gw_constants.ROLE_VERIFIED))

            # Give Success Feedback
            await context.send(f"User <@{user.id}> has been verified")
        else:
            await context.send("❌ Error: Could Not Find Verification Ticket Channel for Given User")

    @commands.hybrid_command(
        name="testapprove", description="[User] [Note] => Tests approve command"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def test_approve(self, context: Context, user: discord.User, note: str = None) -> None:
        post = f"Test for <@{user.id}> (UID: `{user.id}`)"
        if (note is not None) or (len(note.strip()) > 0):
                post += f"\n*NOTE: {note}*"

        await context.guild.get_channel(1205994621658996746).send(post)        

    # =======================================================
    # HELPER
    # =======================================================
    async def find_ticket(self, context: Context, user: discord.User, ticket_type: int) -> discord.TextChannel:
        #print("Find Ticket:")
        # async for message in user.history(limit=100):
        #     print(f"History - {message.channel.name:}")
        #     if "ticket-" in message.channel.name:
        #         return message.channel
        for channel in context.guild.text_channels:
            if channel.category_id == ticket_type:
                async for message in channel.history(limit=100):
                    if message.author.id == user.id:
                        return channel

            # fetchMessage = (await channel.history()).find(lambda m: m.author.id == user.id)
            # if fetchMessage is None:
            #     continue
            # elif "ticket-" in fetchMessage.channel.name:
            #     return fetchMessage.channel

        return None

    async def ticket_collect(self, context: Context, user: discord.User, target_channel_id: int, note: str) -> bool:
        ticket_channel = await self.find_ticket(context, user, gw_constants.CATEGORY_APPROVAL_TICKETS)
        if ticket_channel is not None:
            post = f"<@{user.id}> (ID: `{user.id}`)\nDisplay Name: `{user.display_name}`\nUser Name: `{user.name}`\n"
            post += "\n```\n"
            history = ""
            async for msg in ticket_channel.history(limit=100):
                if msg.author.id == user.id:
                    history = f"{msg.content}\n" + history
            post += history
            post += "```"
            if (note is not None) and (len(note.strip()) > 0):
                post += f"*NOTE: {note}*"
            await context.guild.get_channel(target_channel_id).send(post)
            return True
        else:
            return False

async def setup(bot) -> None:
    await bot.add_cog(Moderation(bot))