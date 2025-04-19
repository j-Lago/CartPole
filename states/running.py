import gamebase as gb
import pygame
from pygame import Vector2
import math
from pathlib import Path
from random import random, uniform, randint, choice, choices
from player import Cart
import states as st
from bindings import *
from game_draw import draw, simulate


class Running(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.game_time = 30
        self.timer_id = self.game.clock.start_timer(pygame.event.Event(TIMEOUT), period_seconds=self.game_time)

    def __str__(self):
        return 'Running'

    def enter(self):
        self.game.clock.resume_timer(self.timer_id)

    def exit(self):
        self.game.clock.pause_timer(self.timer_id)
        self.game.previous_state_screenshot = self.game.active_canvas.copy()

    def handle_event(self, event: pygame.event):
        if bind_test(event, TOGGLE_PAUSE):
            self.change_state(st.Paused(self.game))
        if event.type == TIMEOUT:
            self.change_state(st.Timeout(self.game))
        if bind_test(event, RESTART):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        simulate(self)
        draw(self)
