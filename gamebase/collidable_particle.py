import math
import gamebase as gb
from gamebase.canvas import Canvas
from pygame import Vector2


class BallCollidableParticle(gb.Particle):
    def __init__(self, canvas: Canvas, color, radius, radius_in_pixels=False, *args, min_vel=0.05, collision_decay: float = 0.7, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.canvas = canvas
        self.radius = radius
        self.min_vel = min_vel
        self.radius_in_pixels = radius_in_pixels
        self.collision_decay = collision_decay
        self.interference_lines = []
        # self.collision_points = []
        # self.collision_rewind_points = []
        # self.collision_corrected_points = []

    def step(self):
        start = self.pos
        super().step()
        end = self.pos

        frame_distance = (end-start).magnitude()
        for line in self.interference_lines:

            crossing = gb.find_lines_intersection(start1=start, end1=end, start2=line[0], end2=line[1])
            distance, closest_point = gb.point_line_distance(end, line[0], line[1])
            if distance <= self.radius or crossing:
                overlap = max(0.0, min(1.0, (self.radius - distance) / frame_distance) if frame_distance != 0 else 0.0)

                iter = gb.find_lines_intersection((0, 0), self.vel, line[0], line[1], True, True)
                if iter is None:
                    continue

                _, dir = iter
                super().step_rewind_dt((1-overlap)*self.dt)
                start = self.pos

                vel_mag = self.vel.magnitude()
                # if vel_mag < self.min_vel*2:
                #     vel_mag = vel_mag*self.collision_decay**2
                #     if vel_mag < self.min_vel:
                #         vel_mag = 0.0
                self.vel = dir * vel_mag * self.collision_decay

                super().step_dt((overlap) * self.dt)
                end = self.pos




    def draw(self):
        if self.alive:
            self.canvas.draw_circle(self.color, (self.x, self.y), self.radius, self.radius_in_pixels)