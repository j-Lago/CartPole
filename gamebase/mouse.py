
import pygame
from copy import copy
from pygame import Vector2
import gamebase as gb

class MouseButton:
    def __init__(self):
        self.press_time = None
        self.release_time = None
        self.presspos = None
        self.releasepos = None
        self.dragpos = None
        self.press_keys = None
        self.release_keys = None
        self.drag_keys = None
        self.pressed = False
        self.dragging = False
        self.press_callback = None
        self.release_callback = None
        self.drag_callback = None

    def press(self, pos, keys):
        self.press_keys = copy(keys)
        self.press_time = pygame.time.get_ticks()
        self.presspos = pos
        self.pressed = True
        if self.press_callback is not None:
            self.press_callback(self)

    def release(self, pos, keys):
        self.release_keys = copy(keys)
        self.release_time = pygame.time.get_ticks()
        self.releasepos = pos
        self.pressed = False
        self.dragpos = pos
        self.dragging = False
        if self.release_callback is not None:
            self.release_callback(self)

    def drag(self, pos, keys):
        self.drag_keys = copy(keys)
        self.dragpos = pos
        self.dragging = True
        if self.drag_callback is not None:
            self.drag_callback(self)

    def clear_drag_delta(self):
        self.presspos = self.dragpos


    @property
    def drag_delta(self):
        return self.dragpos[0]-self.presspos[0], self.dragpos[1]-self.presspos[1]


class MouseScroll:
    def __init__(self):
        self.up_callback = None
        self.down_callback = None
        self.up_keys = None
        self.down_keys = None
        self.uppos = None
        self.downpos = None

    def up(self, pos, keys):
        self.up_keys = copy(keys)
        self.uppos = pos
        if self.up_callback is not None:
            self.up_callback(self)

    def down(self, pos, keys):
        self.down_keys = copy(keys)
        self.downpos = pos
        if self.down_callback is not None:
            self.down_callback(self)


class Mouse:
    def __init__(self, game: gb.BaseScreen):
        self.game = game
        self.left = MouseButton()
        self.right = MouseButton()
        self.middle = MouseButton()
        self.scroll = MouseScroll()

    def set_visible(self, visibility):
        pygame.mouse.set_visible(visibility)

    @property
    def screen_pos(self):
        return Vector2(pygame.mouse.get_pos())

    @property
    def pos(self):
        return self.game.canvas.screen_to_world_v2(gb.remap(pygame.mouse.get_pos(), self.game.window, self.game.canvas))

    # @pos.setter
    # def pos(self, pos: Vector2):
    #     screen_pos = gb.remap(self.canvas.world_to_screen_v2(pos), self.canvas, self.window)
    #     pygame.mouse.set_pos(screen_pos)

    def handle_event(self, event, keys):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.left.press(event.pos, keys)
            if event.button == 2:
                self.middle.press(event.pos, keys)
            if event.button == 3:
                self.right.press(event.pos, keys)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.left.release(event.pos, keys)
            if event.button == 2:
                self.middle.release(event.pos, keys)
            if event.button == 3:
                self.right.release(event.pos, keys)

        if event.type == pygame.MOUSEMOTION:
            if self.left.pressed:
                self.left.drag(event.pos, keys)
            if self.middle.pressed:
                self.middle.drag(event.pos, keys)
            if self.right.pressed:
                self.right.drag(event.pos, keys)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll.down(event.pos, keys)
            if event.button == 5:
                self.scroll.up(event.pos, keys)
