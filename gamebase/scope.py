import gamebase as gb
from _collections import deque
from pygame import Vector2
from itertools import islice
import colorsys


class Scope(gb.PopUp):
    def __init__(self, *args, fps, name: str = '', maxlen: int = 400, color=(0, 255, 255), line_colors=None, legend=None, focus_color=(255, 255, 0), rolling: bool = True, x_scale: float = 1.0, y_scale: float | tuple[float, ...] = 1.0, grid_lerp_factor: float = 0.6, bg_lerp_factor: float = 0.9, border_width: int = 2, border_radius: int = 13, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_lerp_factor = bg_lerp_factor
        self.grid_lerp_factor = grid_lerp_factor
        self.fps = fps
        self.data = deque(maxlen=maxlen)
        self.title = name
        self.rolling = rolling
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.color = color
        self.line_colors = line_colors
        self.focus_color = focus_color
        self.focus = False
        self.draw_fun = self.default_draw
        self.border_width = border_width
        self.border_radius = border_radius
        self._legends = None
        self.set_legend(legend)

    @property
    def get_legend(self):
        return self._legends

    def set_legend(self, leg):
        if leg is not None:
            if isinstance(leg, str):
                leg = (leg, )
            self._legends = leg

    def __len__(self):
        return len(self.data)

    @property
    def maxlen(self):
        return self.data.maxlen

    def append(self, x, y):
        if isinstance(y, float | int):
            y = (y, )
        self.data.append((x, y))

    def clear(self):
        self.data.clear()
        # print(f'{self.name} cleared')


    def default_draw(self, canvas: gb.Canvas):

        L = 100

        rect = canvas.get_rect()
        xmin, xmax = rect[0], rect[0] + rect[2]
        ymin, ymax = rect[1] - rect[3], rect[1]
        w = rect[2]
        N = int(L / self.x_scale)

        xscale = (xmax - xmin) / L * self.fps * self.x_scale
        xbias = xmin

        color = self.color
        ch, cs, cv = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
        if self.focus:
            color = self.focus_color

        color_grid = gb.lerp_vec3(color, (30, 30, 30), self.grid_lerp_factor)
        color_bf = gb.lerp_vec3(color, (30, 30, 30), self.bg_lerp_factor)

        canvas.draw_rect(color_bf, rect, 0, 15)

        canvas.draw_line(color_grid, (xmin, 0), (xmax, 0), 1)
        canvas.draw_line(color_grid, (0, ymin), (0, ymax), 1)


        def remap_x(x, scale, bias, lim, shift=0):
            return ((x * scale + shift) % lim) + bias


        if len(self.data) > 1:
            ys = self.data[-1][1]
            x = self.data[-1][0]
            x0 = self.data[-2][0]

            xx = remap_x(x, xscale, xbias, w)
            xx0 = remap_x(x0, xscale, xbias, w)

            y_scales = self.y_scale
            if isinstance(y_scales, float | int):
                y_scales = (y_scales,)*len(ys)
            y_scales = tuple((ymax - ymin) / 2  * ys  for ys in y_scales)

            if xx < xx0 and not self.rolling:
                self.clear()

            if self.line_colors is None:
                if len(ys) == 1:
                    self.line_colors = list(gb.ColorsDiscIterator(len(ys), ch, cs, cv))
                else:
                    self.line_colors = list(gb.ColorsDiscIterator(len(ys), ch, min(cs*1.2, 1.0), min(cv*1.2, 1.0)))

            if len(self.data) > 2:
                for i in range(len(ys)):
                    color_line = self.line_colors[i]

                    data_slice = islice(self.data, max(0, len(self.data) - N), len(self.data) - 1)
                    if not self.rolling:
                        seq = [(remap_x(xx, xscale, xbias, w), yy[i] * y_scales[i]) for xx, yy in data_slice]
                    else:
                        seq = [(remap_x(xx, xscale, xbias, w, shift= w - x * xscale), yy[i] * y_scales[i]) for xx, yy in data_slice]
                    seq = sorted(seq, key=lambda pair: pair[0])

                    canvas.draw_lines(color_line, False, seq, self.border_width)
                    # canvas.draw_circle(color_line, seq[-1], .045)

        canvas.draw_text(color=color, font=self.main_canvas.fonts['scope_title'], text=self.title, pos=(0, ymax), shift=(0, -0.05), anchor='midtop')
        y_pad = .06
        x_pad = .06
        if self._legends is not None and self.line_colors is not None:
            for i, leg in enumerate(reversed(self._legends)):
                # _, _, _, h = canvas.draw_text(color=self.line_colors[i], font=self.main_canvas.fonts['tiny'], text=self._legends[i], pos=Vector2(0, -2)+canvas.screen_to_world_v2((x_pad, -y_pad)), anchor='bottomleft')
                _, _, _, h = canvas.draw_text(color=self.line_colors[i], font=self.main_canvas.fonts['scope_label'],
                                              text=self._legends[i],
                                              pos=Vector2(xmin, ymin) + (x_pad, y_pad),
                                              anchor='bottomleft')
                y_pad += h


        canvas.draw_rect(color, rect, self.border_width, 15)

