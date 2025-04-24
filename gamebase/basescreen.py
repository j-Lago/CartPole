import gamebase as gb
import time
import pygame
import sys
from pygame import Vector2
from pathlib import Path


# import os
# os.environ['SDL_HINT_RENDER_VSYNC'] = '1'


class MetaLoopCall(type):
    """
    Garante que BaseScreen.loop() seja chamado apos o instanciamento de uma subclasse de BaseScreen
    """
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.loop()
        return instance


class BaseScreen(metaclass=MetaLoopCall):
    def __init__(self, window_size: tuple[int, int] = (1280, 720),
                 canvas_size: tuple[int, int] = (1920, 1080),
                 fps: float = 60.0,
                 antialiasing: bool = True,
                 fullscreen: bool = False,
                 font_family: str = 'Consolas',
                 font_base_size: int = 70,
                 flags: int = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF,
                 vsync: bool = True
                 ):

        try:
            pygame.quit()
        except Exception as e:
            print(e)
        finally:
            pygame.init()

        # self.pygame_clock = pygame.time.Clock()
        self.free_fps = False

        self.cols = {
            'bg': (30, 30, 30),
            'info': (255, 128, 128),
        }

        self.fonts = {
            'info': pygame.font.SysFont('Consolas', 22),
            'fps': pygame.font.SysFont('Consolas', 32),
            'fps_small': pygame.font.SysFont('Consolas', 20),
            'scope_title': pygame.font.SysFont('Consolas', 24),
            'scope_label': pygame.font.SysFont('Consolas', 18),
            'tiny': pygame.font.SysFont(font_family, round(font_base_size*0.2571)),
            'small': pygame.font.SysFont(font_family, round(font_base_size*.342835)),
            'medium': pygame.font.SysFont(font_family, round(font_base_size*.42857)),
            'normal': pygame.font.SysFont(font_family, round(font_base_size*1)),
            'big': pygame.font.SysFont(font_family, round(font_base_size*1.71428)),
            'huge': pygame.font.SysFont(font_family, round(font_base_size*2.85714)),
        }

        self._flags = flags
        self.fullscreen = fullscreen
        self.blit_offset = 0, 0

        # self.fps = fps
        self.clock: gb.Clock = gb.Clock(fps)

        self.real_fps = fps
        self.last_time = time.perf_counter()
        self.last_active_frame_time = 0.0
        self.mm_fps = gb.MediaMovel(30)
        self.mm_frame_time = gb.MediaMovel(30)
        self.mm_sleep_compensation = gb.MediaMovel(30)

        self.antialiasing = antialiasing
        self.window_size = window_size
        self.canvas_size = canvas_size
        self.event_loop_callback = None
        self.pre_draw_callback = None
        self.post_draw_callback = None

        self.popups = dict()
        # self.canvases = dict()
        # self.active_canvas_key = None
        # self.last_active_canvas_key = None

        # self.info_position = (30, 30)
        self.show_fps = True
        self.vsync = vsync

        if self.fullscreen:
            self.window = gb.Canvas(surface=pygame.display.set_mode((0, 0), pygame.FULLSCREEN, vsync=self.vsync))
        else:
            self.window = gb.Canvas(surface=pygame.display.set_mode(window_size, self._flags, vsync=self.vsync))


        self.extra_info = []
        self.info_popup = gb.PopUpText(self.window, alpha=200, pos=(10, -10),
                                       color=self.cols['info'], text='', font=self.fonts['info'], visible=False, border_radius=13, border_width=2)
        self.extra_help = []
        self.base_help = [
            f' F1: help',
            f'F12: info',
            f'F11: fullsceen',
            f'F10: fps',
            f' F9: antialiasing',
            f' F8: free fps',
        ]
        self.help_popup = gb.PopUpText(self.window, alpha=200, pos=(10, -10), size=(400, 250),
                                       color=self.cols['info'], text='', font=self.fonts['info'], visible=False,
                                       border_radius=13, border_width=2)

        self.final_window_popups = {
            'info': self.info_popup,
            'help': self.help_popup
        }

        # self.clock = pygame.time.Clock()  # controle de frame rate alterado para solução própria, aparentemente mais consistente

        # sounds
        self.mixer = pygame.mixer
        self.mixer.init()
        self.sounds = dict()

        # images
        self.images = dict()

        self.canvas: gb.Canvas = gb.Canvas(self.canvas_size, fonts=self.fonts)
        self.mouse = gb.Mouse(self)
        self.hide_fps()

    def load_sound(self, file_path: Path, volume: float = 1):
        sound = self.mixer.Sound(file_path)
        sound.set_volume(volume)
        return sound

    def load_image(self, file_path: Path):
        return pygame.image.load(file_path)

    def show_info(self):
        self.info_popup.visible = True

    def hide_info(self):
        self.info_popup.visible = False

    def show_fps(self):
        self.show_fps = True

    def hide_fps(self):
        self.show_fps = False

    def loop(self):
        while True:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                self.mouse.handle_event(event, keys)

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, self._flags, vsync=self.vsync)
                    self.window_size = screen.get_size()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.help_popup.visible = not self.help_popup.visible
                    if event.key == pygame.K_F9:
                        self.antialiasing = not self.antialiasing
                    if event.key == pygame.K_F8:
                        self.free_fps = not self.free_fps
                    elif event.key == pygame.K_F12:
                        self.info_popup.visible = not self.info_popup.visible
                    elif event.key == pygame.K_F10:
                        self.show_fps = not self.show_fps
                    elif event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            _mouse_visibility = pygame.mouse.get_visible()
                            pygame.display.quit()
                            pygame.display.init()
                            pygame.mouse.set_visible(_mouse_visibility)
                            self.window = gb.Canvas(surface=pygame.display.set_mode((0, 0), pygame.FULLSCREEN, vsync=self.vsync))
                        else:
                            self.window = gb.Canvas(surface=pygame.display.set_mode(self.window_size, self._flags, vsync=self.vsync))
                    elif event.key == pygame.K_a:
                        self.antialiasing = not self.antialiasing

                    # for tab_key in self.canvases:
                    #     if event.key == self.canvases[tab_key].shortcut:
                    #         if self.active_canvas_key != tab_key:
                    #             self.last_active_canvas_key = self.active_canvas_key
                    #             self.active_canvas_key = tab_key
                    #             self.canvases[tab_key].got_focus()


                if self.event_loop_callback is not None:
                    self.event_loop_callback(event)


            # draw
            if self.pre_draw_callback is not None:
                self.pre_draw_callback()

            self._draw()

            if self.post_draw_callback is not None:
                self.post_draw_callback()

    def _draw(self):
        self.window.fill(self.cols['bg'])

        canvas = self.canvas
        canvas.fill(self.canvas.bg_color)
        canvas.draw()

        for popup in self.popups.values():
            popup.draw()
            popup.blit_to_main()

        gb.blit_with_aspect_ratio(self.window, self.canvas, self.antialiasing, offset=self.blit_offset)

        self.info_popup.main_canvas = self.window
        self.help_popup.main_canvas = self.window

        self.info_popup.pos = self.window.screen_to_world_v2((10, 20 + (45 if self.show_fps else 0)))
        if self.info_popup.visible:
            rect = self.info_popup.surface.get_rect()
            self.help_popup.pos = self.window.screen_to_world_v2((10, rect[3]+ 25 + (45 if self.show_fps else 0)))
            self.info_popup.text = [
                # f'╭───╮',
                # f'│F12│ to hide info',
                # f'╰───╯',
                f'fps: {self.mm_fps.value:.1f} Hz',
                f'frame_time: {self.mm_frame_time.value * 1000:.1f} ms ({self.mm_frame_time.value * self.clock.fps * 100.0:.1f}%)',
                f'sim_time: {self.clock.t:.1f} s',
                f'antialiasing: {self.antialiasing}',
                f'canvas_res: {canvas.get_size()} px',
                f'window_res: {self.window.get_size()} px',
                f'mouse_window: {pygame.mouse.get_pos()} px',
                f'mouse_world: ({self.mouse.pos[0]:.2f}, {self.mouse.pos[1]:.2f})',
                f'canvas_bias: {self.canvas.bias}',
                f'canvas_scale: {self.canvas.scale:.1f}',
                f'canvas_relative_scale: {self.canvas.relative_scale:.2f}',
                ] + self.extra_info
        else:
            self.help_popup.pos = self.window.screen_to_world_v2((10, 20 + (45 if self.show_fps else 0)))

        if self.help_popup.visible:
            self.help_popup.text = self.base_help + self.extra_help

        for popup in self.final_window_popups.values():
            popup.draw()
            popup.blit_to_main()

        self.mm_fps.append(self.real_fps)
        self.mm_frame_time.append(self.last_active_frame_time)

        # fps
        if self.show_fps:
            # col = game.cols['info']
            col = ((255,30, 30), (30,255, 30))[self.clock.ticks % 2]
            # canvas.draw_circle(col, (-1.55, .946), .02)

            self.window.draw_text(col, self.fonts['fps'],
                             f'{self.mm_fps.value:.1f}',
                             self.window.topleft + (50, -10),
                             anchor='midtop')

            self.window.draw_text(col, self.fonts['fps_small'],
                             f'({self.mm_frame_time.value * self.clock.fps * 100.0:.1f}%)',
                             self.window.topleft + (50, -40),
                             anchor='midtop')

        pygame.display.flip()
        self.fps_control()

    def fps_control(self):
        self.clock.update()

        # self.real_fps = self.pygame_clock.get_fps()
        # self.pygame_clock.tick(self.clock.fps)  # parece impreciso

        ideal_period = 1/self.clock.fps
        self.last_active_frame_time = (time.perf_counter() - self.last_time)
        if not self.free_fps:
            time.sleep(max(0.0, ideal_period - self.last_active_frame_time + self.mm_sleep_compensation.value))
        real_period = (time.perf_counter() - self.last_time)
        self.mm_sleep_compensation.append(ideal_period-real_period)
        self.real_fps = 1/real_period
        self.last_time = time.perf_counter()