from enum import Enum
import pygame


class UserEventEnum(Enum):
    def __new__(cls, valor):
        obj = object.__new__(cls)
        obj._value_ = valor
        cls.count = 100
        return obj

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        if count == 0:
            return pygame.USEREVENT + 1
        ret = last_values[-1] + 1
        if ret >= pygame.NUMEVENTS:
            raise ValueError('Número máximo de eventos do pygame foi ultrapassado')
        return ret

    def __int__(self):
        return self.value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        return super().__eq__(other)

    def __index__(self):
        return self.value
