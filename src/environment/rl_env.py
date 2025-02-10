
import gymnasium as gym
import numpy as np
import math
import random
import pygame
from collections import deque
from gymnasium import spaces
from config import *
import time
from environment.physics import PhysicsEngine
from render.renderer import GameRenderer

class SpaceRLEnv(gym.Env):
    metadata = {'render_modes': ['human', 'rgb_array'], "render_fps": 60}

    def __init__(self, render_mode=None, simulation_fps=1000, max_episode_steps=1000):
        super().__init__()
        
        # 初始化物理引擎
        self.physics = PhysicsEngineWrapper()
        self.simulation_fps = simulation_fps
        self.max_episode_steps = max_episode_steps
        self.render_mode = render_mode
        self._episode_steps = 0
        self._trajectory = deque(maxlen=500)

        # 定义观测空间 [star_pos, ship_pos, ship_vel, disturber_pos, target_pos, target_vel]
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, 
            shape=(12,), dtype=np.float32
        )
        
        # 定义动作空间 [left, right, thrust, reverse_thrust]
        self.action_space = spaces.MultiBinary(4)

        # 初始化渲染系统（仅在需要时）
        if self.render_mode == 'human':
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.renderer = GameRenderer(self)
        elif self.render_mode == 'rgb_array':
            self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.renderer = GameRenderer(self)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.physics = PhysicsEngineWrapper()  # 重置物理引擎
        self._episode_steps = 0
        self._trajectory.clear()
        return self._get_obs(), self._get_info()

    def step(self, action):
        start_time = time.time()
        status = 'playing'
        steps = 0
        
        # 按物理帧率执行多次更新（实现加速）
        while time.time() - start_time < 1.0/self.simulation_fps and steps < 100:
            status = self.physics.update(action)
            steps += 1
            if status != 'playing':
                break
                
        self._episode_steps += 1

        # 计算奖励
        reward = self._calculate_reward(status)
        
        # 检查终止条件
        terminated = status != 'playing'
        truncated = self._episode_steps >= self.max_episode_steps
        
        return self._get_obs(), reward, terminated, truncated, self._get_info()

    def _get_obs(self):
        """获取观测值"""
        return np.array([
            *self.physics.star['pos'],          # 恒星位置 (2)
            *self.physics.ship['pos'],          # 飞船位置 (2)
            *self.physics.ship['velocity'],     # 飞船速度 (2)
            *self.physics.disturber['pos'],     # 干扰行星位置 (2)
            *self.physics.target['pos'],        # 目标行星位置 (2)
            *self.physics.target['velocity']    # 目标行星速度 (2)
        ], dtype=np.float32)  # 总计 12 维

    def _get_info(self):
        """获取调试信息"""
        return {
            'velocity': self.physics.ship['velocity'],
            'distance': math.hypot(
                self.physics.ship['pos'][0] - self.physics.target['pos'][0],
                self.physics.ship['pos'][1] - self.physics.target['pos'][1]
            )
        }

    def _calculate_reward(self, status):
        """计算奖励函数"""
        ship_pos = self.physics.ship['pos']
        target_pos = self.physics.target['pos']
        
        # 1. 距离奖励（指数衰减）
        distance = math.hypot(ship_pos[0]-target_pos[0], ship_pos[1]-target_pos[1])
        distance_reward = 1 / (1 + distance**0.5)
        
        # 2. 速度对齐奖励
        rel_velocity = np.array(self.physics.ship['velocity']) - np.array(self.physics.target['velocity'])
        speed_alignment = -np.linalg.norm(rel_velocity) * 0.1
        
        # 3. 角度对齐奖励
        angle_diff = abs(self.physics.ship['rotation'] % 360 - 180)
        angle_reward = -angle_diff * 0.01
        
        reward = distance_reward + speed_alignment + angle_reward
        
        # 事件奖励
        if status == 'success':
            reward += 100
        elif 'collision' in status:
            reward -= 50
        elif 'timeout' in status:
            reward -= 20
            
        return reward

    def render(self):
        if self.render_mode is None:
            return
        
        # 更新渲染器使用的数据
        self.env.ship = self.physics.ship
        self.env.target['pos'] = self.physics.target['pos']
        self.env.disturber['pos'] = self.physics.disturber['pos']
        
        # 执行渲染
        self.renderer.draw(self.physics.ship['actions'])
        
        if self.render_mode == 'human':
            pygame.display.flip()
        elif self.render_mode == 'rgb_array':
            return pygame.surfarray.array3d(self.screen)

    def close(self):
        if self.render_mode is not None:
            pygame.quit()


