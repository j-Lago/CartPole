from pygame import Vector2, Vector3


def lerp(a: float | int, b: float | int, t) -> float | int:
    return a + (b-a)*t


def lerp_vec2(v0: Vector2, v1: Vector2, t) -> Vector2:
    return Vector2(lerp(v0[0], v1[0], t), lerp(v0[1], v1[1], t))


def lerp_vec3(v0: Vector3 | tuple[float, float, float], v1: Vector3 | tuple[float, float, float], t) -> Vector3:
    return Vector3(lerp(v0[0], v1[0], t), lerp(v0[1], v1[1], t), lerp(v0[2], v1[2], t))
