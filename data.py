#!/usr/bin/env python

import math
import numpy as np


class Point(object):
    def __init__(self, t=0, x=0, y=0, theta=0, kappa=0, s=0, v=0, a=0):
        self.__relative_time = t
        self.__x = x
        self.__y = y
        self.__theta = theta
        self.__kappa = kappa
        self.__s = s
        self.__v = v
        self.__a = a

    def get_relative_time(self):
        return self.__relative_time

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_theta(self):
        return self.__theta

    def get_kappa(self):
        return self.__kappa

    def get_s(self):
        return self.__s

    def get_v(self):
        return self.__v

    def get_a(self):
        return self.__a

    def set_relative_time(self, value):
        self.__relative_time = value

    def set_x(self, value):
        self.__x = value

    def set_y(self, value):
        self.__y = value

    def set_theta(self, value):
        self.__theta = value

    def set_kappa(self, value):
        self.__kappa = value

    def set_s(self, value):
        self.__s = value

    def set_v(self, value):
        self.__v = value

    def set_a(self, value):
        self.__a = value

    def print(self):
        print("point info: relative_time= %f, x= %f, y= %f, theta= %f, kappa= %f, s= %f, v= %f, a= %f"
              %(self.__relative_time, self.__x, self.__y, self.__theta, self.__kappa, self.__s, self.__v, self.__a))


class Trajectory(object):
    def __init__(self):
        self.__relative_time = []
        self.__x = []
        self.__y = []
        self.__theta = []
        self.__kappa = []
        self.__s = []
        self.__v = []
        self.__a = []

    def add_trajectory_point(self, relative_time, x, y, theta, kappa, s, v, a):
        self.__relative_time.append(relative_time)
        self.__x.append(x)
        self.__y.append(y)
        self.__theta.append(theta)
        self.__kappa.append(kappa)
        self.__s.append(s)
        self.__v.append(v)
        self.__a.append(a)

    def get_relative_time(self):
        return self.__relative_time

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_theta(self):
        return self.__theta

    def get_kappa(self):
        return self.__kappa

    def get_s(self):
        return self.__s

    def get_v(self):
        return self.__v

    def get_a(self):
        return self.__a

    def set_relative_time(self, value):
        self.__relative_time = value

    def set_x(self, value):
        self.__x = value

    def set_y(self, value):
        self.__y = value

    def set_theta(self, value):
        self.__theta = value

    def set_kappa(self, value):
        self.__kappa = value

    def set_s(self, value):
        self.__s = value

    def set_v(self, value):
        self.__v = value

    def set_a(self, value):
        self.__a = value


