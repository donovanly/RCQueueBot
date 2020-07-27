from constants import PLAY_ICON_URL
from discord import Embed
from game_mode import GameMode

def generate_queue_embed(description: str, game_mode: GameMode, ready: bool):
    embed = Embed(
        color=0x008000 if ready else 0x800000,
        description=description,
        title=GameMode.get_title(game_mode),
    ).set_thumbnail(
        url=GameMode.get_icon_url(game_mode),
    )

    return embed

def generate_ready_embed(description: str, game_mode: GameMode):
    embed = Embed(
        color=0x008000,
        description=description,
        title=GameMode.get_title(game_mode) + " to Begin Soon."
    ).set_thumbnail(
        url=GameMode.get_icon_url(game_mode),
    )

    return embed

def generate_confirm_embed(description: str, game_mode: GameMode):
    embed = Embed(
        color=0x008000,
        description=description,
        title='Confirm ' + GameMode.get_title(game_mode)
    ).set_thumbnail(
        url=GameMode.get_icon_url(game_mode),
    )

    return embed

def generate_play_embed(game_mode: GameMode):
    description = 'Please remember to select '
    if game_mode == GameMode.SOLO:
        description += 'SOLO '
    elif game_mode == GameMode.SQUAD:
        description += 'SQUAD '
    description += 'in game. Good luck and have fun!'
    embed = Embed(
        color=0x95edd7,
        description=description,
        title='Start ' + GameMode.get_title(game_mode)
    ).set_thumbnail(url=PLAY_ICON_URL)

    return embed