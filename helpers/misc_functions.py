import re

def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
# Zamanın pozitif olup olmadığını değerlendirip döner.
def is_valid_duration(duration):
    if is_number(duration):
        if int(duration) > 0:
            return True
        else:
            return False
    else:
        return False
    

def parse_duration(s):
    if is_number(s):
        return s
    else:
        values = {"w": 604800, "d": 86400, "h": 3600, "m": 60, "s": 1}
        nums = []
        tempnums = []
        for char in s:
            if char.isdigit():
                tempnums.append(char)
            else:
                multiple = values.get(char, 1)
                num = int("".join(tempnums))
                tempnums.clear()
                nums.append(num * multiple)
        if len(nums) > 0:
            return sum(nums)
        else:
            return -1
        
        
def author_is_admin(author):
    return author.guild_permissions.administrator
    
# Komutu kullananın yetkisinin var olup olmadığını + yönetici iznine sahip olup olmadıklarını kontrol eder.
async def author_is_mod(author, storage):
    if author_is_admin(author):
        return True
    guild_id = str(author.guild.id)
    mod_roles = storage.settings["guilds"][guild_id].get("mod_roles")
    if mod_roles is None:
        settings["guilds"][guild_id]["mod_roles"] = []
        await storage.write_settings_file_to_disk()
        mod_roles = storage.settings["guilds"][guild_id].get("mod_roles")
    return set(mod_roles) & set(author.roles)
