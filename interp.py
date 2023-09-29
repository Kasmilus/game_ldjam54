import math
from enum import Enum

__all__ = ["EasingType", "interp"]


class EasingType(Enum):
    Linear = 1,
    Slerp = 2,
    EaseOutElastic = 3,
    EaseInOutQuint = 4,
    EaseOutCubic = 5,
    EaseOutBounce = 6


class InterpFunctions:
    """
    Many functions here are taken from https://easings.net/
    """
    @staticmethod
    def linear(t: float):
        # Linear
        return t

    @staticmethod
    def slerp(t: float):
        # Smooth
        return (1 - math.cos(t * math.pi)) / 2

    @staticmethod
    def ease_out_elastic(t: float):
        # Sharp in, overshoot, come back
        c4 = (2 * math.pi) / 3

        if t == 0:
            return 0
        elif t == 1:
            return 1
        else:
            return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

    @staticmethod
    def ease_in_out_quint(t: float):
        # Smooth in and out with sharp middle
        if t < 0.5:
            return 16 * t * t * t * t * t
        else:
            return 1 - math.pow(-2 * t + 2, 5) / 2

    @staticmethod
    def ease_out_cubic(t: float):
        # Fairly sharp in, smooth out
        return 1 - math.pow(1 - t, 3)

    @staticmethod
    def ease_out_bounce(t: float):
        # Smooth in, bounce out
        n1 = 7.5625
        d1 = 2.75

        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t2 = t-1.5 / d1
            return n1 * t2 * t2 + 0.75
        elif t < (2.5 / d1):
            t2 = t-2.25 / d1
            return n1 * t2 * t2 + 0.9375
        else:
            t2 = t - 2.625 / d1
            return n1 * t2 * t2 + 0.984375


easing_function = {
    EasingType.Linear: InterpFunctions.linear,
    EasingType.Slerp: InterpFunctions.slerp,
    EasingType.EaseOutElastic: InterpFunctions.ease_out_elastic,
    EasingType.EaseInOutQuint: InterpFunctions.ease_in_out_quint,
    EasingType.EaseOutCubic: InterpFunctions.ease_out_cubic,
    EasingType.EaseOutBounce: InterpFunctions.ease_out_bounce,
}


def interp(a: int, b: int, t: float, time: float, easing: EasingType) -> int:
    d = t / time
    d = easing_function.get(easing)(d)

    result = a*(1-d) + b*d
    return round(result)
