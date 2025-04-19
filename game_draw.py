
from __future__ import annotations

import cartpole
import gamebase as gb
import pygame
from pygame import Vector2
import math
from pathlib import Path
from random import random, uniform, randint, choice, choices
from player import Cart
from states import Intro, Running
from bindings import *



def simulate(game: cartpole.CartPoleGame):

        combined_input = 0.0
        for player in game.players.values():
            if player.alive:
                combined_input += math.fabs(player.input.update(player))

        d = random() * game.chash_xoffset * 0.2
        game.chash_xoffset -= d
        shake_intensity = 1.3
        game.blit_offset = uniform(-shake_intensity, shake_intensity) * combined_input * shake_intensity + d, uniform(
            -shake_intensity, shake_intensity) * combined_input * shake_intensity * (1 + abs(d) * .3)

        for player in game.players.values():
            player.step()
        game.sounds['jet'].set_volume(combined_input)


def draw(game: cartpole.CartPoleGame, canvas: gb.Canvas):

    canvas.fill(game.cols['bg'])
    pos = game.mouse_world_pos

    game.stress_test()  # todo: retirar na versão final

    # desenha os mortos por traz
    for player in game.players.values():
        if not player.alive:
            player.draw(game.t)
    for key, player in game.players.items():
        if player.alive:
            player.draw(game.t)

    # timer
    canvas.draw_text(game.cols['timer'], game.fonts['normal'], f'{game.game_duration - game.t:.1f}',
                     (canvas.xmax - 0.05, 0), anchor='midright')
    canvas.draw_text(game.cols['timer'], game.fonts['medium'], 'TIMER', (canvas.xmax - 0.06, -0.08),
                     anchor='midright')

    # scope
    x = game.t
    total_frame_time = 1 / game.real_fps if game.real_fps != 0 else 0
    y = {
        'p2': (
            game.players['p2'].theta - math.pi, game.players['p2'].x, game.players['p2'].v,
            game.players['p2'].omega),
        'p1': (
            game.players['p1'].theta - math.pi, game.players['p1'].x, game.players['p1'].v,
            game.players['p1'].omega),
        'inputs': (game.inputs['p1'].value, game.inputs['p2'].value),
        'times': (game.last_active_frame_time * game.clock.fps - 1, total_frame_time * game.clock.fps - 1),
    }

    # fps
    canvas.draw_text(game.cols['info'], game.fonts['fps'],
                     f'{game.mm_fps.value:.1f}',
                     canvas.topleft + (0.11, -0.02),
                     anchor='midtop')

    canvas.draw_text(game.cols['info'], game.fonts['small'],
                     f'({game.mm_frame_time.value * game.clock.fps * 100.0:.1f}%)',
                     canvas.topleft + (0.11, -0.09),
                     anchor='midtop')

    def another_in_focus(self_key):
        for ikey, iscope in game.scopes.items():
            if ikey != self_key and iscope.focus:
                return True
        return False

    for key, scope in game.scopes.items():
        scope.append(x, y[key])
        scope.focus = scope.collision(game.mouse_world_pos) and not another_in_focus(key)
        scope.draw()
        scope.blit_to_main()
