

import pygame
from copy import copy

class MouseButton:
    def __init__(self):
        self.press_time = None
        self.release_time = None
        self.press_pos = None
        self.release_pos = None
        self.drag_pos = None
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
        self.press_pos = pos
        self.pressed = True
        if self.press_callback is not None:
            self.press_callback(self)

    def release(self, pos, keys):
        self.release_keys = copy(keys)
        self.release_time = pygame.time.get_ticks()
        self.release_pos = pos
        self.pressed = False
        self.drag_pos = pos
        self.dragging = False
        if self.release_callback is not None:
            self.release_callback(self)

    def drag(self, pos, keys):
        self.drag_keys = copy(keys)
        self.drag_pos = pos
        self.dragging = True
        if self.drag_callback is not None:
            self.drag_callback(self)

    @property
    def drag_delta(self):
        return self.drag_pos[0]-self.press_pos[0], self.drag_pos[1]-self.press_pos[1]


class MouseScroll:
    def __init__(self):
        self.up_callback = None
        self.down_callback = None
        self.up_keys = None
        self.down_keys = None
        self.up_pos = None
        self.down_pos = None

    def up(self, pos, keys):
        self.up_keys = copy(keys)
        self.up_pos = pos
        if self.up_callback is not None:
            self.up_callback(self)

    def down(self, pos, keys):
        self.down_keys = copy(keys)
        self.down_pos = pos
        if self.down_callback is not None:
            self.down_callback(self)


class Mouse:
    def __init__(self):
        self.left = MouseButton()
        self.right = MouseButton()
        self.middle = MouseButton()
        self.scroll = MouseScroll()

    def process_event(self, event, keys):
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
