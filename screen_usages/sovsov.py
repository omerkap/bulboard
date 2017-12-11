import numpy as np
import math
from abstract_screen_usage import AbstractScreenUsage
try:
    import matplotlib.pyplot as plt
except ImportError as ex:
    print ex


class Sovsov(AbstractScreenUsage):
    SCALE = 10
    BOARD_SIZE = [17,11]
    DRAW_ORIGIN = [8, 5]

    def __init__(self, phi, dtheta_self, dtheta_inclined, shift_origin):
        self.a= np.asarray(([-1., 1., 1.],
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1,1,-1],
            [-1,-1,-1],
            [1,-1,-1],
            [1,1,-1]))
        self.a *= 3 * self.SCALE
        print self.a
        self.lines = ([0,1],[1,2],[2,3],[3,0],
                        [4,5],[5,6],[6,7],[7,4],
                        [0,4],[1,5],[2,6],[3,7])
        self.shift(shift_origin[0], shift_origin[1], shift_origin[2])
        self.a = np.transpose(self.a)
        self.phi = phi
        self.theta_inclined = 0
        self.dtheta_self = np.deg2rad(dtheta_self)
        self.dtheta_inclined = np.deg2rad(dtheta_inclined)
        self.spin_y(self.phi)

    # screen horizontal is x, vertical is y and depth is z
    def shift(self,x,y,z):
        self.a[:, 0] += x
        self.a[:, 1] += y
        self.a[:, 2] += z

    def spin_x(self,theta):
        spin = ([1,0,0],[0,np.cos(theta),-np.sin(theta)],[0,np.sin(theta),np.cos(theta)])
        self.a = np.dot(spin,self.a)

    def spin_y(self,theta):
        spin = ([np.cos(theta),0,np.sin(theta)],[0,1,0],[-np.sin(theta),0,np.cos(theta)])
        self.a = np.dot(spin,self.a)

    def spin_z(self,theta):
        spin = ([np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1])
        self.a = np.dot(spin,self.a)

    def get_next_step(self):
        self.spin_z(-self.theta_inclined)
        self.spin_y(-self.phi)
        self.spin_z(self.dtheta_self)
        self.spin_y(self.phi)
        self.theta_inclined = self.theta_inclined + self.dtheta_inclined
        self.spin_z(self.theta_inclined)
        return self.get_drawable(render_lines= 1)

    def get_drawable(self, render_lines):
        projected_a = self.a[:2]
        projected_a = np.transpose(projected_a)
        drawable = np.zeros((self.BOARD_SIZE[0]*self.SCALE,self.BOARD_SIZE[1]*self.SCALE))
        if (render_lines == 0):
            for point in projected_a:
                drawable[round(point[0] + self.DRAW_ORIGIN[0]*self.SCALE),
                         round(point[1] + self.DRAW_ORIGIN[1]*self.SCALE)] = 1
        else:
            res_enhance = 2
            for line in self.lines:
                p0 = projected_a[line[0]]
                p1 = projected_a[line[1]]
                vector = p1 - p0
                vector_length = math.sqrt(vector[0]**2 + vector[1]**2)
                vector /= vector_length #normalized
                for step in range(0,int(math.floor(vector_length*res_enhance))):
                    next_p = p0 + vector/res_enhance*step
                    drawable[self.DRAW_ORIGIN[0] * self.SCALE + next_p[0],
                             self.DRAW_ORIGIN[1] * self.SCALE + next_p[1]] = 1
        return drawable

