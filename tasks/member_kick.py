import discord

from helpers.embed_builder import EmbedBuilder


class MemberKick:
    def __init__(self, client_instance):
        self.client = client_instance
        self.storage = self.client.storage
    
    async def handle(self, guild):
        guild_id = str(guild.id)
        log_channel_id = int(self.storage.settings["guilds"][guild_id]["log_channel_id"])
        log_channel = guild.get_channel(log_channel_id)
        
        logged_actions = []
        async for message in log_channel.history(limit=25):
            for embed in message.embeds:
                for field in embed.fields:
                    if field.name == "log_channel_id":
                        logged_actions.append(int(field.value.replace("`", "")))

        # Limit Belirleyin.
        async for entry in guild.audit_logs(action=discord.AuditLogAction.kick, limit=5):
            if entry.user == self.client.user or entry.id in logged_actions:
                continue
            else:
                # Bilgi embedi..
                embed_builder = EmbedBuilder(event="kick") 
                await embed_builder.add_field(name="Işlemi Uygulayan", value=f"`{entry.user.name}`")
                await embed_builder.add_field(name="Atılan Üye", value=f"`{entry.target.name}`")
                await embed_builder.add_field(name="Sebep", value=f"`{entry.reason}`")
                await embed_builder.add_field(name="log_channel_id", value=f"`{entry.id}`")
                embed = await embed_builder.get_embed()
                await log_channel.send(embed=embed)
