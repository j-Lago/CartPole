import datetime
import warnings

import gamebase as gb
import pygame
from pygame import Vector2
import math
from pathlib import Path
from random import random, uniform, randint, choice, choices
from player import Cart, Score
import states as st
from bindings import *
from game_draw import draw, simulate
import json
from codebase_hash import generate_folder_hash


class CartPoleGame(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game_duration = 45

        self.rel_path = Path(__file__).parent
        self.assets_path = self.rel_path / 'assets'
        self.save_file_path = self.rel_path / 'meta' / 'save.json'
        self.hash_file_path = self.rel_path / 'hash' / 'hash.json'
        self.hash_ignore_dirs = {'.idea', '.git', '.venv', '__pycache__', 'hash'}
        self.version = '0.0.1'

        # mouse callbacks
        self.mouse.right.release_callback = self.right_release


        self.load_sounds()
        self.load_colors()
        self.inputs = gb.InputPool()

        self.canvas = gb.Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.state_draw, flags=pygame.HWSURFACE)
        self.event_loop_callback = self.handle_user_input_event

        self.fps_popup = gb.PopUpText(self.canvas, alpha=255,
                                      pos=(self.canvas.xmin + 0.01, self.canvas.ymax - .04),
                                      color=self.cols['fps'], text='', font=self.fonts['medium'], visible=True,
                                      border_width=-1, fill_color=(0, 0, 0, 0))

        self.scopes = {
            'p1': gb.Scope(self.canvas, name='p1 states', legend=('th', 'x', 'vel', 'w'), fps=self.clock.fps,
                           alpha=200, color=self.cols['p1'], focus_color=self.cols['focus'],
                           y_scale=(0.25, 0.25, .25, .25), x_scale=0.5,
                           pos=(-1.75, 0.8), size=(320, 180), maxlen=400, visible=False),
            'p2': gb.Scope(self.canvas, name='p2 states', legend=('th', 'x', 'vel', 'w'), fps=self.clock.fps,
                           alpha=200,color=self.cols['p2'], focus_color=self.cols['focus'],
                           y_scale = (0.25, 0.25, .25, .25), x_scale=0.5,
                           pos=(-1.75, -0.01), size=(320, 180), maxlen=400, visible=False),
            'inputs': gb.Scope(self.canvas, name='inputs', legend=('p1', 'p2'), fps=self.clock.fps,
                               alpha=200,color=self.cols['info'], focus_color=self.cols['focus'],
                               y_scale=(0.8, 0.8), x_scale=0.5,
                               pos=(-1.1, -0.65), size=(320, 180), maxlen=400, visible=False),
            'times': gb.Scope(self.canvas, name='frame time', legend=('active', 'total'), fps=self.clock.fps,
                              alpha=200, color=self.cols['info'], focus_color=self.cols['focus'],
                              x_scale=0.5,
                              pos=(-1.75, -0.65),
                              size=(320, 180), maxlen=400, visible=True),
            'pid': gb.Scope(self.canvas, name='pid output', legend=('p', 'i', 'd'), fps=self.clock.fps,
                            alpha=200, color=self.cols['info'], focus_color=self.cols['focus'],
                            y_scale=(3.0, 3.0, 3.0, 3.0), x_scale=0.5,
                            pos=(1.05, 0.6), size=(320, 180), maxlen=400, visible=True),
        }

        self.progress_timer = gb.ProgressBar(
            self.canvas,
            (+1.72-0.28, -0.1, 0.28, 0.03),
            0, self.game_duration, self.game_duration, self.game_duration*.2,
            self.cols['timer'], self.cols['bg'],
            border_width=2,
            border_radius=0,
        )

        th0 = uniform(-1, 1) * 0.0
        self.players = {
            'p1': Cart('P1', self, self.inputs.get('p1'), Vector2(-0.8, 0.35), base_color=self.cols['p1'],
                       rail_color=(90, 90, 90), th0=th0, death_callback=self.death),
            'p2': Cart('P2', self, self.inputs.get('p2'), Vector2(-0.8, -0.45), base_color=self.cols['p2'],
                       rail_color=(90, 90, 90), th0=th0, death_callback=self.death),
        }

        self.info_popup.visible = False
        self.chash_xoffset: float = 0.0
        self.perturbation: float = 0.0

        self.stress_test_particles = gb.Particles(1200)
        self.stress_test_en = False

        self.extra_help = [
            f'────────────────────────',
            f'ESC: reset',
            f' F2: settings',
            f' F7: toggle stress test',
            f'  1: toggle player 1 en',
            f'  2: toggle player 2 en',
            f'  .: perturb clockwise',
            f'  ,: perturb anticlock',
            f'  s: enable scopes',
            f'm_r: disable scope',
        ]

        self.best_score = self.load_best_score()
        self.show_fps = True

        self.reset()
        self.state = st.Intro(self)

    def reset(self):
        self.clock.reset()
        self.chash_xoffset = 0.0
        self.perturbation = 0.0
        for scope in self.scopes.values():
            scope.clear()
        for player in self.players.values():
            player.reset()
        for input_ in self.inputs.values():
            input_.reset()

    def load_sounds(self):
        self.fonts['reward'] = pygame.font.SysFont('Comic Sans MS', 22)
        self.sounds['beeeep'] = self.load_sound(self.assets_path / 'beep.wav', volume=0.5)
        self.sounds['beep'] = self.load_sound(self.assets_path / 'beep.wav', volume=0.2)
        self.sounds['whistle'] = self.load_sound(self.assets_path / 'whistle.wav', volume=0.2)
        self.sounds['coin'] = self.load_sound(self.assets_path / 'coin.wav', volume=0.1)
        self.sounds['crash'] = self.load_sound(self.assets_path / 'crash.wav', volume=1.0)
        self.sounds['jet'] = self.load_sound(self.assets_path / 'jet.wav', volume=0.0)
        self.sounds['jet'].play(loops=-1)

    def load_colors(self):
        self.cols['focus'] = (255, 255, 0)
        self.cols['scope'] = (55, 255, 200)
        self.cols['fps'] = gb.lerp_vec3(self.cols['info'], (0, 0, 0), 0.6)
        self.cols['p1'] = (90, 140, 190)
        self.cols['p2'] = (190, 90, 140)
        self.cols['tiny_collect'] = (235, 230, 180)
        self.cols['small_collect'] = (220, 200, 60)
        self.cols['big_collect'] = (200, 140, 240)
        self.cols['huge_collect'] = (200, 90, 255)
        self.cols['timer'] = (90, 60, 50)

    def right_release(self, button: gb.MouseButton):
        for scope in self.scopes.values():
            if scope.collision(self.mouse.pos):
                scope.visible = False

    def perturb(self, intensity):
        for player in self.players.values():
            player.perturb(intensity)
            self.perturbation = intensity

    def state_draw(self, canvas: gb.Canvas):
        pygame.display.set_caption(str(self.state))
        self.state.update()
        self.state.draw(canvas)

    def stress_test(self):
        if self.stress_test_en:
            letters = [chr(i) for i in range(945, 970) if i != 962]
            for _ in range(10):
                font_index = randint(0, len(self.particles_fonts)-1)
                self.stress_test_particles.append(
                    gb.TextParticle(self.canvas,
                                    color=gb.lerp_vec3((90, 250, 90), (30, 90, 30), random()),
                                    text=choice(letters),
                                    font=self.particles_fonts[font_index],
                                    pos=(uniform(-1.8, 1.8), 1.05),
                                    vel=(0, -0.8 - font_index * .2), dt=1 / self.clock.fps, g=0, lifetime=-1,
                                    ))
            self.stress_test_particles.step_and_draw()

    def all_dead(self) -> bool:
        all_dead = True
        for player in self.players.values():
            all_dead = all_dead and not player.alive
        return all_dead

    def death(self, player):
        self.sounds['crash'].play()
        self.chash_xoffset = player.v * 500

    def load_best_score(self):
        score = Score(value=0, input_device='', date=datetime.date.min)
        try:
            with open(self.save_file_path, 'r') as save_file:
                data = json.load(save_file)
            with open(self.hash_file_path, 'r') as hash_file:
                hash_ = json.load(hash_file)
            if 'best_score' in data.keys() and 'best_score_device' in data.keys() and 'version' in data.keys() and 'date' in data.keys() and data['version'] == self.version and hash_['hash'] == generate_folder_hash(self.rel_path, self.hash_ignore_dirs):
                score.value = data['best_score']
                score.input_device = data['best_score_device']
                score.date = datetime.date.fromisoformat(data['date'])
        except FileNotFoundError:
            warnings.warn(f"Não foi possivel carregar o arquivo {self.save_file_path}")
        return score

    def save_best_score(self):
        for key, player in self.players.items():
            if player.score > self.best_score.value:
                self.best_score.value = player.score
                self.best_score.input_device = player.input.description
                self.best_score.date = datetime.date.today()
        save = {'version': '0.0.1', 'best_score': self.best_score.value, 'best_score_device': self.best_score.input_device, 'date': self.best_score.date.isoformat()}
        with open(self.save_file_path, 'w') as save_file:
            json.dump(save, save_file)
        code_hash = generate_folder_hash(self.rel_path, self.hash_ignore_dirs)
        hash_ = {'hash': code_hash}
        with open(self.hash_file_path, 'w') as hash_file:
            json.dump(hash_, hash_file)
        hash_file.close()

    def handle_user_input_event(self, event):
        self.state.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                for scope in self.scopes.values():
                    scope.visible = True

            elif event.key == pygame.K_F7:
                self.stress_test_en = not self.stress_test_en
                if self.stress_test_en:
                    if 'particles_fonts' not in self.__dict__:
                        self.particles_fonts = [
                            pygame.font.SysFont('Times', 22),
                            pygame.font.SysFont('Times', 36),
                            pygame.font.SysFont('Times', 54),
                            pygame.font.SysFont('Times', 68),
                    ]
                elif 'particles_fonts' in self.__dict__:
                    del self.particles_fonts

            elif event.key == pygame.K_COMMA:
                self.perturb(0.4)
            elif event.key == pygame.K_PERIOD:
                self.perturb(-0.4)

            elif event.key == pygame.K_KP_MULTIPLY:
                for scope in self.scopes.values():
                    scope.x_scale *= 2
            elif event.key == pygame.K_KP_DIVIDE:
                for scope in self.scopes.values():
                    scope.x_scale /= 2
