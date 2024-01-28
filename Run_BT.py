# import py_trees
# import time

# def run_behavior_tree(environment):
#     # 获取车辆信息
#     def get_vehicle_info(vehicle_id):
#         for vehicle in environment["vehicles"]:
#             if vehicle["id"] == vehicle_id:
#                 # 确保 vehicle 字典包含所有必要的键
#                 if "current lane" in vehicle and "lane position" in vehicle:
#                     return vehicle
#                 else:
#                     print("Vehicle info does not have required keys:", vehicle)
#                     return None
#         return None

#     # 获取当前车道信息
#     def get_current_lane_info(lane_id):
#         for lane in environment["lanes"]:
#             if lane["id"] == lane_id:
#                 return lane
#         return None

#     # 假设的动作执行函数
#     def perform_action(action):
#         print(f"Performing action: {action}")

#     # 检查前方交通情况
#     def check_traffic_ahead(ego_info):
#         if "current lane" not in ego_info or "lane position" not in ego_info:
#             print("Ego info does not have required keys:", ego_info)
#             return py_trees.common.Status.FAILURE
#         for vehicle in environment["vehicles"]:
#             if "id" not in vehicle or "current lane" not in vehicle or "lane position" not in vehicle:
#                 print("Vehicle info does not have required keys:", vehicle)
#                 return py_trees.common.Status.FAILURE
#             if vehicle["id"] != "ego" and vehicle["current lane"] == ego_info["current lane"] and vehicle["lane position"] > ego_info["lane position"]:
#                 if vehicle["lane position"] - ego_info["lane position"] < 10:
#                     return py_trees.common.Status.FAILURE
#         return py_trees.common.Status.SUCCESS

#     # 检查左侧车道是否安全
#     def check_left_lane_safe(ego_info):
#         if "current lane" not in ego_info:
#             print("Ego info does not have required key 'current lane':", ego_info)
#             return py_trees.common.Status.FAILURE
#         current_lane_info = get_current_lane_info(ego_info["current_lane"])
#         if not current_lane_info["left_lanes"]:
#             return py_trees.common.Status.FAILURE
#         left_lane_id = current_lane_info["left_lanes"][0]
#         for vehicle in environment["vehicles"]:
#             if vehicle["id"] != "ego" and vehicle["current_lane"] == left_lane_id and abs(vehicle["lane_position"] - ego_info["lane_position"]) < 10:
#                 return py_trees.common.Status.FAILURE
#         return py_trees.common.Status.SUCCESS

#     # 检查右侧车道是否安全
#     def check_right_lane_safe(ego_info):
#         current_lane_info = get_current_lane_info(ego_info["current_lane"])
#         if not current_lane_info["right_lanes"]:
#             return py_trees.common.Status.FAILURE
#         right_lane_id = current_lane_info["right_lanes"][0]
#         for vehicle in environment["vehicles"]:
#             if vehicle["id"] != "ego" and vehicle["current_lane"] == right_lane_id and abs(vehicle["lane_position"] - ego_info["lane_position"]) < 10:
#                 return py_trees.common.Status.FAILURE
#         return py_trees.common.Status.SUCCESS

#     # 行为节点定义
#     class CheckTrafficAhead(py_trees.behaviour.Behaviour):
#         def update(self):
#             ego_info = get_vehicle_info("ego")
#             return check_traffic_ahead(ego_info)

#     class Faster(py_trees.behaviour.Behaviour):
#         def update(self):
#             action = 'faster'
#             perform_action(action)
#             return py_trees.common.Status.SUCCESS

#     class Slower(py_trees.behaviour.Behaviour):
#         def update(self):
#             action = 'slower'
#             perform_action(action)
#             return py_trees.common.Status.SUCCESS

#     class CheckLeftLaneForSpaceAndSafety(py_trees.behaviour.Behaviour):
#         def update(self):
#             ego_info = get_vehicle_info("ego")
#             return check_left_lane_safe(ego_info)

#     class LaneLeft(py_trees.behaviour.Behaviour):
#         def update(self):
#             action = 'lane_left'
#             perform_action(action)
#             return py_trees.common.Status.SUCCESS

