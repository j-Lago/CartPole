import gamebase as gb
import states as st
from bindings import *


class Settings(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.previous_state = None
        # self.menu = gb.PopUp(main_canvas=self.game.active_canvas, size=(200, 150), bg_color=(200,180,90), fonts=self.game.fonts, draw_fun=draw_settings, got_focus_callback=None)

        self.buttons = dict()
        y, h, py = 0.8, 0.18, .02
        x, w = -0.4, 0.6
        for key, input_ in self.game.inputs.items():
            self.buttons[key] = gb.Button(self.game.active_canvas, (x, y, w, h), key, font=self.game.fonts['normal'], custom_callback=self.select_bt, selected=input_ is self.game.players['p1'].input)
            y -= h + py

        # self.buttons = {
        #     'label': gb.Button(self.game.active_canvas, (0.0, 0.8, .36, .58), 'P1', font=self.game.fonts['big'], selectable=False),
        #     'bt1': gb.Button(self.game.active_canvas, (0.4, 0.4, .6, .18), 'Button 1', font=self.game.fonts['normal'], custom_callback=self.select_bt),
        #     'bt2': gb.Button(self.game.active_canvas, (0.4, 0.6, .6, .18), 'Button 2', font=self.game.fonts['normal'], custom_callback=self.select_bt),
        #     'bt3': gb.Button(self.game.active_canvas, (0.4, 0.8, .6, .18), 'Button 3', font=self.game.fonts['normal'], custom_callback=self.select_bt),
        # }

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


        for key, button in self.buttons.items():
            button.update(self.game)

    def select_bt(self, pressed_button: gb.Button):
        for key, button in self.buttons.items():
            button.selected = button == pressed_button
            if button.selected:
                self.game.players['p1'].input = self.game.inputs[key]