class PhysicsEngineWrapper:
    """独立物理引擎，不依赖Pygame"""
    def __init__(self):
        # 初始化恒星
        self.star = {'pos': [SCREEN_WIDTH//2, SCREEN_HEIGHT//2], **STAR_CONFIG}
        
        # 初始化飞船
        self.ship = self._init_ship()
        
        # 初始化目标行星
        self.target = self._init_target()
        
        # 初始化干扰行星
        self.disturber = self._init_disturber()
        
        # # 初始化目标行星速度
        # self.target['velocity'] = [0, 0]  # 初始速度
        
        # # 初始化干扰行星速度
        # self.disturber['velocity'] = [0, 0]  # 初始速度
        # 初始化目标行星和干扰行星的位置和速度
        self._update_celestial_bodies(0)  # 初始位置
        self._update_velocities(0)       # 初始速度

        self._step_count = 0


    def _init_ship(self):
        return {
            'pos': [100, SCREEN_HEIGHT-100],
            'velocity': [0, 0],
            'rotation': SHIP_CONFIG['initial_angle'],
            **SHIP_CONFIG
        }

    def _init_target(self):
        return {
            'angle': random.uniform(0, 2*math.pi),
            'velocity': [0, 0],  # 初始速度
            **TARGET_CONFIG
        }

    def _init_disturber(self):
        return {
            'orbit_angle': random.uniform(0, 2*math.pi),
            'velocity': [0, 0],  # 初始速度
            **DISTURBER_CONFIG
        }

    def update(self, action, time_step=TIME_STEP):
        """执行物理模拟"""
        # 更新天体位置
        self._update_celestial_bodies(time_step)
        
        # 应用飞船控制
        thrust_x, thrust_y = PhysicsEngine.apply_thrust(self.ship, action)
        
        # 计算引力
        gravity = PhysicsEngine.calculate_gravity(
            self.ship['pos'],
            self.star['pos'],
            self.star['mass'],
            GRAVITY_CONSTANT
        )
        
        # 更新飞船状态
        self.ship['velocity'][0] += (thrust_x + gravity[0]) * time_step
        self.ship['velocity'][1] += (thrust_y + gravity[1]) * time_step
        self.ship['pos'][0] += self.ship['velocity'][0] * time_step
        self.ship['pos'][1] += self.ship['velocity'][1] * time_step
        
        # 更新目标行星和干扰行星的速度
        self._update_velocities(time_step)
        
        # 碰撞检测
        self._step_count += 1
        return self._check_terminal()

    def _update_celestial_bodies(self, time_step):
        """更新天体位置"""
        # 目标行星
        self.target['angle'] += self.target['angular_speed'] * time_step
        self.target['pos'] = PhysicsEngine.calculate_orbital_position(
            self.star['pos'],
            self.target['orbit_radius'],
            self.target['angle']
        )
        
        # 干扰行星
        self.disturber['orbit_angle'] += self.disturber['angular_speed'] * time_step
        self.disturber['pos'] = PhysicsEngine.calculate_orbital_position(
            self.star['pos'],
            self.disturber['orbit_radius'],
            self.disturber['orbit_angle']
        )

    def _update_velocities(self, time_step):
        """更新目标行星和干扰行星的速度"""
        # 目标行星速度
        self.target['velocity'] = PhysicsEngine.calculate_orbital_velocity(
            self.star['pos'],
            self.target['orbit_radius'],
            self.target['angular_speed']
        )
        
        # 干扰行星速度
        self.disturber['velocity'] = PhysicsEngine.calculate_orbital_velocity(
            self.star['pos'],
            self.disturber['orbit_radius'],
            self.disturber['angular_speed']
        )

    def _check_terminal(self):
        """检查终止条件"""
        # 边界检测
        if (self.ship['pos'][0] < 0 or self.ship['pos'][0] > SCREEN_WIDTH or
            self.ship['pos'][1] < 0 or self.ship['pos'][1] > SCREEN_HEIGHT):
            return 'out_of_bounds'
        
        # 碰撞检测
        distance_to_star = math.hypot(
            self.ship['pos'][0] - self.star['pos'][0],
            self.ship['pos'][1] - self.star['pos'][1]
        )
        if distance_to_star < self.star['radius'] + self.ship['radius']:
            return 'star_collision'
        
        # 目标达成检测
        distance_to_target = math.hypot(
            self.ship['pos'][0] - self.target['pos'][0],
            self.ship['pos'][1] - self.target['pos'][1]
        )
        if distance_to_target < self.target['radius']:
            return 'success'
            
        return 'playing'