#     class CheckRightLaneForSpaceAndSafety(py_trees.behaviour.Behaviour):
#         def update(self):
#             ego_info = get_vehicle_info("ego")
#             return check_right_lane_safe(ego_info)

#     class LaneRight(py_trees.behaviour.Behaviour):
#         def update(self):
#             action = 'lane_right'
#             perform_action(action)
#             return py_trees.common.Status.SUCCESS

#     # 构建行为树结构
#     root = py_trees.composites.Selector(name="HighSpeedAvoidCollision", memory=False)

#     phase1 = py_trees.composites.Sequence(name="Phase1", memory=False)
#     check_traffic_ahead_node = CheckTrafficAhead(name="CheckTrafficAhead")
#     faster_node = Faster(name="Faster")
#     phase1.add_children([check_traffic_ahead_node, faster_node])

#     phase1_3 = py_trees.composites.Selector(name="Phase1_3", memory=False)
#     check_left_lane_node = CheckLeftLaneForSpaceAndSafety(name="CheckLeftLaneForSpaceAndSafety")
#     lane_left_node = LaneLeft(name="LaneLeft")
#     phase1_3_1 = py_trees.composites.Sequence(name="Phase1_3_1", memory=False)
#     phase1_3_1.add_children([check_left_lane_node, lane_left_node])

#     check_right_lane_node = CheckRightLaneForSpaceAndSafety(name="CheckRightLaneForSpaceAndSafety")
#     lane_right_node = LaneRight(name="LaneRight")
#     phase1_3_2 = py_trees.composites.Sequence(name="Phase1_3_2", memory=False)
#     phase1_3_2.add_children([check_right_lane_node, lane_right_node])

#     slower_node = Slower(name="Slower")
#     phase1_3.add_children([phase1_3_1, phase1_3_2, slower_node])

#     root.add_children([phase1, phase1_3])

#     behaviour_tree = py_trees.trees.BehaviourTree(root)
#     behaviour_tree.tick()
#     final_node = behaviour_tree.tip()

#     return final_node.name
#     # print(py_trees.display.ascii_tree(root, show_status=True))

import py_trees
import time
import numpy as np

