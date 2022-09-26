import random, aiohttp, replit
import discord, json, asyncio, typing, os, io
import datetime, time
import re
from math import ceil, floor
from collections import defaultdict, OrderedDict
from operator import itemgetter
from statistics import mean
from timeit import default_timer as timer
from mediawiki import MediaWiki
from fandom import set_wiki, page
from replit import db
from discord import app_commands
from rocketbot_client import RocketBotClient

#Attempt to retrieve enviroment from environment.json
working_directory = os.path.dirname(os.path.realpath(__file__))
try:
    with open(os.path.join(working_directory, "environment.json"), "r") as f:
        data = json.loads(f.read())
        for key, value in data.items():
            os.environ[key] = value
except IOError:
    print("Environment.json not found, switching to default environment.")
else:
    print("Found environment.json. Starting bot now...")

#Get sensitive info
try:
    discord_token = os.environ['discord_token']
    rocketbot_user = os.environ['rocketbot_username']
    rocketbot_pass = os.environ['rocketbot_password']
except KeyError:
    print("ERROR: An environment value was not found. Please make sure your environment.json has all the right info or that you have correctly preloaded values into your environment.")
    os._exit(1)

#Set up discord bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
server_config = {}

#Initialize rockebot client
rocketbot_client = RocketBotClient(rocketbot_user, rocketbot_pass)

players = []
bots = []
playing = False

#Set targeted fandom site's api for fandom command
set_wiki("rocketbotroyale")
rocketbotroyale = MediaWiki(url='https://rocketbotroyale.fandom.com/api.php')

#List contains all tank emojis for random_tank and memory command
tanks = ['<:pumpkin_tank:1022568065034104936>', '<:pumpkin_evolved_tank:1022568062035177542>', '<:eyeball_tank:1022568661745143908>', '<:skull_tank:1022568068213379124>', '<:snowman_tank:1012941920844132362>', '<:snowman_evolved_tank:1012941924094713917>', '<:snowmobile_tank:1012941917337698375>', '<:icy_tank:1012941914254876794>', '<:brain_bot_tank:1006531910224322630>', '<:mine_bot_tank:1006532474945417216>', '<:bot_tank:917467970182189056>', '<:default_tank:996465659812774040>', '<:beta_tank:997947350943277106>', '<:canon_tank:997951207840686162>', '<:hotdog_tank:997955038435614934>', '<:wave_tank:997954135951413298>', '<:zig_tank:997954180717215975>', '<:blade_tank:997947874715385856>', '<:buggy_tank:997948966933119016>', '<:burger_evolved_tank:997950412348989562>', '<:burger_tank:997950506976694302>', '<:catapult_evolved_tank:997951715284365323>', '<:catapult_tank:997951809282912346>', '<:crab_evolved_tank:997951966548349009>', '<:crab_tank:997952051940180128>', '<:cyclops_tank:997952308333793322>', '<:diamond_tank:997952379595010048>', '<:dozer_evolved_tank:997952441486155906>', '<:dozer_tank:997952516501278760>', '<:fork_tank:997952581408129084>', '<:fries_tank:997952688656494672>', '<:gears_tank:997952760127434782>', '<:hay_tank:997952813386715148>', '<:hollow_tank:997952878142562384>', '<:medic_tank:997953168673619978>', '<:mixer_tank:997953233098113054>', '<:pagliacci_tank:997953348097560628>', '<:pail_tank:997953413717438575>', '<:pistons_tank:997953494050934864>', '<:reactor_tank:997953557263302666> ', '<:spider_evolved_tank:997953618504335501>', '<:spider_tank:997953676406702161>', '<:spike_tank:997953736041308280>', '<:square_tank:997953791217377381>', '<:trap_tank:997953904610381834>', '<:tread_tank:997953970213494905>', '<:tub_tank:997954029902626886>', '<:tubdown_tank:997954078535598270>', '<:concave_tank:997951897749176450>', '<:crawler_tank:997952124279324753>', '<:log_tank:997953009910829198>', '<:long_tank:997953087006330971>', '<:UFO_evolved_tank:1003007299570376714>', '<:UFO_tank:1003007259657392210>', '<:miner_tank:1003013509006753954>', '<:rover_tank:1003014762327716042>', '<:bug_tank:997948870543814726>', '<:moai_tank:1006528445355917394>']

os.system('clear')

def generate_random_name():
    adjective = [
        "master",
        "crappy",
        "professional",
        "smelly",
        "oily",
        "rusty",
        "crummy",
        "hamstery",
        "crunchy",
        "slippery",
        "watery",
        "super",
        "superlative",
        "creaky",
        "bloody"
    ]

    noun = [
        "blaster",
        "shagster",
        "killer",
        "dunker",
        "krunker",
        "rocketbotter",
        "bot",
        "turbine-engine",
        "diesel-gusher",
        "dumptruck",
        "rat-driver",
        "hamster-manueverer",
        "badengine",
        "killing-machine",
    ]

    name = (adjective).capitalize() + random.choice(noun).capitalize()

    random_number = random.choice([True, False])

    if random_number:
        name += f"{random.randint(0, 9)}{random.randint(0, 9)}00"
    
    return name
    
def add_player_coin(player, name, coins):
    if type(player) is int:
        player_coins = db.get(str(player))
        if player_coins == None:
            db[str(player)] = {"name":name,"money":500, "inventory":{}}
        db[player]["money"] = db[player]["money"] + coins
        return db[str(player)]["money"]
    return 0

def convert_mention_to_id(mention):
    return int(mention[1:][:len(mention)-2].replace("@","").replace("!",""))

def get_name_from_id(user_id):
    guild = discord.Object(id=962142361935314996)
    return guild.fetch_member(user_id)

async def refresh_config():
    '''Refresh game configuration every 10 minutes'''
    global server_config

    while True:
        response = await rocketbot_client.get_config()
        server_config = json.loads(response['payload'])
        await asyncio.sleep(600)

@client.event
async def on_message(message: discord.message):
     if "moyai" in message.content.lower() or "🗿" in message.content.lower() or "moai" in message.content.lower():
           await message.add_reaction("🗿")
     if "!idea" in message.content.lower():
           await message.add_reaction("<:upvote:910250647264329728>")
           await message.add_reaction("<:downvote:910250215217459281>")
     if "moyai" in message.content or "🗿" in message.content:
        await message.add_reaction(":moyai:")
     # (caps with spaces >= 10) or (repeated character or number >=10)
     if bool(re.search(r"\w*[A-Z ]{10}", message.content)) or bool(re.search(r"(?:([a-zA-Z0-9])\1{9,})", message.content)):
           await message.reply("Calm down!")

@client.event
async def on_ready():
    '''Called when the discord client is ready.'''
    
    #Start up the 10 minute config refresher
    asyncio.create_task(refresh_config())

    for key in db.keys():
        print(str(key) + str(db[key]))
    print("Winterpixel community bot is ready.")

@tree.command()
async def leaderboard_points(interaction: discord.Interaction, season: int = -1):
    '''Return the specified season leaderboard (by points), default current'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    curr_season = server_config['season']

    #If season is unreasonable, default to current season
    if season < 0 or season > curr_season:
        season = curr_season

    #Get leaderboard info
    response = await rocketbot_client.query_leaderboard(season)
    records = json.loads(response['payload'])['records']

    #Using f-string spacing to pretty print the leaderboard labels
    message = f"```{'Rank:':<5} {'Name:':<20} {'Points:'}\n{'‾' * 35}\n"
    
    #Using f-string spacing to pretty print the leaderboard.
    for record in records:
        message += f"{'#' + str(record['rank']):<5} {record['username']:<20} {'⬜' + '{:,}'.format(record['score'])}\n"
    message += "```"

    #Send
    await interaction.followup.send(embed=discord.Embed(title=f"Season {season} Leaderboard:", description=message))

@tree.command()
async def leaderboard_trophies(interaction: discord.Interaction, season: int = -1):
    '''Return the specified season leaderboard (by trophies), default current'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    curr_season = server_config['season']

    #If season is unreasonable, default to current season
    if season < 0 or season > curr_season:
        season = curr_season

    #Get leaderboard info
    response = await rocketbot_client.query_leaderboard(season, "tankkings_trophies")
    records = json.loads(response['payload'])['records']

    #Using f-string spacing to pretty print the leaderboard labels
    message = f"```{'Rank:':<5} {'Name:':<20} {'Trophies:'}\n{'‾' * 37}\n"
    
    #Using f-string spacing to pretty print the leaderboard.
    for record in records:
        message += f"{'#' + str(record['rank']):<5} {record['username']:<20} {'🏆' + '{:,}'.format(record['score'])}\n"
    message += "```"

    #Send
    await interaction.followup.send(embed=discord.Embed(title=f"Season {season} Leaderboard:", description=message))

