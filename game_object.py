from typing import List, Tuple, TypedDict, Optional
from enum import Enum

import pyxel

import resources
from constants import *
import utils


class ObjType(Enum):
    Undefined = 0
    Text = 1
    Player = 2
    Wall = 3
    Enemy = 4
    Spawn = 5
    Bullet = 6
    Target = 7
    Background = 8
    EnemyBig = 9
    EnemyDead = 10
    Shotgun = 11
    Speed = 12
    Health = 13


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
        self.velocity = (0, 0)
        self.destroy = False
        self.has_shotgun = False
        self.last_move_dir = 1

        self.move_start_pos = (0, 0)
        self.target_pos = (0, 0)
        self.move_timer = 0

        self.hit_frames = 0

        if bounding_box is None:
            self.bounding_box = (0, 0, GRID_CELL_SIZE, GRID_CELL_SIZE)
        else:
            self.bounding_box = bounding_box
        self.draw_priority = 0  # The higher, the later it will be drawn (on top of others)
        self.anim_speed = 18

        # Player specific
        if obj_type == ObjType.Player:
            self.bounding_box = (0, 0, GRID_CELL_SIZE, GRID_CELL_SIZE)
            self.draw_priority = 3
            self.start_health = 1
            self.health = self.start_health
            self.max_ammo = 3
            self.ammo = self.max_ammo
            self.sprite = resources.SPRITE_PLAYER_IDLE
            self.anim_speed = 65
            self.max_movement = 2
            self.movement = self.max_movement
            self.max_shots = 2
            self.shots = self.max_shots
        if obj_type == ObjType.Enemy:
            self.bounding_box = (2, 2, GRID_CELL_SIZE - 2, GRID_CELL_SIZE - 2)
            self.draw_priority = 3
            self.start_health = 1
            self.health = self.start_health
            self.sprite = resources.SPRITE_ENEMY_IDLE
            self.anim_speed = 8
        if obj_type == ObjType.EnemyBig:
            self.bounding_box = (1, 1, GRID_CELL_SIZE - 1, GRID_CELL_SIZE - 1)
            self.draw_priority = 3
            self.start_health = pyxel.rndi(2, 3)
            self.health = self.start_health
            self.sprite = resources.SPRITE_ENEMY_BIG_IDLE
            self.anim_speed = 8

        if obj_type in [ObjType.Shotgun, ObjType.Speed, ObjType.Health]:
            self.draw_priority = 3
            self.collides = False

        if obj_type == ObjType.Bullet:
            self.bounding_box = (6, 6, GRID_CELL_SIZE-6, GRID_CELL_SIZE-6)
            self.draw_priority = 4

        if obj_type == ObjType.Text:
            self.draw_priority = 2  # Above world, below characters
            self.collides = False
            self.name = "Text"

        if obj_type == ObjType.Background:
            self.draw_priority = 1  # Above world, below characters
            self.collides = False
            self.name = "Bg"

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
            n = pyxel.noise(self.pos_x/10, self.pos_y/10)
            render_sprite = render_sprite[int((pyxel.frame_count - self.last_input_frame + 10*n) / self.anim_speed) % len(render_sprite)]
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

ALL_OBJECTS = {
    "BG": {'name': 'Bg', "sprite": resources.SPRITE_BG, "obj_type": ObjType.Background},
    "BGB": {'name': 'Bg', "sprite": resources.SPRITE_BGB, "obj_type": ObjType.Background},
    "BGC": {'name': 'Bg', "sprite": resources.SPRITE_BGC, "obj_type": ObjType.Background},
    "DARK_BG": {'name': 'Dark bg', "sprite": resources.SPRITE_DARK_BG, "obj_type": ObjType.Background},

    "PLAYER": {'name': 'Player', "sprite": resources.SPRITE_PLAYER, "obj_type": ObjType.Player},

    "SHOTGUN": {'name': 'Bonus gun', "sprite": resources.SPRITE_SHOTGUN, "obj_type": ObjType.Shotgun},
    "HEALTH": {'name': 'Bonus hp', "sprite": resources.SPRITE_HEALTH, "obj_type": ObjType.Health},
    "SPEED": {'name': 'Bonus speed', "sprite": resources.SPRITE_SPEED, "obj_type": ObjType.Speed},

    "WALL_A": {'name': 'Wall', "sprite": resources.SPRITE_WALL_A, "obj_type": ObjType.Wall},
    "WALL_B": {'name': 'Wall', "sprite": resources.SPRITE_WALL_B, "obj_type": ObjType.Wall},
    "WALL_C": {'name': 'Wall', "sprite": resources.SPRITE_WALL_C, "obj_type": ObjType.Wall},
    "WALL_D": {'name': 'Wall', "sprite": resources.SPRITE_WALL_D, "obj_type": ObjType.Wall},
    "WALL_E": {'name': 'Wall', "sprite": resources.SPRITE_WALL_E, "obj_type": ObjType.Wall},
    "WALL_F": {'name': 'Wall', "sprite": resources.SPRITE_WALL_F, "obj_type": ObjType.Wall},
    "WALL_G": {'name': 'Wall', "sprite": resources.SPRITE_WALL_G, "obj_type": ObjType.Wall},
    "WALL_H": {'name': 'Wall', "sprite": resources.SPRITE_WALL_H, "obj_type": ObjType.Wall},
    "WALL_AA": {'name': 'Wall', "sprite": resources.SPRITE_WALL_AA, "obj_type": ObjType.Wall},
    "WALL_BB": {'name': 'Wall', "sprite": resources.SPRITE_WALL_BB, "obj_type": ObjType.Wall},
    "WALL_CC": {'name': 'Wall', "sprite": resources.SPRITE_WALL_CC, "obj_type": ObjType.Wall},
    "WALL_DD": {'name': 'Wall', "sprite": resources.SPRITE_WALL_DD, "obj_type": ObjType.Wall},
    "WALL_EE": {'name': 'Wall', "sprite": resources.SPRITE_WALL_EE, "obj_type": ObjType.Wall},
    "WALL_XX": {'name': 'Wall', "sprite": resources.SPRITE_WALL_XX, "obj_type": ObjType.Wall},
    "WALL_YY": {'name': 'Wall', "sprite": resources.SPRITE_WALL_YY, "obj_type": ObjType.Wall},

    "ENEMY": {'name': 'Enemy', "sprite": resources.SPRITE_Enemy, "obj_type": ObjType.Enemy},
    "ENEMY_BIG": {'name': 'Enemy Big', "sprite": resources.SPRITE_Enemy_BIG, "obj_type": ObjType.EnemyBig},

    "SPAWN": {'name': 'Spawn', "sprite": resources.SPRITE_SPAWN, "obj_type": ObjType.Spawn},
    "TARGET": {'name': 'Target', "sprite": resources.SPRITE_TARGET, "obj_type": ObjType.Target},

    "BULLET": {'name': 'Bullet', "sprite": resources.SPRITE_BULLET, "obj_type": ObjType.Bullet},
}
