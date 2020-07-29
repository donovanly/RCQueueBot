import asyncio
import discord
import logging
from discord.ext import commands, tasks
from game_mode import GameMode
from settings import (
    SOLO_CHANNEL_ID,
    SQUAD_CHANNEL_ID,
    MIN_SOLO_QUEUE,
    MIN_SOLO_TIME,
    MIN_SQUAD_QUEUE,
    MIN_SQUAD_TIME,
    TOKEN,
)
from util import (
    generate_confirm_embed,
    generate_play_embed,
    generate_queue_embed,
    generate_ready_embed,
)
from constants import (
    CANCEL,
    CHECKMARK,
    DEFAULT_DESCRIPTION,
    SOLO_ICON_URL,
    SQUAD_ICON_URL,
    THUMBS_UP,
    UNCONFIRMED,
)

solo_message_id = None
squad_message_id = None
solo_queue_set = set()
squad_queue_set = set()

bot = commands.Bot(command_prefix='!')

def load_logger():
    logger = logging.getLogger('events')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

async def countdown(game_mode: GameMode):
    global solo_queue_set, solo_message_id, squad_queue_set, squad_message_id
    channel = None
    message = None
    if game_mode == GameMode.SOLO:
        channel = bot.get_channel(SOLO_CHANNEL_ID)
        message = await channel.fetch_message(solo_message_id)
        for member in solo_queue_set:
            dm = await member.create_dm()
            await dm.send(embed=generate_ready_embed(
                description='Your ' + GameMode.get_title(game_mode) + ' is ready, countdown will begin in 60 seconds: ' + message.jump_url,
                game_mode=game_mode,
            ))
    elif game_mode == GameMode.SQUAD:
        channel = bot.get_channel(SQUAD_CHANNEL_ID)
        message = await channel.fetch_message(squad_message_id)
        for member in squad_queue_set:
            dm = await member.create_dm()
            await dm.send(embed=generate_ready_embed(
                description='Your ' + GameMode.get_title(game_mode) + ' is ready, countdown will begin in 60 seconds: ' + message.jump_url,
                game_mode=game_mode,
            ))

    await channel.send("Countdown will begin in 50 seconds")
    await asyncio.sleep(20)
    await channel.send("Countdown will begin in 30 seconds")
    await asyncio.sleep(20)
    await channel.send("Press start in {countdown_time}...".format(countdown_time=10))
    for x in reversed(range(1, 10)):
        await asyncio.sleep(1)
        await channel.send("{cur_time}...".format(cur_time=x))
    await asyncio.sleep(1)
    await channel.send(embed=generate_play_embed(game_mode))

    if game_mode == GameMode.SOLO:
        solo_message_id = None
        solo_queue_set = set()
    elif game_mode == GameMode.SQUAD:
        squad_message_id = None
        squad_queue_set = set()

async def solo_lobby_reaction_add(payload):
    global solo_message_id, solo_queue_set
    message = await bot.get_channel(SOLO_CHANNEL_ID).fetch_message(solo_message_id)

    if payload.member not in solo_queue_set:
        solo_queue_set.add(payload.member)

    description = DEFAULT_DESCRIPTION
    description += '\nA minimum of {min_players} players or after {minutes} minutes and {seconds} seconds have passed will the countdown begin.'.format(
        min_players=MIN_SOLO_QUEUE,
        minutes=MIN_SOLO_TIME//60,
        seconds=MIN_SOLO_TIME%60,
    )
    if len(solo_queue_set) > 0:
        description += '\nPlayers in Lobby:\n'
        for player in sorted(solo_queue_set, key=lambda k: k.name):
            description += player.mention + '\n'

    await message.edit(embed=generate_queue_embed(
        description=description,
        game_mode=GameMode.SOLO,
        ready=len(solo_queue_set) >= MIN_SOLO_QUEUE,
    ))
    if len(solo_queue_set) >= MIN_SOLO_QUEUE:
        await countdown(GameMode.SOLO)


@bot.command(name='start_solo', help='Start a solo lobby queue.')
async def start_solo(ctx):
    global solo_message_id

    if ctx.channel.id != SOLO_CHANNEL_ID:
        return

    if solo_message_id is not None:
        await ctx.send("A solo lobby queue has already begun!")
        return

    embed = generate_queue_embed(
        description=DEFAULT_DESCRIPTION + '\nA minimum of {min_players} players or after {minutes} minutes and {seconds} seconds have passed will the countdown begin.'.format(
            min_players=MIN_SOLO_QUEUE,
            minutes=MIN_SOLO_TIME//60,
            seconds=MIN_SOLO_TIME%60,
        ),
        game_mode=GameMode.SOLO,
        ready=False,
    )
    message = await ctx.send(
        embed=embed,
    )
    await message.add_reaction(THUMBS_UP)
    solo_message_id = message.id

    await asyncio.sleep(MIN_SOLO_TIME)
    if solo_message_id:
        description = DEFAULT_DESCRIPTION + '\nPlayers in Lobby:\n'
        for player in sorted(solo_queue_set, key=lambda k: k.name):
            description += player.mention + '\n'
        await message.edit(embed=generate_queue_embed(
            description=description,
            game_mode=GameMode.SOLO,
            ready=True,
        ))

        await countdown(GameMode.SOLO)


