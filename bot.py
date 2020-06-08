import json
import os
import time
import discord
from commands.ban import TempBanCommand, UnBanCommand
from commands.mod import ModCommand
from commands.mute import MuteCommand, TempMuteCommand, UnMuteCommand
from helpers.embed_builder import EmbedBuilder
from storage_management import StorageManagement
from tasks.check_punishments import check_punishments
from tasks.member_ban import MemberBan
from tasks.member_join import MemberJoin
from tasks.member_kick import MemberKick
from tasks.message_delete import MessageDelete
class ModerationBot(discord.Client):

    def __init__(self):
        self.prefix = "py!" # Botun prefixi.
        self.prefix_length = len(self.prefix)
        self.storage = StorageManagement()
        # Mute ve diğer varsayılan rollerin izinleri.
        self.muted_permissions =  discord.PermissionOverwrite(
            send_messages=False, 
            add_reactions=False,
            attach_files=False,
            speak=False,
            send_tts_messages=False
        )
        self.default_permissions = discord.PermissionOverwrite(
            read_messages=False,
            send_messages=False
        )
        # python bot.py yazarak botu çalıştırın.
        discord.Client.__init__(self)
        
    async def on_ready(self):
        print(f"[{self.user}] Adı ile Giriş Yapıldı Hazır Kpatan.") # Konsol mesajı! ({self.user} > tanımlanan botunuzun adı)       
        await self.storage.init()
        for guild in self.guilds:
            await self.setup_guild(guild)
        # Belirlenen görevleri kaydeder.
        self.loop.create_task(check_punishments(self))
    
    async def on_message(self, message):
        user = message.author
        # Sizi ve diğer botları yoksayar.
        if user == self.user or user.bot or len(message.content) == 0:
            return
        command = message.content.split()
        # komut anahtalarını düzenleyin!
        if command[0][:self.prefix_length] == self.prefix:
            if command[0] == self.prefix + "mod":
                mod_command = ModCommand(self)
                await mod_command.handle(message, command)
            elif command[0] == self.prefix + "tempmute":
                temp_mute = TempMuteCommand(self)
                await temp_mute.handle(message, command)
            elif command[0] == self.prefix + "mute":
                mute = MuteCommand(self)
                await mute.handle(message, command)
            elif command[0] == self.prefix + "unmute":
                un_mute = UnMuteCommand(self)
                await un_mute.handle(message, command)
            elif command[0] == self.prefix + "tempban":
                temp_ban = TempBanCommand(self)
                await temp_ban.handle(message, command)
            elif command[0] == self.prefix + "unban":
                un_ban = UnBanCommand(self)
                await un_ban.handle(message, command)
            else:
                await message.channel.send(f"Götünden komut uydurma canım.")
                
    async def on_guild_join(self, guild):
        print(f"Bot {guild.name} sunucusuna eklendi.")
        await self.setup_guild(guild)
    
    async def on_guild_remove(self, guild):
        print(f"Bot {guild.name} sunucusundan atıldı.")
        self.storage.settings.pop(guild.id)
        await self.storage.write_settings_file_to_disk()
        
    async def on_guild_channel_create(self, channel):
        guild = channel.guild
        guild_id = str(guild.id)
        muted_role_id = int(self.storage.settings["guilds"][guild_id]["muted_role_id"])
        muted_role = discord.utils.get(guild.roles, id=muted_role_id)
        if muted_role is not None:
            await channel.set_permissions(target=muted_role, overwrite=self.muted_permissions)
        else:
            return

    async def on_message_delete(self, message):
        message_delete = MessageDelete(self)
        await message_delete.handle(message)
            
    async def on_member_join(self, member):
        member_join = MemberJoin(self)
        await member_join.handle(member)
        
    async def on_member_ban(self, guild, member):
        member_ban = MemberBan(self)
        await member_ban.handle(guild)
        
    async def on_member_remove(self, member):

        member_kick = MemberKick(self)
        await member_kick.handle(member.guild)
    
    async def setup_guild(self, guild):
        if not await self.storage.has_guild(guild.id):
            await self.storage.add_guild(guild.id)
        # Var olmayan mute rolünün oluşturulmasını sağlayan fonksiyon.
        await self.check_for_muted_role(guild)
        # Mute rolünün sunucu içerisindeki yetkilerini ayarlar. Not: kanal izinleri tarafınızca ayarlanmalı.
        await self.add_muted_role_to_channels(guild)
        # Var olmayan log kanalının oluşturulmasını sağlayan fonksiyon.
        await self.create_log_channel(guild)

    async def check_for_muted_role(self, guild):
        guild_id = str(guild.id)
        muted_role_id = int(self.storage.settings["guilds"][guild_id]["muted_role_id"])
        role_test = discord.utils.get(guild.roles, id=muted_role_id)
        if role_test is None:
            # Rol mevcut değilse, bot tarafından oluşturulur.
            muted_role = await guild.create_role(name="Muted") #Rolün Adı.
            self.storage.settings["guilds"][guild_id]["muted_role_id"] = muted_role.id
            await self.storage.write_settings_file_to_disk()
        else:
            return
        
    async def add_muted_role_to_channels(self, guild):
        guild_id = str(guild.id)
        muted_role_id = int(self.storage.settings["guilds"][guild_id]["muted_role_id"])
        muted_role = discord.utils.get(guild.roles, id=muted_role_id)
        if muted_role is None:
            # Rolün var olup silinmediğinden emin olup botu tekrardan başlatın. daha sonra işlemi uygulayın.
            await self.check_for_muted_role(guild)
            muted_role_id = int(self.storage.settings["guilds"][guild_id]["muted_role_id"])
            muted_role = discord.utils.get(guild.roles, id=muted_role_id)
        for text_channel in guild.text_channels:
            await text_channel.set_permissions(target=muted_role, overwrite=self.muted_permissions)

        for voice_channel in guild.voice_channels:
            await voice_channel.set_permissions(target=muted_role, overwrite=self.muted_permissions)

    async def create_log_channel(self, guild):
        guild_id = str(guild.id)
        log_channel_id = int(self.storage.settings["guilds"][guild_id]["log_channel_id"])
        log_channel = discord.utils.get(guild.text_channels, id=log_channel_id)
        overwrites = {guild.default_role: self.default_permissions}
        if log_channel is None:
            # Log kanalı bulunmuyorsa bot tarafından oluşturulur.
            log_channel = await guild.create_text_channel(name="log", overwrites=overwrites)
            await log_channel.send("Log kanalı bulunmadığından bot tarafından oluşturulup kanal izinleri ayarlanmıştır.")
            self.storage.settings["guilds"][guild_id]["log_channel_id"] = log_channel.id
            await self.storage.write_settings_file_to_disk()
        else:
            return


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))          
if __name__ == "__main__":
    bot = ModerationBot()
    bot.run(" token ")
