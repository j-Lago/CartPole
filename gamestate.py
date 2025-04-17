from abc import ABC, abstractmethod
from bindings import *


class GameState(ABC):
    def __init__(self, game):
        self.game = game

    def change_state(self, new_state):
        self.game.state.exit()
        self.game.state = new_state
        self.game.state.enter()

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event: pygame.event):
        pass

    def update(self):
        pass

    def render(self):
        pass

    @abstractmethod
    def __str__(self):
        pass


class Running(GameState, ABC):
    def __init__(self, game):
        super().__init__(game)

    def enter(self):
        print('enter running')

    def handle_event(self, event: pygame.event):
        if bind_test(event, TOGGLE_PAUSE):
            self.change_state(Paused(self.game))


class Paused(GameState, ABC):
    def __init__(self, game):
        super().__init__(game)

    def __str__(self):
        return 'GameState: Paused'

    def handle_event(self, event: pygame.event):
        if bind_test(event, TOGGLE_PAUSE):
            self.change_state(Running(self.game))
