import aiosqlite
import uuid
import time
from datetime import datetime
import discord

class DatabaseManager:
    def __init__(self, *, connection: aiosqlite.Connection) -> None:
        self.connection = connection

# ==================================================================================
# WARNS
# ==================================================================================
    async def add_warn(
        self, user_id: int, server_id: int, moderator_id: int, reason: str
    ) -> int:
        """
        This function will add a warn to the database.

        :param user_id: The ID of the user that should be warned.
        :param reason: The reason why the user should be warned.
        """
        rows = await self.connection.execute(
            "SELECT id FROM warns WHERE user_id=? AND server_id=? ORDER BY id DESC LIMIT 1",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            warn_id = result[0] + 1 if result is not None else 1
            await self.connection.execute(
                "INSERT INTO warns(id, user_id, server_id, moderator_id, reason) VALUES (?, ?, ?, ?, ?)",
                (
                    warn_id,
                    user_id,
                    server_id,
                    moderator_id,
                    reason,
                ),
            )
            await self.connection.commit()
            return warn_id

    async def remove_warn(self, warn_id: int, user_id: int, server_id: int) -> int:
        """
        This function will remove a warn from the database.

        :param warn_id: The ID of the warn.
        :param user_id: The ID of the user that was warned.
        :param server_id: The ID of the server where the user has been warned
        """
        await self.connection.execute(
            "DELETE FROM warns WHERE id=? AND user_id=? AND server_id=?",
            (
                warn_id,
                user_id,
                server_id,
            ),
        )
        await self.connection.commit()
        rows = await self.connection.execute(
            "SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0

    async def get_warnings(self, user_id: int, server_id: int) -> list:
        """
        This function will get all the warnings of a user.

        :param user_id: The ID of the user that should be checked.
        :param server_id: The ID of the server that should be checked.
        :return: A list of all the warnings of the user.
        """
        rows = await self.connection.execute(
            "SELECT user_id, server_id, moderator_id, reason, strftime('%s', created_at), id FROM warns WHERE user_id=? AND server_id=?",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(row)
            return result_list

# ==================================================================================
# COUNTERS
# ==================================================================================
    async def get_counter(self, key: str) -> int:
        # refactor at some point due to sql injection
        rows = await self.connection.execute(
            f"SELECT next_index FROM counters WHERE key='{key}' LIMIT 1",
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0

    async def progress_counter(self, key: str) -> int:
        curr = await self.get_counter(key)
        #print(f"curr = {curr}")
        #, last_updated=DateTime('now')
        await self.connection.execute(
            f"UPDATE counters SET next_index={curr + 1} WHERE key='{key}'",
        )
        await self.connection.commit()
    
    async def reset_counter(self, key: str) -> int:
        await self.connection.execute(
            f"UPDATE counters SET next_index=0, last_updated=DateTime('now') WHERE key='{key}'",
        )
        await self.connection.commit()
        # async with rows as cursor:
        #     result = await cursor.fetchone()
        #     return result[0] if result is not None else 0

# ==================================================================================
# QUESTIONS
# ==================================================================================
    async def add_question(
        self, user_id: int, category: str, question: str) -> str:
        """
        This function will add a question to the database.

        :param user_id: The ID of the user that added it
        :param category: The category of questions this belongs to
        :param question: The question itself
        """
        guid_id = str(uuid.uuid4())
        await self.connection.execute(
            "INSERT INTO questions(id, user_id, category, question) VALUES (?, ?, ?, ?)",
            (
                guid_id,
                user_id,
                category,
                question,
            ),
        )
        await self.connection.commit()
        return guid_id

    async def get_questions(self, category: str) -> list:
        """
        This function will fetch all questions for a category

        :param category: The category of questions this belongs to
        """
        rows = await self.connection.execute(
            f"SELECT * FROM questions WHERE category='{category}'"
        )
        result_list = []
        async with rows as cursor:
            result = await cursor.fetchall()
            for row in result:
                #print(f"{row[0]}")
                result_list.append(row)

        #print(result_list)
        return result_list

    async def add_shuffled_question(
        self, foreign_id: str, order: int, category: str, question: str) -> str:
        """
        This function will add a question to the database.

        :param user_id: The ID of the user that added it
        :param category: The category of questions this belongs to
        :param question: The question itself
        """
        await self.connection.execute(
            "INSERT INTO questions_shuffled VALUES (?, ?, ?, ?)",
            (
                foreign_id,
                order,
                category,
                question,
            ),
        )
        await self.connection.commit()
        return foreign_id

    async def clear_shuffled_questions(self, category: str) -> bool:
        await self.connection.execute(
            f"DELETE FROM questions_shuffled WHERE category='{category}'"
        )
        await self.connection.commit()
        return True

    async def get_shuffled_question(self, order: int, category: str) -> str:
        """
        This function will get a question at a certain order

        :param order: the ordering to retrieve
        :param category: The category of questions this belongs to
        """
        #print(f"order = {order}")
        print(f"SELECT question FROM questions_shuffled WHERE [order]={order} AND category='{category}' LIMIT 1")
        rows = await self.connection.execute(
            f"SELECT question FROM questions_shuffled WHERE [order]={order} AND category='{category}' LIMIT 1",
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0

    async def get_shuffled_count(self, category: str) -> int:
        rows = await self.connection.execute(
            "SELECT COUNT(*) FROM questions_shuffled WHERE category=?",
            (
                category,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0

# ==================================================================================
# STATS
# ==================================================================================

    async def add_membership_stat(self, category: str, role_id: int, role_name: str, role_color: int, member_count: int):
        guid_id = str(uuid.uuid4())
        await self.connection.execute(
            "INSERT INTO membership_stats(id, category, role_id, role_name, role_color, member_count) VALUES (?, ?, ?, ?, ?, ?)",
            (
                guid_id,
                category,
                role_id,
                role_name,
                role_color,
                member_count
            ),
        )
        await self.connection.commit()


# ==================================================================================
# NUT
# ==================================================================================
    async def add_nut(self, user_id: int, server_id: int, channel_id: int, message_id: int, op_author_id: int, content_type: str) -> bool:
        # Check to see if this has already been reacted to by this user
        rows = await self.connection.execute(
            "SELECT COUNT(*) FROM nut WHERE user_id=? AND server_id=? AND channel_id=? AND message_id=?",
            (
                user_id,
                server_id,
                channel_id,
                message_id
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            count = (result[0][0] if result is not None else 0)
            print(f"Count = {count}")
            if count == 0:
                guid_id = str(uuid.uuid4())
                await self.connection.execute(
                    "INSERT INTO nut(id, user_id, server_id, channel_id, message_id, op_author_id, content_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        guid_id,
                        user_id,
                        server_id,
                        channel_id,
                        message_id,
                        op_author_id,
                        content_type
                    ),
                )
                await self.connection.commit()
                return True
            else:
                return False

    async def get_nut_count_message(self, server_id: int, channel_id: int, message_id: int) -> int:
        rows = await self.connection.execute(
            f"SELECT COUNT(*) FROM nut WHERE server_id={server_id} AND channel_id={channel_id} AND message_id={message_id}"
            # "SELECT COUNT(*) FROM nut WHERE server_id=? AND channel_id=? AND message_id=?",
            # (
            #     server_id,
            #     channel_id,
            #     message_id
            # ),
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            return result[0] if result is not None else 0

    async def get_nut_count_author(self, op_author_id: int) -> int:
        #print(f"SELECT * FROM nut WHERE op_author_id={op_author_id}")
        rows = await self.connection.execute(
            f"SELECT COUNT(*) FROM nut WHERE op_author_id={op_author_id}"#,
            # (
            #     op_author_id  
            # ),
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            return result[0] if result is not None else 0

# ==================================================================================
# EVENT: COLORWAR
# ==================================================================================
    async def last_paintball_fired(self, user: discord.Member, team_id: int) -> datetime:
        # check to see if they have a row already
        rows = await self.connection.execute(
            "SELECT last_paintball_shot FROM event_colorwar_players WHERE user_id=? AND server_id=? AND team_role_id=?",
            (
                int(user.id),
                int(user.guild.id),
                int(team_id)
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            #count = (result[0] if result != [] else 0)
            count = len(result)
            print(f"COUNT = {count}")
            # New player started
            if count == 0:
                guid_id = str(uuid.uuid4())
                await self.connection.execute(
                    "INSERT INTO event_colorwar_players(id, user_id, server_id, team_role_id, last_paintball_shot) VALUES (?, ?, ?, ?, ?)",
                    (
                        guid_id,
                        user.id,
                        user.guild.id,
                        team_id,
                        None
                    )
                )
                await self.connection.commit()
                return None
            elif count == 1:
                print(f"RESULT = {result[0][0]}")
                return result[0][0]
                #return result[0] if result is not None else 0
            else:
                raise Exception("Player Has Too Many Entries")

                # await self.connection.execute(
                #     "UPDATE event_colorwar_players SET last_paintball_shot = ? WHERE user_id=? AND server_id=?",
                #     (
                #         DateTime('now'),
                #         user.id,
                #         message.guild.id
                #     )
                # )
                # await self.connection.commit()
    async def update_last_paintball_fired(self, user: discord.Member, team_id: int) -> bool:
        await self.connection.execute(
            "UPDATE event_colorwar_players SET last_paintball_shot=? WHERE user_id=? AND server_id=? AND team_role_id=?",
            (
                datetime.now(),
                user.id,
                user.guild.id,
                team_id
            )
        )
        await self.connection.commit()
        return True

    async def update_colorwar_log(self, message: discord.Message, user_id: int, target_id: int, action: str, target_type: str):
        guid_id = str(uuid.uuid4())
        await self.connection.execute(
            "INSERT INTO event_colorwar_log(id, server_id, channel_id, message_id, user_id, action, target_type, target_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                guid_id,
                message.guild.id,
                message.channel.id,
                message.id,
                user_id,
                action,
                target_type,
                target_id
            )
        )
        await self.connection.commit()
        return None

    async def check_colorwar_message_used(self, message: discord.Message) -> int:
        rows = await self.connection.execute(
            f"SELECT COUNT(*) FROM event_colorwar_log WHERE server_id={message.guild.id} AND channel_id={message.channel.id} AND message_id={message.id}"
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            return result[0] if result is not None else 0

    async def check_paintball_supply(self, team_id: int) -> int:
        rows = await self.connection.execute(
            f"SELECT SUM(paintball_supply) FROM event_colorwar_channel_owner WHERE owner_team_role_id={team_id}"
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            return result[0] if result is not None else 0
    
    # async def use_paintball_supply(self, team_id: int):
    #     rows = await self.connection.execute(
    #         f"SELECT id,paintball_supply FROM event_colorwar_channel_owner WHERE owner_team_role_id='{team_id}' and paintball_supply > 0 LIMIT 1"
    #     )
    #     async with rows as cursor:
    #         result = await cursor.fetchall()

    #TODO: make this more dynamic, but hardcoded is fine for the moment
    async def get_channel_ownership_stats(self):
        rows = await self.connection.execute(
            "SELECT * FROM event_colorwar_channel_owner WHERE server_id = 1204074108942290974"
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            return result
        
    async def get_single_channel_ownership_stats(self, channel_id: int):
        rows = await self.connection.execute(
            f"SELECT * FROM event_colorwar_channel_owner WHERE server_id = 1204074108942290974 and channel_id={channel_id}"
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            return result

    async def colorwar_channel_refresh(self):
        print("[CW] RUNNING colorwar_channel_refresh()")
        channel_stats = await self.get_channel_ownership_stats()
        for row in channel_stats:
            print(f"UPDATE event_colorwar_channel_owner SET paintball_supply={row[5]}, last_resupply=DateTime('now') WHERE id='{row[0]}'")
            await self.connection.execute(
                f"UPDATE event_colorwar_channel_owner SET paintball_supply={row[5]}, last_resupply=DateTime('now') WHERE id='{row[0]}'"
            )
            await self.connection.commit()
            time.sleep(1)

    async def hit_count_in_channel_after_timestamp(self, channel_id: int, team_id: int, stamp: datetime) -> int:
        print(f"SELECT COUNT(*) FROM event_colorwar_log JOIN event_colorwar_players ON event_colorwar_log.user_id = event_colorwar_players.user_id WHERE event_colorwar_log.channel_id={channel_id} and event_colorwar_players.team_role_id={team_id} AND event_colorwar_log.collection_date > '{stamp}'")
        rows = await self.connection.execute(
            f"SELECT COUNT(*) FROM event_colorwar_log JOIN event_colorwar_players ON event_colorwar_log.user_id = event_colorwar_players.user_id WHERE event_colorwar_log.channel_id={channel_id} and event_colorwar_players.team_role_id={team_id} AND event_colorwar_log.collection_date > '{stamp}'"
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0

    async def update_channel_ownership(self, channel_id: int, team_id: int):
        print(f"UPDATE event_colorwar_channel_owner SET owner_team_role_id={team_id}, last_ownership_update=DateTime('now') WHERE channel_id={channel_id}")
        rows = await self.connection.execute(
            f"UPDATE event_colorwar_channel_owner SET owner_team_role_id='{team_id}', last_ownership_update=DateTime('now') WHERE channel_id='{channel_id}'"
        )
        await self.connection.commit()

    async def try_use_channel_paintball_supply(self, team_id: int) -> bool:
        rows = await self.connection.execute(
            f"SELECT * FROM event_colorwar_channel_owner WHERE owner_team_role_id={team_id} AND paintball_supply > 0 LIMIT 1"
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            if len(result) > 0:
                upd_count = int(result[0][6]) - 1
                await self.connection.execute(
                    f"UPDATE event_colorwar_channel_owner SET paintball_supply={upd_count}, last_updated=DateTime('now') WHERE id='{result[0][0]}'"
                )
                await self.connection.commit()
                print("try_use_channel_paintball_supply - TRUE")
                return True
        return False

    async def get_shields(self, user: discord.Member) -> int:
        rows = await self.connection.execute(
            "SELECT inv_count FROM event_colorwar_inventory WHERE user_id=? and server_id=? and item='SHIELD'",
            (
                user.id,
                user.guild.id,
            )
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            if result is None or len(result) == 0:
                return 0
            else:
                return result[0][0]

    async def set_shields(self, user: discord.Member, upd_count: int):
        rows = await self.connection.execute(
            "SELECT * FROM event_colorwar_inventory WHERE user_id=? and server_id=? and item='SHIELD'",
            (
                user.id,
                user.guild.id,
            )
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            # Create Inventory
            print(result)
            if len(result) == 0:
                guid_id = str(uuid.uuid4())
                await self.connection.execute(
                    "INSERT INTO event_colorwar_inventory(id, user_id, server_id, item, inv_count) VALUES (?, ?, ?, ?, ?)",
                    (
                        guid_id,
                        user.id,
                        user.guild.id,
                        "SHIELD",
                        upd_count
                    )
                )
            else:
                await self.connection.execute(
                    "UPDATE event_colorwar_inventory SET inv_count=? WHERE user_id=? and server_id=? and item='SHIELD'",
                    (
                        upd_count,
                        user.id,
                        user.guild.id,
                    )
                )
            await self.connection.commit()

    async def get_grenades(self, user: discord.Member) -> int:
        rows = await self.connection.execute(
            "SELECT inv_count FROM event_colorwar_inventory WHERE user_id=? and server_id=? and item='GRENADE'",
            (
                user.id,
                user.guild.id,
            )
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            if result is None or len(result) == 0:
                return 0
            else:
                return result[0][0]

    async def set_grenades(self, user: discord.Member, upd_count: int):
        rows = await self.connection.execute(
            "SELECT * FROM event_colorwar_inventory WHERE user_id=? and server_id=? and item='GRENADE'",
            (
                user.id,
                user.guild.id,
            )
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            # Create Inventory
            print(result)
            if len(result) == 0:
                guid_id = str(uuid.uuid4())
                await self.connection.execute(
                    "INSERT INTO event_colorwar_inventory(id, user_id, server_id, item, inv_count) VALUES (?, ?, ?, ?, ?)",
                    (
                        guid_id,
                        user.id,
                        user.guild.id,
                        "GRENADE",
                        upd_count
                    )
                )
            else:
                await self.connection.execute(
                    "UPDATE event_colorwar_inventory SET inv_count=? WHERE user_id=? and server_id=? and item='GRENADE'",
                    (
                        upd_count,
                        user.id,
                        user.guild.id,
                    )
                )
            await self.connection.commit()

    async def create_spawn(self, message: discord.Message, item: str, quantity: int):
        guid_id = str(uuid.uuid4())
        await self.connection.execute(
            "INSERT INTO event_colorwar_item_spawn(id, server_id, channel_id, message_id, item_type, item_quantity) VALUES (?, ?, ?, ?, ?, ?)",
            (
                guid_id,
                message.guild.id,
                message.channel.id,
                message.id,
                item,
                quantity
            )
        )
        await self.connection.commit()

    async def get_spawn(self, message: discord.Message):
        rows = await self.connection.execute(
            "SELECT * FROM event_colorwar_item_spawn WHERE server_id=? and channel_id=? and message_id=?",
            (
                message.guild.id,
                message.channel.id,
                message.id
            )
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            if result is None or len(result) == 0:
                return None
            else:
                return result[0]

    async def consume_spawn(self, message: discord.Message, user_id: int) -> bool:
        spawn = await self.get_spawn(message)
        collected_by = spawn[6]
        if collected_by is None or len(collected_by) == 0:
            await self.connection.execute(
                "UPDATE event_colorwar_item_spawn SET collected_by_user_id=?, updated_date=DateTime('now') WHERE id=?",
                (
                    user_id,
                    spawn[0]
                )
            )
            await self.connection.commit()
            return True
        else:
            return False