import pygame
import sys
from canvas import Canvas

class MouseButton:
    def __init__(self):
        self.press_time = None
        self.release_time = None
        self.press_pos = None
        self.release_pos = None
        self.drag_pos = None
        self.pressed = False
        self.dragging = False

    def press(self, pos):
        self.press_time = pygame.time.get_ticks()
        self.press_pos = pos
        self.pressed = True

    def release(self, pos):
        self.release_time = pygame.time.get_ticks()
        self.release_pos = pos
        self.pressed = False
        self.drag_pos = pos
        self.dragging = False

    def drag(self, pos):
        self.drag_pos = pos
        self.dragging = True

    @property
    def drag_delta(self):
        return self.drag_pos[0]-self.press_pos[0], self.drag_pos[1]-self.press_pos[1]


class Screen:
    def __init__(self, window_size: tuple[int, int] = (1600, 900),
                 canvas_size: tuple[int, int] = (1920, 1080),
                 fps: float = 60.0,
                 antialiasing: bool = True,
                 fullscreen: bool = False,
                 ):
        """
        Inicializa uma janela pygame.
        Alguns atalhos de teclado são pre-configurados:
            F10 ativa/destiva antialiasing
            F11 alterna entre modo fullscreen e windoned
            F12 mostra informações da renderização da aplicação
            alt+F4 fecha a aplicação
            ctr+scroll zoom
            right mouse drag
            F1..F3 altera o canvas (tabs) que será renderizado (apenas exemplo, todo: retirar depois)

        :param window_size: tamanho inicial da janela para o modo windoned
        :param canvas_size: tamanho da superficie de renderização. Essa superficie ao final de cada frame será redimensionada para o tamanho atual da janela
        :param fps: taxa de quadros por segundo
        :param antialiasing: define se será ou não aplicado antialiasing no redimensionamento da janela. Não tem efeito se window_size == canvas_size
        :param fullscreen: inicia no modo fullscreen
        """
        self.fullscreen = fullscreen
        self.antialiasing = antialiasing
        self.window_size = window_size
        self.canvas_size = canvas_size
        self.fps = fps
        # self.tabs['main']['scale'] = 1.0
        # self.tabs['main']['bias'] = [0, 0]
        # self.tabs['main']['last_bias'] = [0, 0]
        self.ticks = 0
        self.extra_info = []

        self.event_loop_callback = None
        self.active_tab = None
        self.last_active_tab = None
        self.show_info = False
        self.info_position = (30, 30)

        self.mouse_left = MouseButton()
        self.mouse_middle = MouseButton()
        self.mouse_right = MouseButton()

        pygame.init()

        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode(window_size, pygame.RESIZABLE)

        self.cols = {
            'screen_bg': (30, 30, 30),
            'info': (220, 200, 90),
        }

        self.fonts = {
            'info': pygame.font.SysFont('Consolas', 26),
            'default': pygame.font.SysFont('Courier New', 200),
        }

        self.tabs = dict()
        self.clock = pygame.time.Clock()

    def loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    self.window_size = screen.get_size()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F10:
                        self.antialiasing = not self.antialiasing
                    elif event.key == pygame.K_F12:
                        self.show_info = not self.show_info
                    elif event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            pygame.display.quit()
                            pygame.display.init()
                            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            self.window = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
                    elif event.key == pygame.K_a:
                        self.antialiasing = not self.antialiasing

                    for tab_key in self.tabs:
                        if event.key == self.tabs[tab_key].shortcut:
                            if self.active_tab != tab_key:
                                self.last_active_tab = self.active_tab
                                self.active_tab = tab_key

                if self.event_loop_callback is not None:
                    self.event_loop_callback(event)

            canvas = self.tabs[self.active_tab]
            canvas.fill(self.tabs[self.active_tab].bg_color)
            self.tabs[self.active_tab].draw(canvas)

            self.window.fill(self.cols['screen_bg'])
            blit_with_aspect_ratio(self.window, self.tabs[self.active_tab], self.antialiasing)

            if self.show_info:
                info_list = [f'fps: {self.clock.get_fps():.1f} Hz',
                             f'sim_time: {self.ticks / self.fps:.1f} s',
                             f'antialiasing: {self.antialiasing}',
                             f'active_tab: {self.active_tab} ({self.tabs[self.active_tab].ticks / self.fps:.1f} s)',
                             f'canvas_res: {canvas.get_size()} px',
                             f'window_res: {self.window.get_size()} px',
                             f'mouse: {pygame.mouse.get_pos()} px',
                             f'global_scale: {self.tabs[self.active_tab].scale}',
                             f'global_bias: {self.tabs[self.active_tab].bias}',
                             *self.extra_info
                             ]

                info_pos = self.info_position
                draw_text_list(self.window, info_list, self.fonts['info'], self.cols['info'], info_pos, 26)

            pygame.display.flip()
            self.clock.tick(self.fps)
            self.ticks += 1
            self.tabs[self.active_tab].ticks += 1








def blit_with_aspect_ratio(dest: Canvas, source: pygame.surface.Surface, antialiasing=True, offset: tuple[int, int] | None = None):


    source_width, source_height = source.get_size()
    dest_width, dest_height = dest.get_size()

    source_ratio = source_width / source_height
    dest_ratio = dest_width / dest_height

    if source.get_size() == dest.get_size():
        scaled_surface = source.copy()
        if offset is None:
            offset = (0, 0)
    else:
        rescale = pygame.transform.smoothscale if antialiasing else pygame.transform.scale
        if source_ratio > dest_ratio:
            new_width = dest_width
            new_height = int(dest_width / source_ratio)
        else:
            new_height = dest_height
            new_width = int(dest_height * source_ratio)
        scaled_surface = rescale(source, (new_width, new_height))
        if offset is None:
            offset = (dest_width - new_width) // 2, (dest_height - new_height) // 2   # centralizada
    dest.blit(scaled_surface, offset)



def render_message(text, font, color):
    text_surface = font.render(text, True, color[:3])
    if len(color) == 4:
        text_surface.set_alpha(color[3])
    return text_surface


def render_and_blit_message(canvas, text, font, color, relative_scale=1.0, **kwargs):
    if len(kwargs) == 0:
        kwargs['center'] = (canvas.get_width() // 2, canvas.get_height() // 2)
    text_surface = render_message(text, font, color)
    if relative_scale != 1:
        text_surface = pygame.transform.smoothscale_by(text_surface, relative_scale)

    text_rect = text_surface.get_rect(**kwargs)
    canvas.blit(text_surface, text_rect)


def draw_text_list(canvas, info_list, font, color, pos, vspace):
    for l, info in enumerate(info_list):
        info_render = font.render(info, True, color)
        canvas.blit(info_render, (pos[0], pos[1] + vspace * l))


def world_to_screen(vec2: tuple[float, float], scale: tuple[float, float] | float, bias: tuple[float, float]) -> tuple[int, int]:
    if isinstance(scale, float | int):
        scale = (scale, scale)
    screen_x = round(vec2[0] * scale[0] + bias[0])
    screen_y = round(-vec2[1] * scale[1] + bias[1])
    return screen_x, screen_y


