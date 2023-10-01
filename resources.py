from typing import Tuple

from pyxel import blt, play, playm, pal, text

from constants import GRID_CELL_SIZE, HALF_GRID_CELL

SPRITE_SIZE = 16

IMAGE_SPRITES = 0
IMAGE_UI = 1

SPRITE_BG = (0, 0)
SPRITE_BGB = (1, 0)
SPRITE_BGC = (2, 0)
SPRITE_DARK_BG = (0, 15)

SPRITE_WALL_A = (0, 2)
SPRITE_WALL_B = (1, 2)
SPRITE_WALL_C = (2, 2)
SPRITE_WALL_D = (0, 3)
SPRITE_WALL_E = (2, 3)
SPRITE_WALL_F = (0, 4)
SPRITE_WALL_G = (1, 4)
SPRITE_WALL_H = (2, 4)
SPRITE_WALL_AA = (3, 2)
SPRITE_WALL_BB = (4, 2)
SPRITE_WALL_CC = (5, 2)
SPRITE_WALL_DD = (3, 3)
SPRITE_WALL_EE = (4, 3)
SPRITE_WALL_XX = (3, 4)
SPRITE_WALL_YY = (4, 4)

SPRITE_PLAYER = (0, 5)
SPRITE_Enemy = (0, 6)
SPRITE_Enemy_BIG = (0, 7)
SPRITE_SPAWN = (4, 0)
SPRITE_TARGET = (5, 0)

SPRITE_SHOTGUN = (1, 1)
SPRITE_SPEED = (2, 1)
SPRITE_HEALTH = (3, 1)

SPRITE_BULLET = (0, 1)
SPRITE_BULLET_SHELL = (4, 1)


SPRITE_PLAYER_WALK = [(0, 5), (1, 5), (2, 5), (3, 5)]
SPRITE_PLAYER_IDLE = [(5, 5), (6, 5), (7, 5), (8, 5)]
SPRITE_PLAYER_DEATH = (9, 5)

SPRITE_ENEMY_IDLE = [(0, 6), (1, 6), (2, 6), (3, 6)]
SPRITE_ENEMY_DEATH = (4, 6)
SPRITE_ENEMY_BIG_IDLE = [(0, 7), (1, 7), (2, 7), (3, 7)]
SPRITE_ENEMY_BIG_DEATH = (4, 7)


SPRITE_UI_BOX = (0, 0)
SPRITE_UI_CURSOR = (1, 4)
SPRITE_UI_HIGHLIGHT = (0, 4)
SPRITE_UI_HEART_FULL = (0, 5)
SPRITE_UI_HEART_EMPTY = (1, 5)
SPRITE_UI_AMMO_FULL = (0, 6)
SPRITE_UI_AMMO_EMPTY = (1, 6)

SPRITE_UI_ICON_SHOOT = (0, 7)
SPRITE_UI_ICON_RELOAD = (1, 7)
SPRITE_UI_ICON_RUN = (2, 7)
SPRITE_UI_ICON_ENEMY = (3, 7)
SPRITE_UI_ICON_STUCK = (4, 7)


#
# SOUNDS
#
SOUND_SHOT = 0
SOUND_HIT = 1
SOUND_MISS = 2
SOUND_PLAYER_DEATH = 3
SOUND_ENEMY_DEATH = 4
SOUND_MOVE = 5
SOUND_ROLL = 6
SOUND_CLICK = 7  # action selection, button press, tutorial skip

#
# MUSIC
#
MUSIC_A = 0
MUSIC_B = 1

#
# COLORS
#
COLOR_BACKGROUND = 0
COLOR_TEXT = 1
COLOR_TEXT_INACTIVE = 6
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

def bold_text(x, y, t):
    text(x - 1, y, t, COLOR_HIGHLIGHT)
    text(x, y - 1, t, COLOR_HIGHLIGHT)
    text(x + 1, y, t, COLOR_HIGHLIGHT)
    text(x, y + 1, t, COLOR_HIGHLIGHT)
    text(x, y, t, COLOR_BACKGROUND)


def play_music(music: int) -> None:
    # In-game music should leave channel 1 for sounds
    playm(music, loop=True)


def play_sound(sound: int, channel: int = 1) -> None:
    play(channel, sound)
