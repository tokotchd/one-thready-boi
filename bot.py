import discord
import datetime

TOKEN = ''

client = discord.Client()
THREAD_TIMEOUT = datetime.timedelta(seconds=10)
THREAD_TIMEOUT_CHECK = datetime.timedelta(hours=24)
currentThreads = {}

lastPurgeCheck = datetime.datetime.utcnow()

@client.event
async def on_message(message):
    # Don't parse anything the bot says
    if message.author == client.user:
        return

    # here we check to make sure that we only run the check to purge expired threads once every N seconds
    global lastPurgeCheck
    if datetime.datetime.utcnow() - lastPurgeCheck > THREAD_TIMEOUT_CHECK:
        currentChannels = list(client.get_all_channels()) # copied so we don't have runtime iterator concerns
        # here we delete any threads that haven't been used in at least the thread timeout duration
        for channel in currentChannels:
            if channel.name.startswith('thread'):
                messages = client.logs_from(channel, limit=1, reverse=False)
                lastMessage = None
                async for message in messages:
                    lastMessage = message
                if datetime.datetime.utcnow() - message.timestamp > THREAD_TIMEOUT:
                    await client.delete_channel(channel)
        lastPurgeCheck = datetime.datetime.utcnow()

    # after we've done the purge check, we should then check the message for commands
    if message.content.startswith('!thread'):
        content_split = message.content.split()
        if len(content_split) == 1:
            msg = 'Please include a thread title in your thread create command.'
            await client.send_message(message.channel, msg)
            return
        else:
            channel_name = content_split[1]
            channel_members = content_split[2:]

        server = message.server

        #creates a new channel with copied permissions from current channel
        rolesAndPermissions = {}
        rolesAndPermissions[server.default_role] = discord.PermissionOverwrite(read_messages=False) # sets the default permissions to false
        for role in server.roles:
            rolesAndPermissions[role] = message.channel.overwrites_for(role)
        rolesAndPermissions[server.me] = discord.PermissionOverwrite(read_messages=True) # allows the bot to read the messages

        channel_permissions_list = []
        for role, permissions in rolesAndPermissions.items():
            channel_permissions_list.append(discord.ChannelPermissions(target=role, overwrite=permissions))

        new_channel = await client.create_channel(server, 'thread-' + channel_name, *channel_permissions_list)


        msg = 'Welcome to a thread about: ' + channel_name
        await client.send_message(new_channel, msg)
        msg = 'This thread will be closed automagically after 24 hours of inactivity, please copy what you want to keep!'
        await client.send_message(new_channel, msg)

    # here's the poll command
    if message.content.startswith('!poll'):
        content_split = message.content.split()
        if len(content_split) < 3:
            msg = 'Please include at least 2 items to choose between in the poll command'
            await client.send_message(message.channel, msg)
            return
        else:
            poll_items = content_split[1:]

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
