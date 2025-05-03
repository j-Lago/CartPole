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
        l = (end-start).magnitude()

        frame_distance = (end-start).magnitude()
        for line in self.interference_lines:

            # ext_end = gb.lerp_vec2(start, end, 1+self.radius/l) if l != 0 else end
            # norm = Vector2(*line).rotate(90)
            # ext_end = end + norm*self.radius
            # inter = gb.find_lines_intersection(end, ext_end, line[0], line[1])
            # if inter is not None:
            distance, closest_point = gb.point_line_distance(end, line[0], line[1])
            if distance <= self.radius:

                delta = frame_distance
                overlap = min(1.0, (self.radius-distance) / delta) if delta != 0 else 0.0

                iter = gb.find_lines_intersection((0, 0), self.vel, line[0], line[1], True, True)
                if iter is None:
                    continue

                _, dir = iter
                # pos = collision_point -norm * self.radius
                # l = (collision_point-start).magnitude()
                # pos = gb.lerp_vec2(start, collision_point, 1-self.radius/l)

                # self.collision_points.append(self.pos)
                super().step_rewind_dt(overlap*self.dt)

                # self.collision_rewind_points.append(self.pos)


                vel_mag = self.vel.magnitude()
                # if vel_mag < self.min_vel*2:
                #     vel_mag = vel_mag*self.collision_decay**2
                #     if vel_mag < self.min_vel:
                #         vel_mag = 0.0
                self.vel = dir * vel_mag * self.collision_decay

                super().step_dt(overlap*self.dt)
                # self.collision_corrected_points.append(self.pos)

            # for point in self.collision_points:
            #     self.canvas.draw_circle((240, 90, 90), point, self.radius, 2)
            #
            # for point in self.collision_rewind_points:
            #     self.canvas.draw_circle((90, 255, 90), point, self.radius, 2)
            #
            # for point in self.collision_corrected_points:
            #     self.canvas.draw_circle((90, 90, 255), point, self.radius, 2)





    def draw(self):
        if self.alive:
            self.canvas.draw_circle(self.color, (self.x, self.y), self.radius, self.radius_in_pixels)