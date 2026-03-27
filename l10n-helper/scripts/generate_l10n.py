#!/usr/bin/env python3
"""
L10n.generated.swift 代码生成器

从 String Catalog (.xcstrings) 文件自动生成类型安全的 L10n.generated.swift

使用方法：
    python3 generate_l10n.py [--input-dir DIR] [--output FILE]
    python3 generate_l10n.py --verify    # 验证是否同步
    python3 generate_l10n.py --dry-run   # 预览生成内容

参数：
    --input-dir     包含 .xcstrings 文件的目录 (默认: macos/SwiftTrans/SwiftTrans/Resources)
    --output        输出文件路径 (默认: macos/SwiftTrans/SwiftTrans/Resources/L10n.generated.swift)
    --dry-run       仅显示将生成的内容，不写入文件
    --verify        验证现有文件是否与 String Catalog 同步
"""

import json
import re
import argparse
import hashlib
from pathlib import Path
from datetime import datetime


def parse_xcstrings(file_path: Path) -> dict:
    """解析 .xcstrings 文件，返回 key 列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    keys = list(data.get('strings', {}).keys())
    return {
        'table': file_path.stem,
        'keys': sorted(keys)
    }


def key_to_swift_path(key: str) -> list[str]:
    """
    将 key 转换为 Swift 路径
    例如：'settings.close.prompt' -> ['Settings', 'Close', 'prompt']
    """
    parts = key.split('.')
    result = []
    for i, part in enumerate(parts):
        # 第一个部分和中间部分使用 PascalCase (枚举名)
        # 最后一个部分使用 camelCase (属性名)
        if i < len(parts) - 1:
            # 枚举名：转换为 PascalCase
            result.append(to_pascal_case(part))
        else:
            # 属性名：转换为 camelCase
            result.append(to_camel_case(part))
    return result


def to_pascal_case(s: str) -> str:
    """转换为 PascalCase"""
    # 处理下划线分隔
    parts = s.replace('-', '_').split('_')
    return ''.join(word.capitalize() for word in parts)


def to_camel_case(s: str) -> str:
    """转换为 camelCase"""
    parts = s.replace('-', '_').split('_')
    if not parts:
        return s
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


def detect_format_specifiers(key: str, strings_data: dict) -> list[str]:
    """
    检测字符串中的格式化占位符
    返回占位符类型列表，如 ['String', 'Int']
    """
    if key not in strings_data:
        return []
    
    string_data = strings_data[key]
    localizations = string_data.get('localizations', {})
    
    # 使用英文版本作为参考
    en_data = localizations.get('en', {})
    string_unit = en_data.get('stringUnit', {})
    value = string_unit.get('value', '')
    
    if not value:
        return []
    
    # 匹配格式化占位符
    specifiers = []
    pattern = r'%(?:(\d+)\$)?([lh]?[diouxXeEfFgGaAcspn@])'
    matches = re.findall(pattern, value)
    
    for position, specifier in matches:
        if specifier in ('d', 'i', 'o', 'u', 'x', 'X'):
            specifiers.append('Int')
        elif specifier in ('lld', 'ld'):
            specifiers.append('Int')
        elif specifier in ('e', 'E', 'f', 'F', 'g', 'G', 'a', 'A'):
            specifiers.append('Double')
        elif specifier == '@':
            specifiers.append('String')
        elif specifier == 's':
            specifiers.append('String')
        else:
            specifiers.append('String')
    
    return specifiers


class EnumNode:
    """表示一个枚举节点"""
    def __init__(self, name: str, table: str = None):
        self.name = name
        self.table = table
        self.children: dict[str, 'EnumNode'] = {}
        self.properties: list[tuple[str, str, str, list[str]]] = []  # [(prop_name, key, table, format_args)]
    
    def get_or_create_child(self, name: str, table: str = None) -> 'EnumNode':
        if name not in self.children:
            self.children[name] = EnumNode(name, table)
        return self.children[name]
    
    def add_property(self, prop_name: str, key: str, table: str, format_args: list[str] = None):
        self.properties.append((prop_name, key, table, format_args or []))


def build_enum_tree(catalogs: list[dict], all_strings_data: dict) -> EnumNode:
    """构建枚举树结构"""
    root = EnumNode("L10n")
    
    for catalog in catalogs:
        table = catalog['table']
        strings_data = all_strings_data.get(table, {})
        
        for key in catalog['keys']:
            path = key_to_swift_path(key)
            format_args = detect_format_specifiers(key, strings_data)
            
            if len(path) == 1:
                # 直接在根节点添加属性
                root.add_property(path[0], key, table, format_args)
            else:
                # 创建嵌套枚举
                current = root
                for i, enum_name in enumerate(path[:-1]):
                    current = current.get_or_create_child(enum_name, table if i == 0 else None)
                current.add_property(path[-1], key, table, format_args)
    
    return root


def generate_property(prop_name: str, key: str, table: str, format_args: list[str], indent: int) -> str:
    """生成属性代码"""
    spaces = "  " * indent
    
    # 避免 Swift 关键字冲突
    safe_name = prop_name
    if prop_name in ('default', 'class', 'struct', 'enum', 'protocol', 'extension', 'import', 'return', 'self', 'true', 'false'):
        safe_name = f'`{prop_name}`'
    
    if format_args:
        # 生成带参数的方法
        params = ', '.join([f'_ arg{i}: {t}' for i, t in enumerate(format_args)])
        args = ', '.join([f'arg{i}' for i in range(len(format_args))])
        return f'''{spaces}/// {key}
{spaces}static func {safe_name}({params}) -> String {{
{spaces}  return L10n.format("{key}", table: "{table}", args: {args})
{spaces}}}'''
    else:
        # 生成简单属性
        return f'''{spaces}/// {key}
{spaces}static var {safe_name}: String {{ LocalizationManager.shared.localizedString("{key}", table: "{table}") }}'''


def generate_enum(node: EnumNode, indent: int = 0, is_first_child: bool = False) -> str:
    """递归生成枚举代码"""
    spaces = "  " * indent
    lines = []
    
    # 添加 MARK 注释（仅对一级子枚举）
    if indent == 1 and node.table:
        lines.append(f"")
        lines.append(f"{spaces}// MARK: - {node.name} ({node.table}.xcstrings)")
        lines.append(f"")
    
    if indent == 0:
        lines.append(f"enum {node.name} {{")
    else:
        lines.append(f"{spaces}enum {node.name} {{")
    
    # 生成属性
    for prop_name, key, table, format_args in sorted(node.properties, key=lambda x: x[0]):
        lines.append(generate_property(prop_name, key, table, format_args, indent + 1))
    
    # 生成子枚举
    for i, child_name in enumerate(sorted(node.children.keys())):
        if node.properties:
            lines.append("")  # 属性和子枚举之间添加空行
        child = node.children[child_name]
        lines.append(generate_enum(child, indent + 1, is_first_child=(i == 0)))
    
    lines.append(f"{spaces}}}")
    
    return '\n'.join(lines)


def generate_l10n_swift(catalogs: list[dict], all_strings_data: dict) -> str:
    """生成完整的 L10n.generated.swift 文件内容"""
    tree = build_enum_tree(catalogs, all_strings_data)
    
    # 统计信息
    total_keys = sum(len(c['keys']) for c in catalogs)
    
    header = f'''// L10n.generated.swift
// 自动生成，请勿手动修改
// 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
// String Catalogs: {', '.join(sorted(c['table'] for c in catalogs))}
// 总计 {total_keys} 个本地化 key
//
// 使用方法：
//   python3 Scripts/generate_l10n.py           # 重新生成
//   python3 Scripts/generate_l10n.py --verify  # 验证同步状态
//
// 自定义扩展请添加到 L10n+Extensions.swift

import Foundation

'''
    
    enum_code = generate_enum(tree)
    
    return header + enum_code + '\n'


def compute_content_hash(catalogs: list[dict]) -> str:
    """计算 String Catalog 内容的哈希值"""
    content = json.dumps(catalogs, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


def verify_sync(output_file: Path, catalogs: list[dict], all_strings_data: dict) -> bool:
    """验证生成的文件是否与 String Catalog 同步"""
    if not output_file.exists():
        print(f"❌ {output_file.name} 不存在")
        print(f"   运行 'python3 Scripts/generate_l10n.py' 生成文件")
        return False
    
    # 生成新内容
    new_content = generate_l10n_swift(catalogs, all_strings_data)
    
    # 读取现有文件（去除时间戳行比较）
    with open(output_file, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    # 移除时间戳行进行比较
    def remove_timestamp(content: str) -> str:
        lines = content.split('\n')
        return '\n'.join(line for line in lines if not line.startswith('// 生成时间：'))
    
    existing_normalized = remove_timestamp(existing_content)
    new_normalized = remove_timestamp(new_content)
    
    if existing_normalized == new_normalized:
        print(f"✅ {output_file.name} 已与 String Catalog 同步")
        return True
    else:
        print(f"❌ {output_file.name} 与 String Catalog 不同步")
        print(f"   运行 'python3 Scripts/generate_l10n.py' 更新文件")
        return False


def main():
    parser = argparse.ArgumentParser(description='Generate L10n.generated.swift from String Catalogs')
    parser.add_argument('--input-dir', type=str,
                        default='.',
                        help='Directory containing .xcstrings files (default: current directory)')
    parser.add_argument('--output', type=str,
                        default=None,
                        help='Output file path (default: L10n.generated.swift in --input-dir)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print output instead of writing to file')
    parser.add_argument('--verify', action='store_true',
                        help='Verify if generated file is in sync with String Catalogs')
    
    args = parser.parse_args()

    # Resolve paths relative to current working directory
    project_root = Path.cwd()
    input_dir = (project_root / args.input_dir).resolve()
    output_file = (project_root / args.output).resolve() if args.output else input_dir / "L10n.generated.swift"
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    # 收集所有 .xcstrings 文件
    xcstrings_files = list(input_dir.glob('*.xcstrings'))
    if not xcstrings_files:
        print(f"Error: No .xcstrings files found in {input_dir}")
        return 1
    
    print(f"Found {len(xcstrings_files)} String Catalog files:")
    for f in xcstrings_files:
        print(f"  - {f.name}")
    
    # 解析所有文件
    catalogs = []
    all_strings_data = {}
    
    for file_path in xcstrings_files:
        catalog = parse_xcstrings(file_path)
        catalogs.append(catalog)
        
        # 读取完整数据用于检测格式化占位符
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_strings_data[catalog['table']] = data.get('strings', {})
        
        print(f"  {catalog['table']}: {len(catalog['keys'])} keys")
    
    # 验证模式
    if args.verify:
        print()
        return 0 if verify_sync(output_file, catalogs, all_strings_data) else 1
    
    # 生成代码
    content = generate_l10n_swift(catalogs, all_strings_data)
    
    if args.dry_run:
        print("\n--- Generated L10n.generated.swift ---")
        print(content)
        print("--- End ---")
    else:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Generated: {output_file}")
        print(f"   Total keys: {sum(len(c['keys']) for c in catalogs)}")
    
    return 0


if __name__ == '__main__':
    exit(main())
