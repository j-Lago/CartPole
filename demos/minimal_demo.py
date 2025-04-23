import gamebase as gb


class MinimalDemo(gb.BaseScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvases['main'] = gb.Canvas(self.canvas_size, fonts=self.fonts, draw_fun=self.draw_main)
        self.mouse.set_visible(False)
        # self.show_info()

    def draw_main(self, canvas: gb.Canvas):
        pos = self.mouse_world_pos

        points = gb.fPoints((0, 0), (0.4, 0.2), (0.4, 0.6))

        canvas.draw_polygon((255, 255, 255), points, 2)
        canvas.draw_polygon((255, 255, 0), points.translate(pos), 2)
        canvas.draw_polygon((255, 0, 255), points.rotate(self.clock.t, (0, 0)), 2)
        canvas.draw_polygon((0, 255, 255), points.scale((-1.5, 0.5)), 2)
        canvas.draw_rect((0, 255, 0), points.rotate(self.clock.t, (0, 0)).rect(), 2)

        canvas.draw_text((255, 190, 30), self.fonts['huge'], f'{self.t:.1f}s', (-1.2, -0.75))
        canvas.draw_circle((200, 200, 200), pos, .015)
        canvas.draw_text((200, 200, 200), self.fonts['small'], f'({pos[0]:.2f}, {pos[1]:.2f})', pos, anchor='midtop',
                         shift=(0, -0.03))


if __name__ == '__main__':
    MinimalDemo()


