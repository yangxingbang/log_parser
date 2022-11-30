#!/usr/bin/env python

import math
from data import *


def transform_local_coord(frame):
    x_loc = frame.get_localize().get_x()
    y_loc = frame.get_localize().get_y()
    theta_loc = frame.get_localize().get_theta()

    start_point = transform_start_point(frame.get_start_point(), x_loc, y_loc, theta_loc)
    trajectory = transform_trajectory(frame.get_trajectory(), x_loc, y_loc, theta_loc)
    lanes = transform_lanes(frame.get_lanes(), x_loc, y_loc, theta_loc)
    obstacles = transform_obstacles(frame.get_obstacles(), x_loc, y_loc, theta_loc)

    local_frame = frame
    local_frame.set_start_point(start_point)
    local_frame.set_trajectory(trajectory)
    local_frame.set_lanes(lanes)
    local_frame.set_obstacles(obstacles)
    return local_frame


def transform_start_point(point, x_loc, y_loc, theta_loc):
    pt = point
    [x, y, theta] = transform_coord(pt.get_x(), pt.get_y(), pt.get_theta(), x_loc, y_loc, theta_loc)
    pt.set_x(x)
    pt.set_y(y)
    pt.set_theta(theta)
    return pt


def transform_trajectory(trajectory, x_loc, y_loc, theta_loc):
    traj = Trajectory()
    num_of_traj = len(trajectory.get_x())
    for i in range(0, num_of_traj):
        t = trajectory.get_relative_time()[i]
        x = trajectory.get_x()[i]
        y = trajectory.get_y()[i]
        theta = trajectory.get_theta()[i]
        kappa = trajectory.get_kappa()[i]
        s = trajectory.get_s()[i]
        v = trajectory.get_v()[i]
        a = trajectory.get_a()[i]
        [x, y, theta] = transform_coord(x, y, theta, x_loc, y_loc, theta_loc)
        traj.add_trajectory_point(t, x, y, theta, kappa, s, v, a)
    return traj


def transform_lane(lane, x_loc, y_loc, theta_loc):
    lane_local = Lane()
    lane_local.set_id(lane.get_id())
    num_of_lane_pts = len(lane.get_x())
    for i in range(0, num_of_lane_pts):
        x = lane.get_x()[i]
        y = lane.get_y()[i]
        theta = lane.get_theta()[i]
        kappa = lane.get_kappa()[i]
        [x, y, theta] = transform_coord(x, y, theta, x_loc, y_loc, theta_loc)
        lane_local.add_lane_point(x, y, theta, kappa)
    return lane_local


def transform_lanes(lanes, x_loc, y_loc, theta_loc):
    lanes_local = []
    for lane in lanes:
        lane_local = transform_lane(lane, x_loc, y_loc, theta_loc)
        lanes_local.append(lane_local)
    return lanes_local


def transform_obstacle(obstacle, x_loc, y_loc, theta_loc):
    x = obstacle.get_center_x()
    y = obstacle.get_center_y()
    theta = obstacle.get_theta()
    [x, y, theta] = transform_coord(x, y, theta, x_loc, y_loc, theta_loc)
    obstacle_local = Obstacle(x, y, theta, obstacle.get_length(), obstacle.get_width())
    return obstacle_local


def transform_obstacles(obstacles, x_loc, y_loc, theta_loc):
    obstacles_local = []
    for obstacle in obstacles:
        obstacle_local = transform_obstacle(obstacle, x_loc, y_loc, theta_loc)
        obstacles_local.append(obstacle_local)
    return obstacles_local


def transform_coord(x_veh, y_veh, theta_veh, x_loc, y_loc, theta_loc):
    x_temp = x_veh * math.cos(theta_loc) - y_veh * math.sin(theta_loc)
    y_temp = x_veh * math.sin(theta_loc) + y_veh * math.cos(theta_loc)

    x = x_loc + x_temp
    y = y_loc + y_temp
    theta = normalize_angle(theta_veh + theta_loc)
    return [x, y, theta]


def normalize_angle(angle):
    [integer, a] = math.modf((angle + math.pi) / (2.0 * math.pi))
    if a < 0.0:
        a += math.pi
    return a - math.pi
