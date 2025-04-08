from canvas import Canvas


class PopUp(Canvas):
    def __init__(self, main_canvas, *args, pos = (0, 0), **kwargs):
        super().__init__(*args, **kwargs)
        self.main_canvas = main_canvas
        self.pos = pos

    def blit_to_main(self):
        dest = self.main_canvas
        dest.blit(self, self.pos)