@tree.command()
async def get_user(interaction: discord.Interaction, id: str):
    '''Return info about a specified user'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    # If the user specified a friend code we need to query the server for their ID.
    try:
        if (user_type == "Friend ID"):
            id_response = await rocketbot_client.friend_code_to_id(id)
            id = json.loads(id_response['payload'])['user_id']

        # Get user data
        response = await rocketbot_client.get_user(id)
        user_data = json.loads(response['payload'])[0]
        metadata = user_data['metadata']
    except aiohttp.ClientResponseError:
        # The code is wrong, send an error response
        await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(),
                                                            title="❌ Player not found ❌"))
        return

    # Create message
    message = ""

    # Get award config
    awards_config = server_config['awards']
    default_award = {'type': "Unknown", "name": "Unknown"}

    # Get general player info
    username = user_data['display_name']
    is_online = user_data['online']
    create_time = user_data['create_time']
    timed_bonus_last_collect = metadata['timed_bonus_last_collect']
    current_tank = metadata['skin'].replace(
        '_', ' ').split()[0].title() + " " + awards_config.get(
            awards_config.get(metadata['skin'], default_award)['skin_name'],
            default_award)['name']
    current_trail = awards_config.get(metadata['trail'], default_award)['name']
    current_parachute = awards_config.get(metadata['parachute'],
                                          default_award)['name']
    current_badge = awards_config.get(metadata['badge'], default_award)['name']
    level = metadata['progress']['level']
    XP = metadata['progress']['xp']
    friend_code = metadata['friend_code']
    id = user_data['user_id']

    # Add general player info
    general_info = "```\n"
    general_info += f"Username: {username}\n"
    general_info += f"Online: {is_online}\n"
    general_info += f"Create Time: {datetime.datetime.fromtimestamp(create_time):%Y-%m-%d %H:%M:%S}\n"
    general_info += f"Timed Bonus Last Collect: {datetime.datetime.fromtimestamp(timed_bonus_last_collect):%Y-%m-%d %H:%M:%S}\n"
    general_info += f"Current Tank: {current_tank}\n"
    general_info += f"Current Trail: {current_trail}\n"
    general_info += f"Current Parachute: {current_parachute}\n"
    general_info += f"Current Badge: {current_badge}\n"
    general_info += f"Level: {level}\n"
    general_info += f"XP: {XP}\n"
    general_info += f"Friend Code: {friend_code}\n"
    general_info += f"User ID: {id}\n"
    general_info += "```"

    # Add to embed
    message += f"📓 ***General Info***:\n{general_info}\n"

    # Create badge list
    badge_list = "```\n"

    for badge in metadata['awards']:
        award = awards_config.get(badge, default_award)
        type = award['type']

        if type == "badge":
            badge_list += award['name'] + "\n"
    badge_list += "```"

    # Add to embed
    message += f"🛡️ ***Badges***:\n{badge_list}\n"

    # Get skins info
    tank_common_total = 0
    tank_rare_total = 0
    tank_legendary_total = 0
    tank_purchased_total = 0
    tank_earned_total = 0
    parachute_common_total = 0
    parachute_rare_total = 0
    parachute_legendary_total = 0
    parachute_purchased_total = 0
    parachute_earned_total = 0
    trail_common_total = 0
    trail_rare_total = 0
    trail_legendary_total = 0
    trail_purchased_total = 0
    trail_earned_total = 0

    tank_common_owned = 0
    tank_rare_owned = 0
    tank_legendary_owned = 0
    tank_purchased_owned = 0
    tank_earned_owned = 0
    parachute_common_owned = 0
    parachute_rare_owned = 0
    parachute_legendary_owned = 0
    parachute_purchased_owned = 0
    parachute_earned_owned = 0
    trail_common_owned = 0
    trail_rare_owned = 0
    trail_legendary_owned = 0
    trail_purchased_owned = 0
    trail_earned_owned = 0

    for key, value in awards_config.items():
        try:
            try:
                if value['hidden'] != True:
                    pass
                else:
                    if value['name'] == 'Moai':
                        tank_legendary_total += 1

            except:
                if value['type'] == "skin_set":
                    if value['rarity'] == "common":
                        tank_common_total += 1
                    elif value['rarity'] == "rare":
                        tank_rare_total += 1
                    elif value['rarity'] == "legendary":
                        tank_legendary_total += 1
                    elif value['rarity'] == "purchased":
                        tank_purchased_total += 1
                    elif value['rarity'] == "earned":
                        tank_earned_total += 1
                elif value['type'] == "parachute":
                    if value['rarity'] == "common":
                        parachute_common_total += 1
                    elif value['rarity'] == "rare":
                        parachute_rare_total += 1
                    elif value['rarity'] == "legendary":
                        parachute_legendary_total += 1
                    elif value['rarity'] == "purchased":
                        parachute_purchased_total += 1
                    elif value['rarity'] == "earned":
                        parachute_earned_total += 1
                elif value['type'] == "trail":
                    if value['rarity'] == "common":
                        trail_common_total += 1
                    elif value['rarity'] == "rare":
                        trail_rare_total += 1
                    elif value['rarity'] == "legendary":
                        trail_legendary_total += 1
                    elif value['rarity'] == "purchased":
                        trail_purchased_total += 1
                    elif value['rarity'] == "earned":
                        trail_earned_total += 1
        except:
            pass

    tank_list_duplicated = []
    for tank in metadata['awards']:
        award = awards_config.get(tank, default_award)
        type = award['type']

        if type == "skin":
            tank_list_duplicated.append(award['skin_name'])

    for unique_tank in list(dict.fromkeys(tank_list_duplicated)):
        try:
            if awards_config.get(unique_tank)['rarity'] == "common":
                tank_common_owned += 1
            elif awards_config.get(unique_tank)['rarity'] == "rare":
                tank_rare_owned += 1
            elif awards_config.get(unique_tank)['rarity'] == "legendary":
                tank_legendary_owned += 1
            elif awards_config.get(unique_tank)['rarity'] == "purchased":
                tank_purchased_owned += 1
            elif awards_config.get(unique_tank)['rarity'] == "earned":
                tank_earned_owned += 1
        except:
            pass

    # Create parachute list
    parachute_list = "```\n"

    # Create trail list
    trail_list = "```\n"

    for award in metadata['awards']:
        skin = awards_config.get(award, default_award)

        try:
            if skin['name'] == 'No trail':
                trail_list += "        " + skin['name'] + "\n"
            else:
                type = skin['type']
                rarity = skin['rarity']
                if type == "parachute":
                    if rarity == 'common':
                        parachute_common_owned += 1
                        parachute_list += "     ⭐ " + skin['name'] + "\n"
                    elif rarity == 'rare':
                        parachute_rare_owned += 1
                        parachute_list += "   ⭐⭐ " + skin['name'] + "\n"
                    elif rarity == 'legendary':
                        parachute_legendary_owned += 1
                        parachute_list += " ⭐⭐⭐ " + skin['name'] + "\n"
                    elif rarity == 'purchased':
                        parachute_purchased_owned += 1
                        parachute_list += "     💰 " + skin['name'] + "\n"
                    elif rarity == 'earned':
                        parachute_earned_owned += 1
                        parachute_list += "     🏅 " + skin['name'] + "\n"
                if type == "trail":
                    if rarity == 'common':
                        trail_common_owned += 1
                        trail_list += "     ⭐ " + skin['name'] + "\n"
                    elif rarity == 'rare':
                        trail_rare_owned += 1
                        trail_list += "   ⭐⭐ " + skin['name'] + "\n"
                    elif rarity == 'legendary':
                        trail_legendary_owned += 1
                        trail_list += " ⭐⭐⭐ " + skin['name'] + "\n"
                    elif rarity == 'purchased':
                        trail_purchased_owned += 1
                        trail_list += "     💰 " + skin['name'] + "\n"
                    elif rarity == 'earned':
                        trail_earned_owned += 1
                        trail_list += "     🏅 " + skin['name'] + "\n"
        except:
            pass

    parachute_list += "```"
    trail_list += "```"

    common_owned = tank_common_owned + parachute_common_owned + trail_common_owned
    common_total = tank_common_total + parachute_common_total + trail_common_total
    rare_owned = tank_rare_owned + parachute_rare_owned + trail_rare_owned
    rare_total = tank_rare_total + parachute_rare_total + trail_rare_total
    legendary_owned = tank_legendary_owned + \
        parachute_legendary_owned + trail_legendary_owned
    legendary_total = tank_legendary_total + \
        parachute_legendary_total + trail_legendary_total
    purchased_owned = tank_purchased_owned + \
        parachute_purchased_owned + trail_purchased_owned
    purchased_total = tank_purchased_total + \
        parachute_purchased_total + trail_purchased_total
    earned_owned = tank_earned_owned + parachute_earned_owned + trail_earned_owned
    earned_total = tank_earned_total + \
        parachute_earned_total + trail_earned_total

    tank_owned = tank_common_owned + tank_rare_owned + \
        tank_legendary_owned + tank_purchased_owned + tank_earned_owned
    tank_total = tank_common_total + tank_rare_total + \
        tank_legendary_total + tank_purchased_total + tank_earned_total
    parachute_owned = parachute_common_owned + \
        parachute_rare_owned + parachute_legendary_owned + \
        parachute_purchased_owned + parachute_earned_owned
    parachute_total = parachute_common_total + \
        parachute_rare_total + parachute_legendary_total + \
        parachute_purchased_total + parachute_earned_total
    trail_owned = trail_common_owned + trail_rare_owned + \
        trail_legendary_owned + trail_purchased_owned + trail_earned_owned
    trail_total = trail_common_total + trail_rare_total + \
        trail_legendary_total + trail_purchased_total + trail_earned_total

    owned = tank_owned + parachute_owned + trail_owned
    total = tank_total + parachute_total + trail_total

    s = f"```\n+{'-'*51}+\n|{'Type':^17}|{'Tanks':^5}|{'Parachutes':^10}|{'Trails':^6}|{'Sub-total':^9}|\n+{'-'*17}+{'-'*5}+{'-'*10}+{'-'*6}+{'-'*9}+\n"
    s += f"|    ⭐ {'Common':<10}|{str(tank_common_owned):>2}/{str(tank_common_total):<2}|{str(parachute_common_owned):>4}/{str(parachute_common_total):<5}|{str(trail_common_owned):>2}/{str(trail_common_total):<3}|{str(common_owned):>4}/{str(common_total):<4}|\n+{'-'*17}+{'-'*5}+{'-'*10}+{'-'*6}+{'-'*9}+\n"
    s += f"|  ⭐⭐ {'Rare':<10}|{str(tank_rare_owned):>2}/{str(tank_rare_total):<2}|{str(parachute_rare_owned):>4}/{str(parachute_rare_total):<5}|{str(trail_rare_owned):>2}/{str(trail_rare_total):<3}|{str(rare_owned):>4}/{str(rare_total):<4}|\n+{'-'*17}+{'-'*5}+{'-'*10}+{'-'*6}+{'-'*9}+\n"
    s += f"|⭐⭐⭐ {'Legendary':<10}|{str(tank_legendary_owned):>2}/{str(tank_legendary_total):<2}|{str(parachute_legendary_owned):>4}/{str(parachute_legendary_total):<5}|{str(trail_legendary_owned):>2}/{str(trail_legendary_total):<3}|{str(legendary_owned):>4}/{str(legendary_total):<4}|\n+{'-'*17}+{'-'*5}+{'-'*10}+{'-'*6}+{'-'*9}+\n"
    s += f"|    💰 {'Purchased':<10}|{str(tank_purchased_owned):>2}/{str(tank_purchased_total):<2}|{str(parachute_purchased_owned):>4}/{str(parachute_purchased_total):<5}|{str(trail_purchased_owned):>2}/{str(trail_purchased_total):<3}|{str(purchased_owned):>4}/{str(purchased_total):<4}|\n+{'-'*17}+{'-'*5}+{'-'*10}+{'-'*6}+{'-'*9}+\n"
    s += f"|    🏅 {'Earned':<10}|{str(tank_earned_owned):>2}/{str(tank_earned_total):<2}|{str(parachute_earned_owned):>4}/{str(parachute_earned_total):<5}|{str(trail_earned_owned):>2}/{str(trail_earned_total):<3}|{str(earned_owned):>4}/{str(earned_total):<4}|\n+{'-'*17}+{'-'*5}+{'-'*10}+{'-'*6}+{'-'*9}+\n"
    s += f"| {'Sub-total':^16}|{str(tank_owned):>2}/{str(tank_total):<2}|{str(parachute_owned):>4}/{str(parachute_total):<5}|{str(trail_owned):>2}/{str(trail_total):<3}|{str(owned):>4}/{str(total):<4}|\n+{'-'*17}+{'-'*5}+{'-'*10}+{'-'*6}+{'-'*9}+```"

    # Add to embed
    message += f"📦 ***Items Collected***:\n{s}\n"

    # Create tank list
    tank_list = "```\n"

    for unique_tank in list(dict.fromkeys(tank_list_duplicated)):
        try:
            if awards_config.get(unique_tank,
                                 default_award)['rarity'] == 'common':
                tank_list += "     ⭐ " + awards_config.get(
                    unique_tank, default_award)['name'] + "\n"
            elif awards_config.get(unique_tank,
                                   default_award)['rarity'] == 'rare':
                tank_list += "   ⭐⭐ " + awards_config.get(
                    unique_tank, default_award)['name'] + "\n"
            elif awards_config.get(unique_tank,
                                   default_award)['rarity'] == 'legendary':
                tank_list += " ⭐⭐⭐ " + awards_config.get(
                    unique_tank, default_award)['name'] + "\n"
            elif awards_config.get(unique_tank,
                                   default_award)['rarity'] == 'purchased':
                tank_list += "     💰 " + awards_config.get(
                    unique_tank, default_award)['name'] + "\n"
            elif awards_config.get(unique_tank,
                                   default_award)['rarity'] == 'earned':
                tank_list += "     🏅 " + awards_config.get(
                    unique_tank, default_award)['name'] + "\n"
        except:
            pass

    tank_list += "```"

    # Add to embed
    message += f"🪖 ***Tanks***:\n{tank_list}\n"

    # Add to embed
    message += f"🪂 ***Parachutes***:\n{parachute_list}\n"

    # Add to embed
    message += f"🌟 ***Trails***:\n{trail_list}\n"

    # Create stats
    stat_list = "```\n"
    for key, value in metadata['stats'].items():
        stat_list += f"{key.replace('_', ' ').title()}: {value}\n"
    stat_list += "```"

    # Add to embed
    message += f"🗒️ ***Stats***:\n{stat_list}"

    # Send message
    await interaction.followup.send(embed=discord.Embed(description=message))

@tree.command()
async def bot_info(interaction: discord.Interaction):
    '''Get info about this bot.'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    embed = discord.Embed()
    embed.title = "Bot info:"
    embed.description = "Community discord bot, being hosted on repl.it\n\nFor more info visit https://github.com/Blakiemon/Winterpixel-Community-Bot.\n\n All pull requests will be reviewed, and appreciated."
    await interaction.followup.send(embed=embed)

