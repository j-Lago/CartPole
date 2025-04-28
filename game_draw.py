
from __future__ import annotations

import datetime

import cartpole
import gamebase as gb
import math
from random import random, uniform, randint, choice, choices
import states as st


def simulate(state: st.GameState):
    game: cartpole.CartPoleGame = state.game
    combined_input = 0.0
    for player in game.players.values():
        if player.alive:
            combined_input += math.fabs(player.input.update(player)) if player.fuel >0 else 0
    game.sounds['jet'].set_volume(combined_input)

    d = random() * game.chash_xoffset * 0.2
    game.chash_xoffset -= d
    shake_intensity = 1.3
    game.blit_offset = uniform(-shake_intensity, shake_intensity) * combined_input * shake_intensity + d, uniform(
        -shake_intensity, shake_intensity) * combined_input * shake_intensity * (1 + abs(d) * .3)

    for player in game.players.values():
        player.step()


def feedback(state: st.GameState):
    for player in state.game.players.values():
        player.feedback()

def draw(state: st.GameState, intro=False):
    game: cartpole.CartPoleGame = state.game
    canvas: gb.Canvas = game.canvas

    canvas.fill(game.cols['bg'])
    pos = game.mouse.pos

    game.stress_test()  # todo: retirar na versão final

    # desenha os mortos por traz
    for player in game.players.values():
        if not player.alive:
            player.draw(game.clock.t)
    for key, player in game.players.items():
        if player.alive:
            player.draw(game.clock.t)

    # timer
    remain = game.clock.get_timer_remaining(state.timer_id) if not intro else game.game_duration
    game.progress_timer.update(remain)
    time_col = game.cols['timer'] if remain >= game.progress_timer.low_value else game.progress_timer.low_color
    canvas.draw_text(time_col, game.fonts['normal'], f'{remain:.1f}',
                     (canvas.xmax - 0.05, -0.04), anchor='midright')
    canvas.draw_text(time_col, game.fonts['medium'], 'TIMER', (canvas.xmax - 0.06, 0.05),
                     anchor='midright')


    # score
    canvas.draw_text(game.cols['timer'], game.fonts['normal'], f'{game.best_score.value}',
                     (canvas.xmin + 0.05, 0), anchor='midleft')
    canvas.draw_text(game.cols['timer'], game.fonts['medium'], 'BEST SCORE', (canvas.xmin + 0.06, -0.08),
                     anchor='midleft')
    canvas.draw_text(game.cols['timer'], game.fonts['tiny'], game.best_score.input_device, (canvas.xmin + 0.06, -0.13),
                     anchor='midleft')
    if game.best_score.date > datetime.date.min:
        canvas.draw_text(game.cols['timer'], game.fonts['tiny'], game.best_score.date.isoformat(), (canvas.xmin + 0.06, -0.17),
                     anchor='midleft')




    # scope
    if isinstance(game.players['p1'].input, gb.LinearController):
        pid = game.players['p1'].input.p_out, game.players['p1'].input.i_out,game.players['p1'].input.d_out
    else:
        pid = 0.0, 0.0, 0.0
    x = game.clock.t
    total_frame_time = 1 / game.real_fps if game.real_fps != 0 else 0
    y = {
        'p2': (
            game.players['p2'].theta - math.pi, game.players['p2'].x, game.players['p2'].v,
            game.players['p2'].omega),
        'p1': (
            game.players['p1'].theta - math.pi, game.players['p1'].x, game.players['p1'].v,
            game.players['p1'].omega),
        'inputs': (game.players['p1'].input.value, game.players['p2'].input.value),
        'times': (game.last_active_frame_time * game.clock.fps - 1, total_frame_time * game.clock.fps - 1),
        'pid': pid
    }


    def another_in_focus(self_key):
        for ikey, iscope in game.scopes.items():
            if ikey != self_key and iscope._on_focus:
                return True
        return False

    for key, scope in game.scopes.items():
        scope.append(x, y[key])
        # scope.on_focus = scope.collision(game.mouse.pos) and not another_in_focus(key)
        scope.update(game)


    #

