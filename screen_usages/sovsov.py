import numpy as np

class Sovsov(object):
    BOARD_SIZE = [17,11]
    ORIGIN = [8,5]
    def __init__(self, phi, dtheta_self, dtheta_inclined, shift_origin):
        self.a= ([-1, 1, 1],
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1,1,-1],
            [-1,-1,-1],
            [1,-1-1],
            [1,1,-1])
        connecting_points = ([0,1],[1,2],[2,3],[3,0],
                             [4,1],[5,6],[6,7],[7,4],
                             [0,4],[1,5],[2,6],[3,7])
        self.shift(shift_origin[0], shift_origin[1], shift_origin[2])
        self.a = np.transpose(self.a)
        self.phi = phi
        self.theta_inclined = 0
        self.dtheta_self = dtheta_self
        self.dtheta_inclined = dtheta_inclined
        self.spin_y(self.phi)

    # screen horizontal is x, vertical is y and depth is z
    def shift(self,x,y,z):
        shift_mat = np.zeros(shape=(8,3))
        for point in shift_mat:
            point[0] = x
            point[1] = y
            point[2] = z
        self.a += shift_mat

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
        drawable = self.get_drawable()
        return self.a

    def get_drawable(self):
        projected_a = self.a[0:1]
        projected_a = np.transpose(projected_a)
        # x_region = [0, max(projected_a[0])-min(projected_a[0])]
        # y_region = [0, max(projected_a[1])-min(projected_a[1])]
        # np.zeros(shape=(max(projected_a[0])-min(projected_a[0]),
        #                 max(projected_a[1])-min(projected_a[1])))
        drawable = np.zeros((self.BOARD_SIZE[0],self.BOARD_SIZE[1]))
        for point in projected_a:
            drawable[point[0] + self.ORIGIN[0],point[1] + self.ORIGIN[1]] = 1