@tree.command()
async def battle(interaction: discord.Interaction):
    '''Have a battle with a random bot!'''

    await interaction.response.defer(ephemeral=False, thinking=True)
        
    curr_season = server_config['season']

    events = {
        "The bot dodged your attack. <:bot:917467970182189056>"
        : 70,
        "You destroyed the bot! It drops a single coin. <:coin:910247623787700264>"
        : 10,
        "The bot *expertly* dodged your attack. <:bot:917467970182189056>"
        : 5,
        "You thought you hit the bot, but its health returns to full due to network lag. 📶"
        : 5,
        "You destroyed the bot! It drops a some coins and a crate. <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264> 📦. But <R> comes out of nowhere and steals it."
        : 3,
        "You accidentally hit a teammate and dunk them into the water. <:splash:910252276961128469>"
        : 2,
        "The bot vanishes. An error pops up: `CLIENT DISCONNECTED` <:alertbad:910249086299557888>"
        : 1,
        "<R> comes out of nowhere and kills you and the bot to win the game."
        : 1,
        "<R> comes out of nowhere and shoots a shield at the bot deflecting it back to you and you die."
        : 1,
        "You miss. Before you try to shoot again <R> comes out of nowhere and stands next to the bot and you decide to leave out of sheer intimidation."
        : 1,
        "The missile goes off-screen. Instead of getting a kill, a beachball comes hurtling back at mach 2."
        : 0.3,
        "The bot vanishes. Was there ever really a bot there at all?..."
        : 0.2,
        "You destroyed the bot! It drops what appears to be MILLIONS of coins, filling every pixel on your screen with a different shade of gold. Your game immediately slows to a halt and crashes."
        : 0.2,
        "The missile vanishes off the screen, seemingly lost to the water.\nSuddenly, you hear a flurry of *ping*s! The words \"Long Shot!\" splash across your monitor, followed by \"Two Birds\", \"Double Kill\", \"Triple Kill\", and finally \"Quad Kill\". This is it. This is the moment you thought would never happen. The \"Get a quad kill\" and \"Destroy two tanks with one explosion\" goals you've had for two months are finally complete. As the flood of joy and relief washes over you, so does the rising water over your tank. You've lost the match, but you don't care. The war is already won. In a hurry you leave the match and click to the Goals tab, overcome with anticipation to see those beautiful green *Collect!* buttons. You slide your cursor over.\nBAM! The moment before you click, the screen goes black. All you can see is \"Connecting...\". The loading indicator never goes away."
        : 0.1,
        "You get a quad kill, four birds one stone! It was four bots doing the same exact movement. They drop 4 coins. <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264> <:coin:910247623787700264>"
        : 0.1,
        "🗿 Moyai God comes down from the heavens and blocks your missile. You bow down (as a tank) and repent for your sins."
        : 0.1,
        "Before your bullet hits the bot you were aiming at, a shiny green bot jumps up and takes the hit. Suddenly a green gem appears where it died, floating in midair. JACKPOT<:gem:910247413695016970>": .1
    }
    event = "You fire a missile at a bot. <:rocketmint:910253491019202661>\n" + random.choices(population=list(events.keys()), weights=events.values(), k=1)[0]
    
    if "<R>" in event:
        #Get random name from leaderboard
        response = await rocketbot_client.query_leaderboard(curr_season)
        records = json.loads(response['payload'])['records']
        rand_player = random.choice(records)['username']

        #Formulate response with random name
        event = event.replace("<R>", rand_player)
    else:
        #Otherwise wait half a second
        await asyncio.sleep(.5)
    
    await interaction.followup.send(event)

