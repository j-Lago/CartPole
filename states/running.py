import gamebase as gb
import pygame
from pygame import Vector2
import math
from pathlib import Path
from random import random, uniform, randint, choice, choices
from player import Cart
import states as st
from bindings import *


class Running(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.game_time = 9
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
            self.change_state(st.GameOver(self.game))
        if bind_test(event, RESTART):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        # canvas.draw_text((255, 255, 30), self.game.fonts['huge'], f'RUNNING', (0, 0))
        # canvas.draw_text((255, 255, 30), self.game.fonts['big'], f'Game will end in {self.game.clock.get_timer_remaining(self.timer_id):.0f} s', (0, -.4))

        #simulate
        combined_input = 0.0
        for player in self.game.players.values():
            if player.alive:
                combined_input += math.fabs(player.input.update(player))

        d = random() * self.game.chash_xoffset * 0.2
        self.game.chash_xoffset -= d
        shake_intensity = 1.3
        self.game.blit_offset = uniform(-shake_intensity, shake_intensity) * combined_input * shake_intensity + d, uniform(
            -shake_intensity, shake_intensity) * combined_input * shake_intensity * (1 + abs(d) * .3)

        for player in self.game.players.values():
            player.step()
        self.game.sounds['jet'].set_volume(combined_input)



        canvas.fill(self.game.cols['bg'])
        pos = self.game.mouse_world_pos

        self.game.stress_test()  # todo: retirar na versão final

        # desenha os mortos por traz
        for player in self.game.players.values():
            if not player.alive:
                player.draw(self.game.t)
        for key, player in self.game.players.items():
            if player.alive:
                player.draw(self.game.t)

        # timer
        canvas.draw_text(self.game.cols['timer'], self.game.fonts['normal'], f'{self.game.game_duration - self.game.t:.1f}',
                         (canvas.xmax - 0.05, 0), anchor='midright')
        canvas.draw_text(self.game.cols['timer'], self.game.fonts['medium'], 'TIMER', (canvas.xmax - 0.06, -0.08),
                         anchor='midright')

        # scope
        x = self.game.t
        total_frame_time = 1 / self.game.real_fps if self.game.real_fps != 0 else 0
        y = {
            'p2': (
                self.game.players['p2'].theta - math.pi, self.game.players['p2'].x, self.game.players['p2'].v,
                self.game.players['p2'].omega),
            'p1': (
                self.game.players['p1'].theta - math.pi, self.game.players['p1'].x, self.game.players['p1'].v,
                self.game.players['p1'].omega),
            'inputs': (self.game.inputs['p1'].value, self.game.inputs['p2'].value),
            'times': (self.game.last_active_frame_time * self.game.clock.fps - 1, total_frame_time * self.game.clock.fps - 1),
        }

        # fps
        canvas.draw_text(self.game.cols['info'], self.game.fonts['fps'],
                         f'{self.game.mm_fps.value:.1f}',
                         canvas.topleft + (0.11, -0.02),
                         anchor='midtop')

        canvas.draw_text(self.game.cols['info'], self.game.fonts['small'],
                         f'({self.game.mm_frame_time.value * self.game.clock.fps * 100.0:.1f}%)',
                         canvas.topleft + (0.11, -0.09),
                         anchor='midtop')

        def another_in_focus(game_key):
            for ikey, iscope in self.game.scopes.items():
                if ikey != game_key and iscope.focus:
                    return True
            return False

        for key, scope in self.game.scopes.items():
            scope.append(x, y[key])
            scope.focus = scope.collision(self.game.mouse_world_pos) and not another_in_focus(key)
            scope.draw()
            scope.blit_to_main()