async def squad_lobby_reaction_add(payload):
    global squad_message_id, squad_queue_set
    message = await bot.get_channel(SQUAD_CHANNEL_ID).fetch_message(squad_message_id)

    if payload.member not in squad_queue_set:
        squad_queue_set.add(payload.member)

    description = DEFAULT_DESCRIPTION
    description += '\nA minimum of {min_players} squads or after {minutes} minutes and {seconds} seconds have passed will the countdown begin.'.format(
        min_players=MIN_SQUAD_QUEUE,
        minutes=MIN_SQUAD_TIME//60,
        seconds=MIN_SQUAD_TIME%60,
    )
    if len(squad_queue_set) > 0:
        description += '\nPlayers in Lobby:\n'
        for player in sorted(squad_queue_set, key=lambda k: k.name):
            description += player.mention + '\n'

    await message.edit(embed=generate_queue_embed(
        description=description,
        game_mode=GameMode.SQUAD,
        ready=len(squad_queue_set) >= MIN_SQUAD_QUEUE,
    ))
    if len(squad_queue_set) >= MIN_SQUAD_QUEUE:
        await countdown(GameMode.SQUAD)


@bot.command(name='start_squad', help='Start a squad lobby queue.')
async def start_squad(ctx):
    global squad_message_id

    if ctx.channel.id != SQUAD_CHANNEL_ID:
        return

    if squad_message_id is not None:
        await ctx.send("A squad lobby queue has already begun!")
        return

    embed = generate_queue_embed(
        description=DEFAULT_DESCRIPTION + '\nA minimum of {min_squads} squads or after {minutes} minutes and {seconds} seconds have passed will the countdown begin.'.format(
            min_squads=MIN_SQUAD_QUEUE,
            minutes=MIN_SQUAD_TIME//60,
            seconds=MIN_SQUAD_TIME%60,
        ),
        game_mode=GameMode.SQUAD,
        ready=False,
    )
    message = await ctx.send(
        embed=embed,
    )
    await message.add_reaction(THUMBS_UP)
    squad_message_id = message.id

    await asyncio.sleep(MIN_SQUAD_TIME)
    if squad_message_id:
        description = DEFAULT_DESCRIPTION + '\nSquad Captains in Lobby:\n'
        for player in sorted(squad_queue_set, key=lambda k: k.name):
            description += player.mention + '\n'
        await message.edit(embed=generate_queue_embed(
            description=description,
            game_mode=GameMode.SQUAD,
            ready=True,
        ))

        await countdown(GameMode.SQUAD)


@bot.event
async def on_raw_reaction_add(payload):
    global solo_message_id, squad_message_id
    if payload.member is None or \
        payload.member.bot:
        return

    if payload.message_id == solo_message_id and payload.emoji.name == THUMBS_UP:
        await solo_lobby_reaction_add(payload)

    if payload.message_id == squad_message_id and payload.emoji.name == THUMBS_UP:
        await squad_lobby_reaction_add(payload)

@bot.event
async def on_raw_reaction_remove(payload):
    global solo_message_id, solo_queue_set, squad_message_id, squad_queue_set

    if payload.message_id not in [solo_message_id, squad_message_id] or\
        payload.emoji.name != THUMBS_UP:
        return

    description = DEFAULT_DESCRIPTION
    game_mode = None
    message = None

    if payload.message_id == solo_message_id:
        game_mode = GameMode.SOLO
        message = await bot.get_channel(SOLO_CHANNEL_ID).fetch_message(solo_message_id)
        for member in solo_queue_set:
            if payload.user_id == member.id:
                solo_queue_set.remove(member)
                break
        description += '\nA minimum of {min_players} players or after {minutes} minutes and {seconds} seconds have passed will the countdown begin.'.format(
            min_players=MIN_SOLO_QUEUE,
            minutes=MIN_SOLO_TIME//60,
            seconds=MIN_SOLO_TIME%60,
        )
        description += '\nPlayers in Lobby:\n'
        if len(solo_queue_set) > 0:
            for player in sorted(solo_queue_set, key=lambda k: k.name):
                description += player.mention + '\n'
    elif payload.message_id == squad_message_id:
        game_mode = GameMode.SQUAD
        message = await bot.get_channel(SQUAD_CHANNEL_ID).fetch_message(squad_message_id)
        for member in squad_queue_set:
            if payload.user_id == member.id:
                squad_queue_set.remove(member)
                break
        description += '\nA minimum of {min_players} squads or after {minutes} minutes and {seconds} seconds have passed will the countdown begin.'.format(
            min_players=MIN_SQUAD_QUEUE,
            minutes=MIN_SQUAD_TIME//60,
            seconds=MIN_SQUAD_TIME%60,
        )
        description += '\Squad captains in Lobby:\n'
        if len(squad_queue_set) > 0:
            for player in sorted(squad_queue_set, key=lambda k: k.name):
                description += player.mention + '\n'

    await message.edit(embed=generate_queue_embed(
        description=description,
        game_mode=game_mode,
        ready=False,
    ))

load_logger()
bot.run(TOKEN)
