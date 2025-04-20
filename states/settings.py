import gamebase as gb
import states as st
from bindings import *


class Settings(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.previous_state = None
        # self.menu = gb.PopUp(main_canvas=self.game.active_canvas, size=(200, 150), bg_color=(200,180,90), fonts=self.game.fonts, draw_fun=draw_settings, got_focus_callback=None)
        self.menu = gb.Button(self.game.active_canvas, (0.4, 0.4, .6, .4), 'Teste', font=self.game.fonts['normal'])

    def __str__(self):
        return 'Settings'

    def enter(self):
        self.game.clock.pause()

    def exit(self):
        self.game.clock.resume()

    def handle_event(self, event: pygame.event):
        if bind_test(event, ABORT_NEW_SETTINGS):
            self.change_state(self.previous_state)
        if bind_test(event, CONFIRM_NEW_SETTINGS):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        if self.game.previous_state_screenshot is not None:
            self.game.previous_state_screenshot.set_alpha(127)
            canvas.blit(self.game.previous_state_screenshot, canvas.topleft)
        canvas.draw_text((200, 200, 180), self.game.fonts['huge'], f'SETTINGS', (0, 0))
        canvas.draw_text((200, 200, 180), self.game.fonts['medium'], f'Press ENTER to confirm new settings or ESC to resume', (0, -.2))

        self.menu.update(self.game)
        # self.menu.focus(self.game.mouse_world_pos)
        # self.menu.draw()


# def draw_settings(canvas: gb.Canvas):
    # canvas.fill((255,255,255))
    # canvas.draw_text((255, 255, 0), canvas.fonts['normal'], 'teste', (-0, 0))
