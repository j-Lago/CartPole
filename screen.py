
from abc import ABC, abstractmethod
import pygame
import ctypes
import sys
import os
os.environ['SDL_JOYSTICK_HIDAPI_PS4_RUMBLE'] = '1'


class NormalizedScreen(ABC):
    def __init__(self, name: str,
                 window_size: tuple[int, int] | None,
                 fps: int = 60,
                 aspect_ratio: None | float = 1.0,
                 info_position: tuple[float, float] | None = None,
                 show_info: bool = False,
                 grid_step: float = 1/32,
                 show_grid: bool = False,
                 snap_to_grid: bool = False
                 ):

        pygame.init()
        pygame.font.init()

        self.cols = {'bg': (30, 30, 30),
                     'grid': (60, 60, 60),
                     'mouse': (240, 60, 30),
                     'mouse_left_drag': (180, 90, 60),
                     'mouse_middle_drag': (90, 180, 60),
                     'mouse_right_drag': (90, 60, 180),
                     'text': (160, 130, 120)}
        self.fonts = {'default': pygame.font.SysFont('Consolas', 22)}

        self.extra_info = []
        self.fps = fps
        self.grid_step = grid_step
        self.info_position = info_position
        self.show_info = show_info
        self.show_grid = show_grid
        self.snap_to_grid = snap_to_grid
        self.set_name(name)
        self.left_click = MouseKey()
        self.right_click = MouseKey()
        self.middle_click = MouseKey()
        pygame.mouse.set_visible(False)

        self.ticks = 0
        self.fullscreen_mode = None
        self.screen = None
        self.xy_scale = None
        self.global_scale = 1.0
        self.aspect_ratio = aspect_ratio
        if window_size is None:
            self.original_window_size = (1600, 900)
            self.init_fullscreen_mode()
        else:
            self.original_window_size = window_size
            self.init_window_mode(window_size)

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.clock = pygame.time.Clock()

    def reset(self):
        self.extra_info = []
        self.ticks = 0
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

    def set_name(self, name):
        pygame.display.set_caption(name)

    def loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_screen_mode()
                    if event.key == pygame.K_F12:
                        self.show_info = not self.show_info
                    if event.key == pygame.K_F10:
                        self.show_grid = not self.show_grid
                    if event.key == pygame.K_F9:
                        self.snap_to_grid = not self.snap_to_grid

                keys = pygame.key.get_pressed()
                if event.type == pygame.MOUSEBUTTONDOWN and keys[pygame.K_LCTRL]:
                    if event.button == 5:  # Scroll para baixo
                        self.rescale(self.global_scale/1.1)
                    if event.button == 4:  # Scroll para cima
                        self.rescale(self.global_scale*1.1)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.left_click.press(self.mouse_position)
                    if event.button == 2:
                        self.middle_click.press(self.mouse_position)
                    if event.button == 3:
                        self.right_click.press(self.mouse_position)

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_click.release(self.mouse_position)
                    if event.button == 2:
                        self.middle_click.release(self.mouse_position)
                    if event.button == 3:
                        self.right_click.release(self.mouse_position)




            self.screen.fill(self.cols['bg'])
            if self.show_grid:
                self.draw_grid(self.cols['grid'], self.grid_step)


            self.draw()

            mouse = self.mouse_position
            if self.show_info:
                info_list = [f'fps: {self.clock.get_fps():.1f}',
                             f'res: {self.screen.get_width()} x {self.screen.get_height()}',
                             f'sim_time: {self.ticks / self.fps:.1f}s',
                             f'world_aspect: {self.aspect_ratio}',
                             f'mouse: {mouse[0]:.2f}, {mouse[1]:.2f}',
                             *self.extra_info
                ]

                # for info in self.extra_info:
                #     info_list.append(info)

                info_pos = self.info_position if self.info_position is not None else (self.x_min+30/self.xy_scale[0], self.y_max-30/self.xy_scale[1])
                self.draw_text_list(info_list, self.fonts['default'], self.cols['text'], info_pos, 26)

            # custom mouse
            self.draw_mouse()


            pygame.display.flip()
            self.ticks += 1
            self.clock.tick(self.fps)

    @abstractmethod
    def draw(self):
        pass

    def init_fullscreen_mode(self):
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        self.screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
        self.fullscreen_mode = True
        self.rescale()

    def init_window_mode(self, window_size):
        self.screen = pygame.display.set_mode(window_size)
        self.fullscreen_mode = False
        self.rescale()

    def rescale(self, new_global_scale: float | None = None):
        if new_global_scale is not None:
            self.global_scale = new_global_scale
        w, h = self.screen.get_width(), self.screen.get_height()
        if self.aspect_ratio is None:
            self.xy_scale = w, h
        else:
            m = min(w, h)
            if m == h:
                self.xy_scale = self.global_scale * m, self.global_scale * m / self.aspect_ratio
            else:
                self.xy_scale = self.global_scale * m * self.aspect_ratio, self.global_scale * m

        self.width = w
        self.height = h

    def toggle_screen_mode(self):
        self.fullscreen_mode = not self.fullscreen_mode
        if self.fullscreen_mode:
            self.init_fullscreen_mode()
        else:
            self.init_window_mode(self.original_window_size)

    # @property
    # def scale(self):
    #     return min(self.width, self.height)

    # @property
    # def width(self):
    #     return self.screen.get_width()
    #
    # @property
    # def height(self):
    #     return self.screen.get_height()


    def draw_circle(self, color, center, radius, radius_in_pixels = False, width=0, **kwargs):
        pixel_width = max(int(width * self.xy_scale[0]), 1) if width != 0 else 0
        pygame.draw.circle(self.screen, color, self.world_to_screen(center), radius if radius_in_pixels else round(radius * self.xy_scale[0]), pixel_width, **kwargs)

    def draw_line(self, color, start_pos, end_pos, width=None):
        if width is None:
            width = 1 / min(*self.xy_scale)
        pixel_width = max(int(width * self.xy_scale[0]), 1) if width != 0 else 0
        pygame.draw.line(self.screen, color, self.world_to_screen(start_pos), self.world_to_screen(end_pos), pixel_width)

    def draw_polygon(self, color: tuple[int, int, int], points: tuple[tuple[float, float], ...], width: float | None = 0):
        if width is None:
            width = 1 / min(*self.xy_scale)
        pixel_width = max(int(width * self.xy_scale[0]), 1) if width != 0 else 0
        pygame.draw.polygon(self.screen, color, self.world_to_screen_points(points), pixel_width)

    def draw_text_list(self, info_list, font, color, pos, vspace):
        pos = self.world_to_screen(pos)
        for l, info in enumerate(info_list):
            info_render = font.render(info, True, color)
            self.screen.blit(info_render, (pos[0], pos[1] + vspace * l))

    def draw_mouse(self, ignore_global_scale=True):
        major_marker_size = 1 / 8
        minor_marker_size = 3 / 64
        major_width = 1 / self.height
        minor_width = 3 / self.height
        if ignore_global_scale:
            major_marker_size /= self.global_scale
            minor_marker_size /= self.global_scale
            major_width /= self.global_scale
            minor_width /= self.global_scale

        self.draw_cross(self.cols['mouse'], self.mouse_position, major_marker_size, major_width)
        self.draw_cross(self.cols['mouse'], self.mouse_position, minor_marker_size, minor_width)

        if self.left_click.state:
            self.draw_line(self.cols['mouse_left_drag'], self.left_click.press_pos, self.mouse_position)

        # if not self.left_click.state and self.left_click.release_pos is not None:
        #     self.draw_line(self.cols['mouse_left_drag'], self.left_click.press_pos, self.left_click.release_pos)

        if self.middle_click.state:
            self.draw_line(self.cols['mouse_middle_drag'], self.middle_click.press_pos, self.mouse_position)

        if self.right_click.state:
            self.draw_line(self.cols['mouse_right_drag'], self.right_click.press_pos, self.mouse_position)

    def draw_grid(self, color, step, width=None):
        if width is None:
            width = 1 / min(*self.xy_scale)
        for n in range(int(self.x_min / step) - 1, int(self.x_max / step) + 1):
            self.draw_line(color, (n * step, self.y_min), (n * step, self.y_max), width)
        for n in range(int(self.y_min / step) - 1, int(self.y_max / step) + 1):
            self.draw_line(color, (self.x_min, n * step), (self.x_max, n * step), width)

    def draw_cross(self, color, pos, size: float | tuple[float, float], width: float | None = None):
        if width is None:
            width = 1 / min(*self.xy_scale)
        if isinstance(size, float):
            size = (size, size)
        self.draw_line(color, (pos[0]-size[0]/2, pos[1]), (pos[0]+size[0]/2, pos[1]), width)
        self.draw_line(color, (pos[0], pos[1] - size[1] / 2), (pos[0], pos[1] + size[1] / 2), width)


    @property
    def mouse_position(self):
        x, y = self.screen_to_world(pygame.mouse.get_pos())
        if self.snap_to_grid:
            x = round(x / self.grid_step) * self.grid_step
            y = round(y / self.grid_step) * self.grid_step
        return x,y

    def screen_to_world(self, point: tuple[int, int]) -> tuple[float, float]:
        x = (point[0] - self.width // 2) * 2 / self.xy_scale[0]
        y = -(point[1] - self.height // 2) * 2 / self.xy_scale[1]
        return x, y

    def world_to_screen(self, point: tuple[float, float]) -> tuple[int, int]:
        screen_x = round(point[0] * self.xy_scale[0] / 2) + self.width // 2
        screen_y = -round(point[1] * self.xy_scale[1] / 2) + self.height // 2
        return screen_x, screen_y

    def world_to_screen_points(self, points: tuple[tuple[float, float], ...]) -> tuple[tuple[int, int], ...]:
        return tuple(self.world_to_screen(point) for point in points)


    @property
    def x_max(self):
        return self.width / self.xy_scale[0]

    @property
    def y_max(self):
        return self.height / self.xy_scale[1]

    @property
    def x_min(self):
        return -self.x_max

    @property
    def y_min(self):
        return -self.y_max



class MouseKey:
    def __init__(self):
        self.press_time = None
        self.release_time = None
        self.press_pos = None
        self.release_pos = None
        self.state = False

    def press(self, pos):
        self.press_time = pygame.time.get_ticks()
        self.press_pos = pos
        self.state = True

    def release(self, pos):
        self.release_time = pygame.time.get_ticks()
        self.release_pos = pos
        self.state = False


