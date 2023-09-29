from typing import List, Tuple
from enum import Enum

from game_object import Obj, ObjType


class GameState(Enum):
    Game = 1,
    GameOver = 2


class Game:
    def __init__(self):
        self.game_state: GameState = GameState.Game
        self.objects: List[Obj] = []  # List of only objects in current and surrounding rooms

        self.player_obj: Obj = None  # Reference to the player

        self.camera_x = 0
        self.camera_y = 0
        self.camera_target_x = 0
        self.camera_target_y = 0

        self.stop_frames = 0
        self.cam_shake_timer = 0


def init_game():
    global game
    global game_checkpoint
    game = Game()
    game_checkpoint = None

