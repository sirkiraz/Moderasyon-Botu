import discord

from helpers.embed_builder import EmbedBuilder

class MessageDelete:
    def __init__(self, client_instance):
        self.client = client_instance
        self.storage = self.client.storage
        
    async def handle(self, message):
        # silinen mesajı döner.
        if message.author == self.client.user or message.author.bot:
            return
        # log mesajı
        embed_builder = EmbedBuilder(event="delete")
        await embed_builder.add_field(name="Kanal", value=f"`#{message.channel.name}`")
        await embed_builder.add_field(name="Üye", value=f"`{message.author.name}`")
        await embed_builder.add_field(name="Mesaj", value=f"`{message.content}`")
        await embed_builder.add_field(name="Tarih", value=f"`{message.created_at}`")
        embed = await embed_builder.get_embed()
        
        # log mesajını döner
        guild_id = str(message.guild.id)
        log_channel_id = int(self.storage.settings["guilds"][guild_id]["log_channel_id"])
        log_channel = discord.utils.get(message.guild.text_channels, id=log_channel_id)
        if log_channel is not None:
            await log_channel.send(embed=embed)
