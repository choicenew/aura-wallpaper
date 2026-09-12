#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多源翻译支持语言纯 Diff 差异比对、合并与治理引擎
1. 【纯集合差异比对 (Set Difference)】：比对新老数据交集、新增集 (added) 与缺失集 (removed)，计算重合相似度。
2. 【突变防劣化保护】：若新抓取数据与老版本重合率极低或遭遇空截断，保留历史版本并输出差异警报。
3. 【清晰 Diff 报告】：输出详尽的交集量、增量列表、删改列表及重合度百分比，无任何硬编码假设。
"""
import os
import sys
import csv
import json
from collections import OrderedDict
from datetime import datetime

LANG_CODE_TO_VALUE = {
    "auto": "自动",
    "all": "自动",
    "zh": "中文",
    "zh-cn": "中文",
    "zh-CN": "中文",
    "zh-chs": "中文",
    "zh-CHS": "中文",
    "zh-hans": "中文",
    "zh-Hans": "中文",
    "zh-tw": "中文(台湾)",
    "zh-TW": "中文(台湾)",
    "zh-hant": "中文(台湾)",
    "zh-Hant": "中文(台湾)",
    "zh-hk": "中文(香港)",
    "zh-HK": "中文(香港)",
    "yue": "中文(粤语)",
    "wyw": "中文(文言文)",
    "lzh": "中文(文言文)",
    "en": "英语",
    "ja": "日语",
    "jp": "日语",
    "ko": "韩语",
    "kor": "韩语",
    "fr": "法语",
    "fra": "法语",
    "de": "德语",
    "deu": "德语",
    "es": "西班牙语",
    "spa": "西班牙语",
    "ru": "俄语",
    "rus": "俄语",
    "it": "意大利语",
    "ita": "意大利语",
    "pt": "葡萄牙语",
    "por": "葡萄牙语",
    "th": "泰语",
    "tha": "泰语",
    "vi": "越南语",
    "vie": "越南语",
    "id": "印尼语",
    "ind": "印尼语",
    "ar": "阿拉伯语",
    "ara": "阿拉伯语",
    "hi": "印地语",
    "hin": "印地语",
    "tr": "土耳其语",
    "tur": "土耳其语",
    "pl": "波兰语",
    "pol": "波兰语",
    "nl": "荷兰语",
    "nld": "荷兰语",
    "sv": "瑞典语",
    "swe": "瑞典语",
}

def try_import_translators():
    try:
        import translators as ts
        return ts
    except ImportError:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        local_ts = os.path.join(root_dir, "translators")
        if os.path.exists(local_ts):
            sys.path.insert(0, local_ts)
            try:
                import translators as ts
                return ts
            except Exception:
                pass
        try:
            import subprocess
            print("正在安装 UlionTse/translators 依赖...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "translators"], timeout=60)
            import translators as ts
            return ts
        except Exception as e:
            print(f"提示: 未能在线加载 translators ({e})，将使用历史归档源与 CSV 进行比对合并。")
            return None

def compute_diff(old_list, new_list):
    """计算纯集合差异指标"""
    old_set = set(old_list)
    new_set = set(new_list)
    
    intersection = old_set & new_set
    added = new_set - old_set
    removed = old_set - new_set
    
    similarity = (len(intersection) / len(old_set) * 100.0) if len(old_set) > 0 else (100.0 if len(new_set) > 0 else 0.0)
    
    return {
        "old_count": len(old_set),
        "new_count": len(new_set),
        "common_count": len(intersection),
        "added": sorted(list(added)),
        "removed": sorted(list(removed)),
        "similarity": round(similarity, 1)
    }

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    csv_file = os.path.join(root_dir, "supported_language_map.csv")
    raw_sources_dir = os.path.join(root_dir, "raw_sources")
    os.makedirs(raw_sources_dir, exist_ok=True)
    
    value_order = []
    value_map = {}
    code_to_value = dict(LANG_CODE_TO_VALUE)
    
    # 记录每个源的差异分析结果
    diff_report_entries = []

    # 1. 载入本地 CSV 基础底座
    if os.path.exists(csv_file):
        print(f"📖 [Step 1] 载入本地 CSV 基准映射: {csv_file}")
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                val = row.get("Value", "").strip()
                if not val:
                    continue
                if val not in value_map:
                    value_map[val] = {"Value": val}
                    value_order.append(val)
                for provider, code in row.items():
                    clean_provider = provider.strip() if provider else ""
                    clean_code = code.strip() if code else ""
                    if clean_provider and clean_provider != "Value" and clean_code:
                        value_map[val][clean_provider] = clean_code
                        code_to_value[clean_code.lower()] = val
                        code_to_value[clean_code] = val
        print(f"✓ CSV 载入完成，基准包含 {len(value_map)} 种语言。")

    # 2. 动态抓取 + 纯 Difference 差异比对分析
    ts = try_import_translators()
    if ts is not None:
        pool = getattr(ts, "translators_pool", [])
        print(f"🌐 [Step 2] 动态抓取与 Difference 差异分析 ({len(pool)} 个服务商)...")
        
        for provider in pool:
            provider_file = os.path.join(raw_sources_dir, f"{provider}.json")
            
            old_list = []
            if os.path.exists(provider_file):
                try:
                    with open(provider_file, "r", encoding="utf-8") as f:
                        old_list = json.load(f)
                except Exception:
                    old_list = []

            try:
                lang_dict = ts.get_languages(translator=provider)
                fetched_list = []
                if isinstance(lang_dict, dict):
                    fetched_list = [str(k).strip() for k in lang_dict.keys() if str(k).strip()]
                elif isinstance(lang_dict, (list, tuple, set)):
                    fetched_list = [str(k).strip() for k in lang_dict if str(k).strip()]

                diff = compute_diff(old_list, fetched_list)

                # 判定决策：
                # A. 抓取为空且历史有数据 -> 判定为接口异常，保留历史
                if diff["new_count"] == 0 and diff["old_count"] > 0:
                    status = "🛡️ 抓取为空(保留历史)"
                    final_list = old_list
                # B. 历史有较多数据但重合相似度极低 (< 40%) -> 判定为接口反爬或脏数据，保留历史
                elif diff["old_count"] > 10 and diff["similarity"] < 40.0:
                    status = f"⚠️ 差异突变(相似度 {diff['similarity']}% < 40%，触发保护)"
                    final_list = old_list
                # C. 正常演进（大部分一致，包含新增或部分版本代号修正）
                else:
                    if diff["added"] and diff["removed"]:
                        status = f"🔄 版本变更 (+{len(diff['added'])}, -{len(diff['removed'])})"
                    elif diff["added"]:
                        status = f"✨ 新增扩展 (+{len(diff['added'])})"
                    elif diff["removed"]:
                        status = f"✂️ 上游精简 (-{len(diff['removed'])})"
                    else:
                        status = "✓ 完全一致 (100% 重合)"
                    final_list = fetched_list

                    # 仅在非空且正常时写入更新
                    if final_list:
                        with open(provider_file, "w", encoding="utf-8") as f:
                            json.dump(sorted(list(set(final_list))), f, ensure_ascii=False, indent=2)

                diff["status"] = status
                diff["provider"] = provider
                diff_report_entries.append(diff)
                print(f"  [{provider}] {status} | 老版本: {diff['old_count']}, 新版本: {diff['new_count']}, 重合率: {diff['similarity']}%")
            except Exception as e:
                diff = compute_diff(old_list, [])
                diff["status"] = f"✕ 抓取异常 ({e})"
                diff["provider"] = provider
                diff_report_entries.append(diff)
                print(f"  [{provider}] 抓取异常，沿用历史数据: {e}")

    # 3. 汇总合并 raw_sources/ 目录下的所有文件
    print(f"🔄 [Step 3] 汇总合并所有 Provider 数据...")
    for file_name in os.listdir(raw_sources_dir):
        if file_name.endswith(".json"):
            provider = file_name[:-5]
            file_path = os.path.join(raw_sources_dir, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    codes = json.load(f)
                for lang_code in codes:
                    code_str = str(lang_code).strip()
                    if not code_str:
                        continue
                    val_name = code_to_value.get(code_str.lower(), code_to_value.get(code_str, code_str))
                    if val_name not in value_map:
                        value_map[val_name] = {"Value": val_name}
                        value_order.append(val_name)
                    value_map[val_name][provider] = code_str
            except Exception as e:
                print(f"  读取持久化缓存 {file_name} 警告: {e}")

    # 4. 生成标准 JSON 文件并输出
    print(f"💾 [Step 4] 导出标准 supported_languages.json...")
    def sort_key(val_name):
        if val_name in value_order:
            return (0, value_order.index(val_name))
        return (1, val_name)

    output_list = []
    for val_name in sorted(value_map.keys(), key=sort_key):
        item = value_map[val_name]
        ordered_item = OrderedDict()
        ordered_item["Value"] = item["Value"]
        for k in sorted(item.keys()):
            if k != "Value":
                ordered_item[k] = item[k]
        output_list.append(ordered_item)

    # 写入根目录
    root_json = os.path.join(root_dir, "supported_languages.json")
    with open(root_json, "w", encoding="utf-8") as f:
        json.dump(output_list, f, ensure_ascii=False, indent=4)
    print(f"✓ 产物已生成: {root_json} (合并后语言总数: {len(output_list)})")

    # 5. 生成专业 Markdown Difference 详细对比报告并同步存入 raw_sources 文件夹
    report_content = []
    report_content.append("# 🌐 多源翻译语言 Difference 差异比对报告\n")
    report_content.append(f"- **比对时间**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
    report_content.append(f"- **合并总语言条目**: `{len(output_list)}` 种\n")
    report_content.append("### 各翻译源 Difference 明细表\n")
    report_content.append("| 服务商 (Provider) | 上周数 | 本周数 | 重合交集 | 相似度 | 状态判定 | 新增代码 (Diff Added) | 移除/废弃代码 (Diff Removed) |")
    report_content.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for d in sorted(diff_report_entries, key=lambda x: x["provider"]):
        added_preview = ", ".join([f"`+{c}`" for c in d["added"][:6]]) if d["added"] else "-"
        if len(d["added"]) > 6:
            added_preview += f" 等 {len(d['added'])} 个"
        removed_preview = ", ".join([f"`-{c}`" for c in d["removed"][:6]]) if d["removed"] else "-"
        if len(d["removed"]) > 6:
            removed_preview += f" 等 {len(d['removed'])} 个"
        report_content.append(f"| `{d['provider']}` | {d['old_count']} | {d['new_count']} | {d['common_count']} | `{d['similarity']}%` | {d['status']} | {added_preview} | {removed_preview} |")
    
    full_report_text = "\n".join(report_content) + "\n"

    # 存入 raw_sources/ 目录供 GitHub 仓库持久化归档与文件夹预览
    report_file = os.path.join(raw_sources_dir, "sync_diff_report.md")
    readme_file = os.path.join(raw_sources_dir, "README.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(full_report_text)
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(full_report_text)
    
    print(f"📋 Difference 差异分析报告已同步写入: {report_file} 和 {readme_file}")

if __name__ == "__main__":
    main()
