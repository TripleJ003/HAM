#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将TXT题库转换为CSV（保留所有原始字段）
用法：
  venv/bin/python txt2csv.py                   # 交互选择要转换的TXT文件
  venv/bin/python txt2csv.py --output my_csv   # 指定输出目录
"""

import csv
import re
import os
import sys
import argparse
from pathlib import Path

def parse_qbank_full(input_file):
    """解析题库，保留所有原始字段"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    questions = []
    stats = {
        'total_lines': len(lines),
        'total_parsed': 0,
        'warnings': []
    }
    
    i = 0
    total_lines = len(lines)
    
    while i < total_lines:
        line = lines[i].strip()
        
        # 寻找题目开始标记 [J]
        if line.startswith('[J]'):
            # 初始化题目字典
            q_data = {
                'J': '',      # 编号
                'P': '',      # 章节
                'I': '',      # 类型/难度
                'Q': '',      # 题干
                'T': '',      # 答案
                'A': '',      # 选项A
                'B': '',      # 选项B
                'C': '',      # 选项C
                'D': '',      # 选项D
                'F': '',      # 图片引用（如有）
                'raw_text': '' # 原始文本（备用）
            }
            
            # 提取编号（去掉 [J] 标记，取 LY0402 部分）
            q_data['J'] = line[3:].strip()
            
            i += 1
            
            # 解析后续字段
            current_field = None
            current_content = []
            
            while i < total_lines:
                raw_line = lines[i]
                line = raw_line.strip()
                
                # 检测字段标记
                if line.startswith('[P]'):
                    # 保存上一个字段
                    if current_field and current_content:
                        q_data[current_field] = ' '.join(current_content).strip()
                    current_field = 'P'
                    current_content = [line[3:].strip()]
                    i += 1
                    
                elif line.startswith('[I]'):
                    if current_field and current_content:
                        q_data[current_field] = ' '.join(current_content).strip()
                    current_field = 'I'
                    current_content = [line[3:].strip()]
                    i += 1
                    
                elif line.startswith('[Q]'):
                    if current_field and current_content:
                        q_data[current_field] = ' '.join(current_content).strip()
                    current_field = 'Q'
                    # 清理题干开头的数字标记（如 "1\n"）
                    content = line[3:].strip()
                    # 移除单独的纯数字行
                    content = re.sub(r'^\d+\s*$', '', content)
                    current_content = [content] if content else []
                    i += 1
                    
                elif line.startswith('[T]'):
                    if current_field and current_content:
                        q_data[current_field] = ' '.join(current_content).strip()
                    current_field = 'T'
                    current_content = [line[3:].strip()]
                    i += 1
                    
                elif line.startswith('[A]'):
                    if current_field and current_content:
                        q_data[current_field] = ' '.join(current_content).strip()
                    current_field = 'A'
                    current_content = [line[3:].strip()]
                    i += 1
                    
                elif line.startswith('[B]'):
                    if current_field and current_content:
                        q_data[current_field] = ' '.join(current_content).strip()
                    current_field = 'B'
                    current_content = [line[3:].strip()]
                    i += 1
                    
                elif line.startswith('[C]'):
                    if current_field and current_content:
                        q_data[current_field] = ' '.join(current_content).strip()
                    current_field = 'C'
                    current_content = [line[3:].strip()]
                    i += 1
                    
                elif line.startswith('[D]'):
                    if current_field and current_content:
                        q_data[current_field] = ' '.join(current_content).strip()
                    current_field = 'D'
                    current_content = [line[3:].strip()]
                    i += 1
                    
                elif line.startswith('[F]'):
                    if current_field and current_content:
                        q_data[current_field] = ' '.join(current_content).strip()
                    current_field = 'F'
                    current_content = [line[3:].strip()]
                    i += 1
                    
                elif line.startswith('[J]') or (line.startswith('[') and len(line) > 1 and line[2] == ']'):
                    # 遇到新的题目标记或其他标记，停止当前题目
                    break
                    
                elif line and current_field:
                    # 当前字段的内容续行
                    # 跳过单独的页码数字行
                    if not re.match(r'^\d+$', line):
                        current_content.append(line)
                    i += 1
                    
                elif not line:
                    # 空行，跳过
                    i += 1
                else:
                    # 未识别的行，可能是格式问题，记录警告
                    if line and not line.startswith('====='):
                        stats['warnings'].append(f"第 {stats['total_parsed']+1} 题附近有未识别行: {line[:50]}")
                    i += 1
            
            # 保存最后一个字段
            if current_field and current_content:
                q_data[current_field] = ' '.join(current_content).strip()
            
            # 清理字段内容中的多余空白和换行
            for key in ['Q', 'A', 'B', 'C', 'D']:
                if q_data[key]:
                    # 合并多余空白
                    q_data[key] = re.sub(r'\s+', ' ', q_data[key]).strip()
            
            # 只要题干存在就收录
            if q_data['Q']:
                questions.append(q_data)
                stats['total_parsed'] += 1
                
        else:
            i += 1
    
    return questions, stats

