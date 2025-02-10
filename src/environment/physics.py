import math
import random

class PhysicsEngine:
    @staticmethod
    def calculate_orbital_position(center, radius, angle):
        """计算轨道位置"""
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        return [x, y]
 
    @staticmethod
    def calculate_orbital_velocity(center, radius, angular_speed):
        """
        计算目标行星的轨道速度
        :param center: 恒星的中心位置 [x, y]
        :param radius: 轨道半径
        :param angular_speed: 角速度（弧度/帧）
        :return: 速度向量 [vx, vy]
        """
        # 计算当前轨道角度（假设从初始位置开始）
        angle = angular_speed  # 这里可以根据需要调整
        
        # 计算速度方向（切线方向）
        tangent_angle = angle + math.pi / 2  # 切线方向与半径方向垂直
        
        # 计算速度大小（v = ω * r）
        speed = angular_speed * radius
        
        # 计算速度分量
        vx = speed * math.cos(tangent_angle)
        vy = speed * math.sin(tangent_angle)
        
        return [vx, vy]

    @staticmethod
    def calculate_gravity(ship_pos, star_pos, star_mass, G):
        """计算恒星引力"""
        dx = star_pos[0] - ship_pos[0]
        dy = star_pos[1] - ship_pos[1]
        r = max(math.hypot(dx, dy), 10)  # 防止除以零
        F = G * star_mass / (r**2)
        angle = math.atan2(dy, dx)
        return [F * math.cos(angle), F * math.sin(angle)]

    @staticmethod
    def apply_thrust(ship, actions):
        """处理推进器控制（考虑旋转角度）"""
        thrust = ship['thrust']
        angle_rad = math.radians(ship['rotation'])
        
        thrust_x = 0
        thrust_y = 0
        
        if actions[0]:  # 左旋转
            ship['rotation'] += ship['rotation_speed']
        if actions[1]:  # 右旋转
            ship['rotation'] -= ship['rotation_speed']
            
        if actions[2]:  # 主推进器（后方）
            thrust_x += thrust * math.cos(angle_rad)
            thrust_y -= thrust * math.sin(angle_rad)  # y轴向下
        if actions[3]:  # 反向推进（前方）
            thrust_x -= thrust * math.cos(angle_rad)
            thrust_y += thrust * math.sin(angle_rad)
            
        return thrust_x, thrust_y
        