class Lane(object):
    def __init__(self):
        self.__id = -1
        self.__x = []
        self.__y = []
        self.__theta = []
        self.__kappa = []
        self.__s = []

    def add_lane_point(self, x, y, theta, kappa, s=0):
        self.__x.append(x)
        self.__y.append(y)
        self.__theta.append(theta)
        self.__kappa.append(kappa)
        self.__s.append(s)

    def get_id(self):
        return self.__id

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_theta(self):
        return self.__theta

    def get_kappa(self):
        return self.__kappa

    def get_s(self):
        return self.__s

    def set_id(self, value):
        self.__id = value

    def set_x(self, value):
        self.__x = value

    def set_y(self, value):
        self.__y = value

    def set_theta(self, value):
        self.__theta = value

    def set_kappa(self, value):
        self.__y = value

    def set_s(self, value):
        self.__s = value

    def xy_to_sl(self, x, y):
        [s, l] = self.get_projection(x, y)
        return [s, l]

    def get_reference_point(self, s):
        if s < 1e-10:
            return [self.__x[0], self.__y[0]]
        if s > self.__s[-1] - 1e-10:
            return [self.__x[-1], self.__y[-1]]

        num_of_pts = len(self.__s)
        min_index = 0
        for index in range(0, num_of_pts):
            if self.__s[index] >= s:
                min_index = index
                break

        index_front = (min_index - 1) if (min_index - 1 >= 0) else 0
        if index_front == min_index:
            return [self.__x[min_index], self.__y[min_index]]
        delta_s = s - self.__s[index_front]
        ratio = delta_s / (self.__s[min_index] - self.__s[index_front])
        x = self.__x[index_front] + ratio * (self.__x[min_index] - self.__x[index_front])
        y = self.__y[index_front] + ratio * (self.__y[min_index] - self.__y[index_front])
        return [x, y]

    def get_projection(self, x, y):
        min_distance = math.inf
        min_index = 0
        num_of_pts = len(self.__x)
        for index in range(0, num_of_pts):
            x1 = self.__x[index]
            y1 = self.__y[index]
            distance = math.hypot(x - x1, y - y1)
            if distance < min_distance:
                min_distance = distance
                min_index = index

        if min_index == 0:
            [s, l] = self.get_projection_sl(x, y, min_index, 1)
            return [s, l]
        if min_index == num_of_pts - 1:
            [s, l] = self.get_projection_sl(x, y, min_index - 1, min_index)
            return [self.__s[-2] + s, l]

        index_front = (min_index - 1) if (min_index - 1 >= 0) else 0
        index_back = (min_index + 1) if (min_index + 1 <= num_of_pts - 1) else num_of_pts - 1
        [s_front, l_front] = self.get_projection_sl(x, y, index_front, min_index)
        [s_back, l_back] = self.get_projection_sl(x, y, min_index, index_back)

        if math.fabs(l_front) < math.fabs(l_back):
            return [s_front + self.__s[index_front], l_front]
        else:
            return [s_back + self.__s[min_index], l_back]

    def get_projection_sl(self, x, y, index_front, index_back):
        x0 = self.__x[index_front]
        y0 = self.__y[index_front]
        x1 = self.__x[index_back]
        y1 = self.__y[index_back]

        dx0 = x - x0
        dy0 = y - y0
        dx1 = x1 - x0
        dy1 = y1 - y0

        cross = dx1 * dy0 - dx0 * dy1
        l = cross / (math.hypot(dx1, dy1) + 1e-10)
        s = (dx0 * dx1 + dy0 * dy1) / (math.hypot(dx1, dy1) + 1e-10)
        return [s, l]


class Obstacle(object):
    def __init__(self, x=0, y=0, theta=0, length=0, width=0):
        self.__x = x
        self.__y = y
        self.__theta = theta
        self.__length = length
        self.__width = width
        self.__t = 0
        self.__s = 0
        self.__v = 0
        self.__a = 0
        [self.__corners_x, self.__corners_y, self.__fixed_corner_x, self.__fixed_corner_y] = self.init_corners()
        self.__trajectory = Trajectory()

    def init_corners(self):
        dx1 = math.cos(self.__theta) * self.__length / 2.0
        dy1 = math.sin(self.__theta) * self.__length / 2.0
        dx2 = math.sin(self.__theta) * self.__width / 2.0
        dy2 = -math.cos(self.__theta) * self.__width / 2.0

        corner1_x = self.__x + dx1 + dx2
        corner1_y = self.__y + dy1 + dy2

        corner2_x = self.__x + dx1 - dx2
        corner2_y = self.__y + dy1 - dy2

        corner3_x = self.__x - dx1 - dx2
        corner3_y = self.__y - dy1 - dy2

        corner4_x = self.__x - dx1 + dx2
        corner4_y = self.__y - dy1 + dy2

        corners_x = [corner1_x, corner2_x, corner3_x, corner4_x]
        corners_y = [corner1_y, corner2_y, corner3_y, corner4_y]
        return [corners_x, corners_y, corner4_x, corner4_y]

    def get_center_x(self):
        return self.__x

    def get_center_y(self):
        return self.__y

    def get_corners_x(self):
        return self.__corners_x

    def get_corners_y(self):
        return self.__corners_y

    def get_fixed_corner_x(self):
        return self.__fixed_corner_x

    def get_fixed_corner_y(self):
        return self.__fixed_corner_y

    def get_length(self):
        return self.__length

    def get_width(self):
        return self.__width

    def get_theta(self):
        return self.__theta

    def get_angle(self):
        return self.__theta / math.pi * 180

    def get_trajectory(self):
        return self.__trajectory

    def set_trajectory(self, value):
        self.__trajectory = value

    def set_init_sva(self, s0, v0, a0):
        self.__s = s0
        self.__v = v0
        self.__a = a0

    def calculate_trajectory(self, t0):
        self.__t = t0
        self.__trajectory = Trajectory()
        prediction_time = 8.0
        for time in np.arange(self.__t, prediction_time, 0.1):
            relative_time = time
            x = 0
            y = 0
            theta = 0
            kappa = 0
            s = self.__s + self.__v * (time - self.__t) + 0.5 * self.__a * math.pow(time - self.__t, 2)
            v = self.__v + self.__a * (time - self.__t)
            a = self.__a
            self.__trajectory.add_trajectory_point(relative_time, x, y, theta, kappa, s, v, a)

    def print(self):
        print("Obstacle info: x= %f, y= %f, theta= %f, length= %f, width= %f, s= %f, v= %f, a= %f"
              %(self.__x, self.__y, self.__theta, self.__length, self.__width, self.__s, self.__v, self.__a))


