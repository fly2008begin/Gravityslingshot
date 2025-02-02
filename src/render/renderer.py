import pygame
import math
from config import *
from environment.physics import PhysicsEngine
import random


class GameRenderer:
    def __init__(self, env):
        self.env = env
        self.trail_points = []
        self.trail_length = 300
        
        # 加载贴图
        self.textures = {}
        if USE_TEXTURES:
            for obj in ['star', 'target', 'ship']:
                path = globals()[f"{obj.upper()}_CONFIG"]['texture']
                if path:
                    img = pygame.image.load(path)
                    self.textures[obj] = pygame.transform.smoothscale(
                        img, 
                        (2*globals()[f"{obj.upper()}_CONFIG"]['radius'],)*2
                    )


    def draw_background(self):
        """绘制星空背景"""
        if not RENDER_BACKGROUND:
            return
        
        # 绘制基础星空
        for star in self.env.stars:
            x, y, size, brightness = star
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.env.screen, color, (int(x), int(y)), size)
        
        # 添加美观效果：随机闪烁的星星
        if random.random() < 0.02:  # 2%概率出现闪烁
            idx = random.randint(0, len(self.env.stars)-1)
            x, y, base_size, _ = self.env.stars[idx]
            glow_size = base_size * 3
            alpha = random.randint(100, 150)
            surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255, alpha), 
                             (glow_size, glow_size), glow_size)
            self.env.screen.blit(surface, (x-glow_size, y-glow_size))

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

    def draw_rotated_ship(self):
        """绘制带旋转的飞船"""
        ship = self.env.ship
        if USE_TEXTURES and 'ship' in self.textures:
            texture = pygame.transform.rotate(self.textures['ship'], ship['rotation'])
            rect = texture.get_rect(center=ship['pos'])
            self.env.screen.blit(texture, rect)
        else:
            # 绘制矢量图形
            angle_rad = math.radians(ship['rotation'])
            nose = (
                ship['pos'][0] + ship['radius'] * math.cos(angle_rad),
                ship['pos'][1] - ship['radius'] * math.sin(angle_rad)
            )
            pygame.draw.circle(self.env.screen, (100, 100, 255), ship['pos'], ship['radius'])
            pygame.draw.line(self.env.screen, (255,255,0), ship['pos'], nose, 3)

    def draw_thrusters(self, actions):
        """改进的推进器效果"""
        ship = self.env.ship
        angle_rad = math.radians(ship['rotation'])
        
        # 主推进器（后方）
        if actions[2]:  # W键或上箭头键推进
            self.draw_flame(
                ship['pos'], angle_rad, 
                length=20, color=(255, 100, 100), offset=-1.5  # 向后喷射
            )
        
        # 反向推进器（前方）
        if actions[3]:  # S键或下箭头键反向推进
            self.draw_flame(
                ship['pos'], angle_rad, 
                length=15, color=(100, 255, 100), offset=1.6  # 向前喷射
            )
        
        # 旋转时的横向喷气
        if actions[0] or actions[1]:  # A键或D键旋转
            self.draw_flame(
                ship['pos'], angle_rad + math.pi / 2,  # 横向喷气
                length=10, color=(100, 100, 255), offset=1.2
            )
            self.draw_flame(
                ship['pos'], angle_rad - math.pi / 2,  # 另一侧横向喷气
                length=10, color=(100, 100, 255), offset=1.2
            )

    def draw_flame(self, ship_pos, angle_rad, length, color, offset):
        """
        绘制火焰效果
        :param ship_pos: 飞船位置 [x, y]
        :param angle_rad: 火焰方向（弧度）
        :param length: 火焰长度
        :param color: 火焰颜色
        :param offset: 火焰位置偏移（1: 前方, -1: 后方, 0.5: 侧面）
        """
        # 计算火焰起点
        start_pos = (
            ship_pos[0] + offset * self.env.ship['radius'] * math.cos(angle_rad),
            ship_pos[1] - offset * self.env.ship['radius'] * math.sin(angle_rad)
        )
        
        # 根据推进方向调整终点
        end_offset = -1 if offset < 0 else 1  # 反向推进时方向相反
        end_pos = (
            start_pos[0] + end_offset * length * math.cos(angle_rad),
            start_pos[1] - end_offset * length * math.sin(angle_rad)
        )
        
        # 绘制火焰
        pygame.draw.line(
            self.env.screen, color,
            start_pos, end_pos,
            width=5
        )
        
        # 粒子效果
        for _ in range(5):
            spread = 5
            particle_pos = (
                end_pos[0] + random.uniform(-spread, spread),
                end_pos[1] + random.uniform(-spread, spread)
            )
            pygame.draw.circle(
                self.env.screen, (255, 200, 100),
                particle_pos,
                random.randint(1, 2)
            )


    def draw_info_panel(self):
        """显示目标信息"""
        target_pos = self.env.target['pos']
        ship_pos = self.env.ship['pos']

  
        # 计算目标行星的轨道速度
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
        
        # 计算距离
        distance = math.hypot(
            ship_pos[0] - target_pos[0],
            ship_pos[1] - target_pos[1]
        )
    
        
        # 显示位置（目标右侧）
        text_x = target_pos[0] + self.env.target['radius'] + 20
        text_y = target_pos[1]
        
        # 颜色判断
        color = (173, 216, 230) if rel_speed < 5 else (255, 182, 193)
        
        font = pygame.font.Font(None, 24)
        texts = [
            f"{distance:.1f} m",
            f"{rel_speed:.1f} m/s"
        ]
        
        for i, text in enumerate(texts):
            surf = font.render(text, True, color)
            self.env.screen.blit(surf, (text_x, text_y + i*25))


    def draw_predicted_trajectory(self, steps=100, dt=0.1):
        """绘制预测轨迹"""
        # 复制当前状态进行模拟
        pos = list(self.env.ship['pos'])
        velocity = list(self.env.ship['velocity'])
        points = []
        
        for _ in range(steps):
            # 计算引力
            gravity = PhysicsEngine.calculate_gravity(
                pos, self.env.star['pos'], self.env.star['mass'], GRAVITY_CONSTANT)
            
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

    def draw(self, actions):
        """主绘制方法"""
        self.env.screen.fill((0, 0, 0))

        self.draw_background()
        
        # 更新并绘制轨迹
        self.update_trail(self.env.ship['pos'])
        self.draw_trail()
        
        # 绘制预测轨迹
        self.draw_predicted_trajectory()
        
        # 绘制恒星
        if USE_TEXTURES and 'star' in self.textures:
            rect = self.textures['star'].get_rect(center=self.env.star['pos'])
            self.env.screen.blit(self.textures['star'], rect)
        else:
            pygame.draw.circle(self.env.screen, (255, 215, 0),
                             self.env.star['pos'], self.env.star['radius'])
        
        # 绘制目标
        if USE_TEXTURES and 'target' in self.textures:
            rect = self.textures['target'].get_rect(center=self.env.target['pos'])
            self.env.screen.blit(self.textures['target'], rect)
        else:
            pygame.draw.circle(self.env.screen, (0, 255, 0),
                             self.env.target['pos'], self.env.target['radius'])
        
        # 绘制飞船
        self.draw_rotated_ship()
        
        # 绘制推进器效果
        self.draw_thrusters(actions)
        
        # 绘制信息面板
        self.draw_info_panel()
        
        pygame.display.flip()