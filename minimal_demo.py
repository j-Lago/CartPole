import lerp
from basescreen import BaseScreen
from canvas import Canvas
from math import sin, cos, pi, fmod
from lerp import lerp_vec3

class MinimalDemo(BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvases['main'] = Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)

    def draw_main(self, canvas: Canvas):
        blue = (30, 60, 255)
        red = (255, 30, 60)
        yellow = (255, 200, 30)
        for n in range(N := 400):
            color = lerp_vec3(blue, red, n/N)
            th = fmod(self.t*2, 2*pi)+3*pi*n/N
            h = cos(self.t/2) + 2
            r = cos(h*th) * 0.5
            canvas.draw_circle(color, (r * cos(th), r * sin(th)), .08)
        canvas.draw_text(yellow, self.fonts['huge'], f'{self.t:.1f}s', (0, 0))



if __name__ == '__main__':
    MinimalDemo()
