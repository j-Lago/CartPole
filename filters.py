from _collections import deque


class MediaMovel(deque):
    def __init__(self, n):
        super().__init__(maxlen=n)

    @property
    def value(self):
        if len(self) == 0:
            return 0.0
        return sum(self) / len(self)