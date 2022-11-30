#!/usr/bin/env python

from extractor import Extractor
from player import Player
from controller import Controller
from validator import Validator
import time

planning_loop_hz = 15


class Parser(object):
    def __init__(self):
        extractor = Extractor()
        [self.__frames, self.__localizes] = extractor.do()
        self.__num_of_frames = len(self.__frames)
        self.__player = Player(self.__localizes, self.__num_of_frames)
        self.__controller = Controller(self.__player.get_figure_handle(), self.__num_of_frames)

    def do(self):
        last_index_of_frame = -1
        index_of_frame = 0
        while index_of_frame <= self.__num_of_frames:
            # unit: s
            start_time = time.time()
            # get data
            frame = self.__frames[index_of_frame]
            # debug print
            # frame.get_start_point().print()
            # if frame.has_front_obstacle():
            #     frame.get_front_obstacle().print()

            # validator = Validator(frame)
            # ego_lane_id = validator.ego_lane()
            # frame.set_ego_lane_id(ego_lane_id)
            # display
            is_update_ax_lim = self.__controller.get_is_update_ax_lim()
            is_update_ax_lim = not (index_of_frame == last_index_of_frame)
            last_index_of_frame = index_of_frame
            self.__player.set_update_ax_lim(is_update_ax_lim)
            self.__player.update_draw(frame)
            # update index of frame to display
            step = self.__controller.do()
            # slider
            slider_frame = int(self.__player.get_slider_val() - 1)
            if index_of_frame != slider_frame:
                index_of_frame = slider_frame
            else:
                index_of_frame += step
            # keep in loop for plot and keyboard control
            index_of_frame = min(index_of_frame, self.__num_of_frames - 1)
            index_of_frame = max(index_of_frame, 0)
            self.__player.set_slider_val(index_of_frame + 1)
            # control frequency as planning module
            interval = 1.0 / planning_loop_hz - (time.time() - start_time)
            if interval > 1e-6:
                time.sleep(interval)
            # whether close figure
            if self.__controller.close():
                break


if __name__ == '__main__':
    parser = Parser()
    parser.do()
