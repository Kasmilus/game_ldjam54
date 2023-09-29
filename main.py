import math
from typing import List, Tuple
from enum import Enum
from copy import deepcopy

import pyxel

import constants
import utils
import interp
from controls import Controls
import resources
from game_object import Obj, ObjType
import room
import game

# pyxel run main.py
# pyxel edit
# pyxel package . main.py
# pyxel app2html Pyxel.pyxapp
# pyxel app2exe Pyxel.pyxapp


def init():
    pyxel.init(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, title="LD Game", fps=constants.FPS, display_scale=3)
    pyxel.load("assets/my_resource.pyxres", image=True, tilemap=True, sound=True, music=True)
    pyxel.mouse(False)

    game.init_game()

    # Load level from tilemap
    # Note tilemaps are of size 8x8, our game works on 16x16 so we need to do some work to get correct references
    tilemap = pyxel.tilemap(0)
    for x in range(0, 64):
        for y in range(0, 64):
            tile = tilemap.pget(x*2,y*2)
            tile = int(tile[0]/2), int(tile[1]/2)
            if tile != (0, 0):
                for obj_key in resources.ALL_OBJECTS.keys():
                    if resources.ALL_OBJECTS[obj_key]['sprite'] == tile:
                        game.game.objects.append(Obj(pos=room.get_pos_for_room(cell_pos=(x, y)), **resources.ALL_OBJECTS[obj_key]))

    # Start with player to make sure it's updated before anything else
    #player_obj = Obj(pos=get_pos_for_room(cell_pos=(5, 5)), **resources.ALL_OBJECTS['PLAYER'])
    #game.game.all_objects.append(player_obj)
    #game.game.player_obj = player_obj

    resources.play_music(resources.MUSIC_A)

    global game_checkpoint
    game_checkpoint = deepcopy(game.game)


def update():
    global game
    global game_checkpoint

    if game.game.stop_frames > 0:
        return

    if Controls.right():
        game.game.camera_x += 1

    if Controls.mouse():
        print(f"x: {pyxel.mouse_x}, y: {pyxel.mouse_y}")

    #
    # Update camera
    #
    if game.game.cam_shake_timer > 0.0:
        game.game.cam_shake_timer -= constants.FRAME_TIME
        str = max(1, int(game.game.cam_shake_timer*10))
        pyxel.camera(game.game.camera_x+pyxel.rndi(-str, str), game.game.camera_y+pyxel.rndi(-str, str))
    else:
        pyxel.camera(game.game.camera_x, game.game.camera_y)

    if game.game.game_state == game.GameState.GameOver:
        pass
    else:
        #
        # Game Logic updates
        #
        destroy_list = []
        for obj_idx, obj in enumerate(game.game.objects):
            if obj.obj_type == ObjType.Player:
                pass

        #
        # Frame state reset
        #
        for obj in destroy_list:
            game.game.objects.remove(obj)


def draw():
    if game.game.stop_frames > 0:
        game.game.stop_frames -= 1
        return

    pyxel.cls(resources.COLOR_BACKGROUND)
    if game.game.game_state == game.GameState.GameOver:
        pyxel.text(game.game.camera_x, game.game.camera_y, "RETRY", resources.COLOR_TEXT)
    elif game.game.game_state == game.GameState.Game:
        #
        # Sort draw list
        #
        draw_list = []
        for obj in game.game.objects:
            draw_list.append(obj)
        draw_list.sort(key=lambda x: x.draw_priority)

        #
        # Render
        #
        for obj in draw_list:
            if obj.obj_type == ObjType.Text:
                pyxel.text(obj.pos_x, obj.pos_y, obj.text, resources.COLOR_TEXT)
            else:
                resources.blt_sprite(obj.get_render_sprite(), obj.pos_x, obj.pos_y)

            if constants.DEBUG_DRAW:
                if obj.collides:
                    bbox = obj.get_bbox_world_space()
                    pyxel.rectb(bbox[0], bbox[1], bbox[2]-bbox[0], bbox[3]-bbox[1], resources.COLOR_BACKGROUND)

        # Draw UI
        pos_x = game.game.camera_x
        pos_y = game.game.camera_y+constants.ROOM_SIZE_Y
        resources.blt_ui_sprite(resources.SPRITE_A, (1, 1), pos_x, pos_y)


init()
pyxel.run(update, draw)
