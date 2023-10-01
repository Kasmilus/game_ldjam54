import math
from typing import Tuple

from constants import *
from game_object import ObjType
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
        if obj.collides == True:
            if obj.get_cell() == (x, y):
                return obj
    return None
def is_cell_available(x, y):
    return get_obj_at_pos(x, y) is None

def get_dist_to_player(x, y):
    player = game.game.player_obj
    return abs(player.pos_x - x) + abs(player.pos_y - y)


def floodfill(start_pos: Tuple[int, int]):
    open_list = [start_pos]

    for pos in open_list:
        if 0 > pos[0] > len(game.game.path):
            continue
        if 0 > pos[1] > len(game.game.path[0]):
            continue
        val = game.game.path[pos[0]][pos[1]]
        if val is None:
            val = 0
            game.game.path[pos[0]][pos[1]] = val
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                if game.game.path[pos[0]+x][pos[1]+y] is None:
                    if is_cell_available(pos[0]+x, pos[1]+y):
                        game.game.path[pos[0] + x][pos[1] + y] = val + 1
                        open_list.append((pos[0]+x, pos[1]+y))

def is_path_acceptable(from_pos, to_pos) -> bool:
    if 0 > to_pos[0] > len(game.game.path):
        return False
    if 0 > to_pos[1] > len(game.game.path[0]):
        return False
    val_from = game.game.path[from_pos[0]][from_pos[1]]
    val_to = game.game.path[to_pos[0]][to_pos[1]]
    if val_from is None:
        val_from = 999
    if val_to is None:
        return False
    return val_to < val_from
