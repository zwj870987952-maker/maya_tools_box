# -*- coding: utf-8 -*-
"""
字符串与格式化处理工具：提供自然排序、节点命名安全化与 Markdown 表格生成。
"""
from __future__ import absolute_import, division, print_function

import re


def natural_sort_key(s):
    """
    针对包含数字的字符串提供人类自然排序（Natural Sorting）。
    例如：['Part_1', 'Part_2', 'Part_10', 'Part_20'] 而不是字母顺序的 ['Part_1', 'Part_10', 'Part_2', 'Part_20']。
    """
    if not isinstance(s, (str, bytes)):
        s = str(s)
    # 将文本和数字切分，数字转换为整数比较
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]


def sanitize_node_name(name):
    """
    将输入字符串转换为合法的 Maya 节点短名（去除非法符号，替换空格为下划线）。
    """
    if not name:
        return "unnamed_node"
    # 替换空格和减号为下划线
    cleaned = re.sub(r"[ \-\.]+", "_", str(name).strip())
    # 移除非字母、数字和下划线的字符
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "", cleaned)
    # 确保不以数字开头
    if cleaned and cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned or "node"


def format_markdown_table(headers, rows):
    """
    将表头和行数据格式化为 Markdown 表格文本，便于大模型理解和生成质检报告。
    """
    if not headers:
        return ""
    col_widths = [len(str(h)) for h in headers]
    str_rows = []
    for row in rows:
        formatted_row = [str(item) for item in row]
        # 补全列数
        while len(formatted_row) < len(headers):
            formatted_row.append("")
        str_rows.append(formatted_row)
        for i, val in enumerate(formatted_row[:len(headers)]):
            col_widths[i] = max(col_widths[i], len(val))

    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * max(col_widths[i], 3) for i in range(len(headers))) + " |"
    data_lines = [
        "| " + " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers))) + " |"
        for row in str_rows
    ]
    return "\n".join([header_line, sep_line] + data_lines)
