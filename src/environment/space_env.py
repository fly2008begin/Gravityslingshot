import pygame
import math
import numpy as np
from config import *
import random
from environment.physics import PhysicsEngine

class SpaceEnv:

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 初始化恒星
        self.star = {
            'pos': [SCREEN_WIDTH//2, SCREEN_HEIGHT//2],
            **STAR_CONFIG
        }
        
        # 初始化飞船
        self.ship = {
            'pos': [100, SCREEN_HEIGHT-100],
            'velocity': [0, 0],
            'rotation': SHIP_CONFIG['initial_angle'],
            'angle': SHIP_CONFIG['initial_angle'],  # 添加angle字段
            **SHIP_CONFIG
        }
        
        # 初始化目标
        self.target = {
            'angle': random.uniform(0, 2*math.pi),  # 随机初始角度
            **TARGET_CONFIG
        }
        self.update_target_position()
        
        # 生成固定星空
        self.stars = self.generate_stars()
        
    def update_target_position(self):
        """更新目标位置"""
        self.target['pos'] = PhysicsEngine.calculate_orbital_position(
            self.star['pos'],
            self.target['orbit_radius'],
            self.target['angle']
        )
        self.target['angle'] += self.target['angular_speed']


    def generate_stars(self):
        """生成固定模式的星空"""
        random.seed(BACKGROUND_SEED)
        np.random.seed(BACKGROUND_SEED)
        
        stars = []
        for _ in range(STAR_COUNT):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            size = random.randint(*STAR_SIZE_RANGE)
            brightness = random.randint(*STAR_BRIGHTNESS_RANGE)
            stars.append((x, y, size, brightness))
        return stars