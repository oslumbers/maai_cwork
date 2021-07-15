# -*- coding:utf-8  -*-
# Time  : 2021/04/02 17:07
# Author: Yutong Wu

import torch
from tensorboardX import SummaryWriter
from collections import namedtuple
from itertools import count
from common.log_path import make_logpath

from agent import ini_agents
from common.utils import *
import numpy as np
import random
import os


class Runner:
    def __init__(self, args, env):

        self.args = args

        # torch.manual_seed(self.args.seed_nn)
        # np.random.seed(self.args.seed_np)
        # random.seed(self.args.seed_random)

        self.env = env
        self.agent = ini_agents(args)

        # 保存训练参数 以便复现
        if self.args.reload_config:
            file_name = self.args.algo + "_" + self.args.scenario
            self.args = config_dir = os.path.join(os.getcwd(), "config")
            self.args = load_config(self.args, config_dir, file_name)
        else: # todo: 重复处理
            file_name = self.args.algo + "_" + self.args.scenario
            config_dir = os.path.join(os.getcwd(), "config")
            save_config(self.args, config_dir, file_name=file_name)

    def set_up(self):
        # 定义保存路径
        run_dir, log_dir = make_logpath(self.args.scenario, self.args.algo)
        self.writer = SummaryWriter(str(log_dir))

    def set_seed(self):
        # 设置seed, 以便复现
        self.env.set_seed(seed=self.args.seed_random)
        torch.manual_seed(self.args.seed_nn)

    def add_experience(self, states, state_next, reward, done):
        agent_id = 0
        self.agent.memory.insert("states", agent_id, states)
        self.agent.memory.insert("states_next", agent_id, state_next)
        self.agent.memory.insert("rewards", agent_id, reward)
        self.agent.memory.insert("dones", agent_id, np.array(done, dtype=bool))

    def run(self):

        self.set_up()
        self.set_seed()

        x_threshold = 2.4
        theta_threshold_radians = 0.20943951023931953
        for i_epoch in range(self.args.max_episodes):
            state = self.env.reset()
            Gt = 0
            for t in count():

                action = self.agent.choose_action(state, train=True)

                next_state, reward, done, _, _ = self.env.step(action)


                x, x_dot, theta, theta_dot = next_state
                r1 = (x_threshold - abs(x)) / x_threshold
                r2 = (theta_threshold_radians - abs(theta)) /theta_threshold_radians
                reward = r1 + r2


                self.add_experience(state, next_state, reward, np.float32(done))

                state = next_state

                Gt += reward

                if done:
                    self.agent.learn()
                    # print('i_epoch: ', i_epoch, 'Gt: ', '%.2f' % Gt, 'epi: ', '%.2f' % self.agent.eps)
                    print('i_epoch: ', i_epoch, 'Gt: ', '%.2f' % Gt)
                    reward_tag = 'reward'
                    self.writer.add_scalars(reward_tag, global_step=i_epoch,
                                       tag_scalar_dict={'return': Gt})

                    if i_epoch % self.args.evaluate_rate == 0 and i_epoch > 1:
                        Gt_real = self.evaluate(i_epoch)
                        self.writer.add_scalars(reward_tag, global_step=i_epoch, tag_scalar_dict={'real_return': Gt_real})
                    break

    def evaluate(self, i_epoch):
        record = []
        for _ in range(10):
            state = self.env.reset()
            Gt_real = 0
            for t in count():
                action = self.agent.choose_action(state, train=False)
                next_state, reward, done, _, _ = self.env.step(action, train=False)
                state = next_state
                Gt_real += reward
                if done:
                    record.append(Gt_real)
                    break
        print('===============', 'i_epoch: ', i_epoch, 'Gt_real: ', '%.2f' % np.mean(record))
        return np.mean(record)
