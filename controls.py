import pyxel

import resources


class Controls:
    @staticmethod
    def mouse_cancel(one=True):
        f = pyxel.btn
        if one:
            f = pyxel.btnp
        return f(pyxel.MOUSE_BUTTON_RIGHT)
    @staticmethod
    def mouse(one=True):
        f = pyxel.btn
        if one:
            f = pyxel.btnp
        return f(pyxel.MOUSE_BUTTON_LEFT)

    @staticmethod
    def mouse_hovering(x, y, width, height):
        return x <= pyxel.mouse_x <= x + width and y <= pyxel.mouse_y <= y + height
    @staticmethod
    def mouse_in(x, y, width, height, one=True):
        #pyxel.rectb(x, y, width, height, resources.COLOR_HIGHLIGHT)
        if Controls.mouse(one):
            if Controls.mouse_hovering(x, y, width, height):
                return True
        return False

    @staticmethod
    def key(val):
        if val == 0:
            return pyxel.btnp(pyxel.KEY_1)
        if val == 1:
            return pyxel.btnp(pyxel.KEY_2)
        if val == 2:
            return pyxel.btnp(pyxel.KEY_3)
        assert False

    @staticmethod
    def left(one=False):
        f = pyxel.btn
        if one:
            f = pyxel.btnp
        return f(pyxel.KEY_A) or f(pyxel.KEY_LEFT) or f(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)

    @staticmethod
    def right(one=False):
        f = pyxel.btn
        if one:
            f = pyxel.btnp
        return f(pyxel.KEY_D) or f(pyxel.KEY_RIGHT) or f(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)

    @staticmethod
    def up(one=False):
        f = pyxel.btn
        if one:
            f = pyxel.btnp
        return f(pyxel.KEY_W) or f(pyxel.KEY_UP) or f(pyxel.GAMEPAD1_BUTTON_DPAD_UP)

    @staticmethod
    def down(one=False):
        f = pyxel.btn
        if one:
            f = pyxel.btnp
        return f(pyxel.KEY_S) or f(pyxel.KEY_DOWN) or f(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)

    @staticmethod
    def a(one=False):
        f = pyxel.btn
        if one:
            f = pyxel.btnp
        return f(pyxel.KEY_Z) or f(pyxel.KEY_J) or f(pyxel.GAMEPAD1_BUTTON_A)

    @staticmethod
    def b(one=False):
        f = pyxel.btn
        if one:
            f = pyxel.btnp
        return f(pyxel.KEY_X) or f(pyxel.KEY_K) or f(pyxel.GAMEPAD1_BUTTON_B)

    @staticmethod
    def any(one=True):
        return Controls.a(one) or Controls.b(one) or Controls.left(one) or Controls.right(one) or Controls.up(one) or Controls.down(one)

    @staticmethod
    def any_dir(one=False):
        return Controls.left(one) or Controls.right(one) or Controls.up(one) or Controls.down(one)

