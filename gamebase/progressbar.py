import pygame
import gamebase as gb
import random


class ProgressBar:
    def __init__(self,
                 canvas: gb.Canvas,
                 rect: gb.fRect | tuple[float, float, float, float],
                 min_value: float = 0.0,
                 max_value: float = 1.0,
                 initial_value: float = 0.5,
                 on_color=(200, 200, 200),
                 off_color=(60, 60, 60),
                 border_color=(120, 120, 120),
                 border_radius=0,
                 border_width=1,
                 active=True,
                 selectable=False,
                 orientation='horizontal',
                 show_particles=False
                 ):
        self.canvas = canvas
        if not isinstance(rect, gb.fRect):
            rect = gb.fRect(rect)
        self.rect = rect
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.on_color = on_color
        self.off_color = off_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.border_width = border_width
        self.active = active
        self.selectable = selectable
        self.orientation = orientation
        self.last_value = self.value
        self.show_particles = show_particles
        self.particles = gb.Particles(maxlen=60)

    def draw(self):
        if self.active:
            self.canvas.draw_rect(self.off_color, self.rect, border_radius=int(self.canvas.world_to_screen_f(self.border_radius)))
            x, y, w, h = self.rect
            t = (self.value-self.min_value) / (self.max_value-self.min_value)
            if self.orientation == 'horizontal':
                w = (t*w)
                x += (self.rect[2] - w)
            else:
                raise NotImplementedError

            self.canvas.draw_rect(self.on_color, (x, y, w, h), border_radius=int(self.canvas.world_to_screen_f(self.border_radius)))
            self.canvas.draw_rect(self.border_color, self.rect, border_radius=int(self.canvas.world_to_screen_f(self.border_radius)), width=self.border_width)

            if self.last_value != self.value and self.show_particles:
                for _ in range(random.randint(5, 8)):
                    self.particles.append(
                        gb.BallParticle(self.canvas,
                                        color=gb.lerp_vec3((230, 120, 60), (200,180,90), random.random()),
                                        radius=1/self.canvas.scale,
                                        pos=(x,random.uniform(y,y-h)),
                                        vel=(random.uniform(-.3,0), -random.uniform(-.2,.2)),
                                        dt=1 / 60,
                                        lifetime=.5,
                                        )
                    )
                self.particles.step()
                self.particles.draw()

            self.last_value = self.value

    def collision(self, point):
        if not self.selectable:
            return False
        xmin = self.rect[0]
        xmax = self.rect[0] + self.rect[2]
        ymin = self.rect[1]
        ymax = self.rect[1] + self.rect[3]
        return (xmin <= point[0] <= xmax) and (ymin <= point[1] <= ymax)

    def update(self, value):
        self.value = value
        self.draw()