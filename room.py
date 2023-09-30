import math
from typing import Tuple

from constants import *
import game


def get_pos_for_room(cell_pos: Tuple[int, int], room_coords: Tuple[int, int] = None) -> Tuple[int, int]:
    if room_coords is None:
        room_coords = get_current_room()
    room_origin = get_pos_from_room_coords(room_coords)
    return room_origin[0] + cell_pos[0] * GRID_CELL_SIZE, room_origin[1] + cell_pos[1] * GRID_CELL_SIZE


def get_room_from_pos(pos: Tuple[int, int]) -> Tuple[int, int]:
    cell_coord = round(pos[0] / GRID_CELL_SIZE), round(pos[1] / GRID_CELL_SIZE)
    room_coord = math.floor(cell_coord[0] / ROOM_SIZE_X), math.floor(cell_coord[1] / ROOM_SIZE_Y)
    return room_coord


def get_pos_from_room_coords(room_coords: Tuple[int, int]) -> Tuple[int, int]:
    pos = room_coords[0] * ROOM_SIZE_X * GRID_CELL_SIZE, room_coords[1] * ROOM_SIZE_Y * GRID_CELL_SIZE
    return pos


def move_camera_to_new_room(room_coords: Tuple[int, int]) -> None:
    game.camera_target_x, game.camera_target_y = get_pos_from_room_coords(room_coords)
    game.camera_move_timer = 0


def get_current_room() -> Tuple[int, int]:
    return get_room_from_pos((game.game.camera_target_x, game.game.camera_target_y))


def get_obj_at_pos(x, y):
    for obj in game.game.objects:
        if obj.get_cell() == (x, y):
            return obj
    return None
def is_cell_available(x, y):
    return get_obj_at_pos(x, y) is None

def get_dist_to_player(x, y):
    player = game.game.player_obj
    return abs(player.pos_x - x) + abs(player.pos_y - y)
