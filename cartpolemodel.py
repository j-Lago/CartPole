import numpy as np
from collections import deque
import math


class CartPoleModel:
    def __init__(self, cart_mass, pole_mass, pole_length, x_damping, theta_damping, x0, th0, dt):
        self.ini = 0.
        self.x0 = x0
        self.th0 = th0
        self.L = pole_length
        self.M = cart_mass
        self.m = pole_mass
        self.d = x_damping
        self.q = theta_damping
        self.Famp = 35.
        self.g = -9.8

        self.Ki = dt * 0.5
        self.buf_size = 2

        self.dy = []
        self.y = []

        self.u = 0.
        self.k = 0
        self.reset()


    def reset(self):
        self.dy = []
        self.dy.append(deque([0.] * self.buf_size, maxlen=self.buf_size))
        self.dy.append(deque([0.] * self.buf_size, maxlen=self.buf_size))
        self.dy.append(deque([0.] * self.buf_size, maxlen=self.buf_size))
        self.dy.append(deque([0.] * self.buf_size, maxlen=self.buf_size))

        # th0 = self.ini + (np.random.random() -0.5)*1.4
        # x0 = (np.random.random() -0.5)*4
        th0 = self.th0
        x0 = self.x0

        self.y = []
        self.y.append(deque([x0]* self.buf_size, maxlen=self.buf_size))
        self.y.append(deque([0.]* self.buf_size, maxlen=self.buf_size))
        self.y.append(deque([th0]* self.buf_size, maxlen=self.buf_size))
        self.y.append(deque([0.]* self.buf_size, maxlen=self.buf_size))

        self.u = 0.
        self.k = 0


    @property
    def theta(self):
        theta = math.fmod(self.y[2][0], 2*math.pi)
        return theta if theta >= 0. else theta + 2*math.pi

    @property
    def x(self):
        return self.y[0][0]

    @property
    def v(self):
        return self.y[1][0]

    @property
    def omega(self):
        return self.y[3][0]

    @property
    def linear_acceleration(self):
        return (self.y[1][0] - self.y[1][1]) / (self.Ki*2)


    def step(self, u):
        self.k +=1
        self.u = u
        sin_th = np.sin(self.theta)
        cos_th = np.cos(self.theta)
        D = 1./(self.m*(self.L**2)*(self.M+self.m*(1-cos_th**2)))

        self.dy[0].appendleft(self.y[1][0])
        self.dy[1].appendleft(D*(- (self.m**2)*(self.L**2)*self.g*cos_th*sin_th
                                 + self.m*(self.L**2)*(self.m*self.L*(self.y[3][0]**2)*sin_th
                                 - self.d*self.y[1][0])
                                 + self.m*(self.L**2)* u))
        self.dy[2].appendleft(self.y[3][0])
        self.dy[3].appendleft(D*((self.m+self.M)*self.m*self.g*self.L*sin_th
                                 -self.m*self.L*cos_th*(self.m*self.L*(self.y[3][0]**2)*sin_th
                                 -self.d*self.y[1][0]
                                 +self.q*self.y[3][0])
                                 -self.m*self.L*cos_th*u))

        self.integrate(self.dy, self.y)
        self.y[2][0] = np.fmod(self.y[2][0], 2*np.pi)
        # px = np.sin(self.y[2][0]) * self.L + self.y[0][0]
        # py = -np.cos(self.y[2][0]) * self.L


    def integrate(self, i, o):
        # Ki = 2*pi/fa (fa=frequência de amostragem)
        # i - entrada (deque de pelo menos duas posições)
        # o - integral de i (deque de pelo menos duas posições)
        for k in range(4):
            o[k].appendleft(self.Ki * (i[k][0]+i[k][1]) + o[k][0])



