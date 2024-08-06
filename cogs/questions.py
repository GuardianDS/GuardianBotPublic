import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import gw_constants

ICEBREAKER_CHANNEL_ID = 1214760927841222666
T_OR_D_CHANNEL_ID = 1206114770122707015

class Questions(commands.Cog, name="questions"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="icebreaker", description="Pull a new icebreaker question to be sent in the icebreaker channel"
    )
    async def icebreaker(self, context: Context) -> None:
        await self.get_next_question(context, "icebreakers", ICEBREAKER_CHANNEL_ID, "ICEBREAKER")
        await context.send("Retrieved Icebreaker!", ephemeral=True, delete_after=5)

    @commands.hybrid_command(
        name="truth", description="Pull a new truth to be sent in the T or D channel"
    )
    async def truth(self, context: Context) -> None:
        await self.get_next_question(context, "truths", T_OR_D_CHANNEL_ID, "TRUTH")
        await context.send("Retrieved Truth!", ephemeral=True, delete_after=5)

    @commands.hybrid_command(
        name="dare", description="Pull a new dare to be sent in the T or D channel"
    )
    async def dare(self, context: Context) -> None:
        await self.get_next_question(context, "dares", T_OR_D_CHANNEL_ID, "DARE")
        await context.send("Retrieved Dare!", ephemeral=True, delete_after=5)

    # =======================================================
    # UTILITY FUNCTIONS
    # =======================================================

    async def get_next_question(self, context: Context, category: str, channel: int, prefix: str):
        # check to see if we hit the end of the list
        q_max = await self.bot.database.get_shuffled_count(category)
        q_count = await self.bot.database.get_counter(category)

        # regenerate if so
        if (q_count >= q_max) or q_max == 0:
            await self.bot.database.clear_shuffled_questions(category)
            questions = await self.bot.database.get_questions(category)
            random.shuffle(questions) # shuffles in place
            count = 0
            for q in questions:
                q_id = q[0]
                q_ques = q[3]
                await self.bot.database.add_shuffled_question(q_id, count, category, q_ques)
                count += 1
            await self.bot.database.reset_counter(category)
            q_count = 0

        # fetch next question in sequence and progress counter
        result_question = f"**{prefix}:** "
        result_question += await self.bot.database.get_shuffled_question(q_count, category)
        await self.bot.database.progress_counter(category)
        await context.channel.guild.get_channel(channel).send(result_question)
    
    # async def add_question(self, context: Context, category: str):
    #     guid = await self.bot.database.add_question(context.author.id, category, message.content[17:].strip())
    #     if guid:
    #         await context.channel.send("Added successfully and will be in rotation after the current shuffle is exhausted.")

    async def get_user_prestige(self, user: discord.Member) -> int:
        roles = user.roles
        for role in roles:
            if "prestige" in role.name.lower():
                num = role.name.lower().replace("prestige", "").strip()
                return int(num)
        
        return 0

async def setup(bot) -> None:
    await bot.add_cog(Questions(bot))