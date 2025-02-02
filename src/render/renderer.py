import pygame
import math
from environment.physics import PhysicsEngine
import random


class GameRenderer:

    def __init__(self, env):
        self.env = env
        self.trail_points = []  # 存储轨迹点
        self.trail_length = 500  # 最大轨迹长度
        
    def update_trail(self, ship_pos):
        """更新飞行轨迹"""
        self.trail_points.append(tuple(ship_pos))
        if len(self.trail_points) > self.trail_length:
            self.trail_points.pop(0)
            
    def draw_trail(self):
        """绘制飞行轨迹"""
        if len(self.trail_points) > 1:
            # 使用渐变色绘制轨迹
            for i in range(1, len(self.trail_points)):
                alpha = int(255 * (i / len(self.trail_points)))
                color = (100, 100, 255, alpha)
                start_pos = self.trail_points[i-1]
                end_pos = self.trail_points[i]
                pygame.draw.line(self.env.screen, color, start_pos, end_pos, 2)
                
    def draw_predicted_trajectory(self, ship, star, steps=100, dt=0.1):
        """绘制预测轨迹"""
        # 复制当前状态进行模拟
        pos = list(ship['pos'])
        velocity = list(ship['velocity'])
        points = []
        
        for _ in range(steps):
            # 计算引力
            gravity = PhysicsEngine.calculate_gravity(
                pos, star['pos'], star['mass'], self.env.G)
            
            # 更新速度和位置
            velocity[0] += gravity[0] * dt
            velocity[1] += gravity[1] * dt
            pos[0] += velocity[0] * dt
            pos[1] += velocity[1] * dt
            
            points.append(tuple(pos))
            
        # 绘制预测轨迹
        if len(points) > 1:
            for i in range(1, len(points)):
                alpha = int(255 * (0.2 + 0.8 * (i / len(points))))
                color = (255, 100, 100, alpha)
                pygame.draw.line(self.env.screen, color, points[i-1], points[i], 1)


    def draw_thrusters(self, ship, actions):
        """绘制推进器效果"""
        if any(actions):  # 如果有推进器在工作
            # 推进器基本参数
            base_length = 20
            max_length = 40
            flare_width = 10
            colors = [
                (255, 100, 100),  # 左
                (100, 255, 100),  # 右
                (100, 100, 255),  # 上
                (255, 255, 100)   # 下
            ]
            
            # 推进器位置偏移
            offsets = [
                (15, 0),# 右
                (-15, 0),   # 左 
                (0, 15),     # 下
                (0, -15)   # 上
                
            ]
            
            for i, active in enumerate(actions):
                if active:
                    # 计算火焰长度
                    length = base_length + (max_length - base_length) * random.random()
                    
                    # 火焰顶点
                    start_pos = (
                        ship['pos'][0] + offsets[i][0],
                        ship['pos'][1] + offsets[i][1]
                    )
                    end_pos = (
                        start_pos[0] + offsets[i][0]/5 * length,
                        start_pos[1] + offsets[i][1]/5 * length
                    )
                    
                    # 绘制火焰
                    pygame.draw.line(
                        self.env.screen,
                        colors[i],
                        start_pos,
                        end_pos,
                        flare_width
                    )
                    
                    # 添加随机粒子效果
                    for _ in range(5):
                        particle_pos = (
                            end_pos[0] + random.uniform(-5, 5),
                            end_pos[1] + random.uniform(-5, 5)
                        )
                        pygame.draw.circle(
                            self.env.screen,
                            (255, 255, 255),
                            particle_pos,
                            random.randint(1, 3)
                        )


    def draw(self, env, core, actions):
        env.screen.fill((0, 0, 0))
        
        # 更新并绘制轨迹
        self.update_trail(env.ship['pos'])
        self.draw_trail()
        
        # 绘制预测轨迹
        self.draw_predicted_trajectory(env.ship, env.star)
        
        # 绘制恒星
        pygame.draw.circle(env.screen, (255, 215, 0),
                        env.star['pos'], env.star['radius'])
        
        # 绘制飞船
        ship = env.ship
        pygame.draw.circle(env.screen, (100, 100, 255),
                        [int(ship['pos'][0]), int(ship['pos'][1])],
                        ship['radius'])
        
        # 绘制推进器效果
        self.draw_thrusters(ship, actions)
        
        # 绘制目标区域
        pygame.draw.circle(env.screen, (0, 255, 0),
                        env.target['pos'], env.target['radius'], 2)
        
        # 显示状态信息
        font = pygame.font.Font(None, 24)
        text = font.render(f"Fuel: {ship['fuel']}  Speed: {math.hypot(*ship['velocity']):.1f}", 
                        True, (255, 255, 255))
        env.screen.blit(text, (10, 10))
        
        pygame.display.flip()