@tree.command()
async def build_a_bot(interaction: discord.Interaction):
    '''Bear the responsibility of creating new life... I mean bot'''
    bot_name = generate_random_name()
    response = f"***Meet your lovely new bot!***\n\n`{bot_name}`"
    if len(bots) > 5:
        response += f"\n\n`{bot_name}` can't join because 5 bots have already joined"
    else:
        response += f"\n\n`{bot_name}` is joining the next game"
        players.append(bot_name)
        bots.append(bot_name)
    await interaction.response.send_message(response)

@tree.command()
async def join_game(interaction: discord.Interaction):
    '''Join the current game'''
    response_hidden = False
    if playing:
        await interaction.response.send_message("Can't join because a game is already in progress")
        return
    response = ""
    if interaction.user.mention not in players:
        players.append(interaction.user.mention)
        response += '{} joined'.format(interaction.user.mention)
    else:
        response_hidden = True
        response += '{} you cant join twice'.format(interaction.user.mention)

    await interaction.response.send_message(response)

@tree.command(guild=discord.Object(id=962142361935314996))
async def get_config(interaction: discord.Interaction):
    file = io.StringIO(json.dumps(server_config))
    await interaction.response.send_message(file=discord.File(fp=file, filename="server_config.json"))

@tree.command()
async def start_game(interaction: discord.Interaction):
    '''Start a game with the people joined'''
    global playing 
    if playing:
        return
    playing = True
    response = "Game Starting With: "
    if len(players) <= 1:
        playing = False
        await interaction.response.send_message("Need 2 or more players to start.")
        return
    for i in players:
        response += "\n" + i
    embed1=discord.Embed(color=0xa80022)
    embed1.add_field(name="Players: ", value=response, inline=False)
    await interaction.response.send_message(response)
    msg = await interaction.channel.send("Starting game")
#     await asyncio.sleep(0)
    moneys = OrderedDict()
    while len(players) >= 1:
        embed=discord.Embed(color=0xa80022)
        if len(players) <= 1:
            embed.add_field(name="Players: ", value=players[0], inline=False)
            embed.add_field(name="Game:", value=players[0] + " wins!", inline=False)
            money_txt = ""
            for i in moneys.keys():
                money_txt += i + " " + str(moneys[i]) + "<:coin:910247623787700264>\n"
            if money_txt != "":
                embed.add_field(name="Money:", value=money_txt, inline=False)
            await msg.edit(embed=embed)
            playing = False
            players.clear()
            bots.clear()
            break
        player_text = ""
        players.sort()
        for i in players:
            player_text += i + " "
        embed.add_field(name="Players: ", value=player_text, inline=False)
        action_types = {"Kill": 100, "Miss": 50, "Self": 20, "Special": 0}
        
        action_choice = random.choices(population=list(action_types.keys()), weights=action_types.values(), k=1)[0]
        
        action = ""
        if action_choice == "Kill":
            coin_num = random.choice(range(1,100))
            player_a = random.choice(players)
            players.remove(player_a)
            player_b = random.choice(players)
            players.remove(player_b)
            kill_messages = {
                "<A> kills <B>.": 100,
                "After a long intense fight <A> kills <B>": 40,
                "<A> kills <B> with <U>": 40,
                "<A> hits <B> into the water": 20,
                "<B> shoots it at <A> but <A> blocks it with a shield reflects it back to <B> who dies": 7,
                "<A> pretends to friend <B> but then kills them": 5,
                "<A> intimidates <B> into jumping into the water": 0.5,
            }
#             if len(players) > 2:
#                 kill_messages["<A> kills <B> and <C> `DOUBLE KILL`"] = 10
#             if len(players) > 3:
#                 kill_messages["<A> kills <B> ,<C> and <D> `TRIPPLE KILL`"] = 5
#             if len(players) > 4:
#                 kill_messages["<A> kills <B>, <C>, <D> and <E> `QUAD KILL`"] = 2
            weopons = {
                "A FAT BOI (nuke)": 100,
                "Rapidfire missiles": 100,
                "Grenades": 100,
                "A Homing Missile": 100,
                "A Flak": 100,
                "A Drill": 100,
                "THE POWER OF MOYAI 🗿": 0.1
            }
            event = random.choices(population=list(kill_messages.keys()), weights=kill_messages.values(), k=1)[0]
            event = event.replace("<A>", player_a)
            event = event.replace("<B>", player_b)
            if "<U>" in event:
                event = event.replace("<U>", random.choices(population=list(weopons.keys()), weights=weopons.values(), k=1)[0])
            #B-E die for kills, if we need a non dying player use F
            event += "\n\n" + player_a + " got " + str(coin_num) + " <:coin:910247623787700264>"
            event += " and " + player_b + " lost " + str(coin_num) + " <:coin:910247623787700264>"
            add_player_coin(convert_mention_to_id(player_a),coin_num)
            add_player_coin(convert_mention_to_id(player_b),-coin_num)
            if moneys.get(player_a) == None:
                moneys[player_a] = coin_num
            else:
                moneys[player_a] = moneys[player_a] + coin_num
            if moneys.get(player_b) == None:
                moneys[player_b] = -coin_num
            else:
                moneys[player_b] = moneys[player_b] - coin_num
            if "<C>" in event:
#                 cur_num = random.choice(range(1,100)
                player_c = random.choice(players)
                db[player_c] = db[player_c] - cur_num
                player.remove(player_c)
                event = event.replace("<C>", player_c)
            if "<D>" in event:
#                 coin_num += random.choice(range(1,100)
                player_d = random.choice(players)
                player.remove(player_d)
                event.replace("<D>", player_d)
            if "<E>" in event:
#                 coin_num += random.choice(range(1,100)
                player_e = random.choice(players)
                player.remove(player_e)
                event.replace("<E>", player_e)
            if "<F>" in event:
                player_f = random.choice(players)
                event.replace("<F>", player_f)
            players.append(player_a)
            action = event
        elif action_choice == "Miss":        
            choices = random.sample(set(players), 2)
            player_a = choices[0]
            player_b = choices[1]
#             if "<F>" in event:
#                 player_f = random.choice(players)
#                 event.replace("<F>", player_f)
            action = player_a + " shoots at " + player_b + " but misses."
        elif action_choice == "Self":
            kill_messages = {
                "<A> jumps into the water.": 50,
                "On <A>'s screen an error pops up: `CLIENT DISCONNECTED` <:alertbad:910249086299557888>": 1}
            event = random.choices(population=list(kill_messages.keys()), weights=kill_messages.values(), k=1)[0]
            player_a = random.choice(players)
            players.remove(player_a)
            event = event.replace("<A>", player_a)
            if moneys.get(player_a) == None:
                moneys[player_a] = 0
            action = event
#             case "Special":
#                 pass
        embed.add_field(name="Game:", value=action, inline=False)
        money_txt = ""
        for i in moneys.keys():
            money_txt += i + " " + str(moneys[i]) + "<:coin:910247623787700264>\n"
        if money_txt != "":
            embed.add_field(name="Money:", value=money_txt, inline=False)
        await msg.edit(embed=embed)
        await asyncio.sleep(5)

@tree.command()
async def get_money(interaction: discord.Interaction):
    '''Find out how much money you have in discord'''
    await interaction.response.send_message(str(interaction.user.mention) + " has " + str(add_player_coin(interaction.user.id,interaction.user.username,0)) + " <:coin:910247623787700264>")

@tree.command()
async def discord_coins_leaderboard(interaction: discord.Interaction):
   '''Return the discord coins leaderboard'''
    
#    await interaction.response.defer(ephemeral=False, thinking=True)
    
   test_keys = db
   rankdict = {}
   
   for key in test_keys.keys():
       rankdict[key] = test_keys[key]
   global sorted_rankdict
   sorted_rankdict = sorted(rankdict.items(), key=itemgetter(1), reverse=True)
   message = f"```\n{'Rank:':<5} {'Name:':<20} {'Coins:'}\n{'‾' * 35}\n"
   sorted_rankdict = sorted_rankdict[:10]
   for i in sorted_rankdict:
        message += f"{'#' + str(sorted_rankdict.index(i) + 1):<5} {i[0]:<20} {i[1]:>5,d} 🪙\n"
   message += "```"
   await interaction.channel.send(message)
   embed=discord.Embed(color=0xffd700, title="Discord Coins Leaderboard", description=message)
   await interaction.followup.send(embed=embed)


