import pygame
from environment.space_env import SpaceEnv
from core.game_core import GameCore
from render.renderer import GameRenderer
from config import *


def main():
    pygame.init()
    env = SpaceEnv()
    core = GameCore(env)
    renderer = GameRenderer(env)
    
    running = True
    while running:
        # 处理控制输入
        actions = [False] * 4  # [左转, 右转, 推进, 反向推进]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  # A键或左箭头键左转
            actions[0] = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:  # D键或右箭头键右转
            actions[1] = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:  # W键或上箭头键推进
            actions[2] = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  # S键或下箭头键反向推进
            actions[3] = True
            
        # 更新游戏状态
        status = core.update(actions)
        
        # 渲染画面（传递 actions 参数）
        renderer.draw(actions)
        
        # 处理游戏结束
        if status != 'playing':
            print(f"Game Over: {status}")
            core.reset()  # 自动重置游戏
            renderer.trail_points = []  # 重置轨迹
            
        # 控制帧率
        pygame.time.Clock().tick(60)  # 限制帧率为 60 FPS

    # 退出游戏
    pygame.quit()

if __name__ == "__main__":
    main()