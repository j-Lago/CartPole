import math
import gamebase as gb
from gamebase.canvas import Canvas
from pygame import Vector2


class BallCollidableParticle(gb.Particle):
    def __init__(self, canvas: Canvas, color, radius, radius_in_pixels=False, *args, collision_decay: float = 0.7, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.canvas = canvas
        self.radius = radius
        self.radius_in_pixels = radius_in_pixels
        self.collision_decay = collision_decay
        self.interference_lines = []

    def step(self):

        for line in self.interference_lines:
            start = self.pos
            super().step()
            end = self.pos

            # l = (end-start).magnitude()
            # end = gb.lerp_vec2(start, end, 1+self.radius/l)
            #
            # inter = gb.find_lines_intersection(start, end, line[0], line[1])
            # if inter is not None:
            #     self.vel_y *= -self.collision_decay
            #     x, y = inter
            #     y += self.radius
            #     self.y = y
            #
            if gb.circle_line_collision(self.pos, self.radius, line[0], line[1]):
                self.vel_y *= -self.collision_decay
                x, y = gb.find_lines_intersection(start, self.pos, line[0], line[1], True)
                y += self.radius
                self.y = y


    def draw(self):
        if self.alive:
            self.canvas.draw_circle(self.color, (self.x, self.y), self.radius, self.radius_in_pixels)