@tree.command()
async def random_tank(interaction: discord.Interaction):
    '''Get a random tank'''
    await interaction.response.send_message(random.choice(tanks))

@tree.command()
async def long(interaction: discord.Interaction, length: int, barrel: int = 1):
    '''Build your supercalifragilisticexpialidocious long tank equipped with as many barrels as you want!'''
    try:
        long_emoji = [
            "<:longtank_part1:991838180699541504>",
            "<:longtank_part2:991838184910626916>",
            "<:longtank_part3:991838189591470130>",
            "<:longtank_part4:991838192145793125>"
        ]
        if length < 0: length = 0
        if barrel < 0: barrel = 0
        if barrel > length: barrel = length
        
        def even_space(n, k):
            a = []
            for i in range(k): a.append(n // k)
            for i in range(n % k): a[i] += 1
            b = list(OrderedDict.fromkeys(a))
            global x, y
            x, y = b[0], b[1] if len(b) > 1 else ''
            for i in range(len(a)): a[i] = 'x' if a[i] == b[0] else 'y'
            s = ''.join(str(i) for i in a)
            return s
        
        def palindrome_check(str):
            return sum(map(lambda i: str.count(i) % 2, set(str))) <= 1
        
        def palindrome_rearrange(str):   
            hmap = defaultdict(int)
            for i in range(len(str)): hmap[str[i]] += 1
        
            odd_count = 0
        
            for x in hmap:
                if (hmap[x] % 2 != 0):
                    odd_count += 1
                    odd_char = x
        
            first_half = ''
            second_half = ''
        
            for x in sorted(hmap.keys()):
                s = (hmap[x] // 2) * x
                first_half = first_half + s
                second_half = s + second_half
        
            return (first_half + odd_char + second_half) if (odd_count == 1) else (first_half + second_half)

        even_space_encode = even_space(length - barrel, barrel + 1)
        even_space_encode_palindrome = palindrome_rearrange(even_space_encode) if palindrome_check(even_space_encode) else even_space_encode
        
        even_space_encode_palindrome_decode = []
        for i in even_space_encode_palindrome: even_space_encode_palindrome_decode.append(i)
        for i in range(len(even_space_encode_palindrome_decode)):
            even_space_encode_palindrome_decode[i] = x if even_space_encode_palindrome_decode[i] == 'x' else y
        
        output_middle = ""
        for i in range(len(even_space_encode_palindrome_decode) - 1):
            output_middle += (long_emoji[1] * even_space_encode_palindrome_decode[i] + long_emoji[2])
        output_middle += long_emoji[1] * even_space_encode_palindrome_decode[-1]
        msg = f"{long_emoji[0]}{output_middle}{long_emoji[3]}"
        await interaction.response.send_message(msg)
    except:
        await interaction.response.send_message("The tank is too long to build!")

@tree.command()
async def slot(interaction: discord.Interaction, bet: int):
    '''Play the slot machine game!'''
    await interaction.response.defer(ephemeral=False, thinking=True)
    coin = ["<:coin1:910247623787700264>", "<:coin2:991444836869754950>", "<:coin3:976289335844434000>", "<:coin4:976289358200049704>", "<:coin5:976288324266373130>"]
    
    # if bet > db["player_coin"]:
    #     await interaction.followup.send(embed=discord.Embed(
    #         color=discord.Color.red(),
    #         title="SLOT MACHINE :slot_machine:",
    #         description=f"You don't have enough {coin[0]}"))

    if bet <= 0:
    # elif bet <= 0:
        await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), title="SLOT MACHINE :slot_machine:", description=f"The minimum bet is 1 {coin[0]}"))

    else:
        coins_loop = "<a:coin_loop:992273503288037408>"
        multiplier2 = [1, 2, 3, 4, 8]
        multiplier3 = [4, 8, 12, 16, 32]
        events = {
            coin[0]: 12.5 / 26.25,
            coin[1]: 8 / 26.26,
            coin[2]: 3 / 26.26,
            coin[3]: 1.5 / 26.26,
            coin[4]: 1.25 / 26.25,
        }

        slots = []
        for i in range(3):
            slots.append(random.choices(population=list(events.keys()), weights=events.values())[0])

        slot_embed = discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:", description=f"**{'-' * 18}\n|{' {} |'.format(coins_loop) * 3}\n{'-' * 18}**")

        sent_embed = await interaction.followup.send(embed=slot_embed)
        current_slot_pics = [coins_loop] * 3
        for i in range(len(slots)):
            await asyncio.sleep(1.5)
            current_slot_pics[i] = slots[i]
            slot_results_str = f"**{'-' * 18}\n|"
            for thisSlot in current_slot_pics:
                slot_results_str += f" {thisSlot} |"
            new_slot_embed = discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:", description=f"{slot_results_str}\n{'-' * 18}**")
            await sent_embed.edit(embed=new_slot_embed)

        if slots[0] == slots[1]:
            if slots[1] == slots[2]:
                multiplier = multiplier3[coin.index(slots[0])]
            else:
                multiplier = multiplier2[coin.index(slots[0])]
            win = True
        else:
          win = False
        
        if win == True:
            res_2 = "-- **YOU WON** --"
            profit = bet * multiplier
            # db["player_coin"] += profit
        else:
            res_2 = "-- **YOU LOST** --"
            profit = -bet
            # db["player_coin"] -= bet

        # new_player_coin = db["player_coin"]

        embed = discord.Embed(color=0xffd700, title="SLOT MACHINE :slot_machine:", description=f"{slot_results_str}\n{'-' * 18}**\n{res_2}")
        embed.add_field(name="Bet", value=f"{bet} {coin[0]}", inline=True)
        embed.add_field(name="Profit/Loss", value=f"{profit} {coin[0]}" + (f" ({multiplier}x)" if win else ""), inline=True)
        embed.add_field(name="Balance", value=f"N.A. {coin[0]}", inline=True)
        embed.add_field(name="Pay Table", value=f"{'{}'.format(coin[4]) * 3} - 32x\n{'{}'.format(coin[3]) * 3} - 16x\n{'{}'.format(coin[2]) * 3} - 12x\n{'{}'.format(coin[1]) * 3} - 8x\n{'{}'.format(coin[4]) * 2}:grey_question: - 8x\n{'{}'.format(coin[0]) * 3} - 4x\n{'{}'.format(coin[3]) * 2}:grey_question: - 4x\n{'{}'.format(coin[2]) * 2}:grey_question: - 3x\n{'{}'.format(coin[1]) * 2}:grey_question: - 2x\n{'{}'.format(coin[0]) * 2}:grey_question: - 1x", inline=False)
        await sent_embed.edit(embed=embed)

