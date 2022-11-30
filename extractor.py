#!/usr/bin/env python

import tkinter
from tkinter import filedialog

from data import *
from transform import transform_local_coord
from config import Flags_use_local_coord


key_string_start = "log-parse::PlanningComponent::Proc_start"
key_string_end = "log-parse::PlanningComponent::Proc_end"
key_string_lane = "log-parse::relative_map lane, id-coord: "
key_string_start_point = "log-parse::planning start point: "
key_string_trajectory = "log-parse::Trajectory, coord: "
key_string_obstacle = "log-parse::Obstacle: "
key_string_localize = "log-parse::Localize, x, y, theta: "
key_string_ego_lane = "log-parse::Ego Lane ID: "
key_string_ref_lane = "log-parse::Ref Lane ID: "
key_string_stage = "log-parse::Stage: "
key_string_timestamp = "log-parse::PlanningComponent::TimeStamp: "


def find_log_file():
    root = tkinter.Tk()
    root.withdraw()
    file_paths = tkinter.filedialog.askopenfilenames(
        filetypes=(("log files", ".log"), ("all files", "*.*")))
    return file_paths


class Extractor(object):
    def __init__(self):
        file_paths = find_log_file()
        # open file, read mode
        self.__lines = []
        self.__num_of_lines = 0
        for file_path in file_paths:
            self.__file = open(file_path, "r+")
            self.__lines += self.__file.readlines()
            self.__file.close()
        self.__num_of_lines += len(self.__lines)

    def do(self):
        frames = []
        localizes = []
        frame = Frame()
        localize = Localize()

        index_of_lines = 0
        find_start_frame = False
        while index_of_lines < self.__num_of_lines:
            percentage = round(index_of_lines / self.__num_of_lines * 100)
            print("\rprogress: {}%: ".format(percentage),
                  "▓" * (percentage // 2),
                  end="")
            line = self.__lines[index_of_lines]
            index_of_lines += 1

            # find the line where planning start, create a new Frame
            index = line.find(key_string_start)
            if index != -1:
                frame = Frame()
                find_start_frame = True
                continue

            # find planning timestamp
            index = line.find(key_string_timestamp)
            if index != -1:
                timestamp = self.find_timestamp(line)
                frame.set_timestamp(timestamp)
                continue

            # find lane from relative map
            index = line.find(key_string_lane)
            if index != -1:
                [lane, index_of_lines] = self.find_separate_line(index_of_lines - 1)
                frame.add_lane(lane)
                continue

            # find ego lane
            index = line.find(key_string_ego_lane)
            if index != -1:
                lane_id = self.find_ego_lane_id(line)
                frame.set_ego_lane_id(lane_id)
                continue

            # find ref lane
            index = line.find(key_string_ref_lane)
            if index != -1:
                lane_id = self.find_ref_lane_id(line)
                frame.set_ref_lane_id(lane_id)
                continue

            # find obstacles
            index = line.find(key_string_obstacle)
            if index != -1:
                [obstacles, index_of_lines] = self.find_obstacles(index_of_lines - 1)
                frame.set_obstacles(obstacles)
                continue

            # find front obstacles
            index = line.find("<PLANNING> Unsafe_id:")
            if index != -1:
                [obstacle, index_of_lines] = self.find_front_obstacle(index_of_lines - 1)
                frame.set_front_obstacle(obstacle)
                continue

            # fine localize
            index = line.find(key_string_localize)
            if index != -1:
                localize = self.find_localize(line)
                frame.set_localize(localize)
                continue

            # fine planning stages
            index = line.find(key_string_stage)
            if index != -1:
                stage = self.find_stage(line)
                frame.add_stage(stage)
                continue

            # find planning start point
            index = line.find(key_string_start_point)
            if index != -1:
                point = self.find_start_point(line)
                frame.set_start_point(point)
                continue

            # find planned trajectory
            index = line.find(key_string_trajectory)
            if index != -1:
                [trajectory, index_of_lines] = self.find_trajectory(index_of_lines - 1)
                frame.set_trajectory(trajectory)
                continue

            # find the line where planning end, push the frame to frames
            index = line.find(key_string_end)
            if index != -1 and find_start_frame:
                if Flags_use_local_coord:
                    frame = transform_local_coord(frame)
                frame.calculate_front_obstacle_trajectory()
                frames.append(frame)
                localizes.append(localize)
                find_start_frame = False
                continue

        # close file
        self.__file.close()
        return [frames, localizes]

    def find_timestamp(self, line):
        line_split = line.split(key_string_timestamp)
        return line_split[1].strip()

    def find_stage(self, line):
        line_split = line.split(key_string_stage)
        return line_split[1].strip()

    def find_separate_line(self, start_line_index):
        lane = Lane()
        index_of_lines = start_line_index
        # read lane info
        line = self.__lines[index_of_lines]
        line_split = line.split(key_string_lane)
        content = line_split[1].split(" , ")
        lane_id = int(content[0])
        lane.set_id(lane_id)

        while index_of_lines < self.__num_of_lines:
            line = self.__lines[index_of_lines]
            # find lane from relative map
            index = line.find(key_string_lane)
            if index == -1:
                # break log by callback function
                index_of_lines += 1
                line = self.__lines[index_of_lines]
                index = line.find(key_string_lane)
                if index == -1:
                    index_of_lines -= 1
                    break

            # read lane info
            line_split = line.split(key_string_lane)
            content = line_split[1].split(" , ")
            lane_id = int(content[0])
            if lane_id != lane.get_id():
                break

            x = round(float(content[1]), 5)
            y = round(float(content[2]), 5)
            theta = round(float(content[3]), 5)
            kappa = round(float(content[4]), 5)
            # set lane info
            lane.add_lane_point(x, y, theta, kappa)
            index_of_lines += 1

        return [lane, index_of_lines]

    def find_ego_lane_id(self, line):
        line_split = line.split(key_string_ego_lane)
        if line_split[1] == '\n':
            return -1
        else:
            lane_id = int(line_split[1])
        return lane_id

    def find_ref_lane_id(self, line):
        line_split = line.split(key_string_ref_lane)
        if line_split[1] == '\n':
            return -1
        else:
            lane_id = int(line_split[1])
        return lane_id

    def find_localize(self, line):
        line_split = line.split(key_string_localize)
        content = line_split[1].split(" , ")
        x = round(float(content[0]), 5)
        y = round(float(content[1]), 5)
        theta = round(float(content[2]), 5)
        localize = Localize(x, y, theta)
        return localize

    def find_start_point(self, line):
        line_split = line.split(key_string_start_point)
        content = line_split[1].split(" , ")
        t = round(float(content[0]), 5)
        x = round(float(content[1]), 5)
        y = round(float(content[2]), 5)
        theta = round(float(content[3]), 5)
        kappa = round(float(content[4]), 5)
        s = round(float(content[5]), 5)
        v = round(float(content[6]), 5)
        a = round(float(content[7]), 5)
        point = Point(t, x, y, theta, kappa, s, v, a)
        return point

    def find_trajectory(self, start_line_index):
        trajectory = Trajectory()
        index_of_lines = start_line_index

        while index_of_lines < self.__num_of_lines:
            line = self.__lines[index_of_lines]

            # find planned trajectory
            index = line.find(key_string_trajectory)
            if index == -1:
                # break log by callback function
                index_of_lines += 1
                line = self.__lines[index_of_lines]
                index = line.find(key_string_trajectory)
                if index == -1:
                    index_of_lines -= 1
                    break

            # read trajectory info
            line_split = line.split(key_string_trajectory)
            content = line_split[1].split(" , ")
            relative_time = round(float(content[0]), 5)
            x = round(float(content[1]), 5)
            y = round(float(content[2]), 5)
            theta = round(float(content[3]), 5)
            kappa = round(float(content[4]), 5)
            s = round(float(content[5]), 5)
            v = round(float(content[6]), 5)
            a = round(float(content[7]), 5)

            # set trajectory info
            trajectory.add_trajectory_point(relative_time, x, y, theta, kappa, s, v, a)
            index_of_lines += 1

        return [trajectory, index_of_lines]

    def find_obstacles(self, start_line_index):
        obstacles = []
        index_of_lines = start_line_index
        while index_of_lines < self.__num_of_lines:
            line = self.__lines[index_of_lines]
            index = line.find(key_string_obstacle)
            if index == -1:
                break

            # read obstacle info
            line_split = line.split(key_string_obstacle)
            content = line_split[1].split(" , ")
            x = round(float(content[0]), 5)
            y = round(float(content[1]), 5)
            theta = round(float(content[2]), 5)
            length = round(float(content[3]), 5)
            width = round(float(content[4]), 5)

            obstacle = Obstacle(x, y, theta, length, width)
            obstacles.append(obstacle)
            index_of_lines += 1

        return [obstacles, index_of_lines]

    def find_front_obstacle(self, start_line_index):
        obstacle = Obstacle()
        index_of_lines = start_line_index
        while index_of_lines < self.__num_of_lines:
            line = self.__lines[index_of_lines]
            index = line.find("<PLANNING> Unsafe_id:")
            if index == -1:
                break

            # read front obstacle info
            line_split = line.split("v: ")
            content = line_split[1].split(" dist: ")
            v = round(float(content[0]), 5)
            content = content[1].split(" thw: ")
            s = round(float(content[0]), 5)
            content = content[1].split(" acc: ")
            a = round(float(content[1]), 5)
            obstacle.set_init_sva(s, v, a)
            index_of_lines += 1

        return [obstacle, index_of_lines]




if __name__ == '__main__':
    extractor = Extractor()
    extractor.do()
