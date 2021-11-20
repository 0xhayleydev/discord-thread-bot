import datetime, discord, aiocron

client = discord.Client()

token = open('token.txt', 'r').read()
template = open('template.txt', 'r').read()

channel_id = 898154481894694932
role_id = 885847934619512833

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    create_daily_thread.start()

@aiocron.crontab('0 9 * * *')
async def create_daily_thread():
    thread_parent = client.get_channel(channel_id)
    thread_name = generate_thread_name()

    print(f'Got channel {thread_parent}')

    thread_start_message = await thread_parent.send(template)
    thread = await thread_parent.create_thread(name=thread_name, message=thread_start_message)
    await thread.send(f'<@&{role_id}>')

def generate_thread_name():
    date = datetime.date.today()
    dateformatted = str(date).replace('-', '.')
    name = '{0} Update'.format(dateformatted)
    return name

client.run(token)