@tree.command()
async def memory(interaction: discord.Interaction):
    '''Test your memory by matching 2 tanks!'''
    await interaction.response.defer(ephemeral=False, thinking=True)
    b = [":white_large_square:" for i in range(16)]
    c = ['a1', 'b1', 'c1', 'd1', 'a2', 'b2', 'c2', 'd2', 'a3', 'b3', 'c3', 'd3', 'a4', 'b4', 'c4', 'd4']
    a = random.sample(tanks, 8) * 2
    random.shuffle(a)
    board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
    answer = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {a[0]} {a[1]} {a[2]} {a[3]}\n:two: {a[4]} {a[5]} {a[6]} {a[7]}\n:three: {a[8]} {a[9]} {a[10]} {a[11]}\n:four: {a[12]} {a[13]} {a[14]} {a[15]}\n"

    def check(m):
        return (m.channel.id == interaction.channel.id and m.author == interaction.user)

    embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description="Test your memory by matching 2 tanks!")
    embed.add_field(name="Time", value="<80s\n<100s\n≥100s", inline=True)
    embed.add_field(name="Reward", value="20 <:coin1:910247623787700264>\n10 <:coin1:910247623787700264>\n5 <:coin1:910247623787700264>", inline=True)
    embed.add_field(name="Controls", value="Type `s` to start the game\nType `q` to quit the game", inline=False)
    message = await interaction.followup.send(embed=embed)

    global gamestart
    gamestart = False

    while gamestart == False:
        try:
            msg = await client.wait_for("message", check=check, timeout=15)
            if str(msg.content.lower()) == "q":
                embed = discord.Embed(color=discord.Color.red(), title="MEMORY GAME :brain:", description="You have quit the game")
                await message.edit(embed=embed)
                break
            if ((str(msg.content.lower()) == "s") or (str(msg.content.lower()) == "q")) == False:
                warn = await interaction.followup.send(":x: Invalid input has been entered :x:")
                await asyncio.sleep(2)
                await warn.delete()
            if str(msg.content.lower()) == "s":
                gamestart = True
                embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=board)
                embed.add_field(name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                await message.edit(embed=embed)
                start = timer()
        except asyncio.TimeoutError:
            embed = discord.Embed(color=discord.Color.red(), title="MEMORY GAME :brain:", description="You did not start the game")
            await message.edit(embed=embed)
            break

        pair = 0
        flag = False
        while gamestart == True:
            try:
                msg = await client.wait_for("message", check=check, timeout=15)
                if str(msg.content.lower()) == "q":
                    board = answer
                    embed = discord.Embed(color=discord.Color.red(), title="MEMORY GAME :brain:", description=f"{board}\nYou have quit the game")
                    await message.edit(embed=embed)
                    break
                if (str(msg.content.lower()) in c) == False:
                    warn2 = await interaction.followup.send(":x: Invalid coordinate has been entered :x:")
                    await asyncio.sleep(2)
                    await warn2.delete()
                elif b[c.index(str(msg.content.lower()))] == ":white_large_square:":
                    if flag == False:
                        x = c.index(str(msg.content.lower()))
                        b[x] = a[x]
                        flag = not flag
                        board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                        embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=board)
                        embed.add_field(name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                        await message.edit(embed=embed)
                    else:
                        y = c.index(str(msg.content.lower()))
                        b[y] = a[y]
                        flag = not flag
                        board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                        embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=board)
                        embed.add_field(name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                        await message.edit(embed=embed)
                        await asyncio.sleep(1)
                        if a[x] == a[y]:
                            pair += 1
                        else:
                            b[x] = ":white_large_square:"
                            b[y] = ":white_large_square:"
                            board = f":black_large_square: :regional_indicator_a: :regional_indicator_b: :regional_indicator_c: :regional_indicator_d:\n:one: {b[0]} {b[1]} {b[2]} {b[3]}\n:two: {b[4]} {b[5]} {b[6]} {b[7]}\n:three: {b[8]} {b[9]} {b[10]} {b[11]}\n:four: {b[12]} {b[13]} {b[14]} {b[15]}\n"
                            embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=board)
                            embed.add_field(name="Controls", value="Type `a1` / `A1` to flip the card\nType `q` to quit the game", inline=False)
                            await message.edit(embed=embed)
                    if pair == 8:
                        end = timer()
                        time_diff = end - start
                        if time_diff < 80:
                            reward = 20
                        elif 80 <= time_diff < 100:
                            reward = 10
                        else:
                            reward = 5
                        gamestart = False
                        # db["player_coin"] += reward
                        # new_player_coin = db["player_coin"]
                        embed = discord.Embed(color=0xffd700, title="MEMORY GAME :brain:", description=f"{board}\n:tada: **YOU WON** :tada:")
                        embed.add_field(name="Time", value=f"{time_diff:.2f}s", inline=True)
                        embed.add_field(name="Reward", value=f"{reward} <:coin1:910247623787700264>", inline=True)
                        embed.add_field(name="Balance", value=f"N.A. <:coin1:910247623787700264>", inline=True)
                        await message.edit(embed=embed)
                        break
                    await message.edit(embed=embed)
                else:
                    warn3 = await interaction.followup.send(":x: The card has already been flipped :x:")
                    await asyncio.sleep(2)
                    await warn3.delete()
            except asyncio.TimeoutError:
                board = answer
                embed = discord.Embed(color=discord.Color.red(), title="MEMORY GAME :brain:", description=f"{board}\nThe game has timed out :hourglass:")
                await message.edit(embed=embed)
                break
        break

# @tree.command()
# async def update_players_database(interaction: discord.Interaction):
#     '''Change from user mention to dict'''
#     for key in db.keys():
#         user_id = convert_mention_to_id(key)
#         db[user_id] = {"name":client.get_user(user_id),"money":db[key], "inventory":{}}
#         db.pop(key)
#     print(db.keys())
#     await interaction.response.send_message("DONE =)")

@tree.command()
async def get_crate_stats(interaction: discord.Interaction, one_star: int, two_star: int, three_star: int):
    '''Optimize the use of in game crates and Estimate the amount of coins'''

    await interaction.response.defer(ephemeral=False, thinking=True)

    one_star_total = 0
    two_star_total = 0
    three_star_total = 0

    for key, value in server_config['awards'].items():
        try:
            if value['rarity'] == "common":
                one_star_total += 1
            elif value['rarity'] == "rare":
                two_star_total += 1
            elif value['rarity'] == "legendary":
                three_star_total += 1
        except:
            pass

    total = one_star_total + two_star_total + three_star_total
    one_star_weight, two_star_weight, three_star_weight = server_config[
        'lootbox_rarity_odds']['common'], server_config['lootbox_rarity_odds'][
            'rare'], server_config['lootbox_rarity_odds']['legendary']
    total_weight = one_star_total * one_star_weight + two_star_total * \
        two_star_weight + three_star_total * three_star_weight
    one_star_prob, two_star_prob, three_star_prob = one_star_weight / \
        total_weight, two_star_weight / total_weight, three_star_weight / total_weight

    basic_crate_price = server_config['lootbox_coin_cost']
    elite_crate_price = server_config['unique_lootbox_coin_cost']

    population_crate = list(range(1, total + 1))
    weights_crate = []
    for i in range(1, one_star_total + 1):
        weights_crate.append(one_star_prob)
    for j in range(1, two_star_total + 1):
        weights_crate.append(two_star_prob)
    for k in range(1, three_star_total + 1):
        weights_crate.append(three_star_prob)

    def basic_or_elite(a, b, c):
        time = 1 / (1 - one_star_prob * a - two_star_prob * b -
                    three_star_prob * c)
        expected_basic_crate_coin = basic_crate_price * time
        if expected_basic_crate_coin < elite_crate_price:
            return f":one: The **OPTIMAL** way to unlock **A NEW UNIQUE SKIN** is **EXPECTED** by using **{time:.2f} BASIC CRATE" + (
                "S" if time > 1 else ""
            ) + f" <:crate:988520294132088892>**, which " + (
                "are" if time > 1 else "is"
            ) + f" worth a **TOTAL** of **{expected_basic_crate_coin:,.0f} COINS <:coin:910247623787700264>**\n"
        else:
            return f":one: The **OPTIMAL** way to unlock **A NEW UNIQUE SKIN** is **EXPECTED** by using **1.00 ELITE CRATE <:elitecrate:989954419846184970>**, which is worth a **TOTAL** of **{elite_crate_price:,.0f} COINS <:coin:910247623787700264>**\n"

    def basic_and_elite_simulate(a, b, c):
        expected_basic_crate = []
        expected_elite_crate = []
        expected_coins_spent = []

        for i in range(0, 1001):
            basic_crates = 0
            prob = 1 - one_star_prob * a - two_star_prob * b - three_star_prob * c
            collected = set()
            for i in range(1, 1 + a):
                collected.add(i)
            for j in range(one_star_total + 1, one_star_total + 1 + b):
                collected.add(j)
            for k in range(one_star_total + two_star_total + 1,
                           one_star_total + two_star_total + 1 + c):
                collected.add(k)

            while True:
                if (1 / prob) * basic_crate_price >= elite_crate_price:
                    break
                got = random.choices(population_crate, weights_crate)
                basic_crates += 1
                for i in got:
                    if int(i) not in collected:
                        collected.add(int(i))
                        if 1 <= int(i) <= one_star_total:
                            prob -= one_star_prob
                        elif (one_star_total + 1) <= int(i) <= (
                                one_star_total + two_star_total):
                            prob -= two_star_prob
                        else:
                            prob -= three_star_prob
            elite_crates = total - len(collected)
            coins_spent = basic_crates * basic_crate_price + elite_crates * elite_crate_price
            expected_basic_crate.append(basic_crates)
            expected_elite_crate.append(elite_crates)
            expected_coins_spent.append(coins_spent)
            remaining = total - a - b - c
            expected_basic_crate_mean = mean(expected_basic_crate)
            expected_elite_crate_mean = mean(expected_elite_crate)
        return f":two: The **OPTIMAL** way to unlock **ALL {remaining} REMAINING UNIQUE SKIN" + (
            "S" if remaining > 1 else ""
        ) + "** is **EXPECTED** by using " + (
            (f"**{expected_basic_crate_mean:,.2f} BASIC CRATE" +
             ("S" if expected_basic_crate_mean > 1 else "") +
             " <:crate:988520294132088892>** and ")
            if expected_basic_crate_mean != 0 else ""
        ) + f"**{expected_elite_crate_mean:,.2f} ELITE CRATE" + (
            "S" if expected_elite_crate_mean > 1 else ""
        ) + f" <:elitecrate:989954419846184970>**, which " + (
            "are" if
            (expected_basic_crate_mean + expected_elite_crate_mean) > 1 else
            "is"
        ) + f" worth a **TOTAL** of **{expected_basic_crate_mean * basic_crate_price + expected_elite_crate_mean * elite_crate_price:,.0f} COINS <:coin:910247623787700264>**"

    def all(a, b, c):
        total_owned = a + b + c
        if (1 <= a <= one_star_total) and (0 <= b <= two_star_total) and (
                0 <= c <= three_star_total):
            if total_owned != total:
                return f"**1,000 SIMULATIONS** have been done based on the number of **{a} ONE-STAR :star:**, **{b} TWO-STAR :star::star:** and **{c} THREE-STAR :star::star::star: SKIN" + (
                    "S" if total_owned > 1 else
                    "") + f"** you have already owned:\n" + basic_or_elite(
                        a, b, c) + basic_and_elite_simulate(a, b, c)
            else:
                return f"You have already unlocked **ALL {total} UNIQUE SKINS**! :tada:"
        else:
            return ":x: **INVALID** data has been entered. Please try again. :x:"

    await interaction.followup.send(all(one_star, two_star, three_star))

