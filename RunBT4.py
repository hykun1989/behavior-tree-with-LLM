import py_trees
import numpy as np

def run_behavior_tree(environment):
    # 获取车辆信息
    def get_vehicle_info(vehicle_id):
        for vehicle in environment["vehicles"]:
            if vehicle["id"] == vehicle_id:
                if "current lane" in vehicle and "lane position" in vehicle:
                    return vehicle
                else:
                    raise ValueError("Vehicle info does not have required keys:", vehicle)
        return None

    # 获取当前车道信息
    def get_current_lane_info(lane_id):
        for lane in environment["lanes"]:
            if lane["id"] == lane_id:
                return lane
        return None

    # 假设的动作执行函数
    def perform_action(action):
        print(f"Performing action: {action}")

    # 安全距离计算函数
    def safe_distance(speed, relative_speed=0, reaction_time=1):
        # 基于两秒规则并考虑相对速度调整安全距离
        distance = speed * reaction_time
        # 如果相对速度为正（即自车比前车快），需要增加安全距离
        if relative_speed > 0:
            distance += 0.5 * relative_speed * reaction_time
        return distance

    # 安全距离比较函数
    def is_distance_safe(ego_distance, vehicle_distance, ego_speed, vehicle_speed):
        relative_speed = ego_speed - vehicle_speed
        safe_dist = safe_distance(ego_speed, relative_speed)
        if ego_distance > vehicle_distance:  # ego 在车辆后方
            return ego_distance - vehicle_distance > safe_dist
        else:  # ego 在车辆前方
            return vehicle_distance - ego_distance > safe_dist

    # 检查是否需要减速
    def check_need_to_slow(ego_info):
        if ego_info is None or "current lane" not in ego_info or "lane position" not in ego_info or "speed" not in ego_info:
            raise ValueError("Ego info does not have required keys:", ego_info)
        distant_current = np.array([i["lane position"] - ego_info["lane position"] if i["current lane"] == ego_info["current lane"] and i["id"] != "ego" else 1000000 for i in environment["vehicles"]])
        head_vehicle    = min(distant_current[distant_current>0])
        for vehicle in environment["vehicles"]:
            if vehicle["id"] != "ego" and vehicle["current lane"] == ego_info["current lane"] and vehicle["lane position"] - ego_info["lane position"] == head_vehicle:
                relative_speed = ego_info["speed"] - vehicle["speed"]
                print(safe_distance(ego_info["speed"], relative_speed))
                if relative_speed > 0 and vehicle["lane position"] - ego_info["lane position"] > safe_distance(ego_info["speed"], relative_speed):
                    return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS

    # 检查是否需要保持当前速度
    def check_need_to_idle(ego_info):
        if ego_info is None or "current lane" not in ego_info or "lane position" not in ego_info or "speed" not in ego_info:
            raise ValueError("Ego info does not have required keys:", ego_info)
        distant_current = np.array([i["lane position"] - ego_info["lane position"] if i["current lane"] == ego_info["current lane"] and i["id"] != "ego" else 1000000 for i in environment["vehicles"]])
        head_vehicle    = min(distant_current[distant_current>0])
        for vehicle in environment["vehicles"]:
            if vehicle["id"] != "ego" and vehicle["current lane"] == ego_info["current lane"] and  vehicle["lane position"] - ego_info["lane position"] == head_vehicle:
                relative_speed = ego_info["speed"] - vehicle["speed"]
                print(safe_distance(ego_info["speed"], relative_speed))
                if vehicle["lane position"] - ego_info["lane position"] < safe_distance(ego_info["speed"], relative_speed)-10:
                    return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS

    # 检查前方交通情况函数
    def check_traffic_ahead(ego_info):
        if ego_info is None or "current lane" not in ego_info or "lane position" not in ego_info or "speed" not in ego_info:
            raise ValueError("Ego info does not have required keys:", ego_info)
        distant_current = np.array([i["lane position"] - ego_info["lane position"] if i["current lane"] == ego_info["current lane"] and i["id"] != "ego" else 1000000 for i in environment["vehicles"]])
        head_vehicle    = min(distant_current[distant_current>0])
        for vehicle in environment["vehicles"]:
            if "id" not in vehicle or "current lane" not in vehicle or "lane position" not in vehicle or "speed" not in vehicle:
                raise ValueError("Vehicle info does not have required keys:", vehicle)
            if vehicle["id"] != "ego" and vehicle["current lane"] == ego_info["current lane"] and vehicle["lane position"] - ego_info["lane position"] == head_vehicle:
                # 添加相对速度的考虑
                relative_speed = ego_info["speed"] - vehicle["speed"]
                print(safe_distance(ego_info["speed"], relative_speed))
                # 调整安全距离计算方法
                if vehicle["lane position"] - ego_info["lane position"] < safe_distance(ego_info["speed"], relative_speed):
                    return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS

    # 检查左侧车道安全性函数
    def check_left_lane_safe(ego_info):
        return check_lane_safe(ego_info, is_left_lane=True)

    # 检查右侧车道安全性函数
    def check_right_lane_safe(ego_info):
        return check_lane_safe(ego_info, is_left_lane=False)

    # 检查车道安全性函数
    def check_lane_safe(ego_info, is_left_lane):
        if ego_info is None or "current lane" not in ego_info or "speed" not in ego_info:
            raise ValueError("Ego info does not have required key 'current lane' or 'speed':", ego_info)
        current_lane_info = get_current_lane_info(ego_info["current lane"])
        if current_lane_info is None or not (current_lane_info["left_lanes"] if is_left_lane else current_lane_info["right_lanes"]):
            return py_trees.common.Status.FAILURE
        side_lane_id = (current_lane_info["left_lanes"][-1] if is_left_lane else current_lane_info["right_lanes"][0])
        distant_current = np.array([ego_info["lane position"] - i["lane position"] if i["current lane"] == side_lane_id and i["id"] != "ego" else 1000000 for i in environment["vehicles"]])

        behind_vehicles = distant_current[distant_current <= 0]
        follow_vehicle = max(behind_vehicles) if behind_vehicles.size > 0 else None  # Use None if no vehicles are behind
        
        ahead_vehicles = distant_current[distant_current > 0]
        head_vehicle = min(ahead_vehicles) if ahead_vehicles.size > 0 else None  # Use None if no vehicles are ahead

        for vehicle in environment["vehicles"]:
            if vehicle["current lane"] == side_lane_id:
                distance = ego_info["lane position"] - vehicle["lane position"]
                if (distance != head_vehicle and distance != follow_vehicle):
                    continue
                if not is_distance_safe(distance, 0, ego_info["speed"], vehicle["speed"]):
                    return py_trees.common.Status.FAILURE

        return py_trees.common.Status.SUCCESS

    # 行为节点定义
    class CheckTrafficAhead(py_trees.behaviour.Behaviour):
        def update(self):
            ego_info = get_vehicle_info("ego")
            return check_traffic_ahead(ego_info)
        
    class CheckNeedToSlow(py_trees.behaviour.Behaviour):
        def update(self):
            ego_info = get_vehicle_info("ego")
            return check_need_to_slow(ego_info)

    class CheckNeedToIdle(py_trees.behaviour.Behaviour):
        def update(self):
            ego_info = get_vehicle_info("ego")
            return check_need_to_idle(ego_info)

    class Faster(py_trees.behaviour.Behaviour):
        def update(self):
            action = 'faster'
            perform_action(action)
            return py_trees.common.Status.SUCCESS

    class Slower(py_trees.behaviour.Behaviour):
        def update(self):
            action = 'slower'
            perform_action(action)
            return py_trees.common.Status.SUCCESS

    class CheckLeftLaneForSpaceAndSafety(py_trees.behaviour.Behaviour):
        def update(self):
            ego_info = get_vehicle_info("ego")
            return check_left_lane_safe(ego_info)


    class LaneLeft(py_trees.behaviour.Behaviour):
        def update(self):
            action = 'lane_left'
            perform_action(action)
            return py_trees.common.Status.SUCCESS

    class Idle(py_trees.behaviour.Behaviour):
        def update(self):
            action = 'idle'
            perform_action(action)
            return py_trees.common.Status.SUCCESS

    class CheckRightLaneForSpaceAndSafety(py_trees.behaviour.Behaviour):
        def update(self):
            ego_info = get_vehicle_info("ego")
            return check_right_lane_safe(ego_info)

    class LaneRight(py_trees.behaviour.Behaviour):
        def update(self):
            action = 'lane_right'
            perform_action(action)
            return py_trees.common.Status.SUCCESS

    # 这个代码如何更新
    root = py_trees.composites.Selector(name="HighSpeedAvoidCollision", memory=False)
    # phase 6
    phase6 = py_trees.composites.Sequence(name="Phase6", memory=False)
    check_idle = CheckNeedToIdle(name="CheckNeedToIdle")
    idle2 = Idle(name="Idle")
    phase6.add_children([check_idle, idle2])
    # phase 2
    phase2 = py_trees.composites.Sequence(name='Phase2', memory=False)
    check_left_lane_safe_node = CheckLeftLaneForSpaceAndSafety(name='CheckLeftLaneForSpaceAndSafety')
    lane_left_node = LaneLeft(name='LaneLeft')
    phase2.add_children([check_left_lane_safe_node, lane_left_node])    
    # phase 3
    phase3 = py_trees.composites.Sequence(name='Phase3', memory=False)
    check_right_lane_safe_node = CheckRightLaneForSpaceAndSafety(name='CheckRightLaneForSpaceAndSafety')
    lane_right_node = LaneRight(name='LaneRight')
    phase3.add_children([check_right_lane_safe_node, lane_right_node])
    # phase 4
    phase4 = py_trees.composites.Sequence(name='Phase4', memory=False)
    check_slow = CheckNeedToSlow(name='CheckNeedToSlow')
    slower = Slower(name='Slower')
    phase4.add_children([check_slow, slower])
    # phase 5
    phase5 = py_trees.composites.Sequence(name='Phase5', memory=False)
    check_idle = CheckNeedToIdle(name='CheckNeedToIdle')
    idle = Idle(name='Idle')
    phase5.add_children([check_idle, idle])
    
    phase1 = py_trees.composites.Sequence(name='Phase1', memory=False)
    faster_node = Faster(name="Faster")
    phase1.add_children([faster_node])
    
    root.add_children([phase2, phase3, phase5, phase4, phase1])
    behaviour_tree = py_trees.trees.BehaviourTree(root)
    behaviour_tree.tick()
    # 获取执行的最终节点
    final_node = behaviour_tree.tip()

    return final_node.name
