#!/usr/bin/env python

from data import *
import math


class Validator(object):
    def __init__(self, frame):
        self.__frame = frame

    def ego_lane(self):
        start_pt = self.__frame.get_start_point()
        start_x = start_pt.get_x()
        start_y = start_pt.get_y()
        min_y = 2.5
        ego_id = ""

        for lane_origin in self.__frame.get_lanes():
            lane = self.updata_lane_s(lane_origin)
            [s, l] = lane.xy_to_sl(start_x, start_y)
            # [x1, y1] = lane.get_reference_point(s + 2.0)
            # [x2, y2] = lane.get_reference_point(s + 4.0)
            # avg_y = (y1 + y2) / 2.0
            # print("")
            # print("x1 = ", x1, "y1= ", y1)
            # print("x2 = ", x2, "y2= ", y2)
            # print('Lane ID : ', lane.get_id())
            # print('Offset: ', avg_y)
            if math.fabs(l) < math.fabs(min_y):
                min_y = -l
                ego_id = lane.get_id()
        print("")
        print('Ego Lane ID : ', ego_id)
        print('Offset: ', min_y)
        return ego_id

    def updata_lane_s(self, lane_origin):
        lane = lane_origin
        lane.set_id(lane_origin.get_id())
        s = []
        xs = lane_origin.get_x()
        ys = lane_origin.get_y()
        num_of_pts = len(xs)
        for i in range(0, num_of_pts):
            if i == 0:
                s.append(0)
            else:
                last_s = s[-1]
                last_x = xs[i - 1]
                last_y = ys[i - 1]
                x = xs[i]
                y = ys[i]
                delta_s = math.hypot(x - last_x, y - last_y)
                s.append(last_s + delta_s)

        lane.set_s(s)
        return lane



