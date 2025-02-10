import math
import pygame
from environment.physics import PhysicsEngine
from config import *
import random

class GameCore:
    def __init__(self, env, time_scale=1.0):  # 新增时间缩放参数
        self.env = env
        self.env.core = self
        self.time_scale = time_scale  # 时间加速系数
        self.reset()
        
    def get_elapsed_time(self):
        """获取已用时间（秒）"""
        return (pygame.time.get_ticks() - self.start_time) / 1000

    
    def reset(self):
        """重置游戏状态"""

        # 计算初始角度（弧度）
        angle_rad = math.radians(SHIP_CONFIG['initial_angle'])

        self.env.ship.update({
            'pos': [100, SCREEN_HEIGHT-100],
            'velocity': [
                SHIP_CONFIG['initial_speed'] * math.cos(angle_rad),
                -SHIP_CONFIG['initial_speed'] * math.sin(angle_rad)  # y轴向下
            ],
            'rotation': SHIP_CONFIG['initial_angle'],
            'angle': SHIP_CONFIG['initial_angle']  # 添加angle字段
        })
        
        # 随机化目标初始位置
        self.env.target['angle'] = random.uniform(0, 2*math.pi)
        self.env.update_target_position()

        self.start_time = pygame.time.get_ticks()# 记录游戏开始时间

    def update(self, actions):
        """更新游戏状态"""
        # 更新目标位置
        self.env.update_target_position()
        self.env.update_disturber_position()

        # 检查时间限制
        elapsed_time = self.get_elapsed_time()
        if elapsed_time > GAME_CONFIG['time_limit']:
            return 'timeout'
        
        # 计算推力
        thrust_x, thrust_y = PhysicsEngine.apply_thrust(self.env.ship, actions)
        
        # 计算引力
        gravity = PhysicsEngine.calculate_gravity(
            self.env.ship['pos'],
            self.env.star['pos'],
            self.env.star['mass'],
            GRAVITY_CONSTANT
        )
        
        # 更新速度
        self.env.ship['velocity'][0] += (thrust_x + gravity[0]) * TIME_STEP
        self.env.ship['velocity'][1] += (thrust_y + gravity[1]) * TIME_STEP
        
        # 更新位置
        self.env.ship['pos'][0] += self.env.ship['velocity'][0] * TIME_STEP
        self.env.ship['pos'][1] += self.env.ship['velocity'][1] * TIME_STEP

        # 边界检测
        ship = self.env.ship
        if (ship['pos'][0] < 0 or ship['pos'][0] > SCREEN_WIDTH or
            ship['pos'][1] < 0 or ship['pos'][1] > SCREEN_HEIGHT):
            return 'out_of_bounds'
        
        # 碰撞检测
        distance_to_star = math.hypot(
            self.env.ship['pos'][0] - self.env.star['pos'][0],
            self.env.ship['pos'][1] - self.env.star['pos'][1]
        )
        if distance_to_star < self.env.star['radius'] + self.env.ship['radius']:
            return 'star_collision'
        
        # 干扰行星碰撞检测
        distance = math.hypot(
            self.env.ship['pos'][0] - self.env.disturber['pos'][0],
            self.env.ship['pos'][1] - self.env.disturber['pos'][1]
        )
        if distance < self.env.disturber['radius'] + self.env.ship['radius']:
            return 'disturber_collision'

        # 计算相对速度
        target_vel = PhysicsEngine.calculate_orbital_velocity(
            self.env.star['pos'],
            self.env.target['orbit_radius'],
            self.env.target['angular_speed']
        )
        rel_velocity = [
            self.env.ship['velocity'][0] - target_vel[0],
            self.env.ship['velocity'][1] - target_vel[1]
        ]
        rel_speed = math.hypot(*rel_velocity)
            
        # 目标达成检测
        distance_to_target = math.hypot(
            self.env.ship['pos'][0] - self.env.target['pos'][0],
            self.env.ship['pos'][1] - self.env.target['pos'][1]
        )
        if distance_to_target < self.env.target['radius']:
            # 检查相对速度
            if rel_speed > SUCCESS_CONDITIONS['max_speed']:
                return f'collision:{rel_speed}m/s'  # 速度过快视为碰撞
            
            # 检查降落角度
            angle_diff = abs(ship['rotation'] % 360 - 180)  # 理想角度是180度（底部向下）
            if angle_diff > SUCCESS_CONDITIONS['max_angle_deviation']:
                return 'bad_angle'
            
            return 'success'
            
        return 'playing'