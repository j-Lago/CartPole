import cmath

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
            case complex(): return complex(other.real*self[0, 0] + other.imag*self[0, 1], other.real*self[1, 0] + other.imag*self[1, 1])
            case float() | int(): return Mat2x2(other*self[0, 0], other*self[0, 1], other*self[1, 0], other*self[1, 1])

    def __str__(self):
        return str(self._values)

if __name__ == '__main__':
    v1 = complex(0.5, 0.9)
    v2 = complex(*(.8, -.2))

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
    print('-----------')
    print(m1)
    print(m1[1, 0])
    print(m1[0])
    print(m1[1])
    print(m1[2])
    print(m1[3])
    print(m1*v1)
    print(m1 * 10)
    print(abs(v1))