@tree.command()
async def season(interaction: discord.Interaction):
    '''Return the current season and remaining time'''
    current_unix_time = time.mktime(datetime.datetime.now().timetuple())
    season_start_number = 13
    season_start_timestamp = 1663966800
    season_duration = 3369600
    season_difference = (current_unix_time - season_start_timestamp) / season_duration
    current_season = ceil((season_start_number - 1) + season_difference)
    season_seconds_remaining = (ceil(season_difference) - season_difference) * 3369600
    day = season_seconds_remaining // (24 * 3600)
    hour = season_seconds_remaining % (24 * 3600) // 3600
    minute = season_seconds_remaining % (24 * 3600) % 3600 // 60
    second = season_seconds_remaining % (24 * 3600) % 3600 % 60
    season_percentage = floor((season_difference % 1) * 100)
    final_msg = f"Season {current_season} Ends in: {int(day)}d {int(hour)}h {int(minute)}m {int(second)}s ({season_percentage}%)"
    await interaction.response.send_message(final_msg)

@tree.command()
async def random_bot_name(interaction: discord.Interaction):
    '''Generate a random bot name.'''

    adjective = [
        "gray",
        "brown",
        "red",
        "pink",
        "crimson",
        "carnelian",
        "orange",
        "yellow",
        "ivory",
        "cream",
        "green",
        "viridian",
        "aquamarine",
        "cyan",
        "blue",
        "cerulean",
        "azure",
        "indigo",
        "navy",
        "violet",
        "purple",
        "lavender",
        "magenta",
        "rainbow",
        "iridescent",
        "spectrum",
        "prism",
        "bold",
        "vivid",
        "pale",
        "clear",
        "glass",
        "translucent",
        "misty",
        "dark",
        "light",
        "gold",
        "silver",
        "copper",
        "bronze",
        "steel",
        "iron",
        "brass",
        "mercury",
        "zinc",
        "chrome",
        "platinum",
        "titanium",
        "nickel",
        "lead",
        "pewter",
        "rust",
        "metal",
        "stone",
        "quartz",
        "granite",
        "marble",
        "alabaster",
        "agate",
        "jasper",
        "pebble",
        "pyrite",
        "crystal",
        "geode",
        "obsidian",
        "mica",
        "flint",
        "sand",
        "gravel",
        "boulder",
        "basalt",
        "ruby",
        "beryl",
        "scarlet",
        "citrine",
        "sulpher",
        "topaz",
        "amber",
        "emerald",
        "malachite",
        "jade",
        "abalone",
        "lapis",
        "sapphire",
        "diamond",
        "peridot",
        "gem",
        "jewel",
        "bevel",
        "coral",
        "jet",
        "ebony",
        "wood",
        "tree",
        "cherry",
        "maple",
        "cedar",
        "branch",
        "bramble",
        "rowan",
        "ash",
        "fir",
        "pine",
        "cactus",
        "alder",
        "grove",
        "forest",
        "jungle",
        "palm",
        "bush",
        "mulberry",
        "juniper",
        "vine",
        "ivy",
        "rose",
        "lily",
        "tulip",
        "daffodil",
        "honeysuckle",
        "fuschia",
        "hazel",
        "walnut",
        "almond",
        "lime",
        "lemon",
        "apple",
        "blossom",
        "bloom",
        "crocus",
        "rose",
        "buttercup",
        "dandelion",
        "iris",
        "carnation",
        "fern",
        "root",
        "branch",
        "leaf",
        "seed",
        "flower",
        "petal",
        "pollen",
        "orchid",
        "mangrove",
        "cypress",
        "sequoia",
        "sage",
        "heather",
        "snapdragon",
        "daisy",
        "mountain",
        "hill",
        "alpine",
        "chestnut",
        "valley",
        "glacier",
        "forest",
        "grove",
        "glen",
        "tree",
        "thorn",
        "stump",
        "desert",
        "canyon",
        "dune",
        "oasis",
        "mirage",
        "well",
        "spring",
        "meadow",
        "field",
        "prairie",
        "grass",
        "tundra",
        "island",
        "shore",
        "sand",
        "shell",
        "surf",
        "wave",
        "foam",
        "tide",
        "lake",
        "river",
        "brook",
        "stream",
        "pool",
        "pond",
        "sun",
        "sprinkle",
        "shade",
        "shadow",
        "rain",
        "cloud",
        "storm",
        "hail",
        "snow",
        "sleet",
        "thunder",
        "lightning",
        "wind",
        "hurricane",
        "typhoon",
        "dawn",
        "sunrise",
        "morning",
        "noon",
        "twilight",
        "evening",
        "sunset",
        "midnight",
        "night",
        "sky",
        "star",
        "stellar",
        "comet",
        "nebula",
        "quasar",
        "solar",
        "lunar",
        "planet",
        "meteor",
        "sprout",
        "pear",
        "plum",
        "kiwi",
        "berry",
        "apricot",
        "peach",
        "mango",
        "pineapple",
        "coconut",
        "olive",
        "ginger",
        "root",
        "plain",
        "fancy",
        "stripe",
        "spot",
        "speckle",
        "spangle",
        "ring",
        "band",
        "blaze",
        "paint",
        "pinto",
        "shade",
        "tabby",
        "brindle",
        "patch",
        "calico",
        "checker",
        "dot",
        "pattern",
        "glitter",
        "glimmer",
        "shimmer",
        "dull",
        "dust",
        "dirt",
        "glaze",
        "scratch",
        "quick",
        "swift",
        "fast",
        "slow",
        "clever",
        "fire",
        "flicker",
        "flash",
        "spark",
        "ember",
        "coal",
        "flame",
        "chocolate",
        "vanilla",
        "sugar",
        "spice",
        "cake",
        "pie",
        "cookie",
        "candy",
        "caramel",
        "spiral",
        "round",
        "jelly",
        "square",
        "narrow",
        "long",
        "short",
        "small",
        "tiny",
        "big",
        "giant",
        "great",
        "atom",
        "peppermint",
        "mint",
        "butter",
        "fringe",
        "rag",
        "quilt",
        "truth",
        "lie",
        "holy",
        "curse",
        "noble",
        "sly",
        "brave",
        "shy",
        "lava",
        "foul",
        "leather",
        "fantasy",
        "keen",
        "luminous",
        "feather",
        "sticky",
        "gossamer",
        "cotton",
        "rattle",
        "silk",
        "satin",
        "cord",
        "denim",
        "flannel",
        "plaid",
        "wool",
        "linen",
        "silent",
        "flax",
        "weak",
        "valiant",
        "fierce",
        "gentle",
        "rhinestone",
        "splash",
        "north",
        "south",
        "east",
        "west",
        "summer",
        "winter",
        "autumn",
        "spring",
        "season",
        "equinox",
        "solstice",
        "paper",
        "motley",
        "torch",
        "ballistic",
        "rampant",
        "shag",
        "freckle",
        "wild",
        "free",
        "chain",
        "sheer",
        "crazy",
        "mad",
        "candle",
        "ribbon",
        "lace",
        "notch",
        "wax",
        "shine",
        "shallow",
        "deep",
        "bubble",
        "harvest",
        "fluff",
        "venom",
        "boom",
        "slash",
        "rune",
        "cold",
        "quill",
        "love",
        "hate",
        "garnet",
        "zircon",
        "power",
        "bone",
        "void",
        "horn",
        "glory",
        "cyber",
        "nova",
        "hot",
        "helix",
        "cosmic",
        "quark",
        "quiver",
        "holly",
        "clover",
        "polar",
        "regal",
        "ripple",
        "ebony",
        "wheat",
        "phantom",
        "dew",
        "chisel",
        "crack",
        "chatter",
        "laser",
        "foil",
        "tin",
        "clever",
        "treasure",
        "maze",
        "twisty",
        "curly",
        "fortune",
        "fate",
        "destiny",
        "cute",
        "slime",
        "ink",
        "disco",
        "plume",
        "time",
        "psychadelic",
        "relic",
        "fossil",
        "water",
        "savage",
        "ancient",
        "rapid",
        "road",
        "trail",
        "stitch",
        "button",
        "bow",
        "nimble",
        "zest",
        "sour",
        "bitter",
        "phase",
        "fan",
        "frill",
        "plump",
        "pickle",
        "mud",
        "puddle",
        "pond",
        "river",
        "spring",
        "stream",
        "battle",
        "arrow",
        "plume",
        "roan",
        "pitch",
        "tar",
        "cat",
        "dog",
        "horse",
        "lizard",
        "bird",
        "fish",
        "saber",
        "scythe",
        "sharp",
        "soft",
        "razor",
        "neon",
        "dandy",
        "swamp",
        "marsh",
        "bog",
        "peat",
        "moor",
        "muck",
        "mire",
        "grave",
        "fair",
        "just",
        "brick",
        "puzzle",
        "skitter",
        "prong",
        "fork",
        "dent",
        "dour",
        "warp",
        "luck",
        "coffee",
        "split",
        "chip",
        "hollow",
        "heavy",
        "legend",
        "hickory",
        "mesquite",
        "nettle",
        "rogue",
        "charm",
        "prickle",
        "bead",
        "sponge",
        "whip",
        "bald",
        "frost",
        "fog",
        "oil",
        "veil",
        "cliff",
        "volcano",
        "rift",
        "maze",
        "proud",
        "dew",
        "mirror",
        "shard",
        "salt",
        "pepper",
        "honey",
        "thread",
        "bristle",
        "ripple",
        "glow",
        "zenith"
    ]

    noun = [
        "head",
        "crest",
        "crown",
        "tooth",
        "fang",
        "horn",
        "frill",
        "skull",
        "bone",
        "tongue",
        "throat",
        "voice",
        "nose",
        "snout",
        "chin",
        "eye",
        "sight",
        "seer",
        "speaker",
        "singer",
        "song",
        "chanter",
        "howler",
        "chatter",
        "shrieker",
        "shriek",
        "jaw",
        "bite",
        "biter",
        "neck",
        "shoulder",
        "fin",
        "wing",
        "arm",
        "lifter",
        "grasp",
        "grabber",
        "hand",
        "paw",
        "foot",
        "finger",
        "toe",
        "thumb",
        "talon",
        "palm",
        "touch",
        "racer",
        "runner",
        "hoof",
        "fly",
        "flier",
        "swoop",
        "roar",
        "hiss",
        "hisser",
        "snarl",
        "dive",
        "diver",
        "rib",
        "chest",
        "back",
        "ridge",
        "leg",
        "legs",
        "tail",
        "beak",
        "walker",
        "lasher",
        "swisher",
        "carver",
        "kicker",
        "roarer",
        "crusher",
        "spike",
        "shaker",
        "charger",
        "hunter",
        "weaver",
        "crafter",
        "binder",
        "scribe",
        "muse",
        "snap",
        "snapper",
        "slayer",
        "stalker",
        "track",
        "tracker",
        "scar",
        "scarer",
        "fright",
        "killer",
        "death",
        "doom",
        "healer",
        "saver",
        "friend",
        "foe",
        "guardian",
        "thunder",
        "lightning",
        "cloud",
        "storm",
        "forger",
        "scale",
        "hair",
        "braid",
        "nape",
        "belly",
        "thief",
        "stealer",
        "reaper",
        "giver",
        "taker",
        "dancer",
        "player",
        "gambler",
        "twister",
        "turner",
        "painter",
        "dart",
        "drifter",
        "sting",
        "stinger",
        "venom",
        "spur",
        "ripper",
        "devourer",
        "knight",
        "lady",
        "lord",
        "queen",
        "king",
        "master",
        "mistress",
        "prince",
        "princess",
        "duke",
        "dutchess",
        "samurai",
        "ninja",
        "knave",
        "servant",
        "sage",
        "wizard",
        "witch",
        "warlock",
        "warrior",
        "jester",
        "paladin",
        "bard",
        "trader",
        "sword",
        "shield",
        "knife",
        "dagger",
        "arrow",
        "bow",
        "fighter",
        "bane",
        "follower",
        "leader",
        "scourge",
        "watcher",
        "cat",
        "panther",
        "tiger",
        "cougar",
        "puma",
        "jaguar",
        "ocelot",
        "lynx",
        "lion",
        "leopard",
        "ferret",
        "weasel",
        "wolverine",
        "bear",
        "raccoon",
        "dog",
        "wolf",
        "kitten",
        "puppy",
        "cub",
        "fox",
        "hound",
        "terrier",
        "coyote",
        "hyena",
        "jackal",
        "pig",
        "horse",
        "donkey",
        "stallion",
        "mare",
        "zebra",
        "antelope",
        "gazelle",
        "deer",
        "buffalo",
        "bison",
        "boar",
        "elk",
        "whale",
        "dolphin",
        "shark",
        "fish",
        "minnow",
        "salmon",
        "ray",
        "fisher",
        "otter",
        "gull",
        "duck",
        "goose",
        "crow",
        "raven",
        "bird",
        "eagle",
        "raptor",
        "hawk",
        "falcon",
        "moose",
        "heron",
        "owl",
        "stork",
        "crane",
        "sparrow",
        "robin",
        "parrot",
        "cockatoo",
        "carp",
        "lizard",
        "gecko",
        "iguana",
        "snake",
        "python",
        "viper",
        "boa",
        "condor",
        "vulture",
        "spider",
        "fly",
        "scorpion",
        "heron",
        "toucan",
        "bee",
        "wasp",
        "hornet",
        "rabbit",
        "bunny",
        "hare",
        "brow",
        "mustang",
        "ox",
        "piper",
        "soarer",
        "moth",
        "mask",
        "hide",
        "hero",
        "antler",
        "chill",
        "chiller",
        "gem",
        "ogre",
        "myth",
        "elf",
        "fairy",
        "pixie",
        "dragon",
        "griffin",
        "unicorn",
        "pegasus",
        "sprite",
        "fancier",
        "chopper",
        "slicer",
        "skinner",
        "butterfly",
        "legend",
        "wanderer",
        "rover",
        "raver",
        "loon",
        "lancer",
        "glass",
        "glazer",
        "flame",
        "crystal",
        "lantern",
        "lighter",
        "cloak",
        "bell",
        "ringer",
        "keeper",
        "centaur",
        "bolt",
        "catcher",
        "whimsey",
        "quester",
        "rat",
        "mouse",
        "serpent",
        "wyrm",
        "gargoyle",
        "thorn",
        "whip",
        "rider",
        "spirit",
        "sentry",
        "bat",
        "beetle",
        "burn",
        "cowl",
        "stone",
        "gem",
        "collar",
        "mark",
        "grin",
        "scowl",
        "spear",
        "razor",
        "edge",
        "seeker",
        "jay",
        "ape",
        "monkey",
        "gorilla",
        "koala",
        "kangaroo",
        "yak",
        "sloth",
        "ant",
        "roach",
        "seed",
        "eater",
        "razor",
        "shirt",
        "face",
        "goat",
        "mind",
        "shift",
        "rider",
        "face",
        "mole",
        "vole",
        "pirate",
        "llama",
        "stag",
        "bug",
        "cap",
        "boot",
        "drop",
        "hugger",
        "sargent",
        "snagglefoot",
        "carpet",
        "curtain"
    ]

    generated_random_bot_name = random.choice(noun).capitalize() + random.choice(adjective)
    await interaction.response.send_message(generated_random_bot_name)

