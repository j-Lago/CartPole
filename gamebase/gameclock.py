import pygame

class Clock:
    """
    Esse timer não representa necessariamente o tempo real, mas sim o número de iterações do loop principal do jogo.
    Essa distinção é relevante qaundo da utilização de tecnicas de controle discretas baseaadas em amostragem uniforme.
    """

    def __init__(self, fps: float):
        self.fps = fps
        self._ticks: int = 0
        self.unique_timer_count: int = 0
        self.timers: dict[int, Timer] = dict()
        self.active = True

    def reset(self):
        self._ticks: int = 0
        self.timers: dict[int, Timer] = dict()

    def pause(self):
        self.active = False

    def resume(self):
        self.active = True

    def update(self) -> int:
        if self.active:
            self._ticks += 1
            ids_marked_for_delete = []
            for _id, _timer in self.timers.items():
                if _timer.update(self.ticks):
                    ids_marked_for_delete.append(_id)
            for i in ids_marked_for_delete:
                del self.timers[i]
        return self._ticks

    def start_timer(self, event: pygame.event.Event, period_seconds: float | None = None, period_ticks: int | None = None) -> int:
        if period_seconds is None and period_ticks is None:
            raise ValueError("'period_s' e 'period_ticks' não podem ser ambos Nones.")
        if period_seconds is not None and period_ticks is not None:
            raise ValueError("O periodo do timer não pode ser setado simultaneamente po'period_s' e 'period_ticks'. Utilize apenas um deles.")
        if period_seconds is not None:
            period_ticks = round(period_seconds * self.fps)
        self.unique_timer_count += 1
        self.timers[self.unique_timer_count] = Timer(event, period_ticks, self.ticks)
        return self.unique_timer_count

    def get_timer_remaining(self, timer_id: int, return_in_ticks: bool = False) -> float | int:
        if timer_id not in self.timers.keys():
            return 0 if return_in_ticks else 0.0
        remain_ticks = self.timers[timer_id].remaining(self.ticks)
        return remain_ticks if return_in_ticks else remain_ticks/self.fps

    def get_timers_ids(self) -> list:
        return [*self.timers.keys()]

    def cancel_timers(self):
        self.timers: dict[int, Timer] = dict()

    def cancel_timer(self, timer_id) -> bool:
        if timer_id in self.timers.keys():
            del self.timers[timer_id]
            return True
        return False

    def pause_timer(self, timer_id) -> bool:
        if timer_id in self.timers.keys():
            return self.timers[timer_id].pause(self.ticks)
        return False

    def resume_timer(self, timer_id) -> bool:
        if timer_id in self.timers.keys():
            return self.timers[timer_id].resume(self.ticks)
        return False




    @property
    def ticks(self) -> int:
        return self._ticks

    @property
    def t(self) -> float:
        return self._ticks / self.fps


class Timer:
    """
    baseado em ticks e não em segundos
    """
    def __init__(self, event: pygame.event.Event, period: int, start: int):
        self.event = event
        self.period = period
        self.start = start
        self.pause_start_ticks = None

    def update(self, tick):
        if self.pause_start_ticks is None:
            if tick >= self.start + self.period:
                pygame.event.post(self.event)
                return True
            return False

    def remaining(self, ticks: int):
        return self.start + self.period - ticks

    def pause(self, ticks):
        if self.pause_start_ticks is None:
            self.pause_start_ticks = ticks
            return True
        return False

    def resume(self, ticks):
        if self.pause_start_ticks is not None:
            self.period += ticks - self.pause_start_ticks
            self.pause_start_ticks = None
            return True
        return False
