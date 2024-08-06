import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import gw_constants

class ColorWar(commands.Cog, name="colorwar"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # ==============================================================================
    # CONSTANTS
    # ==============================================================================

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
    MODE_COLOR_WAR = False

    CHANNEL_CW_LOG = 1245628559553462294
    CW_STATS_MESSAGE_ID = 1246106979316011121
    CHANNEL_CW_STATS = 1245628410479247423

    # ==============================================================================
    # HELPERS
    # ==============================================================================

    async def export_teams(self, guild: discord.Guild):
        with open('events/colorwar_teams.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            header = ['UserID', 'DisplayName', 'UserName', 'TeamID', 'TeamName']
            writer.writerow(header)

            async for member in guild.fetch_members():
                data_row = []
                data_row.append(member.id)
                data_row.append(member.display_name)
                data_row.append(member.name)
                for role in member.roles:
                    if role.id in self.COLORWAR_TEAMS:
                        data_row.append(role.id)
                        data_row.append(role.name)
                
                writer.writerow(data_row)

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

    # ==============================================================================
    # COMMANDS
    # ==============================================================================

    # ~~~~~~~~~~~~~~~~
    # INIT
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="cw init", description="Initializes Color War"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN)
    async def cw_init(self, context: Context) -> None:
        #TODO: setup work
        await context.channel.send("init")

    # ~~~~~~~~~~~~~~~~
    # DUMP TEAMS
    # ~~~~~~~~~~~~~~~~

    @commands.hybrid_command(
        name="cw-dump-teams", description="Dumps team rosters to a text file server side"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN)
    async def cw_dump_teams(self, context: Context) -> None:
        await self.export_teams(context.guild)

    # ~~~~~~~~~~~~~~~~
    # REFRESH
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="cw-refresh", description="Force Refresh the stats"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN)
    async def cw_refresh(self, context: Context) -> None:
        await self.refresh_colorwar_stats()

    # ~~~~~~~~~~~~~~~~
    # SEED
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="cw-seed", description="Seed teams"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN)
    async def cw_seed(self, context: Context) -> None:
        await self.seed_colorwar(context.guild)

    # ~~~~~~~~~~~~~~~~
    # CLEAR
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="cw-clear", description="Clear all"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN)
    async def cw_clear(self, context: Context) -> None:
        roles = []
        for role in self.COLORWAR_TEAMS:
            roles.append(context.guild.get_role(role))
        for role in self.COLORWAR_PAINTS:
            roles.append(context.guild.get_role(role))
        async for member in context.channel.guild.fetch_members():
            for role in roles:
                await member.remove_roles(role)

    # ~~~~~~~~~~~~~~~~
    # SET SHIELD
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="cw-set-shield", description="Overrides a user's shields with this value"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def cw_set_shield(self, context: Context, user: discord.User, count: int) -> None:
        if count > 5:
            count = 5
        await self.bot.database.set_shields(user, count)

    # ~~~~~~~~~~~~~~~~
    # SET GRENADE
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="cw-set-grenade", description="Overrides a user's grenades with this value"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def cw_set_grenade(self, context: Context, user: discord.User, count: int) -> None:
        if count > 5:
            count = 5
        await self.bot.database.set_grenades(user, count)

    # ~~~~~~~~~~~~~~~~
    # SPAWN SHIELD
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="cw-spawn-item-shield", description="Spawns a supply box with the given number of shields in it"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def cw_spawn_shield(self, context: Context, count: int) -> None:
        post = "🎈🎈\n📦\nA color war supply box has spawned! React with 🫳 to grab it."
        channel = gw_constants.CHANNEL_GEN_CHAT # (temp mod chat - 1210574473619709983)
        spawn_msg = await context.guild.get_channel(channel).send(post)
        await self.bot.database.create_spawn(spawn_msg, "SHIELD", count)

    # ~~~~~~~~~~~~~~~~
    # SPAWN GRENADE
    # ~~~~~~~~~~~~~~~~
    @commands.hybrid_command(
        name="cw-spawn-item-grenade", description="Spawns a supply box with the given number of grenades in it"
    )
    @discord.ext.commands.has_any_role(gw_constants.ROLE_ADMIN, gw_constants.ROLE_MODERATOR)
    async def cw_spawn_shield(self, context: Context, count: int) -> None:
        post = "🎈🎈\n📦\nA color war supply box has spawned! React with 🫳 to grab it."
        channel = gw_constants.CHANNEL_GEN_CHAT # (temp mod chat - 1210574473619709983)
        spawn_msg = await context.guild.get_channel(channel).send(post)
        await self.bot.database.create_spawn(spawn_msg, "GRENADE", count)

    # ==============================================================================
    # EVENT LISTENERS
    # https://stackoverflow.com/questions/76279755/how-can-i-use-cogs-discord-py
    # ==============================================================================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if self.MODE_COLOR_WAR:
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

async def setup(bot) -> None:
    await bot.add_cog(ColorWar(bot))