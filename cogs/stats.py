import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import gw_constants
from stats.membership_data import MembershipData

class Stats(commands.Cog, name="stats"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # =======================================================
    # UTILITY FUNCTIONS
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

    # ==============================================================================
    # COMMANDS
    # ==============================================================================
    
    @commands.hybrid_command(
        name="collect-stats", description="List all commands the bot has loaded."
    )
    async def collect_stats(self, context: Context) -> None:
        message = context.message
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

async def setup(bot) -> None:
    await bot.add_cog(Stats(bot))