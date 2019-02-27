import discord
import datetime

TOKEN = ''

client = discord.Client()
currentThreads = {}
THREAD_TIMEOUT = datetime.timedelta(days=1)

@client.event
async def on_message(message):
    # here we update "last used" specifications on a thread
    if message.channel.name.startswith('thread'):
        currentThreads[message.channel] = datetime.datetime.now()

    # here we delete any threads that haven't been used in at least the thread timeout duration.
    for channel in client.get_all_channels():
        if channel.name.startswith('thread'):
            if datetime.datetime.now() - currentThreads[channel] > THREAD_TIMEOUT:
                await client.delete_channel(channel)
                del(currentThreads[channel])

    #otherwise, we parse the message for commands
    if message.author == client.user:
        return

    if message.content.startswith('!thread'):
        content_split = message.content.split()
        if len(content_split) == 1:
            channel_name = str(datetime.datetime.now())
        else:
            channel_name = content_split[1]
            channel_members = content_split[2:]

        server = message.server

        #creates a new public channel
        #new_channel = await client.create_channel(server, 'thread-' + channel_name, type = discord.ChannelType.text)

        #creates a new private channel
        # everyone = discord.PermissionOverwrite(read_messages=False)
        # mine = discord.PermissionOverwrite(read_messages=True)
        # new_channel = await client.create_channel(server, 'thread-' + channel_name, (server.default_role, everyone), (server.me, mine))

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
        currentThreads[new_channel] = datetime.datetime.now()

        for currentThread, lastAccessed in currentThreads.items():
            print(currentThread, datetime.datetime.now() - lastAccessed)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    # on the case of reboot, grab all of the current threads by looking at "thread" prefix and set their last access to now.
    for channel in client.get_all_channels():
        if channel.name.startswith('thread'):
            currentThreads[channel] = datetime.datetime.now()

client.run(TOKEN)
