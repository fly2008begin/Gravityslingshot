# [file name]: main.py
import pygame
import argparse
import time
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from environment.rl_env import SpaceRLEnv

def parse_args():
    parser = argparse.ArgumentParser(description='Space Navigation Environment')
    parser.add_argument('--mode', type=str, required=True, 
                       choices=['play', 'train', 'test'],
                       help="Running mode: play/train/test")
    parser.add_argument('--model-path', type=str, default='ppo_asteroid',
                       help="Path to save/load model")
    parser.add_argument('--timesteps', type=int, default=100000,
                       help="Training timesteps")
    parser.add_argument('--simulation-fps', type=int, default=1000,
                       help="Physics simulation frequency (steps per second)")
    return parser.parse_args()

def human_play():
    """人类玩家模式"""
    from environment.space_env import SpaceEnv
    from core.game_core import GameCore
    from render.renderer import GameRenderer
    
    env = SpaceEnv()
    core = GameCore(env)
    renderer = GameRenderer(env)
    
    running = True
    while running:
        actions = [False] * 4
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        keys = pygame.key.get_pressed()
        actions[0] = keys[pygame.K_a] or keys[pygame.K_LEFT]
        actions[1] = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        actions[2] = keys[pygame.K_w] or keys[pygame.K_UP]
        actions[3] = keys[pygame.K_s] or keys[pygame.K_DOWN]
        
        status = core.update(actions)
        renderer.draw(actions)
        
        if status != 'playing':
            print(f"Game Over: {status}")
            core.reset()
            renderer.trail_points = []
            
        pygame.time.Clock().tick(60)
    pygame.quit()

def train(args):
    """强化学习训练模式"""
    # 创建并行环境
    train_env = make_vec_env(
        lambda: SpaceRLEnv(
            render_mode=None,
            simulation_fps=args.simulation_fps,
            max_episode_steps=1000
        ),
        n_envs=4,
        vec_env_cls=DummyVecEnv
    )
    
    # 初始化PPO模型
    model = PPO(
        "MlpPolicy",
        train_env,
        verbose=1,
        tensorboard_log="./ppo_asteroid_tensorboard/",
        device='auto'
    )
    
    # 开始训练
    model.learn(total_timesteps=args.timesteps)
    model.save(args.model_path)
    train_env.close()
    print(f"Training completed. Model saved to {args.model_path}")

def test(args):
    """测试训练结果"""
    env = SpaceRLEnv(
        render_mode='human',
        simulation_fps=60  # 实时渲染速度
    )
    model = PPO.load(args.model_path)
    
    obs, _ = env.reset()
    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, _ = env.step(action)
        env.render()
        
        if terminated or truncated:
            obs, _ = env.reset()
            
    env.close()

if __name__ == "__main__":
    args = parse_args()
    
    if args.mode == 'play':
        human_play()
    elif args.mode == 'train':
        train(args)
    elif args.mode == 'test':
        test(args)