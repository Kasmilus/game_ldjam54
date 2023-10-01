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
    obj = Obj(pos=(6*constants.GRID_CELL_SIZE, 2*constants.GRID_CELL_SIZE), **game_object.ALL_OBJECTS['PLAYER'])
    game.game.objects.append(obj)
    game.game.player_obj = obj
    obj = Obj(pos=(8*constants.GRID_CELL_SIZE, 5*constants.GRID_CELL_SIZE), **game_object.ALL_OBJECTS['SHOTGUN'])
    game.game.objects.append(obj)
    game.game.objects.append(Obj(pos=(8*constants.GRID_CELL_SIZE, 5*constants.GRID_CELL_SIZE), **game_object.ALL_OBJECTS['BG']))
    obj = Obj(pos=(1*constants.GRID_CELL_SIZE, 6*constants.GRID_CELL_SIZE), **game_object.ALL_OBJECTS['HEALTH'])
    game.game.objects.append(obj)
    obj = Obj(pos=(12*constants.GRID_CELL_SIZE, 2*constants.GRID_CELL_SIZE), **game_object.ALL_OBJECTS['SPEED'])
    game.game.objects.append(obj)

    # Load level from tilemap
    # Note tilemaps are of size 8x8, our game works on 16x16 so we need to do some work to get correct references
    tilemap = pyxel.tilemap(0)
    obj_target = None
    for x in range(0, 64):
        for y in range(0, 64):
            tile = tilemap.pget(x*2,y*2)
            tile = int(tile[0]/2), int(tile[1]/2)
            for obj_key in game_object.ALL_OBJECTS.keys():
                if game_object.ALL_OBJECTS[obj_key]['sprite'] == tile:
                    obj = Obj(pos=room.get_pos_for_room(cell_pos=(x, y)), **game_object.ALL_OBJECTS[obj_key])
                    game.game.objects.append(obj)
                    if obj.obj_type == ObjType.Target:
                        obj_target = obj

    assert obj_target is not None
    room.floodfill(obj_target.get_cell())

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
        game.game.time_since_game_over += constants.FRAME_TIME
        if game.game.time_since_game_over > 1.5 and Controls.mouse():
            game.game = deepcopy(game_checkpoint)
            return
    else:
        #
        # Game Logic updates
        #
        if Controls.mouse():
            resources.play_sound(resources.SOUND_CLICK)

        if game.game.game_state == game.GameState.Tutorial:
            game.game.time_since_tutorial_step += constants.FRAME_TIME
            if game.game.time_since_tutorial_step > 0.6:
                if Controls.mouse():
                    game.game.tutorial_step += 1
                    game.game.time_since_tutorial_step = 0
                    if game.game.tutorial_step >= 9:
                        game.game.game_state = game.GameState.Game
                        game_checkpoint = deepcopy(game.game)

        if game.game.action == game.Action.Roll and len(game.game.action_queue ) > 0:
            game.game.action = game.game.action_queue.pop()
        if game.game.action not in [game.Action.Break, game.Action.NewWave] and game.Action.Break not in game.game.action_queue and game.Action.NewWave not in game.game.action_queue:
            game.game.wave_timer -= constants.FRAME_TIME
            game.game.total_time += constants.FRAME_TIME
            if game.game.wave_timer <= 0.0:
                game.game.start_new_wave(started_with_timer=True)

        for i in range(3):
            if game.game.dice_roll_timer[i] > 0:
                game.game.dice_roll_timer[i] -= constants.FRAME_TIME

        if game.game.action == game.Action.Shoot:
            player = game.game.player_obj
            if Controls.mouse():
                if player.ammo > 0:
                    player.ammo -= 1
                    dir = (game.game.shoot_target[0] - player.pos_x - constants.HALF_GRID_CELL, game.game.shoot_target[1] - player.pos_y - constants.HALF_GRID_CELL)
                    dir_init = utils.get_vector_normalised(dir)
                    angle = pyxel.atan2(dir_init[1], dir_init[0])
                    angle += utils.deg_to_rad((pyxel.rndf(0.0, 1.0) - 0.5) * 600)  # TODO: Thats not right?
                    dir = dir_init[0] + pyxel.cos(angle), dir_init[1] + pyxel.sin(angle)
                    obj = Obj(pos=(player.pos_x+dir[0], player.pos_y+dir[1]), **game_object.ALL_OBJECTS['BULLET'])
                    obj.velocity = dir*constants.BULLET_SPEED
                    game.game.objects.append(obj)
                    if player.has_shotgun:
                        obj = Obj(pos=(player.pos_x + dir[0], player.pos_y + dir[1]), **game_object.ALL_OBJECTS['BULLET'])
                        angle = pyxel.atan2(dir_init[1], dir_init[0])
                        angle += utils.deg_to_rad((pyxel.rndf(0.0, 1.0) - 1.5) * 600)  # TODO: Thats not right?
                        dir = dir_init[0] + pyxel.cos(angle), dir_init[1] + pyxel.sin(angle)
                        obj.velocity = dir * constants.BULLET_SPEED
                        game.game.objects.append(obj)
                        obj = Obj(pos=(player.pos_x + dir[0], player.pos_y + dir[1]), **game_object.ALL_OBJECTS['BULLET'])
                        angle = pyxel.atan2(dir_init[1], dir_init[0])
                        angle += utils.deg_to_rad((pyxel.rndf(0.0, 1.0) + 0.5) * 600)  # TODO: Thats not right?
                        dir = dir_init[0] + pyxel.cos(angle), dir_init[1] + pyxel.sin(angle)
                        obj.velocity = dir * constants.BULLET_SPEED
                        game.game.objects.append(obj)

                    resources.play_sound(resources.SOUND_SHOT)
                    game.game.player_obj.shots -= 1
                    if game.game.player_obj.shots <= 0:
                        game.game.action = game.Action.Roll
                        game.game.player_obj.shots = game.game.player_obj.max_shots
                else:
                    resources.play_sound(resources.SOUND_CLICK)
                    game.game.action = game.Action.Roll
                    game.game.do_slide_text("No Ammo!")
            else:
                game.game.shoot_time += constants.FRAME_TIME
                if game.game.shoot_time >= 1.0:
                    game.game.shoot_time -= 2.0
                val = abs(game.game.shoot_time)
                game.game.shoot_target = player.get_pos_mid()
                dir = (pyxel.mouse_x - game.game.shoot_target[0], pyxel.mouse_y - game.game.shoot_target[1])
                dir = utils.get_vector_normalised(dir)
                angle = pyxel.atan2(dir[1], dir[0])
                angle += utils.deg_to_rad((val-0.5)*1600)  # TODO: Thats not right?
                game.game.shoot_target = player.get_pos_mid()
                game.game.shoot_target = (game.game.shoot_target[0] + pyxel.cos(angle)*1.5*constants.GRID_CELL_SIZE, game.game.shoot_target[1] + pyxel.sin(angle)*1.5*constants.GRID_CELL_SIZE)

        destroy_list = []
        for obj_idx, obj in enumerate(game.game.objects):
            if obj.destroy:
                destroy_list.append(obj)

            if obj.obj_type == ObjType.Bullet:
                if obj.velocity == (0, 0):
                    continue
                obj.pos_x += obj.velocity[0]
                obj.pos_y += obj.velocity[1]
                hit_something = False
                for obj_2 in game.game.objects:
                    if obj is not obj_2 and obj_2.obj_type is not ObjType.Player and obj_2.obj_type is not ObjType.Bullet and obj_2.collides:
                        if game_object.collision_obj(obj, obj_2):
                            vel = obj.velocity
                            obj.velocity = (0, 0)
                            obj.draw_priority = 2
                            obj.sprite = resources.SPRITE_BULLET_SHELL
                            obj.collides = False
                            hit_something = True
                            game.game.count_bullets += 1
                            if game.game.count_bullets > 10:
                                for bul in game.game.objects:
                                    if bul.obj_type == ObjType.Bullet:
                                        destroy_list.append(bul)
                                        break

                            if obj_2.obj_type == ObjType.Enemy or obj_2.obj_type == ObjType.EnemyBig:
                                resources.play_sound(resources.SOUND_HIT)
                                obj_2.health -= 1
                                if obj_2.health <= 0:
                                    if obj_2.obj_type == ObjType.Enemy:
                                        obj_2.sprite = resources.SPRITE_ENEMY_DEATH
                                        game.game.stop_frames = 3
                                        game.game.cam_shake_timer = 0.1
                                    elif obj_2.obj_type == ObjType.EnemyBig:
                                        obj_2.sprite = resources.SPRITE_ENEMY_BIG_DEATH
                                        game.game.stop_frames = 5
                                        game.game.cam_shake_timer = 0.15
                                    obj_2.hit_frames = 12
                                    obj_2.target_pos = (obj_2.pos_x + obj.velocity[0]*2, obj_2.pos_y + obj.velocity[1]*2)
                                    obj_2.move_start_pos = obj_2.get_pos()
                                    game.game.enemies_killed += 1
                                    obj_2.obj_type = ObjType.EnemyDead
                                    obj_2.collides = False
                                    resources.play_sound(resources.SOUND_ENEMY_DEATH)
                                    obj.pos_x += vel[0]*2
                                    obj.pos_x += vel[1]*2
                                    game.game.count_enemies_d += 1
                                    if game.game.count_enemies_d > 10:
                                        for bul in game.game.objects:
                                            if bul.obj_type in [ObjType.EnemyDead]:
                                                destroy_list.append(bul)
                                                break
                if hit_something == True:
                    resources.play_sound(resources.SOUND_MISS)
                    game.game.cam_shake_timer = 0.06
            elif obj.obj_type == ObjType.Spawn:
                if game.game.action == game.Action.NewWave:
                    if Controls.mouse_in(obj.pos_x, obj.pos_y, constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE):
                        game.game.cam_shake_timer = 0.03
                        spawn_enemy = 'ENEMY'
                        if game.game.current_wave > 1:
                            if pyxel.rndi(1, 10) < 2:
                                spawn_enemy = 'ENEMY_BIG'
                                game.game.cam_shake_timer = 0.1
                        elif game.game.current_wave > 3:
                            if pyxel.rndi(1, 10) < 3:
                                spawn_enemy = 'ENEMY_BIG'
                                game.game.cam_shake_timer = 0.1
                        elif game.game.current_wave > 4:
                            if pyxel.rndi(1, 10) < 5:
                                spawn_enemy = 'ENEMY_BIG'
                                game.game.cam_shake_timer = 0.1
                        obj = Obj(pos=obj.get_pos(), **game_object.ALL_OBJECTS[spawn_enemy])
                        game.game.objects.append(obj)
                        game.game.action = game.Action.MoveEnemy
                        game.game.selected_enemy = obj
                        game.game.new_wave_enemies -= 1
                        if game.game.new_wave_enemies > 0:
                            game.game.add_action(game.Action.NewWave)
            elif obj.obj_type in [ObjType.Enemy, ObjType.EnemyBig]:
                if obj.target_pos != (0, 0):
                    obj_at_target_pos = room.get_obj_at_pos(int(obj.target_pos[0] / constants.GRID_CELL_SIZE), int(obj.target_pos[1] / constants.GRID_CELL_SIZE))
                    if obj_at_target_pos is None or obj_at_target_pos is obj:
                        obj.move_timer += constants.FRAME_TIME
                        obj.pos_x = interp.interp(obj.move_start_pos[0], obj.target_pos[0], obj.move_timer, constants.MOVE_ANIM_TIME, interp.EasingType.EaseOutCubic)
                        obj.pos_y = interp.interp(obj.move_start_pos[1], obj.target_pos[1], obj.move_timer, constants.MOVE_ANIM_TIME, interp.EasingType.EaseOutCubic)
                        if obj.move_timer >= constants.MOVE_ANIM_TIME or obj.get_pos() == obj.target_pos:
                            obj.pos_x = obj.target_pos[0]
                            obj.pos_y = obj.target_pos[1]
                            obj.target_pos = (0, 0)
                            obj.move_timer = 0
            elif obj.obj_type in [ObjType.EnemyDead]:
                if obj.move_timer < constants.MOVE_ANIM_TIME:
                    obj.move_timer += constants.FRAME_TIME
                    obj.pos_x = interp.interp(obj.move_start_pos[0], obj.target_pos[0], obj.move_timer, constants.MOVE_ANIM_TIME, interp.EasingType.EaseOutCubic)
                    obj.pos_y = interp.interp(obj.move_start_pos[1], obj.target_pos[1], obj.move_timer, constants.MOVE_ANIM_TIME, interp.EasingType.EaseOutCubic)

        #
        # Frame state reset
        #
        for obj in destroy_list:
            if obj in game.game.objects:
                game.game.objects.remove(obj)


