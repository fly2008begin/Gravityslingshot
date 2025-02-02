from environment.space_env import SpaceEnv
from core.game_core import GameCore
from render.renderer import GameRenderer
import pygame

def main():
    pygame.init()
    env = SpaceEnv()
    core = GameCore(env)
    renderer = GameRenderer(env)
    
    running = True
    while running:
        # 处理控制输入
        actions = [False]*4  # [左, 右, 上, 下]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            actions[0] = True
        if keys[pygame.K_RIGHT]:
            actions[1] = True
        if keys[pygame.K_UP]:
            actions[2] = True
        if keys[pygame.K_DOWN]:
            actions[3] = True
            
        # 更新游戏状态
        status = core.update(actions)
        
        # 渲染画面（传入actions用于推进器效果）
        renderer.draw(env, core, actions)
        
        # 处理游戏结束
        if status != 'playing':
            print(f"Game Over: {status}")
            core.reset()
            renderer.trail_points = []  # 重置轨迹
            
        pygame.time.wait(10)

        
if __name__ == "__main__":
    main()

