import gamebase as gb
from abc import ABC, abstractmethod
from bindings import *


class GameState(ABC):
    def __init__(self, game: gb.BaseScreen):
        self.game = game
        self.previous_state = None

    def change_state(self, new_state):
        self.game.state.exit()
        new_state.previous_state = self
        self.game.state = new_state
        self.game.state.enter()

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event):
        pass

    @abstractmethod
    def draw(self, canvas: gb.Canvas):
        pass

    @abstractmethod
    def __str__(self):
        pass