def draw():
    if game.game.stop_frames > 0:
        game.game.stop_frames -= 1
        return

    pyxel.cls(resources.COLOR_BACKGROUND)
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
        if obj.hit_frames > 0:
            resources.flip_colors()

        if obj.obj_type == ObjType.Text:
            pyxel.text(obj.pos_x, obj.pos_y, obj.text, resources.COLOR_TEXT)
        else:
            resources.blt_sprite(obj.get_render_sprite(), obj.pos_x, obj.pos_y, invert=obj.last_move_dir<0)

            if obj.obj_type in [ObjType.Enemy, ObjType.EnemyBig]:
                if Controls.mouse_hovering(obj.pos_x, obj.pos_y, constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE):
                    draw_health(obj)
                if obj.target_pos != (0, 0):
                    if not room.is_cell_available(int(obj.target_pos[0]/constants.GRID_CELL_SIZE), int(obj.target_pos[1]/constants.GRID_CELL_SIZE)):
                        pyxel.line(obj.pos_x+8, obj.pos_y+8, obj.target_pos[0]+8, obj.target_pos[1]+8, resources.COLOR_TEXT)
                        pyxel.circ(obj.target_pos[0]+8, obj.target_pos[1]+8, 3, resources.COLOR_TEXT)
            elif obj.obj_type == ObjType.Player:
                    draw_health(obj)

        if constants.DEBUG_DRAW:
            if obj.collides:
                bbox = obj.get_bbox_world_space()
                pyxel.rectb(bbox[0], bbox[1], bbox[2]-bbox[0], bbox[3]-bbox[1], resources.COLOR_BACKGROUND)

        if obj.hit_frames > 0:
            obj.hit_frames -= 1
            resources.reset_color()

    # Draw UI
    # Debug state
    if game.game.game_state == game.GameState.Game:
        pos_x = game.game.camera_x
        pos_y = game.game.camera_y
        pos_x += 4
        pos_y += 4
        rect_size = utils.get_size_for_text(f"Action: {game.game.action.name}")
        rect_size = rect_size[0]+8, rect_size[1]+8
        pyxel.rect(pos_x, pos_y, *rect_size, 4)
        pyxel.rectb(pos_x, pos_y, *rect_size, resources.COLOR_TEXT_INACTIVE)
        pyxel.text(pos_x+4, pos_y+4, f"Action: {game.game.action.name}", resources.COLOR_TEXT_INACTIVE)

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
        if game.game.can_do_die_action(die):
            pyxel.text(x, y, die.name, resources.COLOR_TEXT)
        else:
            pyxel.text(x, y, die.name, resources.COLOR_TEXT_INACTIVE)
        if Controls.mouse_in(x-5, y-4, 30, 14):
            game.game.take_dice(die)

    draw_action_button(game.Dice.Move, pos_x, pos_y)
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
    pos_x = constants.GRID_CELL_SIZE * 6 - 2
    pos_y = game.game.camera_y+constants.ROOM_SIZE_PIXELS_Y + constants.GRID_CELL_SIZE*2 - 3
    for i in range(len(game.game.dice)):
        txt = game.game.get_dice_text(i)
        col = resources.COLOR_TEXT
        if game.game.can_roll(i) == False:
            col = resources.COLOR_TEXT_INACTIVE
        pyxel.text(pos_x, pos_y, txt, col)

        img = game.game.get_dice_image(i)
        pos_x_img = pos_x + 2
        pos_y_img = pos_y - 22
        if img is not None:
            resources.blt_ui_sprite(img,(16,16), pos_x_img, pos_y_img)

        if Controls.mouse_in(pos_x-8, pos_y-22, 29, 31) or Controls.key(i):
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
                        game.game.player_obj.last_move_dir = pyxel.sgn(x)
                        game.game.player_obj.pos_x = draw_pos[0]
                        game.game.player_obj.pos_y = draw_pos[1]
                        game.game.player_obj.movement -= 1
                        if game.game.player_obj.movement <= 0:
                            game.game.set_action(game.Action.Roll)
                            game.game.player_obj.movement = game.game.player_obj.max_movement
                        for obj in game.game.objects:
                            if obj.get_cell() == (player_cell[0] + x, player_cell[1] + y):
                                if obj.obj_type == ObjType.Shotgun:
                                    game.game.do_slide_text("Found Shotgun!")
                                    obj.destroy = True
                                    game.game.player_obj.has_shotgun = True
                                    game.game.player_obj.max_shots = 3
                                    game.game.player_obj.shots = 3
                                if obj.obj_type == ObjType.Speed:
                                    game.game.do_slide_text("Improved Movement!")
                                    obj.destroy = True
                                    game.game.player_obj.max_movement = 4
                                    game.game.player_obj.movement = 4
                                if obj.obj_type == ObjType.Health:
                                    game.game.do_slide_text("Health & Ammo!")
                                    obj.destroy = True
                                    game.game.player_obj.start_health = 3
                                    game.game.player_obj.health = 3
                                    game.game.player_obj.max_ammo = 5
                                    game.game.player_obj.ammo = 5
                        resources.play_sound(resources.SOUND_MOVE)
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
                    if x == 0 and y == 0:
                        continue
                    if not room.is_path_acceptable(enemy_cell, (enemy_cell[0] + x, enemy_cell[1] + y)):
                        continue
                    obj_at_pos = room.get_obj_at_pos(enemy_cell[0] + x, enemy_cell[1] + y)
                    if obj_at_pos is None or not obj_at_pos.collides or obj_at_pos.obj_type in [ObjType.Enemy, ObjType.EnemyBig, ObjType.Player, ObjType.Target]:
                        draw_pos = enemy_pos[0] + x*constants.GRID_CELL_SIZE, enemy_pos[1] + y*constants.GRID_CELL_SIZE
                        resources.blt_ui_sprite(resources.SPRITE_UI_HIGHLIGHT, (constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE), draw_pos[0], draw_pos[1])
                        if Controls.mouse_in(draw_pos[0], draw_pos[1], constants.GRID_CELL_SIZE, constants.GRID_CELL_SIZE):
                            game.game.selected_enemy.last_move_dir = pyxel.sgn(x)
                            game.game.selected_enemy = None
                            action = game.Action.Roll
                            if obj_at_pos is not None:
                                if obj_at_pos.obj_type == ObjType.Player:
                                    game.game.player_obj.health -= 1
                                    game.game.player_obj.hit_frames = 12
                                    if game.game.player_obj.health <= 0:
                                        game.game.game_over()
                                    else:
                                        action = game.Action.MovePlayer
                                elif obj_at_pos.obj_type == ObjType.Target:
                                    game.game.game_over()
                                elif obj_at_pos.obj_type in [ObjType.Enemy, ObjType.EnemyBig]:
                                    action = game.Action.MoveEnemy
                                    game.game.selected_enemy = obj_at_pos

                            obj.move_start_pos = obj.get_pos()
                            obj.target_pos = draw_pos
                            obj.move_timer = 0

                            resources.play_sound(resources.SOUND_MOVE)
                            if action != game.Action.MoveEnemy:
                                game.game.action = action
                            break
    elif game.game.action == game.Action.Shoot:
        pyxel.circ(game.game.shoot_target[0], game.game.shoot_target[1], 2, resources.COLOR_TEXT)
        pyxel.circ(game.game.shoot_target[0], game.game.shoot_target[1], 1, resources.COLOR_TEXT_INACTIVE)
        pyxel.line(game.game.player_obj.pos_x+8, game.game.player_obj.pos_y+8, game.game.shoot_target[0], game.game.shoot_target[1], resources.COLOR_TEXT_INACTIVE)
    elif game.game.action == game.Action.NewWave:
        for obj in game.game.objects:
            if obj.obj_type == ObjType.Spawn:
                resources.blt_ui_sprite(resources.SPRITE_UI_HIGHLIGHT, (16, 16), obj.pos_x, obj.pos_y)
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

    # Draw path values
    for x in range(len(game.game.path)):
        for y in range(len(game.game.path[0])):
            pos = room.get_pos_for_room(cell_pos=(x, y))
            pos = pos[0]+8, pos[1]+8
            if game.game.path[x][y] is not None and Controls.mouse_hovering(x*16, y*16, 16, 16):
                #pyxel.text(pos[0], pos[1], str(game.game.path[x][y]), resources.COLOR_TEXT_INACTIVE)
                pyxel.circ(pos[0], pos[1], 2, resources.COLOR_TEXT_INACTIVE)
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if game.game.path[x+dx][y+dy] is not None and game.game.path[x+dx][y+dy] < game.game.path[x][y]:
                            pyxel.line(x*constants.GRID_CELL_SIZE+8, y*constants.GRID_CELL_SIZE+8, (x+dx)*constants.GRID_CELL_SIZE+8, (y+dy)*constants.GRID_CELL_SIZE+8, resources.COLOR_TEXT_INACTIVE)

    # Tutorial
    if game.game.game_state == game.GameState.Tutorial:
        if game.game.tutorial_step == 0:
            target_cell = (7, 7)
            draw_tutorial_message(target_cell, "Welcome! BurgerBoy here needs your help.\n\n"
                                               "His hands are greasy, \n"
                                               "knees weak, arms heavy...\n"
                                               "but he's ready, \nto deliver justice!"
                                               "          Click to continue.")
        elif game.game.tutorial_step == 1:
            target_cell = game.game.player_obj.get_cell()
            draw_tutorial_circle(target_cell)
            draw_tutorial_message(target_cell, "Your BurgerBoy is here. Try to keep him alive!\n(Click to continue)")
        elif game.game.tutorial_step == 2:
            target_cell = (1, 3)
            draw_tutorial_circle(target_cell)
            draw_tutorial_message(target_cell, "This here beautiful burger needs to be defended!")
        elif game.game.tutorial_step == 3:
            target_cell = (14, 1)
            draw_tutorial_circle(target_cell)
            target_cell = (14, 9)
            draw_tutorial_circle(target_cell)
            target_cell = (1, 10)
            draw_tutorial_circle(target_cell)
            draw_tutorial_message(target_cell, "Aliens will come out of these holes\nYou have to pick one when new wave comes")
        elif game.game.tutorial_step == 4:
            target_cell = (8, 11)
            draw_tutorial_circle(target_cell)
            draw_tutorial_message(target_cell, "There's your timer. When it runs out, enemies come\n\nTimer stops when new wave of enemies comes")
        elif game.game.tutorial_step == 5:
            target_cell = (6, 12.5)
            draw_tutorial_circle(target_cell)
            target_cell = (10, 12.5)
            draw_tutorial_circle(target_cell)
            target_cell = (8, 12.5)
            draw_tutorial_circle(target_cell)
            draw_tutorial_message(target_cell, "Three symbol spaces. Click on them to roll for a new symbol\n\n"
                                               "Actions require specific symbols\n\n"
                                               "Move: 1 boot symbol\nReload: 1 bullet symbol\nShoot: 2 gun symbols")
        elif game.game.tutorial_step == 6:
            target_cell = (6, 12.5)
            draw_tutorial_circle(target_cell)
            target_cell = (10, 12.5)
            draw_tutorial_circle(target_cell)
            target_cell = (8, 12.5)
            draw_tutorial_circle(target_cell)
            draw_tutorial_message(target_cell, "Careful! \n\n"
                                               "Sometimes your roll will force you to move enemies\n\n"
                                               "or even release a new wave! (if you get an X symbol)")
        elif game.game.tutorial_step == 7:
            target_cell = (3, 12.5)
            draw_tutorial_circle(target_cell)
            target_cell = (1, 12.5)
            draw_tutorial_circle(target_cell)
            draw_tutorial_message(target_cell, "Here are your actions. \n\n"
                                               "You can take an action only \n\nif you have enough matching symbols.")
            target_cell = (3, 13.5)
            draw_tutorial_circle(target_cell)
            target_cell = (1, 13.5)
            draw_tutorial_circle(target_cell)
        elif game.game.tutorial_step == 8:
            target_cell = (13.5, 13.5)
            draw_tutorial_circle(target_cell)
            draw_tutorial_message(target_cell, "Click here to start.\n\n"
                                               "You control enemy movement, \nbut they always have to move towards the burger\n\nGood Luck & Deliver the Greasy Justice!")

    if game.game.player_obj.ammo <= 1:
        if int(pyxel.frame_count / 10) % 3 != 0:
            resources.bold_text(game.game.player_obj.pos_x - 8, game.game.player_obj.pos_y - 8, "LOW AMMO")

    x_pos_slide = 38
    y_pos_slide = 24
    if game.game.slide_text_timer > 0:
        x = interp.interp(game.game.camera_x-100, x_pos_slide, 1-game.game.slide_text_timer, 1, interp.EasingType.Slerp)
        draw_slide_bg(x, y_pos_slide)
        resources.bold_text(x, y_pos_slide, game.game.slide_text,)
        game.game.slide_text_timer -= constants.FRAME_TIME
    elif game.game.slide_text_timer > -1.5:
        if game.game.slide_text_timer < -0.5:
            x = interp.interp( x_pos_slide, game.game.camera_x + pyxel.width+50, abs(game.game.slide_text_timer)-0.5, 1, interp.EasingType.EaseInOutQuint)
            draw_slide_bg(x, y_pos_slide)
            resources.bold_text(x, y_pos_slide, game.game.slide_text,)
        else:
            draw_slide_bg(x_pos_slide, y_pos_slide)
            resources.bold_text(x_pos_slide, y_pos_slide, game.game.slide_text, )
        game.game.slide_text_timer -= constants.FRAME_TIME

    if game.game.action == game.Action.Shoot:
        resources.bold_text(pyxel.mouse_x, pyxel.mouse_y - 8, f"{game.game.player_obj.shots}/{game.game.player_obj.max_shots}")
    elif game.game.action == game.Action.MovePlayer:
        resources.bold_text(pyxel.mouse_x, pyxel.mouse_y - 8, f"{game.game.player_obj.movement}/{game.game.player_obj.max_movement}")
    elif game.game.action == game.Action.NewWave:
        resources.bold_text(pyxel.mouse_x, pyxel.mouse_y - 8, f"{game.game.new_wave_enemies}")
    elif game.game.action == game.Action.MoveEnemy:
        resources.bold_text(pyxel.mouse_x - 8, pyxel.mouse_y - 12, f"Move an enemy!")

    if game.game.game_state == game.GameState.GameOver:
        score = 'F'
        if game.game.current_wave > 7:
            score = 'A+'
        elif game.game.current_wave > 6:
            score = 'B+'
        elif game.game.enemies_killed > 22:
            score = 'B'
        elif game.game.enemies_killed > 20:
            score = 'C+'
        elif game.game.enemies_killed > 12:
            score = 'C'
        elif game.game.current_wave > 4:
            score = 'D'
        elif game.game.current_wave > 3:
            score = 'E'
        draw_tutorial_message((7, 10), f"  You lost!\n\n\n"
                                       f"  Wave: {game.game.current_wave}\n\n"
                                       f"  Enemies killed: {game.game.enemies_killed}\n\n"
                                       f"  Time Survived: {game.game.total_time}\n\n"
                                       f"  Score: {score}\n\n\n"
                                       f"  Click to try again!")

    # Mouse cursor
    resources.blt_ui_sprite(resources.SPRITE_UI_CURSOR, (8, 8), pyxel.mouse_x, pyxel.mouse_y)



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

