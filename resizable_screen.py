import pygame
import sys
from datetime import datetime



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
        self.global_scale = 1.0
        self.global_bias = [0, 0]
        self._last_global_bias = [0, 0]
        self.ticks = 0
        self.extra_info = []

        self.event_loop_callback = None
        self.active_tab = 'main'
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
                        if event.key == self.tabs[tab_key]['shortcut']:
                            self.active_tab = tab_key

                if self.event_loop_callback is not None:
                    self.event_loop_callback(event)

            canvas = self.tabs[self.active_tab]['canvas']
            canvas.fill(self.tabs[self.active_tab]['bg_color'])
            self.tabs[self.active_tab]['draw'](canvas)

            self.window.fill(self.cols['screen_bg'])
            blit_with_aspect_ratio(self.window, self.tabs[self.active_tab]['canvas'], self.antialiasing)

            if self.show_info:
                info_list = [f'fps: {self.clock.get_fps():.1f} Hz',
                             f'sim_time: {self.ticks / self.fps:.1f} s',
                             f'antialiasing: {self.antialiasing}',
                             f'active_tab: {self.active_tab} ({self.tabs[self.active_tab]["ticks"] / self.fps:.1f} s)',
                             f'canvas_res: {canvas.get_size()} px',
                             f'window_res: {self.window.get_size()} px',
                             f'mouse: {pygame.mouse.get_pos()} px',
                             f'global_scale: {self.global_scale}',
                             *self.extra_info
                             ]

                info_pos = self.info_position
                draw_text_list(self.window, info_list, self.fonts['info'], self.cols['info'], info_pos, 26)

            pygame.display.flip()
            self.clock.tick(self.fps)
            self.ticks += 1
            self.tabs[self.active_tab]['ticks'] += 1

    def draw_main(self, canvas):



        size = (1920, 1080)
        center = (size[0]//2+self.global_bias[0], size[1]//2+self.global_bias[1])

        if self.mouse_right.dragging:
            self.global_bias = self.mouse_right.drag_delta[0]+self._last_global_bias[0], self.mouse_right.drag_delta[1]+self._last_global_bias[1]
        else:
            self._last_global_bias = self.global_bias

        scale = min(*size)/2 * self.global_scale
        radius = 0.1 * scale
        pygame.draw.circle(canvas, (255, 255, 255), world_to_screen((+0, +0), scale=scale, bias=center), radius)
        pygame.draw.circle(canvas, (255, 0, 0), world_to_screen((-1, -1), scale=scale, bias=center), radius)
        pygame.draw.circle(canvas, (0, 255, 0), world_to_screen((-1, +1), scale=scale, bias=center), radius)
        pygame.draw.circle(canvas, (0, 0, 255), world_to_screen((+1, +1), scale=scale, bias=center), radius)
        pygame.draw.circle(canvas, (255, 255, 0), world_to_screen((+1, -1), scale=scale, bias=center), radius)



        render_and_blit_message(canvas, datetime.now().strftime("%H:%M:%S"), self.fonts['default'], (30, 120, 30, 128), scale=self.global_scale, center=center)
        width = 1
        M=8
        grid_color = (90, 90, 90)
        for m in range(2*M+1):
            pygame.draw.line(canvas, grid_color, world_to_screen((-1+m/M, -1), scale, center), world_to_screen((-1+m/M, 1), scale, center), width=width)
            pygame.draw.line(canvas, grid_color, world_to_screen((-1, -1+m/M), scale, center), world_to_screen((1, -1+m/M), scale, center), width=width)


    def draw_menu(self, canvas):
        prtsc = self.tabs['main']['canvas'].copy()
        prtsc.set_alpha(128)
        blit_with_aspect_ratio(canvas, prtsc)

        text_surface=render_message('MENU', self.fonts['default'], (0, 0, 0))
        text_rect = text_surface.get_rect(center=(canvas.get_width() // 2, canvas.get_height() // 2))
        pygame.draw.rect(canvas, (255, 255, 30, 128), text_rect, border_radius=30)
        canvas.blit(text_surface, text_rect)

    def draw_extra(self, canvas):
        render_and_blit_message(canvas, 'EXTRA', self.fonts['default'], (240, 120, 30, 128))



class Game(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = {
            'main' : {'canvas': pygame.surface.Surface(self.canvas_size, pygame.SRCALPHA), 'bg_color': (30, 45, 30), 'draw': self.draw_main, 'shortcut': pygame.K_F1, 'ticks': 0},
            'menu' : {'canvas': pygame.surface.Surface(self.canvas_size, pygame.SRCALPHA), 'bg_color': (45, 30, 30), 'draw': self.draw_menu, 'shortcut': pygame.K_F2, 'ticks': 0},
            'extra': {'canvas': pygame.surface.Surface(self.canvas_size, pygame.SRCALPHA), 'bg_color': (30, 45, 45), 'draw': self.draw_extra, 'shortcut': pygame.K_F3, 'ticks': 0},
        }
        self.event_loop_callback = self.process_user_input_event
        self.loop()

    def process_user_input_event(self, event):
        keys = pygame.key.get_pressed()
        if event.type == pygame.MOUSEBUTTONDOWN and keys[pygame.K_LCTRL]:
            if event.button == 5:  # Scroll para baixo
                self.global_scale /= 1.1
            if event.button == 4:  # Scroll para cima
                self.global_scale *= 1.1

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_left.press(event.pos)
            if event.button == 2:
                self.mouse_middle.press(event.pos)
            if event.button == 3:
                self.mouse_right.press(event.pos)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_left.release(event.pos)
            if event.button == 2:
                self.mouse_middle.release(event.pos)
            if event.button == 3:
                self.mouse_right.release(event.pos)

        if event.type == pygame.MOUSEMOTION:
            if self.mouse_left.pressed:
                self.mouse_left.drag(event.pos)
            if self.mouse_middle.pressed:
                self.mouse_middle.drag(event.pos)
            if self.mouse_right.pressed:
                self.mouse_right.drag(event.pos)




def blit_with_aspect_ratio(dest: pygame.surface.Surface, source: pygame.surface.Surface, antialiasing=True, offset: tuple[int, int] | None = None):


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


def render_and_blit_message(canvas, text, font, color, scale=(1.0, 1.0), **kwargs):
    if isinstance(scale, float):
        scale = (scale, scale)
    if len(kwargs) == 0:
        kwargs['center'] = (canvas.get_width() // 2, canvas.get_height() // 2)
    text_surface = render_message(text, font, color)
    if scale != (1.0, 1.0):
        text_surface = pygame.transform.smoothscale_by(text_surface, scale)

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


if __name__ == '__main__':
    Game()