import time
import pygame
import sys
from canvas import Canvas
from mouse import Mouse
from utils import remap
from filters import MediaMovel
from popup import PopUp, PopUpText
from pygame import Vector2
from lerp import lerp_vec3


class MetaLoopCall(type):
    """
    Garante que BaseScreen.loop seja chamado apos o instanciamento de uma subclasse de BaseScreen
    """
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.loop()
        return instance


class BaseScreen(metaclass=MetaLoopCall):
    def __init__(self, window_size: tuple[int, int] = (1600, 900),
                 canvas_size: tuple[int, int] = (1920, 1080),
                 fps: float = 60.0,
                 antialiasing: bool = True,
                 fullscreen: bool = False,
                 font_family: str = 'Consolas',
                 font_base_size: int = 26,
                 flags: int = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
                 ):

        pygame.init()

        self.cols = {
            'bg': (30, 30, 30),
            'info': (255, 128, 128),
        }

        self.fonts = {
            'info': pygame.font.SysFont('Consolas', 22),
            'tiny': pygame.font.SysFont(font_family, round(font_base_size*0.8)),
            'small': pygame.font.SysFont(font_family, round(font_base_size)),
            'normal': pygame.font.SysFont(font_family, round(font_base_size*2)),
            'big': pygame.font.SysFont(font_family, round(font_base_size*4)),
            'huge': pygame.font.SysFont(font_family, round(font_base_size*8)),
        }

        self._flags = flags
        self.fullscreen = fullscreen

        self.fps = fps
        self.real_fps = self.fps
        self.ticks = 0
        self.last_time = time.perf_counter()
        self.last_active_frame_time = 0.0
        self.mm_fps = MediaMovel(20)
        self.mm_frame_time = MediaMovel(20)

        self.antialiasing = antialiasing
        self.window_size = window_size
        self.canvas_size = canvas_size
        self.event_loop_callback = None

        self.popups = dict()
        self.canvases = dict()
        self.active_canvas_key = None
        self.last_active_canvas_key = None

        self.info_position = (30, 30)
        self.mouse = Mouse()

        if self.fullscreen:
            self.window = Canvas(surface=pygame.display.set_mode((0, 0), pygame.FULLSCREEN))
        else:
            self.window = Canvas(surface=pygame.display.set_mode(window_size, self._flags))

        self.extra_info = []
        self.info_popup = PopUpText(self.window, alpha=200, pos=(10, -10), flags=flags,
                                    color=self.cols['info'], text='', font=self.fonts['info'], visible=True, border_radius=13, border_width=2)
        self.extra_help = []
        self.base_help = [
            f' F1: help',
            f'F12: toggle info',
            f'F11: fullsceen/windowned',
            f'F10: toggle antialiasing',
        ]
        self.help_popup = PopUpText(self.window, alpha=200, pos=(10, -10), size=(400, 250), flags=flags,
                                    color=self.cols['info'], text='', font=self.fonts['info'], visible=False,
                                    border_radius=13, border_width=2)

        self.final_window_popups = {
            'info': self.info_popup,
            'help': self.help_popup
        }

        self.clock = pygame.time.Clock()


    @property
    def active_canvas(self):
        if self.active_canvas_key is None:
            self.active_canvas_key = next(iter(self.canvases.keys()))
        return self.canvases[self.active_canvas_key]

    @property
    def t(self):
        return self.ticks / self.fps

    @property
    def mouse_pos(self) -> Vector2:
        return self.mouse.pos

    @property
    def mouse_world_pos(self) -> Vector2:
        canvas = self.active_canvas
        return canvas.screen_to_world_v2(remap(self.mouse.pos, self.window, canvas))

    def loop(self):
        while True:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                self.mouse.process_event(event, keys)

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, self._flags)
                    self.window_size = screen.get_size()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.help_popup.visible = not self.help_popup.visible
                    if event.key == pygame.K_F10:
                        self.antialiasing = not self.antialiasing
                    elif event.key == pygame.K_F12:
                        self.info_popup.visible = not self.info_popup.visible
                    elif event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            _mouse_visibility = pygame.mouse.get_visible()
                            pygame.display.quit()
                            pygame.display.init()
                            pygame.mouse.set_visible(_mouse_visibility)
                            self.window = Canvas(surface=pygame.display.set_mode((0, 0), pygame.FULLSCREEN))
                        else:
                            self.window = Canvas(surface=pygame.display.set_mode(self.window_size, self._flags))
                    elif event.key == pygame.K_a:
                        self.antialiasing = not self.antialiasing

                    for tab_key in self.canvases:
                        if event.key == self.canvases[tab_key].shortcut:
                            if self.active_canvas_key != tab_key:
                                self.last_active_canvas_key = self.active_canvas_key
                                self.active_canvas_key = tab_key
                                self.canvases[tab_key].got_focus()

                if self.event_loop_callback is not None:
                    self.event_loop_callback(event)


            # draw
            self._draw()

    def _draw(self):
        self.window.fill(self.cols['bg'])

        canvas = self.active_canvas
        canvas.fill(self.active_canvas._bg_color)
        canvas.draw()

        for popup in self.popups.values():
            popup.draw()
            popup.blit_to_main()

        blit_with_aspect_ratio(self.window, self.active_canvas, self.antialiasing)

        self.info_popup.main_canvas = self.window
        self.help_popup.main_canvas = self.window
        if self.info_popup.visible:
            rect = self.info_popup.get_rect()
            self.help_popup.pos = self.window.screen_to_world_v2((10, 20+rect[3]))
            self.info_popup.text = [
                # f'╭───╮',
                # f'│F12│ to hide info',
                # f'╰───╯',
                f'fps: {self.mm_fps.value:.1f} Hz',
                f'frame_time: {self.mm_frame_time.value * 1000:.1f} ms ({self.mm_frame_time.value * self.fps * 100.0:.1f}%)',
                f'sim_time: {self.ticks / self.fps:.1f} s',
                f'antialiasing: {self.antialiasing}',
                f"active_canvas: '{self.active_canvas_key}' ({self.active_canvas.ticks / self.fps:.1f} s)",
                f'canvas_res: {canvas.get_size()} px',
                f'window_res: {self.window.get_size()} px',
                f'mouse_window: {pygame.mouse.get_pos()} px',
                f'mouse_world: ({self.mouse_world_pos[0]:.2f}, {self.mouse_world_pos[1]:.2f})',
                f'canvas_bias: {self.active_canvas.bias}',
                f'canvas_scale: {self.active_canvas.scale:.1f}',
                f'canvas_relative_scale: {self.active_canvas.relative_scale:.2f}',
                ] + self.extra_info
        else:
            self.help_popup.pos = self.window.screen_to_world_v2((10, 10))

        if self.help_popup.visible:
            self.help_popup.text = self.base_help + self.extra_help

        for popup in self.final_window_popups.values():
            popup.draw()
            popup.blit_to_main()

        self.mm_fps.append(self.real_fps)
        self.mm_frame_time.append(self.last_active_frame_time)

        pygame.display.flip()
        self.ticks += 1
        self.active_canvas.ticks += 1

        t = time.perf_counter()
        self.last_active_frame_time = (t - self.last_time)

        self.real_fps = self.clock.get_fps()
        self.clock.tick(self.fps)
        self.last_time = time.perf_counter()


