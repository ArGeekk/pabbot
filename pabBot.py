import discord
from discord.ext import commands
import mysql.connector as mc
import datetime
import random
import os
import operator

bot = commands.Bot(command_prefix="!")
conn = mc.connect(host="remotemysql.com", database="8x37utoSFE", user="8x37utoSFE", password="8QNt2hdl5I")
cursor = conn.cursor()
table_level = "level_users"
epoch = datetime.datetime.utcfromtimestamp(0)


async def upgrade_level(user, message):
    xp_plus = random.randrange(1, 7)
    cursor.execute("SELECT exp, lvl, exp_time FROM level_users WHERE id=%s;", (user.id, ))
    infos = cursor.fetchone()
    if infos is not None:
        exp = infos[0]
        lvl = infos[1]
        exp_time = infos[2]

        time_diff = (datetime.datetime.utcnow() - epoch).total_seconds() - exp_time
        if time_diff >= 300:

            exp += xp_plus
            exp_time = (datetime.datetime.utcnow() - epoch).total_seconds()

            await minecraft_lvl(user, message, exp, lvl, exp_time)

    else:
        req = "INSERT INTO level_users (id, exp, lvl, exp_time) VALUES (%s, %s, %s, %s)"
        fonct = (user.id, xp_plus, 0, (datetime.datetime.utcnow() - epoch).total_seconds())
        cursor.execute(req, fonct)
        conn.commit()


async def minecraft_lvl(user, message, exp, lvl, time_diff):

    lvl_start = lvl
    if lvl < 16:
        lvl_end = 2*lvl+7
        if exp >= lvl_end:
            exp -= lvl_end
            lvl += 1
    elif 16 <= lvl <= 30:
        lvl_end = 5*lvl-38
        if exp >= lvl_end:
            exp -= lvl_end
            lvl += 1
    elif lvl >= 31:
        lvl_end = 9*lvl-158
        if exp >= lvl_end:
            exp -= lvl_end
            lvl += 1

    if lvl_start == lvl - 1:
        await message.channel.send(f"Félicitations {user.mention}, il semblerait que tu sois passé niveau {lvl} ! :tada:")

    if lvl == 1:
        asso = discord.utils.get(message.guild.roles, id=757627815444349072)
        await user.add_roles(asso)
        await message.channel.send(f"En passant niveau 1, tu deviens associé ! Félicitations associé {user.mention}")

    if lvl == 16:
        asso = discord.utils.get(message.guild.roles, id=757627384240537701)
        await user.add_roles(asso)
        await message.channel.send(f"En passant niveau 16, tu deviens soldat ! Félicitations soldat {user.mention}")

    if lvl == 31:
        asso = discord.utils.get(message.guild.roles, id=757626451045646488)
        await user.add_roles(asso)
        await message.channel.send(f"En passant niveau 31, tu deviens lieutenant ! Félicitations lieutenant {user.mention}")


    cursor.execute("UPDATE level_users SET exp=%s, lvl=%s, exp_time=%s WHERE id=%s", (exp, lvl, time_diff, user.id))
    conn.commit()


@bot.event
async def on_ready():
    print("Pablo is ready")
    await bot.change_presence(activity=discord.Game("Plata o Plomo"), status=discord.Status.online)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    if message.guild == bot.get_guild(757622696883388537):
        await upgrade_level(message.author, message)


@bot.command()
async def send(ctx, *args):
    if ctx.channel.id == 757633261806551200:
        if args[0] == "p":
            user = bot.get_user(int(args[1]))
            content = " ".join(args[2:])
            await user.send(content)
        if args[0] == "c":
            server = bot.get_guild(int((args[1].split("="))[1]))
            channel = discord.utils.get(server.channels, id=int((args[2].split("="))[1]))
            content = " ".join(args[3:])
            await channel.send(content)


@bot.command()
async def delete(ctx, nbre):
    try:
        nbre = int(nbre)
    except ValueError:
        await ctx.channel.send(f"{nbre} n'est pas un nombre !")
        return

    for mess in await ctx.channel.history(limit=nbre + 1).flatten():
        await mess.delete()


