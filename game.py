from typing import List, Tuple
from enum import Enum

import pyxel

import constants
import resources
from game_object import Obj, ObjType


class GameState(Enum):
    Tutorial = 0
    Game = 1
    GameOver = 2


class Dice(Enum):
    Empty = 0
    Move = 1
    Shoot = 2
    Reload = 3
    Enemy = 4
    Stuck = 5

class Action(Enum):
    Roll = 0
    MovePlayer = 1
    MoveEnemy = 2
    Shoot = 3
    NewWave = 4
    Break = 5

class Game:
    def __init__(self):
        #self.game_state: GameState = GameState.Game
        self.game_state: GameState = GameState.Tutorial
        self.objects: List[Obj] = []  # List of only objects in current and surrounding rooms
        self.path = []
        for i in range(constants.ROOM_SIZE_X):
            self.path.append([None]*constants.ROOM_SIZE_Y)

        self.player_obj: Obj = None  # Reference to the player

        self.tutorial_step = 0
        self.time_since_tutorial_step = 0

        self.enemies_killed = 0
        self.total_time = 0

        self.camera_x = 0
        self.camera_y = 0
        self.camera_target_x = 0
        self.camera_target_y = 0

        self.stop_frames = 0
        self.cam_shake_timer = 0

        self.action: Action = Action.Roll
        self.action_queue: List = []
        self.dice = [Dice.Move, Dice.Move, Dice.Move]
        self.dice_roll_timer = [0, 0, 0]
        self.wave_timer = 90
        self.current_wave = 0
        self.selected_enemy = None
        self.new_wave_enemies = 0

        self.shoot_time = 0
        self.shoot_target = (0, 0)

        self.roll_die(0, True, True)
        self.roll_die(1, True, True)
        self.roll_die(2, True, True)

        self.slide_text = ""
        self.slide_text_timer = -10

        self.time_since_game_over = 0

    def get_dice_image(self, i):
        assert len(self.dice) > i
        d = self.dice[i]
        if self.dice_roll_timer[i] > 0:
            d = Dice(int((pyxel.frame_count + i*12) / 10) % len(Dice))

        if d == Dice.Move:
            return resources.SPRITE_UI_ICON_RUN
        elif d == Dice.Reload:
            return resources.SPRITE_UI_ICON_RELOAD
        elif d == Dice.Shoot:
            return resources.SPRITE_UI_ICON_SHOOT
        elif d == Dice.Enemy:
            return resources.SPRITE_UI_ICON_ENEMY
        elif d == Dice.Stuck:
            return resources.SPRITE_UI_ICON_STUCK

    def get_dice_text(self, i):
        assert len(self.dice) > i
        d = self.dice[i]
        if self.dice_roll_timer[i] > 0:
            d = Dice(int((pyxel.frame_count) / 10) % len(Dice))
        return d.name

    def is_any_die_stuck(self):
        for i in range(len(self.dice)):
            if self.dice[i] == Dice.Stuck:
                return True
        return False
    def can_roll(self, i):
        assert len(self.dice) > i
        if self.dice[i] == Dice.Stuck:
            return False
        if self.action != Action.Roll:
            return False
        return True

    def roll_die(self, i, ignore_stuck: bool = False, ignore_enemy = False):
        assert len(self.dice) > i
        if self.dice[i] == Dice.Stuck and not ignore_stuck:
            return
        if self.action != Action.Roll:
            return

        if ignore_stuck:
            rnd = pyxel.rndi(1,9)
            if ignore_enemy:
                rnd = pyxel.rndi(1,8)
        else:
            rnd = pyxel.rndi(1, 10)
        if rnd <= 2:
            self.dice[i] = Dice.Move
        elif rnd <= 6:
            self.dice[i] = Dice.Shoot
        elif rnd <= 8:
            self.dice[i] = Dice.Reload
        elif rnd <= 9:
            self.dice[i] = Dice.Enemy
            self.action_queue.insert(0, Action.MoveEnemy)
        elif rnd <= 10:
            self.dice[i] = Dice.Stuck
        else:
            assert False
        self.dice_roll_timer[i] = 1.5
        resources.play_sound(resources.SOUND_ROLL)

    def get_required_num_for_die(self, die):
        required = None
        if die == Dice.Move:
            required = 1
        elif die == Dice.Shoot:
            required = 2
        elif die == Dice.Reload:
            required = 1
        return required

    def can_do_die_action(self, die):
        if self.action != Action.Roll:
            return False

        required = self.get_required_num_for_die(die)
        for i in range(len(self.dice)):
            if self.dice[i] == die and self.dice_roll_timer[i] <= 0:
                required -= 1
        if required <= 0:
            return True
        return False

    def take_dice(self, die):
        if self.can_do_die_action(die):
            required = self.get_required_num_for_die(die)
            i = 0
            while required > 0:
                if self.dice[i] == die:
                    self.roll_die(i)
                    required -= 1
                    self.dice[i] = Dice.Empty
                i += 1
            if die == Dice.Move:
                self.action = Action.MovePlayer
                self.do_slide_text("Move!")
            elif die == Dice.Shoot:
                self.action = Action.Shoot
                self.do_slide_text("Shoot!")
            elif die == Dice.Reload:
                self.player_obj.ammo = self.player_obj.max_ammo
                self.do_slide_text("Reloaded!")

    def set_action(self, action):
        self.action_queue.append(action)
        current_action = self.action_queue.pop(0)
        self.action = current_action
    def add_action(self, action):
        self.action_queue.append(action)
    def pop_action(self):
        current_action = self.action_queue.pop(0)
        self.action = current_action


    def start_new_wave(self, started_with_timer: bool = False):
        for i in range(len(self.dice)):
            if self.dice[i] == Dice.Stuck:
                print(i)
                self.roll_die(i, ignore_stuck=True)

        if started_with_timer:
            if self.current_wave >= len(constants.WAVES):
                self.new_wave_enemies += min(self.current_wave*3, 20)
            else:
                self.new_wave_enemies = constants.WAVE_COUNT[self.current_wave]
                self.action_queue.append(Action.Break)
        else:
            self.new_wave_enemies = 5
            self.action_queue.append(Action.NewWave)

        if self.current_wave > 0 or started_with_timer is False:
            self.do_slide_text("New Wave!")

    def unpause_game(self):
        self.action = Action.NewWave
        if self.current_wave < len(constants.WAVES):
            self.wave_timer = constants.WAVES[self.current_wave]
        else:
            self.wave_timer = 45
        self.current_wave += 1

    def game_over(self):
        self.do_slide_text("Game Over")
        self.stop_frames = 6
        self.cam_shake_timer = 0.5
        self.game_state = GameState.GameOver
        resources.play_sound(resources.SOUND_PLAYER_DEATH)
        self.time_since_game_over = 0

    def do_slide_text(self, text):
        self.slide_text = text
        self.slide_text_timer = 1


def init_game():
    global game
    global game_checkpoint
    game = Game()
    game_checkpoint = None

