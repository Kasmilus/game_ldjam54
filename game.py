from typing import List, Tuple
from enum import Enum

import pyxel

import constants
from game_object import Obj, ObjType


class GameState(Enum):
    Game = 1
    GameOver = 2


class Dice(Enum):
    Unrolled = 0
    Run = 1
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
        self.game_state: GameState = GameState.Game
        self.objects: List[Obj] = []  # List of only objects in current and surrounding rooms

        self.player_obj: Obj = None  # Reference to the player

        self.camera_x = 0
        self.camera_y = 0
        self.camera_target_x = 0
        self.camera_target_y = 0

        self.stop_frames = 0
        self.cam_shake_timer = 0

        self.action: Action = Action.MoveEnemy
        self.action_queue: List = []
        self.dice = [Dice.Run, Dice.Run, Dice.Run]
        self.wave_timer = 0
        self.current_wave = 0
        self.selected_enemy = None
        self.new_wave_enemies = 0

        self.roll_die(0, True)
        self.roll_die(1, True)
        self.roll_die(2, True)

    def get_dice_image(self, i):
        assert len(self.dice) > i
        return self.dice[i].name

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

    def roll_die(self, i, ignore_stuck: bool = False):
        assert len(self.dice) > i
        if self.dice[i] == Dice.Stuck:
            return
        if self.action != Action.Roll:
            return

        if ignore_stuck:
            rnd = pyxel.rndi(1,8)
        else:
            rnd = pyxel.rndi(1, 9)
        if rnd <= 2:
            self.dice[i] = Dice.Run
        elif rnd <= 5:
            self.dice[i] = Dice.Shoot
        elif rnd <= 7:
            self.dice[i] = Dice.Reload
        elif rnd <= 8:
            self.dice[i] = Dice.Enemy
            self.action_queue.insert(0, Action.MoveEnemy)
        elif rnd <= 9:
            self.dice[i] = Dice.Stuck
        else:
            assert False

    def get_required_num_for_die(self, die):
        required = None
        if die == Dice.Run:
            required = 1
        elif die == Dice.Shoot:
            required = 2
        elif die == Dice.Reload:
            required = 2
        return required

    def can_do_die_action(self, die):
        if self.action != Action.Roll:
            return False

        required = self.get_required_num_for_die(die)
        for i in range(len(self.dice)):
            if self.dice[i] == die:
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
                i += 1
            if die == Dice.Run:
                self.action = Action.MovePlayer
            elif die == Dice.Shoot:
                self.action = Action.Shoot
            elif die == Dice.Reload:
                self.player_obj.ammo = self.player_obj.max_ammo

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
        print("AAA")
        for i in range(len(self.dice)):
            if self.dice[i] == Dice.Stuck:
                print(i)
                self.roll_die(i, ignore_stuck=True)

        if started_with_timer:
            if self.current_wave >= len(constants.WAVES):
                pass  # TODO: Win!
            else:
                self.action = Action.Break

    def unpause_game(self):
        self.action = Action.NewWave
        self.new_wave_enemies = 5
        self.wave_timer = constants.WAVES[self.current_wave]
        self.current_wave += 1




def init_game():
    global game
    global game_checkpoint
    game = Game()
    game_checkpoint = None

