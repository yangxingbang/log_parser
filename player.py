#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib import lines
from matplotlib import patches
import matplotlib.gridspec as mg
from matplotlib.widgets import Slider
import math
from config import Flags_use_local_coord


class Player(object):
    def __init__(self, localizes, num_of_frames):
        # slider
        self.__slider_val = 0.0

        self.__loc_update = False
        self.__kappa_update = False
        self.__st_update = False
        self.__vt_update = False
        self.__at_update = False
        self.__update_ax_lim = True

        [self.__localizes_x, self.__localizes_y, self.__localizes_theta] = self.handle_localizes(localizes)

        self.__fig = plt.figure()
        grid = mg.GridSpec(5, 2)
        self.__ax_env = plt.subplot(grid[0:2, 0])
        self.__ax_loc = plt.subplot(grid[2:4, 0])
        self.__ax_kappa = plt.subplot(grid[0, 1])
        self.__ax_st = plt.subplot(grid[1, 1])
        self.__ax_vt = plt.subplot(grid[2, 1])
        self.__ax_at = plt.subplot(grid[3, 1])
        self.__ax_slider = plt.subplot(grid[4, 0:2])
        # slider
        self.__ax_slider_factor = Slider(self.__ax_slider,
                                         'frame',
                                         1,
                                         num_of_frames,
                                         valinit=0,
                                         valstep=1)
        self.__ax_slider_factor.on_changed(self.update_ax_slider)

        self.draw_init_info()

        plt.ion()
        plt.tight_layout(pad=0.05)
        self.__fig.canvas.draw()
        plt.show()

    def get_figure_handle(self):
        return self.__fig

    def set_update_ax_lim(self, value):
        self.__update_ax_lim = value

    def draw_init_info(self):
        # set env ax info
        self.__ax_env.set_xlabel(r"$x(m)$")
        self.__ax_env.set_ylabel(r"$y(m)$")
        self.__ax_env.set_xlim([-10, 80])
        self.__ax_env.set_ylim([-8, 8])

        # set localize ax info
        self.__ax_loc.set_xlabel(r"$x(m)$")
        self.__ax_loc.set_ylabel(r"$y(m)$")
        self.__ax_loc.set_title(r"$Current \ Localize$")
        self.draw_localizes()

        # set kappa vs s ax info
        self.__ax_kappa.set_xlabel(r"$s(m)$")
        self.__ax_kappa.set_ylabel(r"$\kappa(m^{-1})$")
        self.__ax_kappa.set_title(r"$\kappa \ vs. \ s$")
        self.__ax_kappa.set_xlim([-10, 100])

        # set s vs t ax info
        self.__ax_st.set_xlabel(r"$time(s)$")
        self.__ax_st.set_ylabel(r"$s(m)$")
        self.__ax_st.set_title(r"$s \ vs. \ t$")
        self.__ax_st.set_xlim([-0.5, 8.5])

        # set v vs t ax info
        self.__ax_vt.set_xlabel(r"$time(s)$")
        self.__ax_vt.set_ylabel(r"$v(m/s)$")
        self.__ax_vt.set_title(r"$v \ vs. \ t$")
        self.__ax_vt.set_xlim([-0.5, 8.5])

        # set a vs t ax info
        self.__ax_at.set_xlabel(r"$time(s)$")
        self.__ax_at.set_ylabel(r"$a(m/s^2)$")
        self.__ax_at.set_title(r"$a \ vs. \ t$")
        self.__ax_at.set_xlim([-0.5, 8.5])

    def update_ax_slider(self, val):
        self.__slider_val = self.__ax_slider_factor.val

    def get_slider_val(self):
        return self.__slider_val

    def set_slider_val(self, value):
        self.__ax_slider_factor.set_val(value)

    def draw_localizes(self):
        localizes_line = lines.Line2D(self.__localizes_x, self.__localizes_y, color='k')
        self.__ax_loc.add_line(localizes_line)

        num_of_localizes = len(self.__localizes_x)
        for index in range(0, num_of_localizes, 1):
            arrow = self.draw_arrow(self.__localizes_x[index], self.__localizes_y[index], self.__localizes_theta[index], "b")
            self.__ax_loc.add_patch(arrow)

        self.__ax_loc.plot(self.__localizes_x, self.__localizes_y, color='k', lw=1.5)

    def update_draw(self, frame):
        self.draw_env(frame)
        self.draw_localize(frame.get_localize())
        self.draw_kappa_s(frame.get_trajectory(), frame.get_start_point())
        self.draw_st(frame.get_trajectory(), frame.get_start_point(),
                     frame.get_front_obstacle(), frame.has_front_obstacle())
        self.draw_vt(frame.get_trajectory(), frame.get_start_point(),
                     frame.get_front_obstacle(), frame.has_front_obstacle())
        self.draw_at(frame.get_trajectory(), frame.get_start_point(),
                     frame.get_front_obstacle(), frame.has_front_obstacle())
        self.draw()

    def draw(self):
        self.__ax_env.draw_artist(self.__ax_env.patch)
        self.__ax_loc.draw_artist(self.__ax_loc.patch)
        self.__ax_kappa.draw_artist(self.__ax_kappa.patch)
        self.__ax_st.draw_artist(self.__ax_st.patch)
        self.__ax_vt.draw_artist(self.__ax_vt.patch)
        self.__ax_at.draw_artist(self.__ax_at.patch)

        for polygon in self.__ax_env.patches:
            self.__ax_env.draw_artist(polygon)
        for line in self.__ax_env.lines:
            self.__ax_env.draw_artist(line)

        for polygon in self.__ax_loc.patches:
            self.__ax_loc.draw_artist(polygon)
        for line in self.__ax_loc.lines:
            self.__ax_loc.draw_artist(line)

        for line in self.__ax_kappa.lines:
            self.__ax_kappa.draw_artist(line)

        for line in self.__ax_st.lines:
            self.__ax_st.draw_artist(line)

        for line in self.__ax_vt.lines:
            self.__ax_vt.draw_artist(line)

        for line in self.__ax_at.lines:
            self.__ax_at.draw_artist(line)

        self.__fig.canvas.blit(self.__ax_env.bbox)
        self.__fig.canvas.blit(self.__ax_loc.bbox)
        self.__fig.canvas.blit(self.__ax_kappa.bbox)
        self.__fig.canvas.blit(self.__ax_st.bbox)
        self.__fig.canvas.blit(self.__ax_vt.bbox)
        self.__fig.canvas.blit(self.__ax_at.bbox)
        self.__fig.canvas.flush_events()

    def draw_env(self, frame):
        while len(self.__ax_env.lines) > 0:
            self.__ax_env.lines[-1].remove()

        while len(self.__ax_env.patches) > 0:
            self.__ax_env.patches[-1].remove()

        self.draw_lanes(frame)
        self.draw_obstacles(frame.get_obstacles())
        self.draw_trajectory(frame.get_trajectory(), frame.get_start_point())
        if Flags_use_local_coord and self.__update_ax_lim:
            self.__ax_env.set_xlim([frame.get_localize().get_x() - 50, frame.get_localize().get_x() + 50])
            self.__ax_env.set_ylim([frame.get_localize().get_y() - 8, frame.get_localize().get_y() + 8])
        elif self.__update_ax_lim:
            self.__ax_env.set_xlim([-10, 80])
            self.__ax_env.set_ylim([-8, 8])

        self.text(frame.get_text_info())

    def text(self, info):
        self.__ax_env.set_title(info)
        self.__ax_env.legend(loc='upper right')

    def draw_localize(self, localize):
        if not self.__loc_update:
            cur_loc = lines.Line2D([localize.get_x()], [localize.get_y()], color='red', marker='o', markersize=5, label=r"$current \ localize$")
            self.__ax_loc.add_line(cur_loc)
            cur_heading = self.draw_arrow(localize.get_x(), localize.get_y(), localize.get_theta(), "r")
            self.__ax_loc.add_patch(cur_heading)
            self.__loc_update = True
        else:
            cur_loc = self.__ax_loc.lines[-1]
            cur_loc.set_data([localize.get_x()], [localize.get_y()])
            self.__ax_loc.patches[-1].remove()
            cur_heading = self.draw_arrow(localize.get_x(), localize.get_y(), localize.get_theta(), "r")
            self.__ax_loc.add_patch(cur_heading)

    def draw_kappa_s(self, trajectory, point):
        if not self.__kappa_update:
            start_point = lines.Line2D([point.get_s()], [point.get_kappa()], color='red', marker='o', markersize=5)
            self.__ax_kappa.add_line(start_point)
            kappa = lines.Line2D(trajectory.get_s(), trajectory.get_kappa(), color='k', lw=1.5)
            self.__ax_kappa.add_line(kappa)
            self.__kappa_update = True
            if not trajectory.get_kappa():
                return
            ymin = min(trajectory.get_kappa())
            ymax = max(trajectory.get_kappa())
            self.__ax_kappa.set_xlim([-10, 100])
            self.__ax_kappa.set_ylim([ymin, ymax])
        else:
            start_point = self.__ax_kappa.lines[-2]
            start_point.set_data([point.get_s()], [point.get_kappa()])
            kappa = self.__ax_kappa.lines[-1]
            kappa.set_data(trajectory.get_s(), trajectory.get_kappa())
            if len(trajectory.get_s()) == 0:
                return
            ymin, ymax = self.__ax_kappa.get_ylim()
            kappa_min = min(trajectory.get_kappa())
            kappa_max = max(trajectory.get_kappa())
            if kappa_min < ymin:
                ymin = kappa_min - abs(kappa_min) * 0.1
            elif kappa_min > ymin + abs(ymin) * 0.1:
                ymin = kappa_min - abs(kappa_min) * 0.1
            if kappa_max > ymax:
                ymax = kappa_max + abs(kappa_max) * 0.1
            elif kappa_max < ymax - abs(ymax) * 0.1:
                ymax = kappa_max + abs(kappa_max) * 0.1
            if self.__update_ax_lim:
                self.__ax_kappa.set_xlim([-10, 100])
                self.__ax_kappa.set_ylim([ymin, ymax])

            # xmin, xmax = self.ax_st.get_xlim()
            # if trajectory.get_s()[-1] > xmax or trajectory.get_s()[-1] < xmax - 10:
            #     self.ax_kappa.set_xlim([trajectory.get_s()[0] - 5, trajectory.get_s()[-1] + 5])

    def draw_st(self, trajectory, point, front_obstacle, has_front_obstacle):
        if not self.__st_update:
            start_point = lines.Line2D([point.get_relative_time()], [point.get_s()], color='red', marker='o', markersize=5)
            self.__ax_st.add_line(start_point)
            s = lines.Line2D(trajectory.get_relative_time(), trajectory.get_s(), color='k', lw=1.5)
            self.__ax_st.add_line(s)
            self.__st_update = True

            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                s_obs = lines.Line2D(obs_traj.get_relative_time(), obs_traj.get_s(), color='r', lw=1.5)
                self.__ax_st.add_line(s_obs)

            if not trajectory.get_s():
                return
            ymin = min(trajectory.get_s())
            ymax = max(trajectory.get_s())

            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                if obs_traj.get_s():
                    ymin = min(min(trajectory.get_s()), min(obs_traj.get_s()))
                    ymax = max(max(trajectory.get_s()), max(obs_traj.get_s()))

            self.__ax_st.set_xlim([-0.5, 8.5])
            self.__ax_st.set_ylim([ymin, ymax])
        else:
            start_point = self.__ax_st.lines[0]
            start_point.set_data([point.get_relative_time()], [point.get_s()])
            s = self.__ax_st.lines[1]
            s.set_data(trajectory.get_relative_time(), trajectory.get_s())
            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                if len(self.__ax_st.lines) > 2:
                    s_obs = self.__ax_st.lines[2]
                    s_obs.set_data(obs_traj.get_relative_time(), obs_traj.get_s())
                else:
                    s_obs = lines.Line2D(obs_traj.get_relative_time(), obs_traj.get_s(), color='r', lw=1.5)
                    self.__ax_st.add_line(s_obs)
            else:
                if len(self.__ax_st.lines) > 2:
                    self.__ax_st.lines[-1].remove()

            if len(trajectory.get_relative_time()) == 0:
                return

            ymin = min(trajectory.get_s())
            ymax = max(trajectory.get_s())
            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                if obs_traj.get_s():
                    ymin = min(min(trajectory.get_s()), min(obs_traj.get_s()))
                    ymax = max(max(trajectory.get_s()), max(obs_traj.get_s()))

            ymin_last, ymax_last = self.__ax_st.get_ylim()

            if (ymax > ymax_last or ymin < ymin_last) and self.__update_ax_lim:
                self.__ax_st.set_xlim([-0.5, 8.5])
                self.__ax_st.set_ylim([ymin - 10, ymax + 10])

    def draw_vt(self, trajectory, point, front_obstacle, has_front_obstacle):
        if not self.__vt_update:
            start_point = lines.Line2D([point.get_relative_time()], [point.get_v()], color='red', marker='o', markersize=5)
            self.__ax_vt.add_line(start_point)
            v = lines.Line2D(trajectory.get_relative_time(), trajectory.get_v(), color='k', lw=1.5)
            self.__ax_vt.add_line(v)
            self.__vt_update = True

            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                v_obs = lines.Line2D(obs_traj.get_relative_time(), obs_traj.get_v(), color='r', lw=1.5)
                self.__ax_vt.add_line(v_obs)

            if not trajectory.get_v():
                return
            ymin = min(trajectory.get_v())
            ymax = max(trajectory.get_v())
            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                if obs_traj.get_v():
                    ymin = min(min(trajectory.get_v()), min(obs_traj.get_v()))
                    ymax = max(max(trajectory.get_v()), max(obs_traj.get_v()))

            self.__ax_vt.set_xlim([-0.5, 8.5])
            self.__ax_vt.set_ylim([ymin, ymax])
        else:
            start_point = self.__ax_vt.lines[0]
            start_point.set_data([point.get_relative_time()], [point.get_v()])
            v = self.__ax_vt.lines[1]
            v.set_data(trajectory.get_relative_time(), trajectory.get_v())

            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                if len(self.__ax_vt.lines) > 2:
                    v_obs = self.__ax_vt.lines[2]
                    v_obs.set_data(obs_traj.get_relative_time(), obs_traj.get_v())
                else:
                    v_obs = lines.Line2D(obs_traj.get_relative_time(), obs_traj.get_v(), color='r', lw=1.5)
                    self.__ax_vt.add_line(v_obs)
            else:
                if len(self.__ax_vt.lines) > 2:
                    self.__ax_vt.lines[-1].remove()

            if len(trajectory.get_relative_time()) == 0:
                return
            ymin, ymax = self.__ax_vt.get_ylim()
            v_min = min(trajectory.get_v())
            v_max = max(trajectory.get_v())
            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                if obs_traj.get_v():
                    v_min = min(min(trajectory.get_v()), min(obs_traj.get_v()))
                    v_max = max(max(trajectory.get_v()), max(obs_traj.get_v()))

            if v_min < ymin or v_min > ymin + abs(ymin) * 0.1:
                ymin = v_min - 0.1

            if v_max > ymax or v_max < ymax - abs(ymax) * 0.1:
                ymax = v_max + 0.1
            if self.__update_ax_lim:
                self.__ax_vt.set_xlim([-0.5, 8.5])
                self.__ax_vt.set_ylim([ymin, ymax])

    def draw_at(self, trajectory, point, front_obstacle, has_front_obstacle):
        if not self.__at_update:
            start_point = lines.Line2D([point.get_relative_time()], [point.get_a()], color='red', marker='o', markersize=5)
            self.__ax_at.add_line(start_point)
            a = lines.Line2D(trajectory.get_relative_time(), trajectory.get_a(), color='k', lw=1.5)
            self.__ax_at.add_line(a)
            self.__at_update = True

            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                a_obs = lines.Line2D(obs_traj.get_relative_time(), obs_traj.get_a(), color='r', lw=1.5)
                self.__ax_at.add_line(a_obs)

            if not trajectory.get_a():
                return
            ymin = min(trajectory.get_a())
            ymax = max(trajectory.get_a())
            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                if obs_traj.get_a():
                    ymin = min(min(trajectory.get_a()), min(obs_traj.get_a()))
                    ymax = max(max(trajectory.get_a()), max(obs_traj.get_a()))

            self.__ax_at.set_xlim([-0.5, 8.5])
            self.__ax_at.set_ylim([ymin, ymax])
        else:
            start_point = self.__ax_at.lines[0]
            start_point.set_data([point.get_relative_time()], [point.get_a()])
            a = self.__ax_at.lines[1]
            a.set_data(trajectory.get_relative_time(), trajectory.get_a())

            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                if len(self.__ax_at.lines) > 2:
                    a_obs = self.__ax_at.lines[2]
                    a_obs.set_data(obs_traj.get_relative_time(), obs_traj.get_a())
                else:
                    a_obs = lines.Line2D(obs_traj.get_relative_time(), obs_traj.get_a(), color='r', lw=1.5)
                    self.__ax_at.add_line(a_obs)
            else:
                if len(self.__ax_at.lines) > 2:
                    self.__ax_at.lines[-1].remove()

            if len(trajectory.get_relative_time()) == 0:
                return
            ymin, ymax = self.__ax_at.get_ylim()
            a_min = min(trajectory.get_a())
            a_max = max(trajectory.get_a())

            if has_front_obstacle:
                obs_traj = front_obstacle.get_trajectory()
                if obs_traj.get_a():
                    a_min = min(min(trajectory.get_a()), min(obs_traj.get_a()))
                    a_max = max(max(trajectory.get_a()), max(obs_traj.get_a()))

            if a_min < ymin or a_min > ymin + abs(ymin) * 0.1:
                ymin = a_min - 0.1

            if a_max > ymax or a_max < ymax - abs(ymax) * 0.1:
                ymax = a_max + 0.1
            if self.__update_ax_lim:
                self.__ax_at.set_xlim([-0.5, 8.5])
                self.__ax_at.set_ylim([ymin, ymax])

    def handle_localizes(self, localizes):
        x = []
        y = []
        theta = []
        for localize in localizes:
            x.append(localize.get_x())
            y.append(localize.get_y())
            theta.append(localize.get_theta())
        return [x, y, theta]

    def draw_arrow(self, x, y, theta, color):
        arrow_length = 0.3
        dx = arrow_length * math.cos(theta)
        dy = arrow_length * math.sin(theta)
        arrow = patches.FancyArrow(x, y, dx, dy, color=color, width=0.02, head_length=0.2, head_width=0.1)
        return arrow

    def draw_lanes(self, frame):
        for lane in frame.get_lanes():
            self.draw_lane(lane, frame.get_ego_lane_id(), frame.get_ref_lane_id())

    def draw_lane(self, lane, ego_lane_id, ref_lane_id):
        color = "k"
        label_string = r"$center \ line$"
        if lane.get_id() == ego_lane_id and lane.get_id() == ref_lane_id:
            color = "y"
            label_string = r"$ego&ref\ center \ line$"
        elif lane.get_id() == ego_lane_id:
            color = "b"
            label_string = r"$ego\ center \ line$"
        elif lane.get_id() == ref_lane_id:
            color = "g"
            label_string = r"$ref\ center \ line$"

        center_lane = lines.Line2D(lane.get_x(), lane.get_y(), color=color, label=label_string)
        self.__ax_env.add_line(center_lane)

    def draw_trajectory(self, trajectory, point):
        traj = lines.Line2D(trajectory.get_x(), trajectory.get_y(), color='red', label=r"$trajectory$")
        self.__ax_env.add_line(traj)
        start_point = lines.Line2D([point.get_x()], [point.get_y()], color='red', marker='o', markersize=5)
        self.__ax_env.add_line(start_point)

    def draw_obstacles(self, obstacles):
        for obstacle in obstacles:
            self.draw_obstacle(obstacle)

    def draw_obstacle(self, obstacle):
        rect = patches.Rectangle((obstacle.get_fixed_corner_x(), obstacle.get_fixed_corner_y()),
                                 width=obstacle.get_length(), height=obstacle.get_width(), angle=obstacle.get_angle(), color="red")
        self.__ax_env.add_patch(rect)
