import math
from typing import Tuple


def clamp(val: float, a: float, b: float) -> float:
    if val < a:
        val = a
    if val > b:
        val = b
    return val


def clamp01(val: float) -> float:
    return clamp(val, 0, 1)


def get_vector_len(vec: Tuple[int, int]) -> float:
    return math.sqrt(vec[0]**2 + vec[1]**2)


def get_vector_normalised(vec: Tuple[int, int]) -> Tuple[float, float]:
    len = get_vector_len(vec)
    return vec[0]/len, vec[1]/len

def get_size_for_text(txt: str) -> Tuple[int, int]:
    lines = txt.splitlines()
    line = max(lines, key=len)
    return len(line)*4, 6*len(lines)

def deg_to_rad(deg):
    return deg*3.14/180
