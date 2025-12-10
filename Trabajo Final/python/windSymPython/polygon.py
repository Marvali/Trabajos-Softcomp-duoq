import numpy as np
from matplotlib import pyplot as plt
import random
import math
import time

def sign(x):
    return 1 if x >= 0 else -1

class Polygon:
    def __init__(self, vertices):
        self.vertices = vertices
        self.nsides = vertices.shape[1]-1
        self.bounds = np.vstack([vertices.min(1), vertices.max(1)]).T

    def __covers_aux(self, point):
        # https://www.codeproject.com/tips/84226/is-a-point-inside-a-polygon
        # https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html

        if point[0] < self.bounds[0,0] or point[0] > self.bounds[0,1] or point[1] < self.bounds[1,0] or point[1] > self.bounds[1,1]:
            return False

        in_flag = False
        for i in range(self.nsides):
            vert1 = self.vertices[:,i]
            vert2 = self.vertices[:,i+1]

            #if ((vert1[1] > point[1]) != (vert2[1] > point[1])) and (point[0] < (vert2[0]-vert1[0])*(point[1]-vert1[1])/(vert2[1]-vert1[1]) + vert1[0]):
            # the line above is modified to avoid division by 0

            # We use the sign because we if we multiply an inequation by a negative number it flips
            # if we multiply twice by that negative number it stays the same
            sgn = sign(vert2[1]-vert1[1])
            if ((vert1[1] >= point[1]) ^ (vert2[1] >= point[1])) & (sgn*(point[0] - vert1[0])*(vert2[1]-vert1[1]) <= sgn*(vert2[0]-vert1[0])*(point[1]-vert1[1])):
                in_flag = ~in_flag

            # Slower but more clever, it's a shame really, because it was cool :(
            #in_flag ^= (((vert1[1] >= point[1]) ^ (vert2[1] >= point[1])) & ((point[0] - vert1[0])*abs(vert2[1]-vert1[1]) <= sgn*(vert2[0]-vert1[0])*(point[1]-vert1[1])))

        return in_flag

    def covers(self, points):
        """
        Parallelized version of __convex_aux, it's roughtly the same code but avoiding branches
        """

        result = np.zeros(points.shape[1], dtype=np.bool)
        outside_bounds = (points[0,:] < self.bounds[0,0]) | (points[0,:] > self.bounds[0,1]) | (points[1,:] < self.bounds[1,0]) | (points[1,:] > self.bounds[1,1])

        result_cropped = result[~outside_bounds]
        points_cropped = points[:, ~outside_bounds]
        for i in range(self.nsides):
            vert1 = self.vertices[:,i]
            vert2 = self.vertices[:,i+1]

            sgn = sign(vert2[1]-vert1[1])
            result_cropped = result_cropped ^ (((vert1[1] >= points_cropped[1,:]) ^ (vert2[1] >= points_cropped[1,:])) & ((points_cropped[0,:] - vert1[0])*abs(vert2[1]-vert1[1]) <= sgn*(vert2[0]-vert1[0])*(points_cropped[1,:]-vert1[1])))

        result[~outside_bounds] = result_cropped

        return result


def test_random_points(npoints = 1000):
    vertices = np.array([[0,1,1,0],[0,0,1,1]])
    vertices = np.array([[0.25,0.75,1,0,0.25],[0,0,1,1,0]])
    #theta = np.linspace(0, 2*np.pi, 10)
    #vertices = np.array([np.cos(theta), np.sin(theta)])*0.75

    #vertices = vertices + np.random.normal(0, 0.4, vertices.shape)

    start = time.time()
    p = Polygon(vertices)
    end = time.time()
    #print(f"time taken to initialize polygon: {(end-start)*1000}")


    print(f"generated a shape with {p.nsides} sides")
    #print("its bounds are:")
    #print(p.bounds)

    time_total = 0
    #for i in range(npoints):
    #    point_check = np.array([random.random(),random.random()])*2-1
    #
    #    start = time.time()
    #    is_blue = p.covers_aux(point_check)
    #    end = time.time()
    #    time_total += end-start
    #
    #    color = "bo" if is_blue else "ro"
    #    plt.plot(point_check[0], point_check[1], color)

    points_check = np.random.uniform(0,1,[2, npoints])*2-1
    print(points_check.shape)
    print(vertices.shape)

    start = time.time()
    is_blue = p.covers(points_check)
    end = time.time()

    for i in range(points_check.shape[1]):
        color = "bo" if is_blue[i] else "ro"
        plt.plot(points_check[0,i], points_check[1,i], color, ms=1)

    print(f"average time taken: {(end-start)*1000}")

    plt.plot(p.vertices[0,:], p.vertices[1,:], "g", linewidth=1)
    plt.plot(p.vertices[0,:], p.vertices[1,:], "kx")

    plt.show()


if __name__ == '__main__':
    test_random_points(2000)