def save_to_csv_full(questions, output_file):
    """保存所有字段到CSV"""
    if not questions:
        print("没有题目可保存")
        return
    
    # 获取所有可能的字段（确保每行字段一致）
    all_fields = ['J', 'P', 'I', 'Q', 'T', 'A', 'B', 'C', 'D', 'F']
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        
        # 写入表头
        writer.writerow(all_fields)
        
        # 写入数据
        for q in questions:
            row = [q.get(field, '') for field in all_fields]
            writer.writerow(row)

def print_report(questions, stats, input_file, output_file):
    """打印解析报告"""
    print()
    print("=" * 70)
    print("转换完成 - 详细报告")
    print("=" * 70)
    
    print("\n源文件: %s" % input_file)
    print("源文件行数: %d" % stats['total_lines'])
    print("成功解析: %d 道题目" % stats['total_parsed'])
    
    if stats['warnings']:
        print("\n警告 (%d 条):" % len(stats['warnings']))
        for warn in stats['warnings'][:5]:
            print("  * %s" % warn)
    
    # 统计字段完整性
    print("\n字段统计:")
    fields = ['J', 'P', 'I', 'Q', 'T', 'A', 'B', 'C', 'D', 'F']
    for field in fields:
        count = sum(1 for q in questions if q.get(field))
        print("  - %s: %d 题" % (field, count))
    
    # 输出文件信息
    print("\n输出文件: %s" % output_file)
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        if size < 1024:
            print("文件大小: %d 字节" % size)
        elif size < 1024 * 1024:
            print("文件大小: %.1f KB" % (size / 1024.0))
        else:
            print("文件大小: %.1f MB" % (size / (1024.0 * 1024.0)))
    
    print()
    print("=" * 70)
    print("转换完成！")
    print("=" * 70)


def find_txt_files(root_dir):
    """递归查找所有TXT文件（排除 venv/ csv_output/ 等无关目录）"""
    exclude_dirs = {'venv', 'csv_output', '__pycache__'}
    txt_files = []
    root = Path(root_dir)
    for f in sorted(root.rglob('*.txt')):
        # 跳过排除目录中的文件
        rel = os.path.relpath(str(f), root_dir)
        parts = rel.replace('\\', '/').split('/')
        if any(p in exclude_dirs for p in parts):
            continue
        txt_files.append(str(f))
    return txt_files


def select_file_interactive(txt_files):
    """交互式选择要转换的文件"""
    if not txt_files:
        print("未找到任何TXT文件")
        return None
    
    # 按目录分组显示
    print("找到以下TXT文件，请选择要转换的：")
    print()
    for idx, f in enumerate(txt_files, 1):
        size = os.path.getsize(f)
        if size < 1024:
            size_str = "%d B" % size
        elif size < 1024 * 1024:
            size_str = "%.1f KB" % (size / 1024.0)
        else:
            size_str = "%.1f MB" % (size / (1024.0 * 1024.0))
        print("  [%d] %s  (%s)" % (idx, f, size_str))
    
    print()
    while True:
        choice = input("请输入编号 (1-%d) 或 q 退出: " % len(txt_files)).strip()
        if choice.lower() == 'q':
            return None
        try:
            idx = int(choice)
            if 1 <= idx <= len(txt_files):
                return txt_files[idx - 1]
            else:
                print("编号超出范围，请重新输入")
        except ValueError:
            print("输入无效，请输入数字或 q")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='将TXT题库转换为CSV')
    parser.add_argument('--output', '-o', default='csv_output',
                        help='输出目录（默认: csv_output）')
    args = parser.parse_args()
    
    output_dir = args.output
    
    # 递归查找所有TXT文件
    txt_files = find_txt_files('.')
    
    if not txt_files:
        print("未找到任何TXT文件")
        sys.exit(1)
    
    # 交互选择
    selected = select_file_interactive(txt_files)
    if selected is None:
        print("已取消")
        sys.exit(0)
    
    print()
    
    # 构造输出路径：去掉 txt_output/ 前缀，直接保持子目录结构
    rel_path = os.path.relpath(selected, '.')
    # 去掉顶层的输入目录前缀（如 txt_output/）
    parts = rel_path.replace('\\', '/').split('/')
    if len(parts) > 1 and parts[0] in ('txt_output',):
        rel_path = os.sep.join(parts[1:])
    csv_name = os.path.splitext(rel_path)[0] + '.csv'
    csv_path = os.path.join(output_dir, csv_name)
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    print("正在转换: %s" % selected)
    print("输出文件: %s" % csv_path)
    
    # 解析题库
    questions, stats = parse_qbank_full(selected)
    
    # 保存CSV
    save_to_csv_full(questions, csv_path)
    
    # 打印报告
    print_report(questions, stats, selected, csv_path)