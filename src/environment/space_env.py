import pygame
import math
import numpy as np

class SpaceEnv:
    def __init__(self):
        # 窗口设置
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # 天体参数
        self.star = {
            'pos': [self.screen_width//2, self.screen_height//2],
            'mass': 1e5,
            'radius': 30
        }
        
        # 飞船参数
        self.ship = {
            'pos': [100, self.screen_height-100],
            'velocity': [0, 0],  # 初始速度由角度决定
            'angle': 45,         # 发射角度（度）
            'speed': 5,          # 初始速度模长
            'thrust': 0.2,       # 单推进器加速度
            'fuel': 1000,        # 燃料总量
            'radius': 10
        }
        
        # 目标区域
        self.target = {
            'pos': [self.screen_width-200, 200],
            'radius': 50
        }
        
        # 物理常数
        self.G = 0.5  # 引力常数（简化版）
        self.dt = 0.1  # 时间步长