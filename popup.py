from canvas import Canvas


class PopUp(Canvas):
    def __init__(self, main_canvas, *args, pos=(0, 0), alpha=255, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_canvas = main_canvas
        self.pos = pos
        self.set_alpha(alpha)


    def blit_to_main(self):
        dest = self.main_canvas
        dest.blit(self, self.pos)


