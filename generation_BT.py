#!/usr/bin/env python3
import os

import openai
from utils import post_processing, subtree_assembly
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
        node_type = node_info[0]              # 节点类型，如 '?', '->', '!'
        node_name = ''.join(node_info[1:])    # 节点名称
        parsed_data.append((indent_level, node_type, node_name))
    
    return parsed_data

def create_behavior_tree(tree_data):
    bt = Digraph('BehaviorTree', filename='behavior_tree.gv')

    parent_stack = [('R', -1)]                # 以根节点开始
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


def LLM_generation(generate_file, model_name, final_prompt, sub_tree_dir, api_key):
    openai.api_key = api_key
    with open(generate_file + "prompt.txt", "wt+") as file:
        file.write(final_prompt)
    response = openai.Completion.create(
        model=model_name,
        prompt=final_prompt,
        temperature=0,
        max_tokens=500,
        top_p=1,
        presence_penalty=0,
        frequency_penalty=0.2
    )

    raw_string = str(response['choices'][0]['text'])
    print(len(raw_string))
    # response = openai.ChatCompletion.create(
    #     model=model_name,                       # "gpt-4" gpt-3.5-turbo gpt-3.5-turbo-16k-0613
    #     temperature=0.0,
    #     max_tokens=500,
    #     top_p=1,
    #     presence_penalty=0,
    #     frequency_penalty=0.2,
    #     messages=[
    #         {"role": "user", "content": final_prompt}
    #     ]
    # )
    # raw_string = str(response.choices[0].message['content'].strip())

    # 检查目录是否存在
    os.makedirs(generate_file, exist_ok=True)
    raw_path  = generate_file + "raw.txt"
    full_path = generate_file + "test.tree"

    raw_text_file = open(raw_path, "wt+")
    n = raw_text_file.write(raw_string)
    raw_text_file.close()

    output_text = post_processing(raw_string)
    print(output_text)

    text_file = open(full_path, "wt")
    m = text_file.write(subtree_assembly(output_text, sub_tree_dir))
    text_file.close()

def read_prompt(prompt_path):
    with open(prompt_path, "r") as file:
        content = file.read()
    return content

if __name__ == '__main__':
    generate_file   = "../config/result/"                                      # 结果写入
    sub_tree_dir    = "../config/subtree/"              
    openai.api_base = "https://api.macc.cc/v1"                                 # "https://www.wushuangai.com/v1"           
    api_key         = 'sk-4bn327nYOXoLpZGL5fC35484F8104408A7795d6f38B5B396'    #'sk-DviL7op5EEUdYYvFD72b84A2F32d4bE4A130C3F1404c372f'
    model_name      = "gpt-3.5-turbo-instruct"                                 # "gpt-3.5-turbo-instruct" 
    
    # 构造提示词
    # 保存已有的知识库复用，生成行为树的向量化
    
    final_prompt  = read_prompt("../config/prompt/environment_description.txt") + \
                    '\n' + \
                    read_prompt("../config/prompt/existing_sub_trees.txt") + \
                    '\n' + \
                    read_prompt("../config/prompt/source_behavior_tree.txt")
                    # '\n' + \
                    # read_prompt("../config/prompt/robot_sensing_abilities.txt") 
    LLM_generation(generate_file, model_name, final_prompt, sub_tree_dir, api_key)
    
    # 可视化行为树
    tree_data = parse_tree_file('/home/behavior_tree_generation/config/result/test.tree')
    create_behavior_tree(tree_data)


#/bt_fsm_comparison/submodules
