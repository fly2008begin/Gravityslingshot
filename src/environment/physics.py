import math

class PhysicsEngine:
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
        """处理推进器控制"""
        thrust_x = 0
        thrust_y = 0
        fuel_cost = 0
        
        # 左/右推进器
        if actions[0]:  # 左推
            thrust_x -= ship['thrust']
            fuel_cost += 1
        if actions[1]:  # 右推
            thrust_x += ship['thrust']
            fuel_cost += 1
            
        # 上/下推进器
        if actions[2]:  # 上推
            thrust_y -= ship['thrust']
            fuel_cost += 1
        if actions[3]:  # 下推
            thrust_y += ship['thrust']
            fuel_cost += 1
            
        return thrust_x, thrust_y, fuel_cost