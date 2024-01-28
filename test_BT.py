import os
import json
import numpy as np
import gymnasium as gym
from gymnasium.wrappers import RecordVideo
import RunBT4
from scenario.scenario import Scenario

# 定义映射字典
action_mapping = {
    'Faster': 3,
    'Slower': 4,
    'LaneLeft': 0,
    'LaneRight': 2,
    'Idle': 1
}

# 函数：根据输入的字符串返回对应的整数
def get_action_code(input_str):
    for action in action_mapping.keys():
        if action in input_str:
            return action_mapping[action]
    return -1  # 如果动作不在字典中，返回-1

# 设置环境
vehicleCount = 15
# environment setting
config = {
    "observation": {
        "type": "Kinematics",
        "features": ["presence", "x", "y", "vx", "vy"],
        "absolute": True,
        "normalize": False,
        "vehicles_count": vehicleCount,
        "see_behind": True,
    },
    "action": {
        "type": "DiscreteMetaAction",
        "target_speeds": np.linspace(0, 32, 9),
    },
    "duration": 40,
    "vehicles_density": 2,
    "show_trajectories": True,
    "render_agent": True,
}
env = gym.make('highway-v0', render_mode="rgb_array")
env.configure(config)
env = RecordVideo(env, './results-video', name_prefix="highwayv0")
env.unwrapped.set_record_video_wrapper(env)
obs, info = env.reset()
env.render()

# 设置数据库和工具
if not os.path.exists('results-db/'):
    os.mkdir('results-db/')
database = f"results-db/highwayv0.db"
sce = Scenario(vehicleCount, database)

# 仿真循环
output = None
done = truncated = False
frame = 0
try:
    while not (done or truncated):
        # 更新行为树
        sce.upateVehicles(obs, frame)
        environment_json = sce.export2json()
        environment = json.loads(environment_json)  # 将 JSON 字符串转换为字典
        # print(environment)
        action_id = RunBT4.run_behavior_tree(environment)  # 确保传递字典
        print('输出是',action_id)
        action_code = get_action_code(action_id)
        obs, reward, done, info, X = env.step(action_code)
        # print("obs", obs)
        # print("info", info)
        # print("X", X)
        print({"action_id": action_code})
        frame += 1
finally:
    env.close()
