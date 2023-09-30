import math
from typing import List, Tuple
from enum import Enum
from copy import deepcopy

import pyxel

import constants
import game_object
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

    # Add player
    obj = Obj(pos=(5*constants.GRID_CELL_SIZE, 5*constants.GRID_CELL_SIZE), **game_object.ALL_OBJECTS['PLAYER'])
    game.game.objects.append(obj)
    game.game.player_obj = obj

    # Load level from tilemap
    # Note tilemaps are of size 8x8, our game works on 16x16 so we need to do some work to get correct references
    tilemap = pyxel.tilemap(0)
    for x in range(0, 64):
        for y in range(0, 64):
            tile = tilemap.pget(x*2,y*2)
            tile = int(tile[0]/2), int(tile[1]/2)
            for obj_key in game_object.ALL_OBJECTS.keys():
                if game_object.ALL_OBJECTS[obj_key]['sprite'] == tile:
                    obj = Obj(pos=room.get_pos_for_room(cell_pos=(x, y)), **game_object.ALL_OBJECTS[obj_key])
                    game.game.objects.append(obj)

    game.game.start_new_wave(started_with_timer=True)

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
        if game.game.action == game.Action.Roll and len(game.game.action_queue ) > 0:
            game.game.action = game.game.action_queue.pop()
        if game.game.action not in [game.Action.Break, game.Action.NewWave] and game.Action.NewWave not in game.game.action_queue:
            game.game.wave_timer -= constants.FRAME_TIME
            if game.game.wave_timer <= 0.0:
                game.game.start_new_wave(started_with_timer=True)

        destroy_list = []
        for obj_idx, obj in enumerate(game.game.objects):
            if obj.obj_type == ObjType.Bullet:
                obj.pos_x += obj.velocity[0]
                obj.pos_y += obj.velocity[1]
                for obj_2 in game.game.objects:
                    if obj is not obj_2 and obj_2.obj_type is not ObjType.Player:
                        if game_object.collision_obj(obj, obj_2):
                            destroy_list.append(obj)
                            if obj_2.obj_type == ObjType.Enemy:
                                obj_2.health -= 1
                                if obj_2.health <= 0:
                                    destroy_list.append(obj_2)
            elif obj.obj_type == ObjType.Spawn:
                if game.game.action == game.Action.NewWave:
                    if Controls.mouse_in(obj.pos_x, obj.pos_y, constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE):
                        obj = Obj(pos=obj.get_pos(), **game_object.ALL_OBJECTS['ENEMY'])
                        game.game.objects.append(obj)
                        game.game.action = game.Action.MoveEnemy
                        game.game.selected_enemy = obj
                        game.game.new_wave_enemies -= 1
                        if game.game.new_wave_enemies > 0:
                            game.game.add_action(game.Action.NewWave)

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

                if obj.obj_type == ObjType.Enemy:
                    if Controls.mouse_hovering(obj.pos_x, obj.pos_y, constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE):
                        draw_health(obj)
                elif obj.obj_type == ObjType.Player:
                        draw_health(obj)

            if constants.DEBUG_DRAW:
                if obj.collides:
                    bbox = obj.get_bbox_world_space()
                    pyxel.rectb(bbox[0], bbox[1], bbox[2]-bbox[0], bbox[3]-bbox[1], resources.COLOR_BACKGROUND)

        # Draw UI
        # Debug state
        pos_x = game.game.camera_x
        pos_y = game.game.camera_y
        pyxel.rect(pos_x, pos_y, *utils.get_size_for_text(f"{game.game.action_queue}"), resources.COLOR_TEXT)
        pyxel.text(pos_x, pos_y, f"{game.game.action_queue}", resources.COLOR_TEXT_INACTIVE)
        pos_y += 10
        pyxel.rect(pos_x, pos_y, *utils.get_size_for_text(f"Action: {game.game.action.name}"), resources.COLOR_TEXT)
        pyxel.text(pos_x, pos_y, f"Action: {game.game.action.name}", resources.COLOR_TEXT_INACTIVE)

        pos_x = game.game.camera_x
        pos_y = game.game.camera_y+constants.ROOM_SIZE_PIXELS_Y-constants.GRID_CELL_SIZE
        resources.blt_ui_sprite(resources.SPRITE_UI_BOX, (constants.SCREEN_WIDTH, constants.UI_SIZE+constants.GRID_CELL_SIZE), pos_x, pos_y)

        #
        # Timer
        #
        pos_x += constants.SCREEN_WIDTH/2 + 5
        pos_y += constants.HALF_GRID_CELL + 2
        resources.bold_text(pos_x, pos_y, f"{int(game.game.wave_timer)}")
        pos_x = game.game.camera_x
        pos_y = game.game.camera_y+constants.ROOM_SIZE_PIXELS_Y

        #
        # Actions
        #
        pos_x += constants.GRID_CELL_SIZE - 2
        pos_y += constants.HALF_GRID_CELL + 5
        def draw_action_button(die, x, y):
        #for die in [game.Dice.Run, game.Dice.Shoot, game.Dice.Reload]:
            if game.game.can_do_die_action(die):
                pyxel.text(x, y, die.name, resources.COLOR_TEXT)
            else:
                pyxel.text(x, y, die.name, resources.COLOR_TEXT_INACTIVE)
            if Controls.mouse_in(x-5, y-4, 30, 14):
                game.game.take_dice(die)
        draw_action_button(game.Dice.Run, pos_x, pos_y)
        pos_y += constants.GRID_CELL_SIZE
        draw_action_button(game.Dice.Shoot, pos_x, pos_y)
        pos_x += constants.GRID_CELL_SIZE*2
        pos_y -= constants.GRID_CELL_SIZE
        draw_action_button(game.Dice.Reload, pos_x, pos_y)
        pos_y += constants.GRID_CELL_SIZE
        #
        # Unstuck
        #
        unstuck_text = "STUCK"
        col = resources.COLOR_TEXT
        if not game.game.is_any_die_stuck():
            col = resources.COLOR_TEXT_INACTIVE
        pyxel.text(pos_x, pos_y, unstuck_text, col)
        if Controls.mouse_in(pos_x-5, pos_y-4, 30, 14):
            if game.game.is_any_die_stuck():
                game.game.start_new_wave()

        #
        # Ammo
        #
        pos_x = game.game.camera_x + constants.GRID_CELL_SIZE + 2
        pos_y = game.game.camera_y+constants.ROOM_SIZE_PIXELS_Y - 6
        for i in range(game.game.player_obj.max_ammo):
            if i < game.game.player_obj.ammo:
                spr = resources.SPRITE_UI_AMMO_FULL
            else:
                spr = resources.SPRITE_UI_AMMO_EMPTY
            resources.blt_ui_sprite(spr, (8, 8), pos_x, pos_y)
            pos_x += constants.HALF_GRID_CELL + 2

        #
        # Dice
        #
        pos_x += constants.GRID_CELL_SIZE * 2 - 2
        pos_y = game.game.camera_y+constants.ROOM_SIZE_PIXELS_Y + constants.GRID_CELL_SIZE*2 - 3
        for i in range(len(game.game.dice)):
            img = game.game.get_dice_image(i)
            col = resources.COLOR_TEXT
            if game.game.can_roll(i) == False:
                col = resources.COLOR_TEXT_INACTIVE
            pyxel.text(pos_x, pos_y, img, col)

            if Controls.mouse_in(pos_x-8, pos_y-22, 29, 31):
                    game.game.roll_die(i)

            pos_x += constants.GRID_CELL_SIZE*2


        if game.game.action == game.Action.Roll:
            pass
        elif game.game.action == game.Action.MovePlayer:
            player_pos = game.game.player_obj.pos_x, game.game.player_obj.pos_y
            player_cell = game.game.player_obj.get_cell()
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x == 0 and y == 0:
                        continue
                    if room.is_cell_available(player_cell[0]+x, player_cell[1]+y):
                        draw_pos = player_pos[0] + x*constants.GRID_CELL_SIZE, player_pos[1] + y*constants.GRID_CELL_SIZE
                        resources.blt_ui_sprite(resources.SPRITE_UI_HIGHLIGHT, (constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE), draw_pos[0], draw_pos[1])
                        if Controls.mouse_in(draw_pos[0], draw_pos[1], constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE):
                            game.game.player_obj.pos_x = draw_pos[0]
                            game.game.player_obj.pos_y = draw_pos[1]
                            game.game.set_action(game.Action.Roll)
                            break
        elif game.game.action == game.Action.MoveEnemy:
            if game.game.selected_enemy is None:
                for obj in game.game.objects:
                    if obj.obj_type == game_object.ObjType.Enemy:
                        resources.blt_ui_sprite(resources.SPRITE_UI_HIGHLIGHT, (constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE), obj.pos_x, obj.pos_y)
                        if Controls.mouse_in(obj.pos_x, obj.pos_y, constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE):
                            game.game.selected_enemy = obj
                            break
            else:
                obj = game.game.selected_enemy
                enemy_pos = obj.pos_x, obj.pos_y
                enemy_cell = obj.get_cell()
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if  x == 0 and y == 0:
                            continue
                        obj_at_pos = room.get_obj_at_pos(enemy_cell[0] + x, enemy_cell[1] + y)
                        if obj_at_pos is None or obj_at_pos.obj_type in [ObjType.Enemy, ObjType.Player, ObjType.Target]:
                            #if room.get_dist_to_player(obj.pos_x+x, obj.pos_y+y) > dist_to_player:
                            #    continue  # TODO: This will not be correct, we need to define paths manually?
                            draw_pos = enemy_pos[0] + x*constants.GRID_CELL_SIZE, enemy_pos[1] + y*constants.GRID_CELL_SIZE
                            resources.blt_ui_sprite(resources.SPRITE_UI_HIGHLIGHT, (constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE), draw_pos[0], draw_pos[1])
                            if Controls.mouse_in(draw_pos[0], draw_pos[1], constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE):
                                game.game.selected_enemy = None
                                action = game.Action.Roll
                                if obj_at_pos is not None and obj_at_pos.obj_type in [ObjType.Player, ObjType.Target]:
                                    game.game.player_obj.health -= 1
                                    if game.game.player_obj.health <= 0:
                                        game.game.game_over()
                                else:
                                    if obj_at_pos is not None and obj_at_pos.obj_type == ObjType.Enemy:
                                        action = game.Action.MoveEnemy
                                        game.game.selected_enemy = obj_at_pos
                                    obj.pos_x = draw_pos[0]
                                    obj.pos_y = draw_pos[1]

                                if action == game.Action.MoveEnemy:
                                    game.game.action_queue.insert(0, action)
                                else:
                                    game.game.action_queue.append(action)
                                break
        elif game.game.action == game.Action.Shoot:
            if Controls.mouse():
                player = game.game.player_obj
                if player.ammo > 0:
                    player.ammo -= 1
                    dir = (pyxel.mouse_x - player.pos_x, pyxel.mouse_y - player.pos_y)
                    dir = utils.get_vector_normalised(dir)
                    obj = Obj(pos=(player.pos_x+dir[0], player.pos_y+dir[1]), **game_object.ALL_OBJECTS['BULLET'])
                    obj.velocity = dir*20
                    game.game.objects.append(obj)

        elif game.game.action == game.Action.NewWave:
            pass
        elif game.game.action == game.Action.Break:
            pos_x = constants.SCREEN_WIDTH - 48
            pos_y = constants.SCREEN_HEIGHT - constants.GRID_CELL_SIZE - 2
            resources.bold_text(pos_x, pos_y, "NEXT WAVE")
            if Controls.mouse_in(pos_x-8, pos_y-5, 48, 14):
                game.game.unpause_game()
        if game.game.action != game.Action.Break:
            pos_x = constants.SCREEN_WIDTH - 48
            pos_y = constants.SCREEN_HEIGHT - constants.GRID_CELL_SIZE - 2
            resources.bold_text(pos_x, pos_y, f"Wave: {game.game.current_wave}")

        # Mouse cursor
        resources.blt_ui_sprite(resources.SPRITE_UI_CURSOR, (4, 4), pyxel.mouse_x, pyxel.mouse_y)


def draw_health(obj):
    if obj.start_health == 1:
        adv_x = 4
    elif obj.start_health == 2:
        adv_x = 0
    else:
        adv_x = -5
    for i in range(obj.start_health):
        spr = resources.SPRITE_UI_HEART_FULL
        if obj.health <= i:
            spr = resources.SPRITE_UI_HEART_EMPTY
        resources.blt_ui_sprite(spr, (8, 8), obj.pos_x + 9 * i + adv_x, obj.pos_y - constants.HALF_GRID_CELL)


init()
pyxel.run(update, draw)
