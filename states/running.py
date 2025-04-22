import gamebase as gb
import pygame
from pygame import Vector2
import math
from pathlib import Path
from random import random, uniform, randint, choice, choices
from player import Cart
import states as st
from bindings import *
from game_draw import draw, simulate, feedback


class Running(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.game.reset()
        self.timer_id = self.game.clock.start_timer(pygame.event.Event(TIMEOUT), period_seconds=self.game.game_duration)

    def __str__(self):
        return 'Running'

    def enter(self):
        self.game.clock.resume_timer(self.timer_id)

    def exit(self):
        self.game.sounds['jet'].set_volume(0)
        self.game.clock.pause_timer(self.timer_id)
        self.game.previous_state_screenshot = self.game.active_canvas.copy()

    def handle_event(self, event: pygame.event):
        if bind_test(event, TOGGLE_PAUSE):
            self.change_state(st.Paused(self.game))
        elif event.type == TIMEOUT:
            self.change_state(st.Timeout(self.game))
        elif bind_test(event, RESTART):
            self.change_state(st.Intro(self.game))
        elif bind_test(event, SETTINGS):
            self.change_state(st.Settings(self.game))

    def draw(self, canvas: gb.Canvas):
        simulate(self)
        feedback(self)
        draw(self)

        if self.game.all_dead():
            self.change_state(st.GameOver(self.game))
