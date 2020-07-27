from enum import Enum
from constants import SOLO_ICON_URL, SQUAD_ICON_URL

class GameMode(Enum):
    SOLO = 1
    DUO = 2
    SQUAD = 3

    def get_icon_url(game_mode):
        if game_mode == GameMode.SOLO:
            return SOLO_ICON_URL
        if game_mode == GameMode.SQUAD:
            return SQUAD_ICON_URL

    def get_title(game_mode):
        if game_mode == GameMode.SOLO:
            return 'Solo Lobby Queue'
        if game_mode == GameMode.SQUAD:
            return 'Squad Lobby Queue'