def run_behavior_tree(environment):
    # 获取车辆信息
    def get_vehicle_info(vehicle_id):
        for vehicle in environment["vehicles"]:
            if vehicle["id"] == vehicle_id:
                # 确保 vehicle 字典包含所有必要的键
                if "current lane" in vehicle and "lane position" in vehicle:
                    return vehicle
                else:
                    print("Vehicle info does not have required keys:", vehicle)
                    return None
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

    # 检查前方交通情况
    def check_traffic_ahead(ego_info):
        if ego_info is None or "current lane" not in ego_info or "lane position" not in ego_info:
            print("Ego info does not have required keys:", ego_info)
            return py_trees.common.Status.FAILURE
        for vehicle in environment["vehicles"]:
            if "id" not in vehicle or "current lane" not in vehicle or "lane position" not in vehicle:
                print("Vehicle info does not have required keys:", vehicle)
                return py_trees.common.Status.FAILURE
            if vehicle["id"] != "ego" and vehicle["current lane"] == ego_info["current lane"] and vehicle["lane position"] > ego_info["lane position"]:
                if vehicle["lane position"] - ego_info["lane position"] < 30:
                    return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS

    # 检查左侧车道是否安全
    def check_left_lane_safe(ego_info):
        if ego_info is None or "current lane" not in ego_info:
            print("Ego info does not have required key 'current lane':", ego_info)
            return py_trees.common.Status.FAILURE
        current_lane_info = get_current_lane_info(ego_info["current lane"])
        if current_lane_info is None or not current_lane_info["left_lanes"]:
            return py_trees.common.Status.FAILURE
        # print(current_lane_info["left_lanes"])
        left_lane_id = current_lane_info["left_lanes"][-1]
        # print("左边车道的编号", ego_info["lane position"])
        distant_current = np.array([ego_info["lane position"] - i["lane position"] if i["current lane"] == left_lane_id and i["id"] != "ego" else 1000000 for i in environment["vehicles"]])
        # distant_current = [i["lane position"] - ego_info["lane position"] if i["lane position"] == left_lane_id else 1000000 for i in environment["vehicles"]]
        if min(np.abs(distant_current[distant_current<0])) < 30: # ego_info["speed"]:
            return py_trees.common.Status.FAILURE
        # for vehicle in environment["vehicles"]:
        #     if vehicle["id"] != "ego" and vehicle["current lane"] == left_lane_id and abs(vehicle["lane position"] - ego_info["lane position"]) < 60:
        #        return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS

    # 检查右侧车道是否安全
    def check_right_lane_safe(ego_info):
        if ego_info is None or "current lane" not in ego_info:
            print("Ego info does not have required key 'current lane':", ego_info)
            return py_trees.common.Status.FAILURE
        current_lane_info = get_current_lane_info(ego_info["current lane"])
        if current_lane_info is None or not current_lane_info["right_lanes"]:
            return py_trees.common.Status.FAILURE
        right_lane_id = current_lane_info["right_lanes"][0]
        # print("右边测到的编号", ego_info["lane position"])
        distant_current = np.array([ego_info["lane position"] - i["lane position"] if i["current lane"] == right_lane_id and i["id"] != "ego" else 1000000 for i in environment["vehicles"]])
        # distant_current = [i["lane position"] - ego_info["lane position"] if i["lane position"] == right_lane_id else 1000000 for i in environment["vehicles"]]
        if min(np.abs(distant_current[distant_current<0])) < 30: # ego_info["speed"]:
            return py_trees.common.Status.FAILURE
        # for vehicle in environment["vehicles"]:
        #    if vehicle["id"] != "ego" and vehicle["current lane"] == right_lane_id and abs(vehicle["lane position"] - ego_info["lane position"]) < 60:
        #         return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS

    # 行为节点定义
    class CheckTrafficAhead(py_trees.behaviour.Behaviour):
        def update(self):
            ego_info = get_vehicle_info("ego")
            return check_traffic_ahead(ego_info)

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

    class CheckRightLaneForSpaceAndSafety(py_trees.behaviour.Behaviour):
        def update(self):
            ego_info = get_vehicle_info("ego")
            return check_right_lane_safe(ego_info)

    class LaneRight(py_trees.behaviour.Behaviour):
        def update(self):
            action = 'lane_right'
            perform_action(action)
            return py_trees.common.Status.SUCCESS

    # 构建行为树结构，通过大模型决策构建的。已知的信息包括5个动作，3个判断函数（节点）
    root = py_trees.composites.Selector(name="HighSpeedAvoidCollision", memory=False)

    phase1 = py_trees.composites.Sequence(name="Phase1", memory=False)
    check_traffic_ahead_node = CheckTrafficAhead(name="CheckTrafficAhead")
    faster_node = Faster(name="Faster")
    phase1.add_children([check_traffic_ahead_node, faster_node])

    phase1_3 = py_trees.composites.Selector(name="Phase1_3", memory=False)
    check_left_lane_node = CheckLeftLaneForSpaceAndSafety(name="CheckLeftLaneForSpaceAndSafety")
    lane_left_node = LaneLeft(name="LaneLeft")
    phase1_3_1 = py_trees.composites.Sequence(name="Phase1_3_1", memory=False)
    phase1_3_1.add_children([check_left_lane_node, lane_left_node])

    check_right_lane_node = CheckRightLaneForSpaceAndSafety(name="CheckRightLaneForSpaceAndSafety")
    lane_right_node = LaneRight(name="LaneRight")
    phase1_3_2 = py_trees.composites.Sequence(name="Phase1_3_2", memory=False)
    phase1_3_2.add_children([check_right_lane_node, lane_right_node])

    slower_node = Slower(name="Slower")
    phase1_3.add_children([phase1_3_1, phase1_3_2, slower_node])

    root.add_children([phase1, phase1_3])

    behaviour_tree = py_trees.trees.BehaviourTree(root)
    behaviour_tree.tick()
    # 获取执行的最终节点
    final_node = behaviour_tree.tip()

    return final_node.name
