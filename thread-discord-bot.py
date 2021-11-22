"""required imports are
datetime - to get today's date, for the thread name
discord - to run the bot
aiocron - to run tasks at set times"""
import datetime, discord, aiocron

"""create the client"""
client = discord.Client()

"""Read from a file the bot's token and the template message the bot will send"""
token = open('token.txt', 'r').read()
template = open('template.txt', 'r').read()

"""the role id to ping & channel id to create the thread in"""
channel_id = 898154481894694932
role_id = 885847934619512833

"""when the bot starts
1. output that the bot has connected
2. start the async event"""
@client.event
async def on_ready():
    print(f'I am {client.user}')
    create_daily_thread.start()#

"""create a daily thread at 9am on weekdays (using cron)"""
@aiocron.crontab('0 9 * * *')
async def create_daily_thread():
    date = datetime.date.today()
    if (date.weekday() in [5, 6]):
        return
    
    thread_parent = client.get_channel(channel_id)
    thread_name = generate_thread_name(date)

    print(f'Got channel {thread_parent}')

    thread_start_message = await thread_parent.send(template)
    thread = await thread_parent.create_thread(name=thread_name, message=thread_start_message)
    await thread.send(f'<@&{role_id}>')

"""create a thread name from the date"""
def generate_thread_name(date):
    name = f'{date.day}.{date.month}.{date.year} Update'
    return name

"""start the bot"""
client.run(token)