@bot.command()
async def level(ctx, member=None):

    if member is not None:

        if not ctx.author.guild_permissions.administrator:
            await ctx.message.delete()
            await ctx.author.send("Tu n'as pas la permission pour faire ça !")
            return
        user = ctx.guild.get_member(int(member[3:-1]))

    else:
        user = ctx.author
        

    print(user)

    cursor.execute("SELECT exp, lvl FROM level_users WHERE id=%s", (user.id, ))
    infos = cursor.fetchone()

    if infos is None:
        await ctx.channel.send("Ce joueur n'a pas encore de niveau !")
        return

    xp = infos[0]
    lvl = infos[1]
    embed = discord.Embed(title=f"Niveau de {user.name}", description=f"Progression du niveau de {user.mention}", colour=107300)
    embed.set_thumbnail(url="https://zupimages.net/up/20/40/k0sp.png")
    embed.add_field(name="Niveau", value=f"{lvl}")

    progression = 0
    if lvl < 16:
        progression = (xp * (10 / (2 * lvl + 7))) * 10
    if 16 <= lvl <= 30:
        progression = (xp * (10 / (5 * lvl - 38))) * 10
    if lvl >= 31:
        progression = (xp * (10 / (9 * lvl - 158))) * 10

    spl_prog = str(progression).split(".")

    if not spl_prog[1] == "0":

        if int(spl_prog[1][1]) >= 5:
            spl_prog[1] = str(int(spl_prog[1][0]) + 1)
        else:
            spl_prog[1] = spl_prog[1][0]

        if spl_prog[1] == "10":
            progression = str(int(spl_prog[0]) + 1)
        else:
            progression = ",".join(spl_prog)
    else:
        progression = spl_prog[0]

    embed.add_field(name="Progression du niveau", value=f"{progression}%")

    today = datetime.datetime.today().strftime("%A %d %B %Y")

    cursor.execute("SELECT id, lvl FROM level_users")
    all_users = cursor.fetchall()
    all_levels = {}

    for element in all_users:
        all_levels[element[0]] = element[1]

    all_levels = sorted(all_levels.items(), key=operator.itemgetter(1), reverse=True)
    i = 1
    finded = False

    while not finded:
        if user.id == all_levels[i-1][0]:
            finded = True
        else:
            i += 1

    if i == 1:
        embed.add_field(name="Rang", value=f"{i}ere place")
    else:
        embed.add_field(name="Rang", value=f"{i}e place")

    rest = 0

    if lvl < 16:
        rest = (2 * lvl + 7) - xp
    if 16 <= lvl <= 30:
        rest = (5 * lvl - 38) - xp
    if lvl >= 31:
        rest = (9 * lvl - 158) - xp

    embed.add_field(name="Prochain niveau", value=f"{rest} XP")
    embed.set_author(name=user.name, icon_url=user.avatar_url)
    embed.set_footer(text=f"{bot.user.name} · {today}")

    await ctx.channel.send(embed=embed)


@bot.command()
async def leaderboard(ctx):

    embed = discord.Embed(title="Classement des niveaux", colour=int("8f0828", 16))
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://zupimages.net/up/20/40/k0sp.png")

    today = datetime.datetime.today().strftime("%A %d %B %Y")
    embed.set_footer(text=f"{bot.user.name} · {today}")

    cursor.execute("SELECT id, lvl FROM level_users")
    all_users = cursor.fetchall()
    sort_users = {}

    for element in all_users:
        if ctx.guild.get_member(element[0]) is not None:
            sort_users[element[0]] = element[1]

    sort_users = sorted(sort_users.items(), key=operator.itemgetter(1), reverse=True)
    sort_users = sort_users[:11]

    i = 1

    while i - 1 < len(sort_users):
        id = sort_users[i-1][0]
        player_mention = ctx.guild.get_member(id)

        if i == 1:
            embed.add_field(name=f"{i}ere place",
                            value=f'{player_mention.mention} (niveau {sort_users[i-1][1]})', inline=False)
        else:
            embed.add_field(name=f"{i}e place",
                            value=f'{player_mention.mention} (niveau {sort_users[i-1][1]})', inline=False)
        i += 1

    await ctx.channel.send(embed=embed)

bot.run(os.environ["DISCORD_TOKEN"])
