#!/usr/bin/env python

import matplotlib.pyplot as plt


class Controller(object):
    def __init__(self, fig, num_of_frames):
        self.__fig_handle = fig
        self.__num_of_frames = num_of_frames
        self.__fig_handle.canvas.mpl_connect("key_press_event", self.press)
        self.__pause = True
        self.__close = False
        self.__step_control_key_pressed = False
        self.__start_over = False
        self.__step = 1
        self.__saved_figure_num = 1

    def press(self, event):

        if event.key == " ":
            self.__pause = not self.__pause

        if event.key == "s" or event.key == "S" or event.key == "ctrl+s" or event.key == "ctrl+S":
            saved_fig_name = "./figure/figure_" + str(self.__saved_figure_num)
            plt.savefig(saved_fig_name)
            self.__saved_figure_num += 1

        if event.key == "q" or event.key == "Q":
            plt.close(self.__fig_handle)
            self.__close = True

        if event.key == "left":
            self.__step = -1
            self.__step_control_key_pressed = True

        if event.key == "right":
            self.__step = 1
            self.__step_control_key_pressed = True

        if event.key == "pageup":
            self.__step = 10
            self.__step_control_key_pressed = True

        if event.key == "pagedown":
            self.__step = -10
            self.__step_control_key_pressed = True

        if event.key == "r" or event.key == "R":
            self.__start_over = True

    def close(self):
        return self.__close

    def get_is_update_ax_lim(self):
        return not self.__pause

    def reset(self):
        self.__step_control_key_pressed = False
        self.__start_over = False
        self.__step = 1

    def do(self):
        step = 1
        if self.__pause and self.__step_control_key_pressed:
            step = self.__step
        elif self.__pause and not self.__step_control_key_pressed:
            step = 0
        elif not self.__pause and self.__step_control_key_pressed:
            step = self.__step
        elif not self.__pause and not self.__step_control_key_pressed:
            step = 1
        if self.__start_over:
            step = -self.__num_of_frames - 1
        self.reset()
        return step
