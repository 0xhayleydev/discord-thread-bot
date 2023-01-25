from http import server
from xmlrpc.client import Server
import discord
from discord import app_commands
import datetime
import json
import aiocron

# class which stores information about the guild
class ServerInfo:
    def __init__(self, save_data: bool, guild: str, channel: str, role: str, last_thread: str, message: str, cron: str):
        self.guild = guild
        if save_data:
            self.channel = channel
            self.role = role
            self.last_thread = last_thread
            self.saveToJSON()
            self.exists = True
            self.message = message
            self.cron = cron
        else:
            self.loadFromJSON()
        
    def __str__(self):
        output = ''
        output = output + f'guild: {self.guild}, '
        output = output + f'channel: {self.channel}, '
        output = output + f'role: {self.role}, '
        output = output + f'last_thread: {self.last_thread}, '
        return output
        
    def saveToJSON(self):
        data = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        f = open(f'guilds/{self.guild}.guild', 'w')
        f.write(data)
        f.close()

    def loadFromJSON(self):
        try:
            raw = self.load_file()
            data = json.loads(raw)
            self.guild = data["guild"]
            self.channel = data["channel"]
            self.role = data["role"]
            self.last_thread = data["last_thread"]
            self.exists = True
        except FileNotFoundError:
            self.exists = False
    
    def load_file(self):
        f = open(f'guilds/{self.guild}.guild', 'r')
        data = f.read()
        f.close()
        return data
        
class bot_client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
    
    async def on_ready(self):
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f"I am {self.user}.")
        
client = bot_client()
tree = app_commands.CommandTree(client)

async def start_all_crons():
    for i in range(len(client.guilds)):
        server_info = ServerInfo(False, client.guilds[i].id)
        aiocron.crontab(server_info.cron, func=create_daily_thread, args=(server_info.guild), start=True)

async def create_daily_thread(guild):
    if (guild.exists == True):
        thread = await create_thread(guild.guild, guild.channel, guild.role)
        print(guild.last_thread)
        await close_thread(guild.guild, guild.last_thread)
        guild.last_thread = str(thread.id)
        guild.saveToJSON()

def get_discord_channel(guild_id, channel_id):
    channel = client.get_guild(int(guild_id)).get_channel_or_thread(int(channel_id))
    return channel

async def close_thread(guild_id, channel_id):
    thread = get_discord_channel(guild_id, channel_id)
    if (thread != None):
        await thread.edit(archived=True)
        
async def create_thread(guild_id, channel_id, role_id):
    thread_name = get_thread_name()
    channel = get_discord_channel(guild_id, channel_id)
    thread_with_message = await channel.create_thread(name=thread_name, content=scrum_message)
    thread = thread_with_message.thread
    await thread.send(f"""<@&{role_id}>\n\nPLEASE NOTE: Bot is in BETA. Please contact hayley#1811 (<@175635927954227200>) if you have any issues or suggestions.
    
    Over the next few day the bot will be updated which may break pings in your server. For assistance in resolving this, please contact, hayley#1811""")
    return thread

def get_thread_name():
    date = datetime.date.today()
    thread_name = f'[{date.day}.{date.month}.{date.year}] Update'
    return thread_name

async def create_template_post(interaction, channel, role, cron):
    await interaction.response.send_message(f"Working...", ephemeral = True)
    thread = await create_thread(interaction.guild.id, channel.id, role.id)
    await interaction.edit_original_response(content=f"I will ping <@&{role.id}> in <#{channel.id}> with cron: {cron}")
    return thread

# COMMANDS
@tree.command(name = "scrum_legacy", description = "Setup the scrum message in the specified channel.")
async def self(interaction: discord.Interaction, channel: discord.ForumChannel, role: discord.Role):
    thread = await create_template_post(interaction, channel, role, "0 9 * * 1-5")
    server_info = ServerInfo(True, interaction.guild.id, channel.id, role.id, thread.id)
    server_info.loadFromJSON()

@tree.command(name = "scrum", description = "Setup the scrum message in the specified channel with a specific cron.")
async def self(interaction: discord.Interaction, channel: discord.ForumChannel, role: discord.Role, cron: str):
    thread = await create_template_post(interaction, channel, role, cron)
    server_info = ServerInfo(True, interaction.guild.id, channel.id, role.id, thread.id)
    server_info.loadFromJSON()

@tree.command(name = "test", description = "Test the bot.")
async def self(interaction: discord.Interaction):
    server_info = ServerInfo(False, interaction.guild.id)
    await create_daily_thread()
    await interaction.response.send_message(f"Request Sent", ephemeral = True)
    server_info.loadFromJSON()
    
@tree.command(name = "get_data", description = "Print the JSON data that is stored on the server.")
async def self(interaction: discord.Interaction):
    server_info = ServerInfo(False, interaction.guild.id)
    await interaction.response.send_message(server_info.load_file(), ephemeral=True)

scrum_message = open('template.txt', 'r').read()
token = open('token.txt', 'r').read()
client.run(token)