import pygame
from canvas import Canvas
from inputs import Joystick, JOYBUTTON
import math
from canvas import rotate_vec2s
from random import random, randint, uniform, choice
from particles import BallParticle, Particles, TextParticle
from pygame import Vector2
from lerp import lerp, lerp_vec2, lerp_vec3
from basescreen import BaseScreen
from mouse import MouseButton, MouseScroll, Mouse
from utils import remap, ColorsDiscIterator, outer_rect
from scope import Scope
from popup import PopUp, PopUpText
from pathlib import Path
from utils import points_from_rect, RotateMatrix
from image import Image


class Demo(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rel_path = Path(__file__).parent
        self.assets_path = self.rel_path / 'assets'


        self.mouse.left.press_callback = self.left_click
        self.mouse.left.release_callback = self.left_release
        self.mouse.right.press_callback = self.right_click
        self.mouse.right.release_callback = self.right_release
        self.mouse.scroll.up_callback = self.scroll_up
        self.mouse.scroll.down_callback = self.scroll_down

        self.canvases = {
            'rocket': Canvas(self.canvas_size, bg_color=self.cols['bg'], fonts=self.fonts, draw_fun=self.draw_rocket, shortcut=pygame.K_1),
            'menu': Canvas(self.canvas_size, bg_color=self.cols['bg'], fonts=self.fonts, draw_fun=self.draw_menu, shortcut=pygame.K_2),
            'test'  : Canvas(self.canvas_size, bg_color=self.cols['bg'], fonts=self.fonts, draw_fun =self.draw_color_wheel, shortcut=pygame.K_3),
        }

        self.event_loop_callback = self.process_user_input_event
        self.canvases['rocket'].got_focus_callback = self.rocket_got_focus_callback

        self.cols['focus'] = (255, 255, 0)
        self.cols['scope'] = (55, 255, 200)
        # flags = pygame.HWSURFACE | pygame.SRCALPHA
        self.scopes = {
            'ch1': Scope(self.canvases['rocket'], name='frame time', legend=('active', 'total'),   fps=self.fps, alpha=200, color=self.cols['scope'], focus_color=self.cols['focus'], pos=(0.5, 0.5), size=(400, 250), maxlen=400),
            'ch2': Scope(self.canvases['rocket'], name='inputs',     legend=('throttle', 'steer'), fps=self.fps, alpha=200, color=self.cols['scope'], y_scale=(0.9, 1.7, 1.0), focus_color=self.cols['focus'], pos=(0.5, -0.1), size=(400, 250), maxlen=400),
        }

        self.hue_ncols_exemple = 20
        self.hue_shift_exemple = 0
        self.hue_radius_exemple = 0.55

        self.particle_en = True

        self.steer = None
        self.throttle = None
        self.throttle_min = 0.1
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.steer = Joystick(joystick, 2)
            self.throttle = Joystick(joystick, 4, normalization=lambda x: (x+1)/2)

        self.particles = Particles(100)
        self.text_particles = Particles(300)
        self.particles_fonts = [
            pygame.font.SysFont('Times', 22),
            pygame.font.SysFont('Times', 36),
            pygame.font.SysFont('Times', 54),
            pygame.font.SysFont('Times', 68),
        ]

        self.letters = [chr(i) for i in range(945, 970) if i != 962]

        self.extra_help = [
            f'────────────────────────',
            f' F7: enable/disable particles',
            f' F8: show/hide external rects',
            f'  1: tab rocket example',
            f'  2: tab pause example',
            f'  3: tab hue dic example',
            f'  v: ',
            f'  b: ',
            f'  +: ',
            f'  -: ',
            f'  *: ',
            f'  /: ',
            f'  r: ',
            f'  t: ',
            f'  g: ',
        ]

        self.sounds['beep'] = self.load_sound(self.assets_path / 'beep.wav', volume=0.6)
        self.sounds['jet'] = self.load_sound(self.assets_path / 'jet.wav', volume=0.0)
        self.sounds['jet'].play(loops=-1)

        self.images['jet'] = pygame.transform.smoothscale_by(pygame.transform.rotate(self.load_image(self.assets_path / 'jet.png'), 90), 0.5)

        self.show_external_rects = False

        self.pre_draw_callback = self.pre_draw


    def pre_draw(self):
        if self.active_canvas_key != 'rocket':
            self.sounds['jet'].set_volume(0)




    def left_release(self, button: MouseButton):
        self.sounds['beep'].play()

    def left_click(self, button: MouseButton):
        key = 'left_click'
        if key in self.popups.keys():
            del self.popups[key]

    def right_click(self, button: MouseButton):
        pos = self.mouse_world_pos

        key = 'left_click'
        text = f'{pos[0]:.2f}, {pos[1]:.2f}'
        if key in self.popups.keys():
            self.popups[key].text = text
            self.popups[key].pos = pos
        else:
            self.popups[key] = PopUpText(self.canvases['rocket'], alpha=180, pos=pos,
                                         color=(255, 255, 0), text=text, font=self.fonts['info'],
                                         visible=True, border_radius=0, border_width=1)



    def right_release(self, button: MouseButton):
        pass

    def scroll_up(self, scroll: MouseScroll):
        if scroll.up_keys[pygame.K_LCTRL]:
            self.active_canvas.scale /= 1.1

    def scroll_down(self, scroll: MouseScroll):
        if scroll.down_keys[pygame.K_LCTRL]:
            self.active_canvas.scale *= 1.1

    def process_user_input_event(self, event):
        if self.mouse.right.dragging and self.mouse.right.drag_keys[pygame.K_LCTRL]:
            self.active_canvas.bias = (int(self.active_canvas.bias[0] + self.mouse.right.drag_delta[0]), int(self.active_canvas.bias[1] + self.mouse.right.drag_delta[1]))
            self.mouse.right.clear_drag_delta()

        for scope in self.scopes.values():
            if self.mouse.left.dragging and scope.focus:
                canvas = self.active_canvas
                delta = canvas.screen_to_world_delta_v2(remap(self.mouse.left.drag_delta, self.window, canvas))
                # print(self.mouse.left.drag_delta, '->', remap(self.mouse.left.drag_delta, self.window, canvas), '->', canvas.screen_to_world_delta_v2(remap(self.mouse.left.drag_delta, self.window, canvas)))
                scope.pos = Vector2(scope.pos) + delta
                self.mouse.left.clear_drag_delta()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F8:
                self.show_external_rects = not self.show_external_rects
            elif event.key == pygame.K_F7:
                self.particle_en = not self.particle_en
            if event.key == pygame.K_LEFT:
                self.hue_radius_exemple -= 0.05
            elif event.key == pygame.K_RIGHT:
                self.hue_radius_exemple += 0.05
            elif event.key == pygame.K_UP:
                self.hue_ncols_exemple += 1
            elif event.key == pygame.K_DOWN:
                if self.hue_ncols_exemple > 2:
                    self.hue_ncols_exemple -= 1
            elif event.key == pygame.K_r:
                self.scopes['ch1'].clear()
                self.scopes['ch1'].rolling = not self.scopes['ch1'].rolling
            elif event.key == pygame.K_v:
                self.scopes['ch1'].visible = not self.scopes['ch1'].visible
            elif event.key == pygame.K_KP_MULTIPLY:
                self.scopes['ch1'].x_scale *= 2
            elif event.key == pygame.K_KP_DIVIDE:
                self.scopes['ch1'].x_scale /= 2

            elif event.key == pygame.K_t:
                self.scopes['ch2'].clear()
                self.scopes['ch2'].rolling = not self.scopes['ch2'].rolling
            elif event.key == pygame.K_b:
                self.scopes['ch2'].visible = not self.scopes['ch2'].visible
            elif event.key == pygame.K_KP_PLUS:
                self.scopes['ch2'].x_scale *= 2
            elif event.key == pygame.K_KP_MINUS:
                self.scopes['ch2'].x_scale /= 2



    def draw_color_wheel(self, canvas: Canvas):
        width = 1
        M = 10
        grid_color = (100, 100, 100)
        for m in range(4 * M + 1):
            canvas.draw_line(grid_color, (-2 + m / M, -1), (-2 + m / M, 1), width=width)
        for m in range(2 * M + 1):
            canvas.draw_line(grid_color, (-2, -1 + m / M), (2, -1 + m / M), width=width)

        radius = 0.12
        for n in range(11):
            canvas.draw_circle((180, 255, 180), (+0, +0), radius * n, width=1)
        canvas.draw_circle((255, 0, 0), (-1, -1), radius)
        canvas.draw_circle((0, 255, 0), (-1, +1), radius)
        canvas.draw_circle((0, 0, 255), (+1, +1), radius)
        canvas.draw_circle((255, 255, 0), (+1, -1), radius)

        self.hue_shift_exemple += 3 / 360
        r = radius
        cols_iter = ColorsDiscIterator(self.hue_ncols_exemple, self.hue_shift_exemple, 1.0, 0.9)
        for i, col in enumerate(cols_iter):
            ang = i * 2 * math.pi / len(cols_iter)
            canvas.draw_circle(col, (self.hue_radius_exemple * math.cos(ang), self.hue_radius_exemple * math.sin(ang)), r)

        canvas.draw_text(color=(255, 255, 255), font=self.fonts['big'], text='Use as setas!', pos=(0, 0), anchor='center')
        canvas.draw_text(color=(30, 30, 30), font=self.fonts['small'], text='-1, +1', pos=(-1, +1), anchor='midtop')
        canvas.draw_text(color=(30, 30, 30), font=self.fonts['small'], text='+1, +1', pos=(+1, +1), anchor='midtop')
        canvas.draw_text(color=(30, 30, 30), font=self.fonts['small'], text='-1, -1', pos=(-1, -1), anchor='midbottom')
        canvas.draw_text(color=(30, 30, 30), font=self.fonts['small'], text='+1, -1', pos=(+1, -1), anchor='midbottom')

    def draw_menu(self, canvas: Canvas):
        prtsc = self.canvases[self.last_active_canvas_key].copy()
        prtsc.set_alpha(128)
        offset = (canvas.xmin, canvas.ymax)
        canvas.blit(prtsc, offset)

        blue = (30, 60, 255)
        red = (255, 30, 60)
        yellow = (255, 200, 30)
        for n in range(N := 400):
            color = lerp_vec3(blue, red, n / N)
            th = math.fmod(self.t * 2, 2 * math.pi) + 3 * math.pi * n / N
            h = math.cos(self.t / 2) + 2
            r = math.cos(h * th) * 0.5
            canvas.draw_circle(color, (r * math.cos(th), r * math.sin(th)), .08)
        canvas.draw_text(yellow, self.fonts['huge'], f'PAUSED!', (0, 0))

    def rocket_got_focus_callback(self, canvas: Canvas):
        for key, scope in self.scopes.items():
            scope.clear()

    def draw_rocket(self, canvas: Canvas):

        self.extra_info = [
        ]

        if self.steer is not None:
            self.steer.update()
            self.throttle.update()
            angle = self.steer.value * math.pi / 6
            throttle = max(self.throttle_min, self.throttle.value)
        else:
            angle = 0.0
            throttle = self.throttle_min

        self.sounds['jet'].set_volume(throttle)

        if self.particle_en:
            for _ in range(int(2*60/self.fps)):
                font_index = randint(0, len(self.particles_fonts)-1)
                self.text_particles.append(
                    TextParticle(canvas,
                                 color=lerp_vec3((90, 250, 90), (30, 90, 30), random()),
                                 text=choice(self.letters),
                                 font=self.particles_fonts[font_index],
                                 pos=(uniform(-1.8, 1.8), 1.05),
                                 vel=(0, -0.8-font_index*.2), dt=1/self.fps, g=0, lifetime=-1,
                                 ))
        self.text_particles.step_and_draw()




        # jet : todo: refacto 'função rotate_image_around(img, angle, center)'
        bias_throttle = (throttle + 0.25)
        img: pygame.Surface = pygame.transform.scale_by(self.images['jet'], bias_throttle*uniform(0.8, 1.2)*canvas.relative_scale)

        pivot = canvas.screen_to_world_v2(canvas.center_pixels() + (0, 30 * canvas.relative_scale))

        #fixme: Image(canvas, img).rotate_rad_around(angle, pivot).blit()

        img_screen_rect = img.get_rect()
        screen_pivot = canvas.center_pixels() + (0, 30*canvas.relative_scale)
        img_screen_rect.midtop = screen_pivot
        img_rect = canvas.screen_to_world_rect(img_screen_rect)

        pivot = canvas.screen_to_world_v2(screen_pivot)

        points = points_from_rect(img_rect)

        rot_points = RotateMatrix(angle) * points

        ext_rect = outer_rect(rot_points)
        ext_points = points_from_rect(ext_rect)


        canvas.blit(pygame.transform.rotate(img, math.degrees(angle)), ext_rect)

        # jet particles
        emmit_l = Vector2(-0.05*bias_throttle, -0.04).rotate_rad(angle)
        emmit_r = Vector2(0.05*bias_throttle, -0.04).rotate_rad(angle)
        if self.particle_en:
            for _ in range(int(randint(round(8 * bias_throttle), round(10 * bias_throttle)) * 60 / self.fps)):
                vel = Vector2(uniform(-0.2, .07), uniform(-5, -8)) * bias_throttle
                self.particles.append(BallParticle(canvas,
                                                   lerp_vec3(lerp_vec3((255, 60, 0), (200, 200, 60), random()),
                                                             (255, 255, 255), random() * 0.5),
                                                   uniform(.003, .006),
                                                   pos=lerp_vec2(emmit_l, emmit_r, random()),
                                                   vel=vel.rotate_rad(angle),
                                                   dt=1 / self.fps, lifetime=uniform(.1, .15), g=0))
            self.particles.step_and_draw()


        # rocket
        canvas.draw_polygon((90, 90, 100),
                            rotate_vec2s(((0.06, 0.05), (0.08, -0.1), (-0.08, -0.1), (-0.06, 0.05)), angle))  # angle
        canvas.draw_polygon((120, 120, 130),
                            ((0.1, 0.0), (0.1, 0.6), (0.06, 0.75), (0.0, 0.8), (-0.06, 0.75), (-0.1, 0.6), (-0.1, 0.0)))

        canvas.draw_circle((255, 200, 60), (0, 0.25), 0.05, width=0, draw_top_left=True, draw_bottom_right=True)
        canvas.draw_circle((0, 0, 0), (0, 0.25), 0.05, width=0, draw_top_right=True, draw_bottom_left=True)


        # extrenal rects for debug
        if self.show_external_rects:
            canvas.draw_polygon((0, 255, 255), points, 2)
            canvas.draw_circle((0, 255, 255), points[0], .015)
            canvas.draw_polygon((255, 0, 255), rot_points, 2)
            canvas.draw_circle((255, 0, 255), rot_points[0], .015)
            canvas.draw_polygon((255, 0, 0), ext_points, 2)
            canvas.draw_circle((255, 0, 0), ext_points[0], .015)



        # scope
        x = self.t
        total_frame_time = 1/self.real_fps if self.real_fps != 0 else 0
        y = {
            'ch1': (self.last_active_frame_time * self.fps - 1, total_frame_time * self.fps - 1), #(self.mm_frame_time.value * self.fps - 1, self.last_active_frame_time * self.fps - 1),
            'ch2': (throttle, angle),
        }

        def another_in_focus(self_key):
            for ikey, iscope in self.scopes.items():
                if ikey != self_key and iscope.focus:
                    return True
            return False

        for key, scope in self.scopes.items():
            scope.append(x, y[key])
            scope.focus = scope.collision(self.mouse_world_pos) and not another_in_focus(key)
            scope.draw()
            scope.blit_to_main()



if __name__ == '__main__':
    Demo(fps=60)