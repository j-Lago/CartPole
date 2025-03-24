from typing import Dict, Any

from functools import partial
import pygame
import sys
from player import Cart
from inputs import Joystick, KeysControl, IAControl, JOYBUTTON, LinearControl
import math
import random
import assets
from assets import colors as cols
from tools import lerp_v3, centered_rect
import json
from copy import copy, deepcopy
from particle import TextParticle, BallParticle, Particles
from overlay import Overlay
from progressbar import ProgressBar
from game_state import GAMESTATE

import os
os.environ['SDL_JOYSTICK_HIDAPI_PS4_RUMBLE'] = '1'



class Game():
    def __init__(self, name: str,
                 window_size: tuple[int, int] | None,
                 fps: int, sounds: dict,
                 fonts: dict, images: dict,
                 game_duration: float = 30.,
                 max_power: float = 18.,
                 th0: float = 0.,
                 save_file: str = 'meta/save.json',
                 DO_NOT_RENDER: bool = False,
                 STEP_BY_STEP: bool = False,
                 verbose: bool = False,
                 training_mode = False,):




        if fps not in [30, 60]:
            raise ValueError(f"Valor fps={fps} inválido. Apenas 30 e 60 são suportados.")

        self.fps = fps
        self.duration = game_duration
        self.MAX_POWER = max_power
        self.save_file_name =  save_file
        self.DO_NOT_RENDER = DO_NOT_RENDER
        self.VERBOSE = verbose
        self.STEP_BY_STEP = STEP_BY_STEP
        self.screen_shake_disable = True
        self.MAX_PARTICLES = 1000
        self.training_mode = training_mode
        self.th0 = th0


        pygame.init()
        pygame.mouse.set_visible(False)

        if window_size is None:
            screen_info = pygame.display.Info()
            self.screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(window_size)

        self.last_screen = copy(self.screen)

        pygame.display.set_caption(name)
        self.mixer = pygame.mixer
        self.mixer.init()

        self.joysticks = dict()
        for i in range(pygame.joystick.get_count()):
            key = f'p{i+1}'
            self.joysticks[key] = pygame.joystick.Joystick(i)
            self.joysticks[key].init()

        self.available_controllers = {
            'classic': LinearControl(),
            'ia': IAControl(),
            'keyboard (<>)': KeysControl(source=pygame.key, key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT, key_intensity=pygame.K_RALT),
            'keyboard (ad)': KeysControl(source=pygame.key, key_left=pygame.K_a, key_right=pygame.K_d, key_intensity=pygame.K_SPACE),
        }

        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.available_controllers[f'joystick ({i})'] = joystick

        self.axes = dict()
        key = 'p1'
        if key in self.joysticks.keys():
            # self.axes[key] = Joystick(source=self.joysticks[key], channel=2, dead_zone=0.05)
            self.axes[key] = LinearControl()
        else:
            # self.axes[key] = KeysControl(source=pygame.key, key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT, key_intensity=pygame.K_RALT)
            self.axes[key] = LinearControl()

        key = 'p2'
        if key in self.joysticks.keys():
            self.axes[key] = Joystick(source=self.joysticks[key], channel=2, dead_zone=0.05)
        else:
            # self.axes[key] = KeysControl(source=pygame.key, key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT, key_intensity=pygame.K_RALT)
            # self.axes[key] = KeysControl(source=pygame.key, key_left=pygame.K_a, key_right=pygame.K_d, key_intensity=pygame.K_SPACE)
            self.axes[key] = IAControl()

        # assets
        self.sounds = load_sounds(sounds)
        self.fonts = load_fonts(fonts)
        self.images = load_images(images)

        # self.popups = [
        #     Overlay(self.screen, centered_rect(self.screen, 600, 200), False, selectable=False, custom_draw=partial(centered_text, text='popup test', font=self.fonts['normal'])),
        # ]
        # for l in range(3):
        #     for c in range(3):
        #         self.popups.append(Overlay(self.screen, (80+c*90, 80+l*90, 80, 80), False,
        #                                    custom_draw=partial(centered_text, text=f'{l}{c}', font=self.fonts['small']),
        #                                    custom_callback=lambda: self.sounds['beep'].play()
        #                                    ))

        self.popups = {
            'p1': SelectInput(self, name='p1', pos=(200, 25), options=self.available_controllers.keys(), anchor='nw'),
            'p2': SelectInput(self, name='p2', pos=(200, self.screen.get_height()-25), options=self.available_controllers.keys(), anchor='sw'),
        }

        # -- reset --------------------------------------
        self.clock = None
        self.time = None
        self.paused_time = None
        self.state = None
        self.npcs = dict()
        self.players = dict()
        self.inputs = dict()
        self.particles = None
        self.bars = None
        self.marked_to_end = None
        self.perturbation = 0
        self.perturbation_ticks = 0
        # -- reset --------------------------------------
        self.reset()

        try:
            with open(self.save_file_name, 'r') as arquivo_json:
                data = json.load(arquivo_json)
            if 'best_score' in data.keys() and 'best_score_device' in data.keys():
                self.best_score = data['best_score']
                self.best_score_device = data['best_score_device']
            else:
                self.best_score = 0
                self.best_score_device = None

        except:
            self.best_score = 0
            self.best_score_device = None

        self.pre_init()
        if not self.STEP_BY_STEP:
            self.loop()

    def reset(self):
        self.perturbation = 0
        self.perturbation_ticks = 0
        self.mixer.quit()
        self.mixer = pygame.mixer
        self.mixer.init()
        self.particles = Particles(maxlen=self.MAX_PARTICLES)
        self.clock = pygame.time.Clock()
        self.time = 0.
        self.paused_time = 0.
        self.state = GAMESTATE.PRE_INIT
        self.marked_to_end = False
        y_sup = 0.35
        y_inf = 0.78
        self.npcs = {
                'target_p1': Cart(self.screen, None, (self.screen_center[0]     , int(self.screen_height*y_sup)), color=cols['p1'], width=3, size=assets.sizes['cart'], th0=math.pi, alive=False),
                'target_p2': Cart(self.screen, None, (self.screen_center[0]     , int(self.screen_height*y_inf)), color=cols['p2'], width=3, size=assets.sizes['cart'], th0=math.pi, alive=False),
            }
        dth = random.random()*.1
        th0 = self.th0 if not self.training_mode else random.uniform(0., 2*math.pi)
        x0 = 0.3 if not self.training_mode else random.uniform(0.2, 0.8)
        if not self.DO_NOT_RENDER and not self.STEP_BY_STEP:
            self.players = {
                'p1'       : Cart(self.screen, self.axes['p1'], (self.screen_width * x0, int(self.screen_height*y_sup)), color=cols['p1'], width=3, size=assets.sizes['cart'], th0=th0+dth, force_factor=self.MAX_POWER, fps=self.fps, training_mode=self.training_mode),
                'p2'       : Cart(self.screen, self.axes['p2'], (self.screen_width * x0, int(self.screen_height*y_inf)), color=cols['p2'], width=3, size=assets.sizes['cart'], th0=th0+dth, force_factor=self.MAX_POWER, fps=self.fps, training_mode=self.training_mode),
            }
        else:
            self.players = {
                'p2'       : Cart(self.screen, self.axes['p2'], (self.screen_width * x0, int(self.screen_height*y_inf)), color=cols['p2'], width=3, size=assets.sizes['cart'], th0=th0+dth, force_factor=self.MAX_POWER, fps=self.fps, training_mode=self.training_mode),
            }

        fuel_bar_width = 500
        fuel_bar_height = 14
        self.bars = {
            'timer': ProgressBar(self.screen,
                                 (self.screen_width - 150 - 30, self.screen_center[1] - 10 + 45, 150, 14),
                                 initial_value=1,
                                 on_color=cols['timer'], border_color=cols['timer'], off_color=cols['bg']),
            'p1': ProgressBar(self.screen,
                              (self.screen_width - fuel_bar_width - 30, 5 + fuel_bar_height, fuel_bar_width,fuel_bar_height),
                              initial_value=1,
                              orientation='horizontal',
                              on_color=cols['p1'], border_color=cols['p1'], off_color=cols['bg'], show_particles=True),
            'p2': ProgressBar(self.screen,
                              (self.screen_width - fuel_bar_width - 30, self.screen_height -20 - fuel_bar_height, fuel_bar_width, fuel_bar_height),
                              initial_value=1,
                              orientation='horizontal',
                              on_color=cols['p2'], border_color=cols['p2'], off_color=cols['bg'], show_particles=True),
        }

        for axis in self.axes.values():
            axis.reset()

        pygame.event.clear()
        self.clear_popups()
        self.enable_rendering(not self.DO_NOT_RENDER)
        if self.DO_NOT_RENDER and self.state == GAMESTATE.PRE_INIT:
            self.state = GAMESTATE.RUN

    def inc_time(self):
        if self.state == GAMESTATE.RUN:
            self.time += 1/self.fps  # não usar o tempo real do sistema permite acelerar simulação para treinamento
            if self.time > self.duration:
                self.timeout()
                self.bars['timer'].active = False

            self.bars['timer'].value = max((self.duration - self.time) / self.duration, 0.)

        # if self.marked_to_end:
        #     self.game_over()

        if self.all_dead() and self.state not in [GAMESTATE.PRE_INIT, GAMESTATE.TIMEOUT, GAMESTATE.GAME_OVER]:
            self.game_over()
            # self.marked_to_end = True

    def loop(self):
        while True:

            if self.state == GAMESTATE.RUN:
                self.inc_time()

            else:
                self.paused_time += 1/self.fps
                if self.state == GAMESTATE.PRE_INIT:
                    if self.paused_time > 0.5:
                        self.start()
                    else:
                        self.pre_init()

            mouse = pygame.mouse.get_pos()
            on_focus = False
            for popup in reversed(self.popups.values()):
                if not on_focus:
                    popup.collision(mouse)
            #         if popup.collision(mouse):
            #             popup.on_focus = True
                        # on_focus = True
                    # else:
                    #     popup.on_focus = False
                # else:
                #     popup.on_focus = False


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_to_file()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse = pygame.mouse.get_pos()
                        on_focus = False
                        for popup in reversed(self.popups.values()):
                            if not on_focus:
                                if popup.collision(mouse) and popup.active:
                                    popup.callback()
                                    on_focus = True


                if event.type in [pygame.JOYBUTTONDOWN, pygame.KEYDOWN]:
                    for joystick in self.joysticks.values():
                        if joystick.get_button(JOYBUTTON['start']): self.pause()
                        if joystick.get_button(JOYBUTTON['PS']): self.reset()
                        if joystick.get_button(JOYBUTTON['select']): self.popup()

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_RETURN]: self.pause()
                    if keys[pygame.K_ESCAPE]: self.reset()
                    if keys[pygame.K_k]: self.screen_shake_disable = not self.screen_shake_disable
                    if keys[pygame.K_p]: self.popup()
                    if keys[pygame.K_COMMA]: self.perturb(0.4)
                    if keys[pygame.K_PERIOD]: self.perturb(-0.4)


            if self.state == GAMESTATE.RUN:
                self.process_inputs()

            self.simulate()
            if self.state == GAMESTATE.RUN:
                self.process_feedback()

            if not self.DO_NOT_RENDER:
                self.draw()

            if not self.DO_NOT_RENDER:
                self.process_sounds()

            if not self.DO_NOT_RENDER:
                pygame.display.flip()
                self.clock.tick(self.fps)

            # m = self.players['p1'].model
            # dx = m.y[0][0] / 16
            # dth = abs(math.pi - abs(m.y[2][0])) / math.pi
            # print(dth, dx)

    def perturb(self, intensity):
        for player in self.players.values():
            player.perturb(intensity)
            self.perturbation = intensity

    def enable_rendering(self, state):
        self.DO_NOT_RENDER = not state
        if self.DO_NOT_RENDER:
            self.screen.fill(cols['bg'])
            text = self.fonts['normal'].render(f"RENDERING DISABLED", True, cols['hud'])
            self.screen.blit(text, (
            self.screen_center[0] - text_center(text)[0], self.screen_center[1] - text_center(text)[1]))

            pygame.display.flip()

    @property
    def screen_center(self) -> tuple[int, int]:
        return self.screen.get_width() // 2, self.screen.get_height() // 2

    @property
    def screen_width(self) -> int:
        return self.screen.get_width()

    @property
    def screen_height(self) -> int:
        return self.screen.get_height()

    def pre_init(self):
        if self.STEP_BY_STEP:
            self.state = GAMESTATE.RUN

    def save_to_file(self):
        save = {'best_score': self.best_score, 'best_score_device': self.best_score_device}
        with open(self.save_file_name, 'w') as json_file:
            json.dump(save, json_file)

    def game_over(self):
        self.state = GAMESTATE.GAME_OVER
        for player in self.players.values():
            player.alive = False
        self.save_score()

    def timeout(self):
        self.state = GAMESTATE.TIMEOUT
        for player in self.players.values():
            player.alive = False
        if not self.DO_NOT_RENDER:
            self.sounds['whistle'].play()
        self.save_score()

    def start(self):
        self.state = GAMESTATE.RUN
        for player in self.players.values():
            player.alive = True
        if not self.DO_NOT_RENDER:
            self.sounds['beep'].play()
            self.sounds['jet_r'].play(loops=-1)
            self.sounds['jet_l'].play(loops=-1)

    def clear_popups(self):
        for popup in self.popups.values():
            popup.active = False
        pygame.mouse.set_visible(False)




    def popup(self):

        for popup in self.popups.values():
            popup.active = not popup.active


        any_active = False
        for popup in self.popups.values():
            any_active |= popup.active

        if self.state == GAMESTATE.RUN or (self.state == GAMESTATE.PAUSED and not any_active):
            self.pause(any_active)
        pygame.mouse.set_visible(any_active)




    def pause(self, new_state = None):
        if new_state is None:
            new_state = False if self.state == GAMESTATE.PAUSED else True

        if self.state == GAMESTATE.RUN and new_state:
            self.state = GAMESTATE.PAUSED
        elif self.state == GAMESTATE.PAUSED and not new_state:
            self.state = GAMESTATE.RUN
            self.clear_popups()
        else:
            self.reset()

        for player in self.players.values():
            player.paused = True if self.state == GAMESTATE.PAUSED else False

    def save_score(self):
        for key, player in self.players.items():
            if player.score > self.best_score:
                self.best_score = player.score
                self.best_score_device = player.input.device_type

        if self.VERBOSE:
            print(f'{self.state} (', end='')
            for key, player in self.players.items():
                if not key.startswith('target_'):
                    print(f'{key}: {player.score}', end=', ')
            print('\b\b)')


    def process_inputs(self):
        for key, axis in self.axes.items():
            axis.update(self.players[key])
        for key, player in self.players.items():
            self.inputs[key] = self.axes[key].value * self.MAX_POWER

    def ia_step(self, input_key_value: dict) -> bool:   # ex: {'p2': -0.78}
        """
        Para uso exclusivo do treinamento da IA
        """
        for key, value in input_key_value.items():
            self.axes[key].value = value
            self.inputs[key] = self.axes[key].value * self.MAX_POWER

        if self.state == GAMESTATE.RUN:
            self.inc_time()
            self.simulate()


        if not self.DO_NOT_RENDER:
            self.draw()
            pygame.display.flip()
            # self.clock.tick(self.fps)

        all_dead = True
        for key, value in input_key_value.items():
            all_dead = all_dead and not self.players[key].alive

        all_empy = True
        for key, value in input_key_value.items():
            all_empy = all_empy and self.players[key].fuel == 0

        return all_dead or all_empy

    def simulate(self):
        f = 60 / self.fps
        time_to_collect = int(10/f)
        collect_shift = int(0/f)
        balls_emmit = random.randint(int(10*f), int(30*f))

        play_sound_for_collected_score = False
        for key, player in self.players.items():
            collect_shift += time_to_collect // 2
            player.step()
            self.bars[key].value = player.fuel
            if player.alive and self.bars[key].value < 0.2:
                self.bars[key].on_color = cols['low_fuel']
                self.bars[key].border_color = cols['low_fuel']
                # self.bars[key].border_width = 2
            if not player.alive and player.ticks_since_death == 0 and not self.DO_NOT_RENDER:
                self.sounds['death'].play()
            if not self.DO_NOT_RENDER:
                uncollected_score = player.uncollected_score
                if player.alive and (player.ticks+collect_shift) % time_to_collect == 0 and uncollected_score > 0:
                    collected = player.collect_score()
                    vel_y = 90
                    color = cols['tiny_collect'] if collected <= f * time_to_collect * player.reward_pole_on_target_short \
                        else cols['small_collect'] if collected <= f * time_to_collect * player.reward_pole_on_target_long\
                        else cols['big_collect'] if collected <= f * time_to_collect * (player.reward_cart_on_target_short+player.reward_pole_on_target_long) \
                        else cols['huge_collect']
                    color = lerp_v3(color, (random.randint(5,250), random.randint(5,250), random.randint(5,250)), random.random()*0.1 + 0.1 )
                    self.particles.append(
                        TextParticle(self.screen,
                                     color,
                                     f'+{collected}',
                                     self.fonts['particles'],
                                     pos=player.pole_tip_pos,
                                     vel=((random.random() - 0.5) * 200, random.random() * vel_y + vel_y),
                                     dt=1/self.fps,
                                     lifetime=random.uniform(0.5,1.5),
                                     linear_factor=1000)
                    )
                    for _ in range(balls_emmit):
                        self.particles.append(
                            BallParticle(self.screen,
                                         (random.randint(5,250), random.randint(5,250), random.randint(5,250)),
                                         1,
                                         pos=player.pole_tip_pos,
                                         vel=((random.random() - 0.5) * 300, random.random() * vel_y + vel_y),
                                         dt=1 / self.fps,
                                         lifetime=random.uniform(0.5, 1.5),
                                         linear_factor=1000)
                        )
                    play_sound_for_collected_score = True

        if not self.DO_NOT_RENDER and not self.training_mode:
            if play_sound_for_collected_score:
                self.sounds['coin'].play()

            if self.state != GAMESTATE.PAUSED:
                self.particles.step()
            # self.particles.garbage_collect()

    def all_dead(self) -> bool:
        all_dead = True
        for player in self.players.values():
            all_dead = all_dead and not player.alive
        return all_dead


    def process_sounds(self):
        r_volume = abs(self.players['p1'].input.value) if self.players['p1'].alive else 0.
        l_volume = abs(self.players['p2'].input.value) if self.players['p2'].alive else 0.

        self.sounds['jet_r'].set_volume(r_volume if self.state == GAMESTATE.RUN else 0.)
        self.sounds['jet_l'].set_volume(l_volume if self.state == GAMESTATE.RUN else 0.)

    def process_feedback(self):
        if self.state == GAMESTATE.RUN:
            for player in self.players.values():
                player.feedback()

    def draw(self):
        if self.state != GAMESTATE.PAUSED:
            self.screen.fill(cols['bg'])
            for npc in self.npcs.values():
                npc.draw()

            for player in self.players.values():
                player.draw()

            if self.perturbation != 0:
                for player in self.players.values():
                    if player.alive:
                        direction = (abs(player.model.y[2][0]) < math.pi/2) ^ (self.perturbation > 0)
                        w, h = 80, 50
                        x, y = player.pole_tip_pos
                        if not direction:
                            x -= w
                        y -= h//2 - 10
                        dedo = pygame.transform.smoothscale(
                            pygame.transform.flip(self.images['dedo'], direction, False),(w, h))
                        self.screen.blit(dedo, (x, y, w, h))
                self.perturbation_ticks += 1
                if self.perturbation_ticks * 1/self.fps > 0.2:
                    self.perturbation = 0
                    self.perturbation_ticks = 0


            self.particles.draw()

            dcols = { key: cols[key] if self.players[key].alive else lerp_v3(cols[key], (60, 60, 50), 0.85) for key in self.players.keys()}

            for bar in self.bars.values():
                bar.draw()

            fps = self.clock.get_fps()
            text_fps = self.fonts['small'].render(f"{fps:.1f}", True, cols['fps'])
            text_fps_label = self.fonts['small'].render(f"FPS", True, cols['fps'])
            text_timer = self.fonts['normal'].render(f"{max(self.duration-self.time, 0.0):.1f}", True, cols['timer'])
            text_timer_label = self.fonts['small'].render(f"TIMER", True, cols['timer'])
            if 'p1' in self.players.keys():
                text_p1 = self.fonts['medium'].render(f"{self.players['p1'].score:>10d}", True, dcols['p1'])
                text_p1_label2 = self.fonts['tiny'].render(f"{self.axes['p1'].device_type}", True, dcols['p1'])
            else:
                dcols['p1'] = (60, 60, 50)
                text_p1 = self.fonts['medium'].render(f"{0:>10d}", True, dcols['p1'])
                text_p1_label2 = self.fonts['small'].render(f"-", True, dcols['p1'])


            for key in self.players.keys():
                if not self.players[key].alive:
                    self.bars[key].on_color = dcols[key]
                    self.bars[key].border_color = dcols[key]

            text_p2 = self.fonts['medium'].render(f"{self.players['p2'].score:>10d}", True, dcols['p2'])
            text_best = self.fonts['normal'].render(f"{self.best_score:<10d}", True, cols['best_score'])
            text_p1_label = self.fonts['small'].render(f"P1 SCORE", True, dcols['p1'])
            text_p2_label = self.fonts['small'].render(f"P2 SCORE", True, dcols['p2'])
            text_p2_label2 = self.fonts['tiny'].render(f"{self.axes['p2'].device_type}", True, dcols['p2'])
            text_best_label = self.fonts['small'].render(f"BEST SCORE", True, cols['best_score'])
            text_best_device = self.fonts['tiny'].render(f"{self.best_score_device}", True, cols['best_score'])
            self.screen.blit(text_fps, (30, 60))
            self.screen.blit(text_fps_label, (30, 30))
            self.screen.blit(text_p1, (self.screen_width - text_p1.get_width() - 30, 40))
            self.screen.blit(text_p2, (self.screen_width - text_p2.get_width() - 30, self.screen_height - 140))
            self.screen.blit(text_best, ( 30, self.screen_center[1] - text_center(text_best)[1]))
            self.screen.blit(text_timer, (self.screen_width - text_timer.get_width() - 30, self.screen_center[1] - text_center(text_timer)[1]))
            self.screen.blit(text_timer_label, (self.screen_width - text_timer_label.get_width()-30, self.screen_center[1] - text_center(text_timer_label)[1]-50))
            self.screen.blit(text_p1_label, (self.screen_width - text_p1_label.get_width() - 30, 150))
            self.screen.blit(text_p1_label2, (self.screen_width - text_p1_label2.get_width() - 30, 150+30))
            self.screen.blit(text_p2_label, (self.screen_width - text_p2_label.get_width() - 30, self.screen_height - 170))
            self.screen.blit(text_p2_label2,(self.screen_width - text_p2_label2.get_width() - 30, self.screen_height - 170 -20))
            self.screen.blit(text_best_label, (30, self.screen_center[1] - text_center(text_best_label)[1]-50))
            self.screen.blit(text_best_device, (30, self.screen_center[1] - text_center(text_best_device)[1]+40))

            if self.state == GAMESTATE.PRE_INIT:
                text = self.fonts['big'].render(f"START", True, cols['hud'])
                self.screen.blit(text, (self.screen_center[0] - text_center(text)[0], self.screen_center[1] - text_center(text)[1]))

            if self.state == GAMESTATE.GAME_OVER:
                text = self.fonts['big'].render(f"GAME OVER", True, cols['hud'])
                self.screen.blit(text, (self.screen_center[0] - text_center(text)[0], self.screen_center[1] - text_center(text)[1]))

            if self.state == GAMESTATE.TIMEOUT:
                text = self.fonts['big'].render(f"TIMEOUT", True, cols['hud'])
                self.screen.blit(text, (self.screen_center[0] - text_center(text)[0], self.screen_center[1] - text_center(text)[1]))


            self.shake_screen()
            # self.last_screen = copy(self.screen)

        if self.state == GAMESTATE.PAUSED:
            screen = copy(self.last_screen)
            self.screen.fill(cols['bg'])
            self.screen.blit(screen, (0, 0))

            text = self.fonts['big'].render(f"PAUSED", True, cols['hud'])
            self.screen.blit(text, (self.screen_center[0] - text.get_width() // 2, self.screen_center[1] - text.get_height() // 2))

        for popup in self.popups.values():
            popup.draw()


    def shake_screen(self):
        if self.screen_shake_disable:# and self.state == GAMESTATE.RUN and not self.all_dead():
                shake_abs = 0.
                shake_dir = 0.
                for player in self.players.values():
                    if player.alive:
                        shake_dir += player.input.value
                        shake_abs += abs(player.input.value)*(random.random()-0.5)
                    elif player.ticks_since_death < 0.2 * self.fps:
                        shake_dir += 10 * (-1 if player.pos[0] < self.screen_center[0] else 1)
                        shake_abs += 10 * (random.random()-0.5)
                shake_x = shake_dir / len(self.players) * 9
                shake_y = shake_abs / len(self.players) * 9
                self.last_screen = copy(self.screen)
                self.screen.fill(cols['bg'])
                self.screen.blit(self.last_screen, (random.random()*shake_x, random.random()*shake_y))





class SelectInput:
    def __init__(self, game, name, pos, options, anchor='nw'):
        self.name = name

        N_BUTTONS = len(options)
        w = 300
        h = 60
        pad = 10

        if anchor.lower() == 'nw':
            x0, y0 = pos
        elif anchor.lower() == 'sw':
            x0 = pos[0]
            y0 = pos[1] - N_BUTTONS * h - (N_BUTTONS-1) * pad
        else:
            raise ValueError(f"'anchor' deve ser 'nw' ou 'sw', mas {anchor} foi fornecido.")

        self.callback = self.default_callback
        surface=game.screen
        self.buttons = dict()
        for i, key in enumerate(options):
            self.buttons[key] = (Overlay(surface, (x0, y0 + i * (h+pad), w, h), False, selectable=True, custom_draw=partial(centered_text, text=key, font=game.fonts['small'])))

    def default_callback(self):
        for button in self.buttons.values():
            if button.on_focus:
                button.selected = True
            else:
                button.selected = False



    @property
    def active(self):
        active = False
        for button in self.buttons.values():
            active |= button.active
        return active

    @active.setter
    def active(self, value):
        for button in self.buttons.values():
            button.active = value

    @property
    def on_focus(self):
        on_focus = False
        for button in self.buttons.values():
            on_focus |= button.on_focus
        return on_focus

    # @on_focus.setter
    # def on_focus(self, value):
    #     for button in self.buttons.values():
    #         button.on_focus = value

    def collision(self, point):
        collision = False
        for button in self.buttons.values():
            button.on_focus = button.collision(point)
            collision |= self.on_focus
        return collision

    def draw(self):
        for button in self.buttons.values():
            button.draw()













def load_sounds(description: dict) -> dict:
    sounds = {}
    for k, v in description.items():
        sound = pygame.mixer.Sound(v[0])
        sound.set_volume(v[1])
        sounds[k] = sound
    return sounds


def load_fonts(description: dict) -> dict:
    return {k: pygame.font.SysFont(*v) for k, v in description.items()}


def load_images(description: dict) -> dict:
    return {k: pygame.image.load(v) for k, v in description.items()}


def text_center(text) -> tuple[int, int]:
    return text.get_width() // 2, text.get_height() // 2


def centered_text(surface, rect, text, font):
    text_popup = font.render(text, True, (120, 120, 120))
    tw, th = text_popup.get_width(), text_popup.get_height()
    cx, cy = rect[0]+rect[2]//2, rect[1]+rect[3]//2
    surface.blit(text_popup, (cx-tw//2, cy-th//2))


