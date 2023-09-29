from typing import List, Tuple, TypedDict, Optional
from enum import Enum

import pyxel

from constants import *
import utils


class ObjType(Enum):
    Undefined = 0
    Text = 1
    Player = 2
    World = 3


class Obj:
    def __init__(self, obj_type: ObjType, sprite: Tuple[int, int], pos: Tuple[int, int], name: str = "Unknown", collides: bool = True, bounding_box: Tuple[int, int, int, int] = None, text: str = None):
        self.name = name
        self.obj_type = obj_type
        self.sprite = sprite
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.collides = collides
        self.last_input_frame = 0  # for anim
        self.text = text

        if bounding_box is None:
            self.bounding_box = (0, 0, GRID_CELL_SIZE, GRID_CELL_SIZE)
        else:
            self.bounding_box = bounding_box
        self.draw_priority = 0  # The higher, the later it will be drawn (on top of others)
        self.anim_speed = 18

        # Player specific
        if obj_type == ObjType.Player:
            self.bounding_box = (5, 7, GRID_CELL_SIZE-5, GRID_CELL_SIZE)
            self.draw_priority = 3

        if obj_type == ObjType.Text:
            self.draw_priority = 2  # Above world, below characters
            self.collides = False
            self.name = "Text"

    def __repr__(self):
        pos = int(self.pos_x / GRID_CELL_SIZE), int(self.pos_y / GRID_CELL_SIZE)
        return f"[OBJ] {self.name} ({pos[0]}, {pos[1]})"

    def get_pos(self) -> Tuple[int, int]:
        return self.pos_x, self.pos_y

    def get_pos_mid(self) -> Tuple[int, int]:
        return self.pos_x + HALF_GRID_CELL, self.pos_y + HALF_GRID_CELL

    def get_cell(self) -> Tuple[int, int]:
        mid_pos = self.get_pos()
        return int(mid_pos[0]/GRID_CELL_SIZE), int(mid_pos[1]/GRID_CELL_SIZE)

    def get_bbox_world_space(self) -> Tuple[int, int, int, int]:
        return self.pos_x + self.bounding_box[0], self.pos_y + self.bounding_box[1], self.pos_x + self.bounding_box[2], self.pos_y + self.bounding_box[3]

    def get_render_sprite(self) -> Tuple[int, int]:
        render_sprite = self.sprite
        if type(render_sprite) is list:
            render_sprite = render_sprite[int((pyxel.frame_count - self.last_input_frame) / self.anim_speed) % len(render_sprite)]
        return render_sprite


def collision_bb(pos_a: Tuple[int, int], bb_a: Tuple[int, int, int, int], pos_b: Tuple[int, int], bb_b: Tuple[int, int, int, int]) -> bool:
    collides = pos_a[0] + bb_a[0] < pos_b[0] + bb_b[2] and \
               pos_a[0] + bb_a[2] > pos_b[0] + bb_b[0] and \
               pos_a[1] + bb_a[1] < pos_b[1] + bb_b[3] and \
               pos_a[1] + bb_a[3] > pos_b[1] + bb_b[1]
    return collides

def objs_can_collide(obj_a: Obj, obj_b: Obj) -> bool:
    if obj_a is obj_b:
        return False
    if obj_a.collides is False:
        return False
    if obj_b.collides is False:
        return False

    return True

def collision_obj(obj_a: Obj, obj_b: Obj) -> bool:
    if not objs_can_collide(obj_a, obj_b):
        return False
    return collision_bb(obj_a.get_pos(), obj_a.bounding_box, obj_b.get_pos(), obj_b.bounding_box)


def _line_intersection_distance(x1, y1, x2, y2, x3, y3, x4, y4) -> Tuple[float, float]:
    denominator = ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))

    if denominator == 0:
        return -1, -1

    u_a = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator
    u_b = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator
    return u_a, u_b

def get_line_intersection_point(line_a_start: Tuple[float, float],line_a_end: Tuple[float, float], line_b_start: Tuple[float, float],line_b_end: Tuple[float, float],) -> Optional[Tuple[float, float]]:
    u_a, u_b = _line_intersection_distance(line_a_start[0], line_a_start[1], line_a_end[0], line_a_end[1],
                                           line_b_start[0], line_b_start[1], line_b_end[0], line_b_end[1])
    if 0 <= u_a <= 1 and 0 <= u_b <= 1:
        intersection_x = line_a_start[0] + (u_a * (line_a_end[0]-line_a_start[0]))
        intersection_y = line_a_start[1] + (u_a * (line_a_end[1]-line_a_start[1]))
        return intersection_x, intersection_y

    return None

def get_line_bb_intersection_point(line_start: Tuple[float, float],line_end: Tuple[float, float], bb: Tuple[int, int, int, int],) -> Optional[Tuple[float, float]]:
    a = get_line_intersection_point(line_start, line_end, (bb[0], bb[1]), (bb[2], bb[1]))
    if a is not None:
        return a
    b = get_line_intersection_point(line_start, line_end, (bb[0], bb[1]), (bb[0], bb[3]))
    if b is not None:
        return b
    c = get_line_intersection_point(line_start, line_end, (bb[0], bb[3]), (bb[2], bb[3]))
    if c is not None:
        return c
    d = get_line_intersection_point(line_start, line_end, (bb[2], bb[1]), (bb[2], bb[3]))
    if d is not None:
        return d

    return None

def get_dist_obj(obj_a: Obj, obj_b: Obj) -> float:
    # TODO: Use bbox center?
    return utils.get_vector_len((obj_b.pos_x - obj_a.pos_x, obj_b.pos_y - obj_a.pos_y))

def check_obj_move_collision(obj_a: Obj, obj_b: Obj, move_dir: Tuple[int, int]) -> Tuple[int, int]:
    """ Note: you probably want to pass in normalised move_dir!"""
    if not objs_can_collide(obj_a, obj_b):
        return move_dir
    move_dir = [move_dir[0], move_dir[1]]
    if collision_bb((obj_a.pos_x + move_dir[0], obj_a.pos_y), obj_a.bounding_box, obj_b.get_pos(), obj_b.bounding_box):
        move_dir[0] = 0
    if collision_bb((obj_a.pos_x, obj_a.pos_y + move_dir[1]), obj_a.bounding_box, obj_b.get_pos(), obj_b.bounding_box):
        move_dir[1] = 0

    return move_dir[0], move_dir[1]