@tree.command()
async def fandom(interaction: discord.Interaction, article: str):
    '''Fetch any articles from Rocket Bot Royale fandom wiki here!'''
    await interaction.response.defer(ephemeral=False, thinking=True)
    p = rocketbotroyale.page(article)
    try:
      page1 = page(title = article)
      sent_embed = await interaction.followup.send(embed=discord.Embed(description="Fetching page..."))
      output = discord.Embed(
              color=0xffd700,
              title=page1.title,
              description=page1.summary,
              url=f"https://rocketbotroyale.fandom.com/wiki/{page1.title}".replace(" ", "_"),
              timestamp=datetime.datetime.utcnow())
      list_of_images = p.images
      png_or_gif = [ x for x in list_of_images if ".png" in x or ".gif" in x]
      set_image = "https://static.wikia.nocookie.net/rocketbotroyale/images/c/c4/Slide1_mainpage.png/revision/latest?cb=20220712121433" if len(png_or_gif) == 0 else png_or_gif[0]
      output.set_image(url=set_image)
      output.set_thumbnail(url="https://static.wikia.nocookie.net/rocketbotroyale/images/e/e6/Site-logo.png")
      output.set_footer(text="All information is gathered through fandom.com")
      await sent_embed.edit(embed=output)
    except:
      await interaction.followup.send(embed=discord.Embed(color=0xff0000, description=f':x: "{article}" is not found. Make sure capitalization is correct!',timestamp=datetime.datetime.utcnow()))

@tree.command(guild=discord.Object(id=962142361935314996))
async def sync_commands(interaction: discord.Interaction):
    await tree.sync()
    await tree.sync(guild=discord.Object(id=962142361935314996))
    await interaction.response.send_message("Commands synced.")

def main():
    client.run(discord_token)

if (__name__ == "__main__"):
    main()
""
