import math
from environment.physics import PhysicsEngine

class GameCore:
    def __init__(self, env):
        self.env = env
        self.reset()
        
    def reset(self):
        """重置游戏状态"""
        # 初始化飞船速度和方向
        angle_rad = math.radians(self.env.ship['angle'])
        self.env.ship['velocity'] = [
            self.env.ship['speed'] * math.cos(angle_rad),
            -self.env.ship['speed'] * math.sin(angle_rad)  # y轴向下
        ]
        self.env.ship['fuel'] = 1000
        self.env.ship['pos'] = [100, self.env.screen_height-100]
        
    def update(self, actions):
        """更新游戏状态"""
        ship = self.env.ship
        
        # 计算推进器推力
        thrust_x, thrust_y, fuel_cost = PhysicsEngine.apply_thrust(ship, actions)
        ship['fuel'] = max(ship['fuel'] - fuel_cost, 0)
        
        # 计算引力
        gravity = PhysicsEngine.calculate_gravity(
            ship['pos'],
            self.env.star['pos'],
            self.env.star['mass'],
            self.env.G
        )
        
        # 更新速度
        ship['velocity'][0] += (thrust_x + gravity[0]) * self.env.dt
        ship['velocity'][1] += (thrust_y + gravity[1]) * self.env.dt
        
        # 更新位置
        ship['pos'][0] += ship['velocity'][0] * self.env.dt
        ship['pos'][1] += ship['velocity'][1] * self.env.dt
        
        # 边界检测
        if (ship['pos'][0] < 0 or ship['pos'][0] > self.env.screen_width or
            ship['pos'][1] < 0 or ship['pos'][1] > self.env.screen_height):
            return 'out_of_bounds'
            
        # 恒星碰撞检测
        distance_to_star = math.hypot(
            ship['pos'][0] - self.env.star['pos'][0],
            ship['pos'][1] - self.env.star['pos'][1]
        )
        if distance_to_star < self.env.star['radius'] + ship['radius']:
            return 'star_collision'
            
        # 目标达成检测
        distance_to_target = math.hypot(
            ship['pos'][0] - self.env.target['pos'][0],
            ship['pos'][1] - self.env.target['pos'][1]
        )
        if distance_to_target < self.env.target['radius']:
            return 'success'
            
        return 'playing'