def blit_with_aspect_ratio(dest: Canvas, source: Canvas, antialiasing=True, offset: tuple[int, int] | None = None):
    source_size = source.get_size()
    dest_size = dest.get_size()

    source_ratio = source_size[0] / source_size[1]
    dest_ratio = dest_size[0] / dest_size[1]

    if source_size == dest_size:
        scaled_surface = source.copy()
        if offset is None:
            offset = (0, 0)
    else:
        rescale = pygame.transform.smoothscale if antialiasing else pygame.transform.scale
        if source_ratio > dest_ratio:
            new_width = dest_size[0]
            new_height = int(dest_size[0] / source_ratio)
        else:
            new_height = dest_size[1]
            new_width = int(dest_size[1] * source_ratio)
        scaled_surface = rescale(source.surface, (new_width, new_height))
        if offset is None:
            offset = (dest_size[0] - new_width) // 2, (dest_size[1] - new_height) // 2   # centralizada
    dest.blit(scaled_surface, dest.screen_to_world_v2(offset))



# def render_message(text, font, color):
#     text_surface = font.render(text, True, color[:3])
#     if len(color) == 4:
#         text_surface.set_alpha(color[3])
#     return text_surface
#
#
# def draw_text_list(canvas, info_list, font, color, pos, vspace):
#     for l, info in enumerate(info_list):
#         info_render = font.render(info, True, color)
#         canvas.blit(info_render, (pos[0], pos[1] + vspace * l))


# def world_to_screen(vec2: tuple[float, float], scale: tuple[float, float] | float, bias: tuple[float, float]) -> tuple[int, int]:
#     if isinstance(scale, float | int):
#         scale = (scale, scale)
#     screen_x = round(vec2[0] * scale[0] + bias[0])
#     screen_y = round(-vec2[1] * scale[1] + bias[1])
#     return screen_x, screen_y


