import gamebase as gb
import states as st
from bindings import *


class Settings(st.GameState):
    def __init__(self, game):
        super().__init__(game)
        self.previous_state = None
        # self.menu = gb.PopUp(main_canvas=self.game.active_canvas, size=(200, 150), bg_color=(200,180,90), fonts=self.game.fonts, draw_fun=draw_settings, got_focus_callback=None)

        self.buttons_p1 = dict()
        h = .1
        py = .015
        w = 0.5

        y0 = 0.9
        y = y0
        x = 0.26
        for key, input_ in self.game.inputs.items():
            self.buttons_p1[key] = gb.BaseButton(self.game.canvas, (x, y, w, h), key,
                                                 font=self.game.fonts['medium'],
                                                 custom_callback=self.select_bt_p1,
                                                 selected=input_ is self.game.players['p1'].input,
                                                 bg_selected_color=self.game.players['p1'].base_color,
                                                 selected_color=self.game.players['p1'].base_color,
                                                 font_selected_color=self.game.cols['bg'],
                                                 focus_color=self.game.players['p1'].base_color,
                                                 font_focus_color=self.game.players['p1'].base_color,
                                                 border_width=2,
                                                 )
            y -= h + py

        dw, dh = w, h * len(self.game.inputs) + py * (len(self.game.inputs) - 1)
        self.buttons_p1_dummy = gb.BaseButton(
            self.game.canvas, (x - w - py, y0, dw, dh),
            text='P1', font=self.game.fonts['huge'],
            selectable=False,
            bg_unselectable_color=self.game.players['p1'].base_color,
            font_unselectable_color=self.game.cols['bg'],
        )

        self.frame_rgb1 = gb.Frame(self.game.canvas, (x-2*dw-2*py, y0, dw, dh), alpha=255, bg_color=self.game.cols['bg'], origin='topleft')
        self.slider_r1 = gb.Slider(self.frame_rgb1, (0.05, -0.05, 0.10, 0.5), text='r', font=self.game.fonts['small'], min_value=0, max_value=255, init_value=self.game.players['p1'].base_color[0], bg_color=self.game.cols['bg'] ,fg_color=(255,60,60))
        self.slider_g1 = gb.Slider(self.frame_rgb1, (0.20, -0.05, 0.10, 0.5), text='g', font=self.game.fonts['small'], min_value=0, max_value=255, init_value=self.game.players['p1'].base_color[1], bg_color=self.game.cols['bg'] ,fg_color=(60,255,60))
        self.slider_b1 = gb.Slider(self.frame_rgb1, (0.35, -0.05, 0.10, 0.5), text='b', font=self.game.fonts['small'], min_value=0, max_value=255, init_value=self.game.players['p1'].base_color[2], bg_color=self.game.cols['bg'] ,fg_color=(60,60,255))



        self.buttons_p2 = dict()
        y0 = -0.28
        y = y0
        for key, input_ in self.game.inputs.items():
            self.buttons_p2[key] = gb.BaseButton(self.game.canvas, (x, y, w, h), key,
                                                 font=self.game.fonts['medium'],
                                                 custom_callback=self.select_bt_p2,
                                                 selected=input_ is self.game.players['p2'].input,
                                                 bg_selected_color=self.game.players['p2'].base_color,
                                                 selected_color=self.game.players['p2'].base_color,
                                                 font_selected_color=self.game.cols['bg'],
                                                 focus_color=self.game.players['p2'].base_color,
                                                 font_focus_color=self.game.players['p2'].base_color,
                                                 )
            y -= h + py
        dw, dh = w, h * len(self.game.inputs) + py * (len(self.game.inputs) - 1)
        self.buttons_p2_dummy = gb.BaseButton(
            self.game.canvas, (x - w - py, y0, dw, dh),
            text='P2', font=self.game.fonts['huge'],
            selectable=False,
            bg_unselectable_color=self.game.players['p2'].base_color,
            font_unselectable_color=self.game.cols['bg'],
        )


        self.frame_rgb2 = gb.Frame(self.game.canvas, (x-2*dw-2*py, y0, dw, dh), alpha=255, bg_color=self.game.cols['bg'], origin='topleft')
        self.slider_r2 = gb.Slider(self.frame_rgb2, (0.05, -0.05, 0.10, 0.5), text='r', font=self.game.fonts['small'], min_value=0, max_value=255, init_value=self.game.players['p2'].base_color[0], bg_color=self.game.cols['bg'] ,fg_color=(255,60,60))
        self.slider_g2 = gb.Slider(self.frame_rgb2, (0.20, -0.05, 0.10, 0.5), text='g', font=self.game.fonts['small'], min_value=0, max_value=255, init_value=self.game.players['p2'].base_color[1], bg_color=self.game.cols['bg'] ,fg_color=(60,255,60))
        self.slider_b2 = gb.Slider(self.frame_rgb2, (0.35, -0.05, 0.10, 0.5), text='b', font=self.game.fonts['small'], min_value=0, max_value=255, init_value=self.game.players['p2'].base_color[2], bg_color=self.game.cols['bg'] ,fg_color=(60,60,255))


    def __str__(self):
        return 'Settings'

    def enter(self):
        self.game.clock.pause()

    def exit(self):
        gb.DragLock.remove(self.frame_rgb1)
        gb.DragLock.remove(self.frame_rgb2)

        self.game.clock.resume()

    def handle_event(self, event: pygame.event):
        # if bind_test(event, ABORT_NEW_SETTINGS):
        #     self.change_state(self.previous_state)
        if bind_test(event, CONFIRM_NEW_SETTINGS):
            self.change_state(st.Intro(self.game))

    def draw(self, canvas: gb.Canvas):
        if self.game.previous_state_screenshot is not None:
            self.game.previous_state_screenshot.set_alpha(127)
            canvas.blit(self.game.previous_state_screenshot, canvas.topleft)
        canvas.draw_text((200, 200, 180), self.game.fonts['huge'], f'SETTINGS', (0, 0))
        canvas.draw_text((200, 200, 180), self.game.fonts['medium'], f'Press ENTER to confirm and restart', (0, -.2))

        for key, button in self.buttons_p1.items() | self.buttons_p2.items():
            button.selectable = self.game.inputs[key].active_player_key is None
            button.update(self.game)

        self.buttons_p1_dummy.draw()
        self.buttons_p2_dummy.draw()
        self.frame_rgb1.update(self.game)
        self.frame_rgb2.update(self.game)

        #update colors
        self.game.players['p1'].base_color = self.slider_r1.value, self.slider_g1.value, self.slider_b1.value
        self.buttons_p1_dummy.bg_unselectable_color = self.game.players['p1'].base_color
        self.game.players['p1'].progress_fuel.on_color = self.game.players['p1'].base_color
        for key, input_ in self.game.inputs.items():
            self.buttons_p1[key].bg_selected_color=self.game.players['p1'].base_color
            self.buttons_p1[key].selected_color=self.game.players['p1'].base_color
            self.buttons_p1[key].focus_color=self.game.players['p1'].base_color
            self.buttons_p1[key].font_focus_color=self.game.players['p1'].base_color

        self.game.players['p2'].base_color = self.slider_r2.value, self.slider_g2.value, self.slider_b2.value
        self.buttons_p2_dummy.bg_unselectable_color = self.game.players['p2'].base_color
        self.game.players['p2'].progress_fuel.on_color = self.game.players['p2'].base_color
        self.game.scopes['p2'].color = self.game.players['p2'].base_color
        for key, input_ in self.game.inputs.items():
            self.buttons_p2[key].bg_selected_color=self.game.players['p2'].base_color
            self.buttons_p2[key].selected_color=self.game.players['p2'].base_color
            self.buttons_p2[key].focus_color=self.game.players['p2'].base_color
            self.buttons_p2[key].font_focus_color=self.game.players['p2'].base_color

    def select_bt(self, pressed_button: gb.BaseButton, player, buttons):
        for key, button in buttons.items():
            button.selected = button == pressed_button
            if button.selected:
                player.input.active_player_key = None
                player.input = self.game.inputs[key]
                player.input.active_player_key = player.name

    def select_bt_p1(self, pressed_button: gb.BaseButton):
        self.select_bt(pressed_button, self.game.players['p1'], self.buttons_p1)

    def select_bt_p2(self, pressed_button: gb.BaseButton):
        self.select_bt(pressed_button, self.game.players['p2'], self.buttons_p2)




