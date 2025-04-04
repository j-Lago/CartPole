import math
import cmath

Vec2 = tuple[float, float]
Color3 = tuple[int, int, int]

def scale_vec2(vec: Vec2, scale: float):
    return vec[0] * scale, vec[1] * scale


def translate_vec2(vec: Vec2, translation: Vec2) -> Vec2:
    return vec[0] + translation[0], vec[1] + translation[1]


def translate_vec2s(vecs: tuple[Vec2, ...], translation: Vec2) -> tuple[Vec2, ...]:
    return tuple(translate_vec2(vec, translation) for vec in vecs)


def rotate_vec2(vec: Vec2, angle: float, center: Vec2 = (0.0, 0.0)):
    c, s = math.cos(angle), math.sin(angle)
    if center != (0.0, 0.0):
        translate = -center[0], -center[1]
        vec = translate_vec2(vec, translate)
    return c * vec[0] - s * vec[1] + center[0], s * vec[0] + c * vec[1] + center[1]


def rotate_vec2s(vecs: tuple[Vec2, ...], angle: float, center: Vec2 = (0.0, 0.0)) -> tuple[Vec2, ...]:
    return tuple(rotate_vec2(vec, angle, center) for vec in vecs)


def scale_vec2s(vecs: tuple[Vec2, ...], scale) -> tuple[Vec2, ...]:
    return tuple(scale_vec2(vec, scale) for vec in vecs)


def lerp(a, b, t):
    return a + (b-a)*t


def lerp_vec2(v0: Vec2, v1: Vec2, t) -> Vec2:
    return lerp(v0[0], v1[0], t), lerp(v0[1], v1[1], t)


def lerp_vec3(v0, v1, t):
    return lerp(v0[0], v1[0], t), lerp(v0[1], v1[1], t), lerp(v0[2], v1[2], t)
