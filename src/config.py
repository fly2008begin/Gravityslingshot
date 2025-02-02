import os
import math

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, 'assets')

# 图形模式配置
USE_TEXTURES = True  # 是否使用贴图

# 窗口设置
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = (0, 0, 0)

# 物理常数
GRAVITY_CONSTANT = 0.5  # 引力常数（简化版）
TIME_STEP = 0.1  # 时间步长

# 恒星配置
STAR_CONFIG = {
    'texture': os.path.join(ASSETS_PATH, 'images/star.png') if USE_TEXTURES else None,
    'radius': 50,
    'mass': 1e5,
    'color': (255, 215, 0)  # 金色
}

# 目标行星配置
TARGET_CONFIG = {
    'texture': os.path.join(ASSETS_PATH, 'images/planet.png') if USE_TEXTURES else None,
    'radius': 30,
    'orbit_radius': 300,  # 轨道半径
    'angular_speed': 0.002,  # 角速度（弧度/帧）
    'color': (0, 255, 0)  # 绿色
}

# 飞船配置
SHIP_CONFIG = {
    'texture': os.path.join(ASSETS_PATH, 'images/ship.png') if USE_TEXTURES else None,
    'radius': 10,
    'thrust': 0.2,
    'initial_speed': 3.0,  # 初始速度模长
    'rotation_speed': 3,  # 度/帧
    'initial_angle': 45,  # 初始角度（度）
    'color': (100, 100, 255),  # 蓝色
    'thruster_color': (255, 100, 100),  # 红色
    'trail_color': (100, 100, 255),  # 蓝色
    'max_trail_length': 300,


}

# 轨迹预测配置
PREDICTION_CONFIG = {
    'steps': 100,
    'time_step': 0.1,
    'color': (255, 100, 100),  # 红色
    'min_alpha': 50,
    'max_alpha': 200
}

# 信息面板配置
INFO_PANEL_CONFIG = {
    'font_size': 24,
    'font_color': (255, 255, 255),  # 白色
    'position': (10, 10),
    'line_spacing': 25
}

# 推进器效果配置
THRUSTER_CONFIG = {
    'base_length': 15,
    'max_length': 25,
    'flare_width': 5,
    'particle_count': 5,
    'particle_spread': 5,
    'particle_colors': [
        (255, 200, 100),  # 亮黄色
        (255, 150, 50)    # 橙色
    ]
}

SUCCESS_CONDITIONS = {
    'max_speed': 17.0,       # 最大允许相对速度
    'max_angle_deviation':30  # 最大允许角度偏差（度）
}


# 背景配置
RENDER_BACKGROUND = True  # 是否渲染星空背景
STAR_COUNT = 200         # 星星数量
STAR_SIZE_RANGE = (1, 3) # 星星尺寸范围（像素）
STAR_BRIGHTNESS_RANGE = (50, 255) # 亮度范围（0-255）
BACKGROUND_SEED = 42     # 随机种子（固定此值可使星空不变）

