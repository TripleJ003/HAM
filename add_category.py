#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为总题库CSV标注题目类别（A/B/C），输出到 csv_output/
"""

import csv
import os
import re

# ===== 1. 从A/B/C类TXT中提取每个类别的题目编号 =====
base = 'txt_output/业余无线电台操作技术能力验证题库（2025年版）'

category_questions = {}  # { 'A': set(), 'B': set(), 'C': set() }

for cat in ['A', 'B', 'C']:
    path = os.path.join(base, '%s类题库.txt' % cat)
    ids = set()
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'\[J\](\S+)', line.strip())
            if m:
                ids.add(m.group(1))
    category_questions[cat] = ids
    print("%s类题库: %d 题" % (cat, len(ids)))

# ===== 2. 读取总题库CSV，标注类别 =====
input_csv = '题库.csv'
output_csv = 'csv_output/总题库.csv'

rows = []
with open(input_csv, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader)
    # 确保有"类别"列
    if '类别' not in header:
        header.append('类别')
    rows.append(header)
    
    for row in reader:
        j_id = row[0]  # 第一列是J编号
        cats = []
        for cat in ['A', 'B', 'C']:
            if j_id in category_questions[cat]:
                cats.append(cat)
        # 如果没找到标记为'?'（可能不在A/B/C中，但出现在总题库中）
        label = ''.join(cats) if cats else '?'
        # 确保行长度匹配表头
        while len(row) < len(header):
            row.append('')
        row[-1] = label  # 最后一列是类别
        rows.append(row)

# ===== 3. 写入输出 =====
os.makedirs(os.path.dirname(output_csv), exist_ok=True)
with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print("\n输出: %s" % output_csv)
print("总行数: %d (含表头)" % len(rows))

# 统计各类别数量
from collections import Counter
counter = Counter()
for row in rows[1:]:
    counter[row[-1]] += 1
print("类别统计:")
for k, v in sorted(counter.items()):
    print("  %s: %d 题" % (k, v))