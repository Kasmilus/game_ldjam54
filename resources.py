from typing import Tuple

from pyxel import blt, play, playm, pal

from constants import GRID_CELL_SIZE, HALF_GRID_CELL
from game_object import ObjType

SPRITE_SIZE = 16

IMAGE_SPRITES = 0
IMAGE_UI = 1

SPRITE_A = (1, 0)
SPRITE_B = (2, 0)

SPRITE_ANIM = [(0, 0), (1, 0), (2, 0), (3, 0)]

#
# SPRITES
#
ALL_OBJECTS = {
    "PLAYER": {'name': 'Player', "sprite": SPRITE_ANIM, "obj_type": ObjType.Player},

    "A": {'name': 'A', "sprite": SPRITE_A, "obj_type": ObjType.Player},
    "B": {'name': 'B', "sprite": SPRITE_B, "obj_type": ObjType.Player},
}


#
# SOUNDS
#
SOUND_A = 0
SOUND_B = 1

#
# MUSIC
#
MUSIC_A = 0
MUSIC_B = 1

#
# COLORS
#
COLOR_BACKGROUND = 3
COLOR_TEXT = 6
COLOR_HIGHLIGHT = 2


def flip_colors() -> None:
    for i in range(0, 8):
        pal(i, i+8)


def reset_color() -> None:
    pal()


def blt_sprite(spritesheet_pos: Tuple[int, int], x: int, y: int, transparent_color=COLOR_BACKGROUND, invert: bool = False, invert_y: bool = False) -> None:
    size_x = SPRITE_SIZE
    size_y = SPRITE_SIZE
    if invert:
        size_x = -size_x
    if invert_y:
        size_y = -size_y

    blt(x, y, IMAGE_SPRITES,
        SPRITE_SIZE*spritesheet_pos[0], SPRITE_SIZE*spritesheet_pos[1],
        size_x, size_y, colkey=transparent_color)


def blt_ui_sprite(spritesheet_pos: Tuple[int, int], size: Tuple[int, int], x: int, y: int, transparent_color=COLOR_BACKGROUND) -> None:
    blt(x, y, IMAGE_UI,
        SPRITE_SIZE*spritesheet_pos[0], SPRITE_SIZE*spritesheet_pos[1],
        size[0], size[1], colkey=transparent_color)

def play_music(music: int) -> None:
    # In-game music should leave channel 1 for sounds
    playm(music, loop=True)


def play_sound(sound: int, channel: int = 1) -> None:
    play(channel, sound)