def draw_tutorial_circle(target_cell):
    target_pos = room.get_pos_for_room(target_cell)
    target_pos = target_pos[0] + 8, target_pos[1] + 8
    pyxel.circb(target_pos[0], target_pos[1], 11, resources.COLOR_TEXT_INACTIVE)
    pyxel.circb(target_pos[0], target_pos[1], 12, resources.COLOR_TEXT)
    pyxel.circb(target_pos[0], target_pos[1], 13, resources.COLOR_TEXT_INACTIVE)


def draw_tutorial_message(target_cell, txt):
    txt_size = utils.get_size_for_text(txt)
    target_pos_orig = room.get_pos_for_room(target_cell)
    target_pos = target_pos_orig[0] - txt_size[0]/2, target_pos_orig[1] - txt_size[1] - 16
    if target_pos[0] < 16:
        target_pos = 16, target_pos[1]
    if target_pos[0]+txt_size[0] > constants.SCREEN_WIDTH:
        target_pos = constants.SCREEN_WIDTH - txt_size[0]-8, target_pos[1]
    pyxel.rect(target_pos[0]-4, target_pos[1]-4, txt_size[0]+8, txt_size[1]+8, 4)
    pyxel.rectb(target_pos[0]-4, target_pos[1]-4, txt_size[0]+8, txt_size[1]+8, 5)
    pyxel.text(target_pos[0], target_pos[1], txt, resources.COLOR_TEXT_INACTIVE)

def draw_slide_bg(x_pos, y_pos):
    for y in range(-10, 10):
        n = pyxel.noise((y_pos + y*2) / 20, pyxel.frame_count / 30) * 10
        pyxel.line(x_pos, y_pos + y, x_pos + 96 + n, y_pos+ y, 4)
        n = pyxel.noise((y_pos + y*2) / 20, (pyxel.frame_count+5) / 30)*10
        pyxel.line(x_pos-40, y_pos + y, x_pos + 52 + n, y_pos+ y, 5)
        n = pyxel.noise((y_pos + y*2) / 20, (pyxel.frame_count+10) / 30)*10
        pyxel.line(x_pos - 46 + n, y_pos + y, x_pos - 16 + n, y_pos+ y, 6)


init()
pyxel.run(update, draw)
