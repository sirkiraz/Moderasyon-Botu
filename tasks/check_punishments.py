import asyncio
import time
from helpers.embed_builder import EmbedBuilder
async def check_punishments(client):
    while True:
        for guild in client.guilds:
            guild_id = str(guild.id)
            muted_role_id = int(client.storage.settings["guilds"][guild_id]["muted_role_id"])
            log_channel_id = int(client.storage.settings["guilds"][guild_id]["log_channel_id"])
            muted_role = guild.get_role(muted_role_id)
            log_channel = guild.get_channel(log_channel_id)
            muted_users = client.storage.settings["guilds"][guild_id]["muted_users"]
            mutes_to_remove = []
            for user_info in muted_users.items():
                user_id = int(user_info[0])
                duration = int(user_info[1]["duration"])
                normal_duration = user_info[1]["normal_duration"]
                if -1 < duration < int(time.time()):
                    user = guild.get_member(user_id)
                    if user is None:
                        continue
                    await user.remove_roles(muted_role, reason="Geçici yasağın süresi doldu.")
                    mutes_to_remove.append(user_id)
                    
                    embed_builder = EmbedBuilder(event="muteexpire")
                    await embed_builder.add_field(name="Susturulması kaldırılan üye", value=f"`{user.name}`")
                    await embed_builder.add_field(name="Zaman", value=f"`{normal_duration}`")
                    embed = await embed_builder.get_embed()
                    await log_channel.send(embed=embed)
            for user_id in mutes_to_remove:
                client.storage.settings["guilds"][guild_id]["muted_users"].pop(str(user_id))
            await client.storage.write_settings_file_to_disk()
            
            banned_users = client.storage.settings["guilds"][guild_id]["banned_users"]
            bans_to_remove = []
            for user_info in banned_users.items():
                user_id = int(user_info[0])
                duration = int(user_info[1]["duration"])
                normal_duration = user_info[1]["normal_duration"]
                if -1 < duration < int(time.time()):
                    user = await client.fetch_user(user_id)
                    if user is None:
                        print(f"Tanımlanan id ile eşleşen üye bulunmadı. {user_id}")
                        continue
                    await guild.unban(user, reason="Geçici yasağın süresi doldu.")
                    bans_to_remove.append(user_id)
                    
                    # Bilgi embedi.
                    embed_builder = EmbedBuilder(event="banexpire")
                    await embed_builder.add_field(name="Yasağı kaldırılan üye", value=f"`{user.name}`")
                    await embed_builder.add_field(name="Zaman", value=f"`{normal_duration}`")
                    embed = await embed_builder.get_embed()
                    await log_channel.send(embed=embed)
            for user_id in bans_to_remove:
                client.storage.settings["guilds"][guild_id]["banned_users"].pop(str(user_id))
            await client.storage.write_settings_file_to_disk()
        await asyncio.sleep(5)
