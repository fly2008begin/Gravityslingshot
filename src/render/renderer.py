import pygame
import math
from config import *
from environment.physics import PhysicsEngine
import random


class GameRenderer:
    def __init__(self, env):
        self.env = env
        self.trail_points = []
        self.trail_length = 600
        
        # 加载贴图
        self.textures = {}
        if USE_TEXTURES:
            for obj in ['star', 'target', 'ship', 'disturber']:  # 包括干扰行星
                path = globals()[f"{obj.upper()}_CONFIG"]['texture']
                if path:
                    img = pygame.image.load(path)
                    
                    # 特殊处理干扰行星贴图
                    if obj == 'disturber':
                        # 获取原始贴图尺寸
                        # 根据贴图原始比例缩放
                        original_w, original_h = img.get_size()
                        scale = DISTURBER_CONFIG['texture_scale']
                        target_w = int(DISTURBER_CONFIG['radius'] * 2 * scale)
                        target_h = int(target_w * (original_h/original_w))  # 保持比例
                        self.textures['disturber'] = pygame.transform.smoothscale(img, (target_w, target_h))

                    else:
                        # 其他天体按原逻辑处理
                        self.textures[obj] = pygame.transform.smoothscale(
                            img, 
                            (2 * globals()[f"{obj.upper()}_CONFIG"]['radius'],) * 2
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

    def draw_disturber(self):
        """绘制双星系统"""
        d = self.env.disturber
        if USE_TEXTURES and 'disturber' in self.textures:
            # 旋转贴图
            rotated = pygame.transform.rotate(self.textures['disturber'], d['rotation_angle'])
            rect = rotated.get_rect(center=d['pos'])
            self.env.screen.blit(rotated, rect)
        else:
            # 矢量图形模式
            pygame.draw.circle(self.env.screen, d['color'], d['pos'], d['radius'])
            # 绘制自转标记
            angle_rad = math.radians(d['rotation_angle'])
            marker = (
                d['pos'][0] + d['radius']*math.cos(angle_rad),
                d['pos'][1] - d['radius']*math.sin(angle_rad)
            )
            pygame.draw.line(self.env.screen, (0,0,0), d['pos'], marker, 2)

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
        text_y = target_pos[1] - 20
        
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

    def draw_target_decorations(self):
        """绘制目标行星的装饰效果"""
        target = self.env.target
        center = target['pos']
        radius = target['radius'] * 1.5  # 装饰圈半径
        
        # 获取与信息面板一致的颜色
        ship_pos = self.env.ship['pos']
        target_vel = PhysicsEngine.calculate_orbital_velocity(
            self.env.star['pos'],
            target['orbit_radius'],
            target['angular_speed']
        )
        rel_velocity = [
            self.env.ship['velocity'][0] - target_vel[0],
            self.env.ship['velocity'][1] - target_vel[1]
        ]
        rel_speed = math.hypot(*rel_velocity)
        color = (173, 216, 230) if rel_speed < 5 else (255, 182, 193)
        
        # 绘制四个对称半弧线
        arc_radius = radius
        arc_width = 3
        for i in range(4):
            start_angle = math.radians(i * 90 + 20)
            end_angle = math.radians(i * 90 + 70)
            pygame.draw.arc(self.env.screen, color,
                        (center[0]-arc_radius, center[1]-arc_radius,
                            arc_radius*2, arc_radius*2),
                        start_angle, end_angle, arc_width)
        


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


    def draw_orbit_decorations(self):
        """绘制目标行星和干扰行星的轨道"""
        # 目标行星轨道
        self.draw_dashed_circle(
            self.env.star['pos'], 
            self.env.target['orbit_radius'], 
            color=(173, 216, 230, 99),  # 浅蓝色，半透明
            dash_length=15, 
            gap_length=15
        )
        
        # 干扰行星轨道
        self.draw_dashed_circle(
            self.env.star['pos'], 
            self.env.disturber['orbit_radius'], 
            color=(255, 182, 193, 99),  # 浅红色，半透明
            dash_length=15, 
            gap_length=15
        )

    def draw_dashed_circle(self, center, radius, color, dash_length, gap_length):
        """
        绘制虚线圆
        :param center: 圆心 [x, y]
        :param radius: 半径
        :param color: 颜色 (R, G, B, A)
        :param dash_length: 每段虚线长度
        :param gap_length: 每段间隔长度
        """
        # 计算圆周长
        circumference = 2 * math.pi * radius
        num_segments = int(circumference / (dash_length + gap_length))
        
        # 绘制每段虚线
        for i in range(num_segments):
            start_angle = 2 * math.pi * i / num_segments
            end_angle = 2 * math.pi * (i + dash_length / (dash_length + gap_length)) / num_segments
            pygame.draw.arc(
                self.env.screen, color,
                (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
                start_angle, end_angle, 2
            )

    def draw_time_panel(self):
        """绘制时间面板"""
        elapsed_time = self.env.core.get_elapsed_time()
        remaining_time = max(0, GAME_CONFIG['time_limit'] - elapsed_time)
        
        # 颜色：剩余时间不足时显示红色
        color = (255, 0, 0) if remaining_time < GAME_CONFIG['warning_time'] else (255, 255, 255)
        
        # 显示时间
        font = pygame.font.Font(None, 24)
        text = font.render(f"Time: {int(remaining_time)}s", True, color)
        self.env.screen.blit(text, (SCREEN_WIDTH - 120, 10))
        
    def draw(self, actions):
        """主绘制方法"""
        self.env.screen.fill((0, 0, 0))

        # 绘制时间面板
        self.draw_time_panel()

        self.draw_background()

        # 绘制轨道装饰
        # self.draw_orbit_decorations()

        
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
        
        # 绘制目标行星
        if USE_TEXTURES and 'target' in self.textures:
            rect = self.textures['target'].get_rect(center=self.env.target['pos'])
            self.env.screen.blit(self.textures['target'], rect)
        else:
            pygame.draw.circle(self.env.screen, (0, 255, 0),
                            self.env.target['pos'], self.env.target['radius'])

        # 新增：绘制目标装饰UI
        self.draw_target_decorations()
        
        # 绘制干扰行星
        self.draw_disturber()

        # 绘制飞船
        self.draw_rotated_ship()
        
        # 绘制推进器效果
        self.draw_thrusters(actions)
        
        # 绘制信息面板
        self.draw_info_panel()
        
        pygame.display.flip()