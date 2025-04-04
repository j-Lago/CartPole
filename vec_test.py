

class Mat2x2:
    def __init__(self, e00, e01, e10, e11):
        self._values = ((e00, e01), (e10, e11))

    def __getitem__(self, item):
        match item:
            case tuple() | list(): return self._values[item[0]][item[1]]
            case int(): return self._values[item // 2][item % 2]
            case _: raise ValueError(f'item do tipo {type(item)} não é suportado.')

    def __mul__(self, other):
        match other:
            case Vec2(): return Vec2(other[0]*self[0, 0] + other[1]*self[0, 1], other[0]*self[1, 0] + other[1]*self[1, 1])
            case float() | int() : return Mat2x2(other*self[0,0], other*self[0,1], other*self[1,0], other*self[1,1])

    def __str__(self):
        return str(self._values)


class Vec2:
    def __init__(self, *pair):
        self._values = tuple(pair) if len(pair) == 2 else tuple(*pair)

    def __get__(self, instance, owner):
        return self._values

    def __getitem__(self, item):
        return self._values[item]

    @property
    def x(self):
        return self._values[0]

    @property
    def y(self):
        return self._values[1]

    def __add__(self, other):
        if isinstance(other, float | int):
            return Vec2(self._values[0] + other, self._values[1] + other)
        return Vec2(self._values[0] + other[0], self._values[1] + other[1])

    def __sub__(self, other):
        if isinstance(other, float | int):
            return Vec2(self._values[0] - other, self._values[1] - other)
        return Vec2(self._values[0] - other[0], self._values[1] - other[1])

    def __mul__(self, other: int | float | tuple):
        if isinstance(other, float | int):
            return Vec2(self._values[0] * other, self._values[1] * other)
        return Vec2(self._values[0] * other[0], self._values[1] * other[1])

    def __truediv__(self, other: int | float | tuple):
        if isinstance(other, float | int):
            return Vec2(self._values[0] / other, self._values[1] / other)
        return Vec2(self._values[0] / other[0], self._values[1] / other[1])

    def __floordiv__(self, other: int | float | tuple):
        if isinstance(other, float | int):
            return Vec2(int(self._values[0] // other), int(self._values[1] // other))
        return Vec2(int(self._values[0] // other[0]), int(self._values[1] // other[1]))

    def __str__(self):
        return str(self._values)



if __name__ == '__main__':
    v1 = Vec2(0.5, 0.9)
    v2 = Vec2((.8, -.2))

    m1 = Mat2x2(1, 2, 3, 4)

    print(v1)
    print(v2)
    print(v2 + 10)
    print(v2 - 10)
    print(v2 + v1)
    print(v2 - v1)
    print(v1 * v2)
    print(v1 * 5)
    print(v1 * 5.0)
    print(v1*20 / 5)
    print(v1*20 / 5.0)
    print(v1*20 // 5)
    print(v1*20 // 5.0)
    print('-----------')
    print(m1)
    print(m1[1, 0])
    print(m1[0])
    print(m1[1])
    print(m1[2])
    print(m1[3])
    print(m1*v1)
    print(m1 * 10)