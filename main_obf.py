import json
import os

import discord
from discord.ext import commands

# Ini
# Discord
token = "token"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# MAIN
sid = 1016258495126982717
cid = 1036676015931527218
lbcid = 1027553126582079568

current_croissants = {}
current_croissants_msg = {}

# Leaderboard
path = "croissant_lb.json"
if os.path.exists(path):
    with open(path, "r") as f:
        croissant_lb = json.load(f)
else:
    croissant_lb = {"croissanteurs": {}, "croissanted": {}}
    with open(path, "w") as f:
        json.dump(croissant_lb, f)

# Backup leaderboard file
async def backup():
    with open(path, "w") as _f:
        json.dump(croissant_lb, _f)

# Returns name of a discord user by user id
async def get_name_by_id(_id):
    return bot.get_user(int(_id)).name

# Returns dpy user object by user id
async def get_author_by_id(_id):
    return bot.get_user(int(_id))

# Generate embed when someone gget croissanted
async def generate_main_embed(_id):
    # Ini
    embed = discord.Embed(title="Croissants", color=0xf5ce42)
    embed.set_thumbnail(
        url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/croissant_1f950.png")
    embed.set_footer(text="Made with ❤️ by @Shaft")

    # Main Field
    field_name = f"Quelqu'un a été croissanted !!"
    field_value = f"{(await get_author_by_id(_id)).mention} on pense fort à toi !\n\nRéagis pour prendre un " \
                  f"croissant ! :croissant:\n\nVictime, réagis pour arrêter le massacre ! :no_entry_sign:\n"
    embed.add_field(name=field_name, value=field_value)

    # Mangeurs Field
    field_name = "Mangeurs:"
    field_value = ""
    i = 0
    for __id in current_croissants[_id]["peoples"]:
        if i == 25:
            i = 0
            embed.add_field(name=field_name, value=field_value, inline=False) if field_value != "" else None
            field_value = ""
        field_value += f"{(await get_name_by_id(__id))}\n"
        i += 1
    embed.add_field(name=field_name, value=field_value, inline=False) if field_value != "" else None
    return embed

# Generate embed when a croissanting is stopped
async def generate_post_embed(_id):
    # Ini
    embed = discord.Embed(title=f"On remercie très fort {await get_name_by_id(_id)} !", color=0xf5ce42)
    embed.set_footer(text="Made with ❤️by Shaft")
    embed.set_thumbnail(
        url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/croissant_1f950.png")

    # Main Field
    field_name = f"Les esiearques suivants ont très faim:"
    field_value = ""
    for _id in current_croissants[_id]["peoples"]:
        field_value += f"{(await get_name_by_id(_id))}\n"
    if field_value == "":
        field_value = "Personne ! C'est un croissantage parfait !"
    embed.add_field(name=field_name, value=field_value)
    return embed

# Generate leaderboard embed
async def generate_lb_embed():
    # Ini
    embed = discord.Embed(title=f"Croissant leaderboard !", color=0xf5ce42)
    embed.set_footer(text="Made with ❤️by Shaft")
    embed.set_thumbnail(
        url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/croissant_1f950.png")
    medals = {1: "🥇", 2: "🥈", 3: "🥉", 4: "4.", 5: "5."}

    # Croissanted Field
    field_name = f"Les esiearques suivants se sont fait le plus croissanter !"
    field_value = ""
    rank = [[0, None] for i in range(5)]
    # Fetch croissanted
    for croissanted in croissant_lb["croissanted"]:
        for i in range(len(rank)):
            if croissant_lb["croissanted"][croissanted] > rank[i][0]:
                rank[i][0] = croissant_lb["croissanted"][croissanted]
                rank[i][1] = croissanted
                break
    # Build Field
    for i in range(len(rank)):
        if rank[i][1] is not None:
            field_value += medals[i+1] + await get_name_by_id(rank[i][1]) + str(rank[i][0]) + "\n"
    if field_value == "":
        field_value = "Personne n'a été croissanted.."
    embed.add_field(name=field_name, value=field_value, inline=False)

    # Fetch croissanteurs
    field_name = f"Les esiearques suivants ont le plus croissanté !"
    field_value = ""
    rank = [[0, None] for i in range(5)]
    for croissanteur in croissant_lb["croissanteurs"]:
        for i in range(len(rank)):
            if croissant_lb["croissanteurs"][croissanteur] > rank[i][0]:
                rank[i][0] = croissant_lb["croissanteurs"][croissanteur]
                rank[i][1] = croissanteur
                break
    # Build Field
    for i in range(len(rank)):
        if rank[i][1] is not None:
            field_value += medals[i + 1] + await get_name_by_id(rank[i][1]) + str(rank[i][0]) + "\n"
    if field_value == "":
        field_value = "Personne n'a croissant.."
    embed.add_field(name=field_name, value=field_value, inline=True)
    return embed

@bot.event
async def on_ready():
    print("Bot ready")
    """
    # Delete message from id
    channel_id = 1036676015931527218
    msg_id = 1036680192728506539
    c = await bot.fetch_channel(channel_id)
    m = await c.fetch_message(msg_id)
    await m.delete()
    """


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    try:
        await message.delete() if message.channel.id == cid and message.author.id != bot.user.id else None
    except:
        pass


@bot.command()
async def croissant(ctx, *args):
    if ctx.channel.id != cid:
        return
    # Try to get croissanteur name
    try:
        croissanteur = args[0].replace("<", "").replace(">", "").replace("@", "").replace("!", "")
        name = await get_name_by_id(int(croissanteur))
    except:
        croissanteur = None
    croissanted = ctx.author.id
    # Update leaderboard
    if croissanteur in croissant_lb['croissanteurs'] and croissanteur is not None:
        croissant_lb['croissanteurs'][croissanteur] += 1
    elif croissanteur is not None:
        croissant_lb['croissanteurs'][croissanteur] = 1
    if croissanteur in croissant_lb['croissanted']:
        croissant_lb['croissanted'][croissanted] += 1
    else:
        croissant_lb['croissanted'][croissanted] = 1
    # Backup lb file
    await backup()

    # Initialise a new croissanting
    current_croissants[ctx.author.id] = {"peoples": [], "mid": None}
    msg = await ctx.channel.send(embed=await generate_main_embed(ctx.author.id))
    current_croissants[ctx.author.id]["mid"] = msg.id
    current_croissants_msg[msg.id] = ctx.author.id
    await msg.add_reaction("🥐")
    await msg.add_reaction("🚫")

@bot.command()
async def leaderboard(ctx, *args):
    if ctx.channel.id == lbcid:
        await ctx.channel.send(embed=await generate_lb_embed())
    await ctx.message.delete()


@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id != cid or payload.message_id not in current_croissants_msg or payload.user_id == bot.user.id:
        return

    if payload.emoji.name == "🥐":
        current_croissants[current_croissants_msg[payload.message_id]]["peoples"].append(payload.user_id)
        msg = await bot.get_channel(cid).fetch_message(payload.message_id)
        await msg.edit(embed=await generate_main_embed(current_croissants_msg[payload.message_id]))

    elif payload.emoji.name == "🚫" and payload.user_id == current_croissants_msg[payload.message_id]:
        msg = await bot.get_channel(cid).fetch_message(payload.message_id)
        await msg.delete()
        await msg.channel.send(embed=await generate_post_embed(payload.user_id))
        del current_croissants[current_croissants_msg[payload.message_id]]
        del current_croissants_msg[payload.message_id]


bot.run(token)
