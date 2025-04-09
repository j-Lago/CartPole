from canvas import Canvas
from popup import PopUp
from _collections import deque
from lerp import lerp_vec3
import math
from itertools import islice

class Scope(PopUp):
    def __init__(self, *args, maxlen: int = 400, color=(255, 255, 255), rolling: bool = True, x_scale: float = 1.0, y_scale: float = 1.0, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = deque(maxlen=maxlen)
        self.rolling = rolling
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.color = color
        self.focus = False
        self.draw_fun = self.default_draw

    def __len__(self):
        return len(self.data)

    @property
    def maxlen(self):
        return self.data.maxlen

    def append(self, x, y):
        self.data.append((x, y))


    def clear(self):
        self.data.clear()


    def default_draw(self, canvas: Canvas):

        L = 100

        rect = canvas.get_world_rect()
        xmin, xmax = rect[0], rect[0] + rect[2]
        ymin, ymax = rect[1] - rect[3], rect[1]
        w = rect[2]
        N = int(L / self.x_scale)
        xscale = (xmax - xmin) / L * 60 * self.x_scale
        yscale = (ymax - ymin) / 2  *  self.y_scale
        xbias = xmin

        color = self.color
        color_line = color
        color_grid = lerp_vec3(color, (30, 30, 30), 0.7)
        color_bf = lerp_vec3(color, (30, 30, 30), 0.9)
        width = 2

        canvas.draw_rect(color_bf, rect, 0, 15)

        canvas.draw_line(color_grid, (xmin, 0), (xmax, 0), 1)
        canvas.draw_line(color_grid, (0, ymin), (0, ymax), 1)


        def remap_x(x, scale, bias, lim, shift=0):
            return ((x * scale + shift) % lim) + bias


        if len(self.data) > 1:
            x = self.data[-1][0]
            x0 = self.data[-2][0]

            xx = remap_x(x, xscale, xbias, w)
            xx0 = remap_x(x0, xscale, xbias, w)

            if xx < xx0 and not self.rolling:
                self.clear()

        if len(self.data) > 2:

            data_slice = islice(self.data, max(0, len(self) - N), len(self.data) - 1)
            if not self.rolling:
                seq = [(remap_x(xx, xscale, xbias, w), yy * yscale) for xx, yy in data_slice]
            else:
                seq = [(remap_x(xx, xscale, xbias, w, shift= w - x * xscale), yy * yscale) for xx, yy in data_slice]
            seq = sorted(seq, key=lambda pair: pair[0])

            canvas.draw_lines(color_line, False, seq, width)
            # canvas.draw_circle(color, seq[-1], .035)

        if self.focus:
            color = (255, 255, 0)

        canvas.draw_rect(color, rect, width, 15)

