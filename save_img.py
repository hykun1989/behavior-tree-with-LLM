# from graphviz import Digraph

# def parse_tree_file(filename):
#     with open(filename, 'r') as file:
#         lines = file.readlines()

#     parsed_data = []
#     for line in lines:
#         # 计算每行的缩进级别（每个制表符代表一个层级）
#         indent_level = line.count('\t')
#         # 清除空白字符并分割以获取节点类型和名称
#         node_info = line.strip().split(' ')
#         node_type = node_info[0]  # 节点类型，如 '?', '->', '!'
#         node_name = ''.join(node_info[1:])  # 节点名称
#         parsed_data.append((indent_level, node_type, node_name))
    
#     return parsed_data

# def create_behavior_tree(tree_data):
#     bt = Digraph('BehaviorTree', filename='behavior_tree.gv')

#     parent_stack = [('R', -1)]  # 以根节点开始
#     for indent, node_type, node_name in tree_data:
#         while indent <= parent_stack[-1][1]:
#             parent_stack.pop()

#         node_id = f'Node{len(bt.body)}'  # 为每个节点生成唯一ID
#         bt.node(node_id, f'{node_type} {node_name}' if node_name else node_type)
#         bt.edge(parent_stack[-1][0], node_id)

#         parent_stack.append((node_id, indent))

#     # 保存为PNG格式的图片
#     bt.render(filename='behavior_tree', format='png', cleanup=True)

# tree_data = parse_tree_file('/home/behavior_tree_generation/config/result/test.tree')
# create_behavior_tree(tree_data)

from graphviz import Digraph

def parse_tree_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    parsed_data = []
    for line in lines:
        # 计算每行的缩进级别（每个制表符代表一个层级）
        indent_level = line.count('\t')
        # 清除空白字符并分割以获取节点类型和名称
        node_info = line.strip().split(' ')
        node_type = node_info[0]  # 节点类型，如 '?', '->', '!'
        node_name = ''.join(node_info[1:])  # 节点名称
        parsed_data.append((indent_level, node_type, node_name))
    
    return parsed_data

def create_behavior_tree(tree_data):
    bt = Digraph('BehaviorTree', filename='behavior_tree.gv')

    parent_stack = [('R', -1)]  # 以根节点开始
    for indent, node_type, node_name in tree_data:
        while indent <= parent_stack[-1][1]:
            parent_stack.pop()

        node_id = f'Node{len(bt.body)}'  # 为每个节点生成唯一ID

        # 根据节点类型设置不同的样式和颜色
        if node_type == '->':
            bt.node(node_id, f'{node_type} {node_name}' if node_name else node_type, shape='box', style='filled', color='lightblue')
        elif node_type == '?':
            bt.node(node_id, f'{node_type} {node_name}' if node_name else node_type, shape='diamond', style='filled', color='lightgrey')
        elif node_type == '<!>':
            bt.node(node_id, f'{node_type} {node_name}' if node_name else node_type, shape='ellipse', style='filled', color='orange')
        else:  # 默认样式
            bt.node(node_id, f'{node_type} {node_name}' if node_name else node_type)

        bt.edge(parent_stack[-1][0], node_id)
        parent_stack.append((node_id, indent))

    # 保存为PNG格式的图片
    bt.render(filename='behavior_tree', format='png', cleanup=True)

tree_data = parse_tree_file('/home/behavior_tree_generation/config/result/test.tree')
create_behavior_tree(tree_data)