class Localize(object):
    def __init__(self, x=0, y=0, theta=0):
        self.__x = x
        self.__y = y
        self.__theta = theta

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_theta(self):
        return self.__theta

    def set_x(self, value):
        self.__x = value

    def set_y(self, value):
        self.__y = value

    def set_theta(self, value):
        self.__theta = value


class HistoryLocalize(object):
    def __init__(self):
        self.__x = []
        self.__y = []
        self.__theta = []

    def add_localize(self, localize=Localize()):
        self.__x.append(localize.get_x())
        self.__y.append(localize.get_y())
        self.__theta.append(localize.get_theta())

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_theta(self):
        return self.__theta


class Frame(object):
    def __init__(self):
        self.__timestamp = ""
        self.__stages = ""
        self.__lanes = []
        self.__obstacles = []
        self.__start_point = Point()
        self.__trajectory = Trajectory()
        self.__ego_lane_id = -1
        self.__ref_lane_id = -1
        self.__localize = Localize()
        self.__has_front_obstacle = False
        self.__front_obstacle = Obstacle()

    def add_stage(self, stage):
        if len(self.__stages) < 1:
            self.__stages = stage
        else:
            self.__stages = self.__stages + "--->" + stage

    def add_lane(self, lane):
        self.__lanes.append(lane)

    def add_obstacle(self, obstacle):
        self.__obstacles.append(obstacle)

    def get_text_info(self):
        return "TimeStamp: " + self.__timestamp + ", Stage: " + self.__stages

    def get_timestamp(self):
        return self.__timestamp

    def get_stages(self):
        return self.__stages

    def get_lanes(self):
        return self.__lanes

    def get_obstacles(self):
        return self.__obstacles

    def get_start_point(self):
        return self.__start_point

    def get_trajectory(self):
        return self.__trajectory

    def get_ego_lane_id(self):
        return self.__ego_lane_id

    def get_ref_lane_id(self):
        return self.__ref_lane_id

    def get_localize(self):
        return self.__localize

    def get_front_obstacle(self):
        return self.__front_obstacle

    def has_front_obstacle(self):
        return self.__has_front_obstacle

    def set_timestamp(self, value):
        self.__timestamp = value

    def set_stages(self, value):
        self.__stages = value

    def set_lanes(self, value):
        self.__lanes = value

    def set_start_point(self, value):
        self.__start_point = value

    def set_trajectory(self, value):
        self.__trajectory = value

    def set_ego_lane_id(self, value):
        self.__ego_lane_id = value

    def set_ref_lane_id(self, value):
        self.__ref_lane_id = value

    def set_obstacles(self, value):
        self.__obstacles = value

    def set_localize(self, value):
        self.__localize = value

    def set_front_obstacle(self, value):
        self.__has_front_obstacle = True
        self.__front_obstacle = value

    def calculate_front_obstacle_trajectory(self):
        if not self.__has_front_obstacle:
            return
        t0 = self.__start_point.get_relative_time()
        self.__front_obstacle.calculate_trajectory(t0)
