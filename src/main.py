from discord.ext import commands
import discord
import random
import http
import json
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)

bot.author_id = 000000000000000000

# Configuration variables
moderation_activated = False
users_flood = {}  # Dictionnaire pour suivre le nombre de messages des utilisateurs
threshold_flood = 10
time_flood = 2

@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command('ping')
async def pong(ctx):
    await ctx.send('pong')

@bot.command('hello')
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command('name')
async def name(ctx):
    await ctx.send(ctx.author.name)

@bot.command('d6')
async def d6(ctx):
    await ctx.send(random.randint(1,6))

@bot.event
async def on_message(message):
    if message.content == "Salut tout le monde":
        await message.channel.send("Salut tout seul")
        await message.channel.send(message.author.mention)
    await bot.process_commands(message)

@bot.command('admin')
async def admin(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Admin")
    if not role:
        await ctx.guild.create_role(name="Admin", permissions=discord.Permissions(8))
    await member.add_roles(role)
    await ctx.send("Admin role given to " + member.name)

@bot.command('ban')
async def ban(ctx, member: discord.Member, reason = "None"):
    await member.ban(reason=reason)
    if reason == "None":
        await ctx.send(random.choice(["You're banned", "You're out", "You're not welcome here", "Get out of here", "You're not allowed here"]))

@bot.event
async def on_message(message): 
    if message.author == bot.user:
        return

    if moderation_activated and message.content != "!flood":
        author_id = str(message.author.id)
        current_time = message.created_at.timestamp()

        if author_id not in users_flood:
            users_flood[author_id] = []

        users_flood[author_id] = [
            msg
            for msg in users_flood[author_id]
            if current_time - msg <= 60 * time_flood
        ]

        users_flood[author_id].append(current_time)

        if len(users_flood[author_id]) > threshold_flood:
            await message.channel.send(f"Stop spamming {message.author.mention}!")

    await bot.process_commands(message)

@bot.command('flood')
async def flood(ctx):
    global moderation_activated
    moderation_activated = not moderation_activated
    if moderation_activated:
        await ctx.send('flood activated')
    else :
        await ctx.send("flood deactivated.")

@bot.command('xkcd')
async def xkcd(ctx):
    connection = http.client.HTTPSConnection("xkcd.com")
    connection.request("GET", f"{random.randint(1, 2846)}/info.0.json")
    response = connection.getresponse()

    if response.status == 200:
        data = response.read()
        comic_data = data.decode("utf-8")
        data_json = json.loads(comic_data)
        await ctx.send(f"{data_json['img']}")
    else:
        await ctx.send("Ah...")

@bot.command('poll')
async def poll(ctx, question, time = 10):
    await ctx.send("@here " + question)
    message = await ctx.send(question)
    await message.add_reaction('👍')
    await message.add_reaction('👎')

    await asyncio.sleep(time)

    poll_message = await ctx.channel.fetch_message(message.id)

    thumbs_up = 0
    thumbs_down = 0
    for reaction in poll_message.reactions:
        if str(reaction.emoji) == "👍":
            thumbs_up = reaction.count - 1
        elif str(reaction.emoji) == "👎":
            thumbs_down = reaction.count - 1

    await ctx.send(
        f"**Results to** \"{question}\":👍: {thumbs_up} | 👎: {thumbs_down}"
    )
    await message.delete()

token = "<token>"
bot.run(token)  # Starts the bot