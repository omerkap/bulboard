import numpy as np
from abstract_screen_usage import AbstractScreenUsage
import matplotlib.pyplot as plt


class Sovsov(AbstractScreenUsage):
    SCALE = 5
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
        self.a *= 2 * self.SCALE
        print self.a
        self.connecting_points = ([0,1],[1,2],[2,3],[3,0],
                             [4,1],[5,6],[6,7],[7,4],
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
        return self.get_drawable()

    def get_drawable(self):
        projected_a = self.a[:2]
        projected_a = np.transpose(projected_a)
        drawable = np.zeros((self.BOARD_SIZE[0]*self.SCALE,self.BOARD_SIZE[1]*self.SCALE))
        for point in projected_a:
            drawable[round(point[0] + self.DRAW_ORIGIN[0]*self.SCALE),
                     round(point[1] + self.DRAW_ORIGIN[1]*self.SCALE)] = 1
        return drawable

