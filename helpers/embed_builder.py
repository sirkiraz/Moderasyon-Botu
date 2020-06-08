import discord

class EmbedBuilder:
    def __init__(self, event):
        if event == "delete":
            self.embed = discord.Embed(title="Denetim Kaydı!", description="Eylem: Mesaj Silme.", color=0xffc1fd)
        elif event == "kick":
            self.embed = discord.Embed(title="Ceza Bilgi!", description="Eylem: Kick.", color=0xffc1fd)
        elif event == "mute":
            self.embed = discord.Embed(title="Ceza Bilgi!", description="Eylem: Mute.", color=0xffc1fd)
        elif event == "tempmute":
            self.embed = discord.Embed(title="Ceza Bilgi!", description="Eylem: Tempmute.", color=0xffc1fd)
        elif event == "unmute":
            self.embed = discord.Embed(title="Ceza Bilgi!", description="Eylem: Unmute.", color=0xffc1fd)
        elif event == "tempban":
            self.embed = discord.Embed(title="Ceza Bilgi!", description="Eylem: Tempban.", color=0xffc1fd)
        elif event == "ban":
            self.embed = discord.Embed(title="Ceza Bilgi!", description="Eylem: Ban.", color=0xffc1fd)
        elif event == "unban":
            self.embed = discord.Embed(title="Ceza Bilgi!", description="Eylem: Unban.", color=0xffc1fd)
        elif event == "banexpire":
            self.embed = discord.Embed(title="Ceza Bilgi!", description="Geçici Ban Yasağı Doldu.", color=0xffc1fd)
        elif event == "muteexpire":
            self.embed = discord.Embed(title="Ceza Bilgi!", description="Üyenin Susturulması Doldu.", color=0xffc1fd)
        else:
            self.embed = discord.Embed(title=event)
        
    async def add_field(self, name, value, inline=False):
        self.embed.add_field(name=name, value=value, inline=inline)

    async def get_embed(self):
        return self.embed