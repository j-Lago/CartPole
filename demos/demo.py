import gamebase as gb
import pygame
from pygame import Vector2
import math
from random import random, randint, uniform, choice
from pathlib import Path



class Demo(gb.BaseScreen):
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

        self.canvas = gb.Canvas(self.canvas_size, bg_color=self.cols['bg'], fonts=self.fonts, draw_fun=self.draw_rocket)

        self.event_loop_callback = self.process_user_input_event

        self.cols['focus'] = (255, 255, 0)
        self.cols['scope'] = (55, 255, 200)
        self.scopes = {
            'ch1': gb.Scope(self.canvas, name='frame time', legend=('active', 'total'), fps=self.clock.fps, alpha=200, color=self.cols['scope'], focus_color=self.cols['focus'], pos=(0.5, 0.5), size=(400, 250), maxlen=400),
            'ch2': gb.Scope(self.canvas, name='inputs', legend=('throttle', 'steer'), fps=self.clock.fps, alpha=200, color=self.cols['scope'], y_scale=(0.9, 1.7, 1.0), focus_color=self.cols['focus'], pos=(0.5, -0.1), size=(400, 250), maxlen=400),
        }


        self.particle_en = True
        self.steer = None
        self.throttle = None
        self.throttle_min = 0.1
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.steer = gb.Joystick(joystick, 2)
            self.throttle = gb.Joystick(joystick, 4, normalization=lambda x: (x+1)/2)

        self.particles = gb.Particles(100)
        self.text_particles = gb.Particles(300)
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
            f' F6: show/hide external rects',
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
        self.show_outer_rects = False
        self.pre_draw_callback = self.pre_draw


    def pre_draw(self):
        self.sounds['jet'].set_volume(0)




    def left_release(self, button: gb.MouseButton):
        self.sounds['beep'].play()

    def left_click(self, button: gb.MouseButton):
        key = 'left_click'
        if key in self.popups.keys():
            del self.popups[key]

    def right_click(self, button: gb.MouseButton):
        pos = self.mouse_world_pos

        key = 'left_click'
        text = f'{pos[0]:.2f}, {pos[1]:.2f}'
        if key in self.popups.keys():
            self.popups[key].text = text
            self.popups[key]._pos = pos
        else:
            self.popups[key] = gb.PopUpText(self.canvases['rocket'], alpha=180, pos=pos,
                                         color=(255, 255, 0), text=text, font=self.fonts['info'],
                                         visible=True, border_radius=0, border_width=1)



    def right_release(self, button: gb.MouseButton):
        pass

    def scroll_up(self, scroll: gb.MouseScroll):
        if scroll.up_keys[pygame.K_LCTRL]:
            self.canvas.scale /= 1.1

    def scroll_down(self, scroll: gb.MouseScroll):
        if scroll.down_keys[pygame.K_LCTRL]:
            self.canvas.scale *= 1.1

    def process_user_input_event(self, event):
        if self.mouse.right.dragging and self.mouse.right.drag_keys[pygame.K_LCTRL]:
            self.canvas.bias = (int(self.canvas.bias[0] + self.mouse.right.drag_delta[0]), int(self.canvas.bias[1] + self.mouse.right.drag_delta[1]))
            self.mouse.right.clear_drag_delta()

        for scope in self.scopes.values():
            if self.mouse.left.dragging and scope.focus:
                canvas = self.canvas
                delta = canvas.screen_to_world_delta_v2(gb.remap(self.mouse.left.drag_delta, self.window, canvas))
                # print(self.mouse.left.drag_delta, '->', remap(self.mouse.left.drag_delta, self.window, canvas), '->', canvas.screen_to_world_delta_v2(remap(self.mouse.left.drag_delta, self.window, canvas)))
                scope.pos = Vector2(scope.pos) + delta
                self.mouse.left.clear_drag_delta()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F6:
                self.show_outer_rects = not self.show_outer_rects
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



    # def draw_color_wheel(self, canvas: gb.Canvas):
    #     width = 1
    #     M = 10
    #     grid_color = (100, 100, 100)
    #     for m in range(4 * M + 1):
    #         canvas.draw_line(grid_color, (-2 + m / M, -1), (-2 + m / M, 1), width=width)
    #     for m in range(2 * M + 1):
    #         canvas.draw_line(grid_color, (-2, -1 + m / M), (2, -1 + m / M), width=width)
    #
    #     radius = 0.12
    #     for n in range(11):
    #         canvas.draw_circle((180, 255, 180), (+0, +0), radius * n, width=1)
    #     canvas.draw_circle((255, 0, 0), (-1, -1), radius)
    #     canvas.draw_circle((0, 255, 0), (-1, +1), radius)
    #     canvas.draw_circle((0, 0, 255), (+1, +1), radius)
    #     canvas.draw_circle((255, 255, 0), (+1, -1), radius)
    #
    #     self.hue_shift_exemple += 3 / 360
    #     r = radius
    #     cols_iter = gb.ColorsDiscIterator(self.hue_ncols_exemple, self.hue_shift_exemple, 1.0, 0.9)
    #     for i, col in enumerate(cols_iter):
    #         ang = i * 2 * math.pi / len(cols_iter)
    #         canvas.draw_circle(col, (self.hue_radius_exemple * math.cos(ang), self.hue_radius_exemple * math.sin(ang)), r)
    #
    #     canvas.draw_text(color=(255, 255, 255), font=self.fonts['big'], text='Use as setas!', pos=(0, 0), anchor='center')
    #     canvas.draw_text(color=(30, 30, 30), font=self.fonts['small'], text='-1, +1', pos=(-1, +1), anchor='midtop')
    #     canvas.draw_text(color=(30, 30, 30), font=self.fonts['small'], text='+1, +1', pos=(+1, +1), anchor='midtop')
    #     canvas.draw_text(color=(30, 30, 30), font=self.fonts['small'], text='-1, -1', pos=(-1, -1), anchor='midbottom')
    #     canvas.draw_text(color=(30, 30, 30), font=self.fonts['small'], text='+1, -1', pos=(+1, -1), anchor='midbottom')


    def rocket_got_focus_callback(self, canvas: gb.Canvas):
        for key, scope in self.scopes.items():
            scope.clear()

    def draw_rocket(self, canvas: gb.Canvas):

        self.extra_info = [
        ]

        if self.steer is not None:
            self.steer.update()
            self.throttle.update()
            angle = self.steer._value * math.pi / 6
            throttle = max(self.throttle_min, self.throttle._value)
        else:
            angle = 0.0
            throttle = self.throttle_min

        self.sounds['jet'].set_volume(throttle)

        if self.particle_en:
            for _ in range(int(2*60/self.clock.fps)):
                font_index = randint(0, len(self.particles_fonts)-1)
                self.text_particles.append(
                    gb.TextParticle(canvas,
                                 color=gb.lerp_vec3((90, 250, 90), (30, 90, 30), random()),
                                 text=choice(self.letters),
                                 font=self.particles_fonts[font_index],
                                 pos=(uniform(-1.8, 1.8), 1.05),
                                 vel=(0, -0.8-font_index*.2), dt=1/self.clock.fps, g=0, lifetime=-1,
                                 ))
        self.text_particles.step_and_draw()




        # jet : todo: refacto 'função rotate_image_around(img, angle, center)'

        # cimg = Image(canvas, self.images['jet'])
        # cimg.blit()


        bias_throttle = (throttle + 0.25)
        temp: pygame.Surface = pygame.transform.scale_by(self.images['jet'], bias_throttle*uniform(0.8, 1.2)*canvas.relative_scale)

        # canvas.blit(temp, (0.5, -0.5))

        img = gb.Image(canvas, temp)
        img.midtop = Vector2(0, 0)
        img = img.rotate_rad_around(angle, Vector2(0, -0.06))
        img.blit()


        # pivot = canvas.screen_to_world_v2(canvas.center_pixels() + (0, 30 * canvas.relative_scale))
        #
        #
        # img_screen_rect = img.get_rect()
        # screen_pivot = canvas.center_pixels() + (0, 30*canvas.relative_scale)
        # img_screen_rect.midtop = screen_pivot
        # img_rect = canvas.screen_to_world_rect(img_screen_rect)
        # pivot = canvas.screen_to_world_v2(screen_pivot)
        # points = points_from_rect(img_rect)
        # rot_points = RotateMatrix(angle) * points
        # ext_rect = outer_rect(rot_points)
        # ext_points = points_from_rect(ext_rect)

        # canvas.blit(pygame.transform.rotate(img, math.degrees(angle)), ext_rect)



        # jet particles
        emmit_l = Vector2(-0.05*bias_throttle, -0.04).rotate_rad(angle)
        emmit_r = Vector2(0.05*bias_throttle, -0.04).rotate_rad(angle)
        if self.particle_en:
            for _ in range(int(randint(round(8 * bias_throttle), round(10 * bias_throttle)) * 60 / self.clock.fps)):
                vel = Vector2(uniform(-0.2, .07), uniform(-5, -8)) * bias_throttle
                self.particles.append(gb.BallParticle(canvas,
                                                   gb.lerp_vec3(gb.lerp_vec3((255, 60, 0), (200, 200, 60), random()),
                                                             (255, 255, 255), random() * 0.5),
                                                   uniform(.003, .006),
                                                   pos=gb.lerp_vec2(emmit_l, emmit_r, random()),
                                                   vel=vel.rotate_rad(angle),
                                                   dt=1 / self.clock.fps, lifetime=uniform(.1, .15), g=0))
            self.particles.step_and_draw()


        # rocket
        draw_rocket(canvas, (0, 0), angle)

        # extrenal rects for debug
        if self.show_outer_rects:
            img.draw_rect((0, 255, 255))



        # scope
        x = self.clock.t
        total_frame_time = 1/self.real_fps if self.real_fps != 0 else 0
        y = {
            'ch1': (self.last_active_frame_time * self.clock.fps - 1, total_frame_time * self.clock.fps - 1), #(self.mm_frame_time.value * self.fps - 1, self.last_active_frame_time * self.fps - 1),
            'ch2': (throttle, angle),
        }

        def another_in_focus(self_key):
            for ikey, iscope in self.scopes.items():
                if ikey != self_key and iscope.focus:
                    return True
            return False

        for key, scope in self.scopes.items():
            scope.append(x, y[key])
            scope.focus = scope.collision(self.mouse.pos) and not another_in_focus(key)
            scope.draw()
            scope.blit_to_main()


def draw_rocket(canvas: gb.Canvas, pos = (0,0), angle=0):
    canvas.draw_polygon((90, 90, 100),
                        gb.translate_vec2s(
                            gb.rotate_vec2s(((0.06, 0.05), (0.08, -0.1), (-0.08, -0.1), (-0.06, 0.05)), angle),
                            pos))  # angle
    canvas.draw_polygon((120, 120, 130),
                        gb.translate_vec2s(
                            ((0.1, 0.0), (0.1, 0.6), (0.06, 0.75), (0.0, 0.8), (-0.06, 0.75), (-0.1, 0.6), (-0.1, 0.0)),
                            pos))

    canvas.draw_circle((255, 200, 60), pos + (0, 0.25), 0.05, width=0, draw_top_left=True, draw_bottom_right=True)
    canvas.draw_circle((0, 0, 0), pos + (0, 0.25), 0.05, width=0, draw_top_right=True, draw_bottom_left=True)



if __name__ == '__main__':
    Demo(fps=60)