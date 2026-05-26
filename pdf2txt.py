#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将PDF文件转换为TXT文本（去除页码）
用法：
  python pdf2txt.py                          # 默认输出到 txt_output/
  python pdf2txt.py --output my_txts          # 指定输出目录
"""

import os
import sys
import re
import argparse
from pathlib import Path
from pypdf import PdfReader

def pdf_to_text(pdf_path, txt_path):
    """提取PDF中的文本并保存到TXT文件（去除页码）"""
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        all_lines = []
        skipped_page_nums = 0
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    stripped = line.strip()
                    if re.match(r'^\d+$', stripped):
                        skipped_page_nums += 1
                        continue
                    if stripped:
                        all_lines.append(line)
        
        full_text = '\n'.join(all_lines)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(txt_path), exist_ok=True)
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # 输出格式：处理 xxx.pdf，输出 xxxx 行 txt，忽略 xxx 页码
        print("处理 %s，输出 %d 行 txt，忽略 %d 页码" % (
            pdf_path, len(all_lines), skipped_page_nums))
        
        return True
    
    except Exception as e:
        print("处理 %s 失败: %s" % (pdf_path, e))
        return False


def find_pdf_files(root_dir):
    """递归查找所有PDF文件"""
    pdf_files = []
    root = Path(root_dir)
    for f in sorted(root.rglob('*.pdf')):
        pdf_files.append(str(f))
    return pdf_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='将PDF转换为TXT文本（去除页码）')
    parser.add_argument('--output', '-o', default='txt_output',
                        help='输出目录（默认: txt_output）')
    args = parser.parse_args()
    
    output_dir = args.output
    
    # 查找当前目录及子目录下所有PDF文件
    pdf_files = find_pdf_files('.')
    
    if not pdf_files:
        print("未找到PDF文件")
        sys.exit(1)
    
    print("找到 %d 个PDF文件:\n" % len(pdf_files))
    for f in pdf_files:
        print("  - %s" % f)
    print()
    
    success = 0
    for pdf_path in pdf_files:
        # 构造输出路径：保持子目录结构
        # 例如 ./业余无线电台/总题库.pdf -> txt_output/业余无线电台/总题库.txt
        rel_path = os.path.relpath(pdf_path, '.')
        txt_name = os.path.splitext(rel_path)[0] + '.txt'
        txt_path = os.path.join(output_dir, txt_name)
        
        if pdf_to_text(pdf_path, txt_path):
            success += 1
    
    print("\n完成: %d/%d 个PDF成功转换为TXT" % (success, len(pdf_files)))
    print("输出目录: %s" % output_dir)