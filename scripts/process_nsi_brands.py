import os
import json
import re
import glob

# 环境变量：兼容 GitHub Actions 和本地测试
WORKSPACE = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NSI_REPO_PATH = os.path.join(WORKSPACE, 'nsi_repo')
BRANDS_OUT_DIR = os.path.join(WORKSPACE, 'veherego_assets', 'brands')

# NSI 类目 -> VehereGo 业务线映射 (一级分类, 二级分类, 默认主题色)
CATEGORY_MAP = {
    'amenity/cafe': ('drink', 'coffee', '#0D9488'),
    'amenity/bubble_tea': ('drink', 'milk_tea', '#0D9488'),
    'amenity/fast_food': ('food', 'fast_food', '#F97316'),
    'amenity/restaurant': ('food', 'restaurant', '#F97316'),
    'amenity/food_court': ('food', 'restaurant', '#F97316'),
    'shop/convenience': ('supermarket', 'convenience', '#16A34A'),
    'shop/supermarket': ('supermarket', 'hypermarket', '#16A34A'),
    'shop/bakery': ('food', 'bakery', '#F97316'),
    'shop/pastry': ('food', 'bakery', '#F97316'),
    'shop/beverages': ('drink', 'fruit_tea', '#0D9488'),
    'shop/coffee': ('drink', 'coffee', '#0D9488'),
    'amenity/post_office': ('express', 'station', '#3B82F6'),
    'amenity/post_depot': ('express', 'courier', '#3B82F6'),
    'amenity/parcel_locker': ('express', 'locker', '#3B82F6'),
    'office/logistics': ('express', 'courier', '#3B82F6'),
    'office/courier': ('express', 'courier', '#3B82F6'),
}

# 语言白名单（仅提取目标国家常用语言，防止字典膨胀）
LANG_WHITELIST = {
    'cn': ['zh', 'zh-Hans', 'zh-Hant', 'en'],
    'tw': ['zh', 'zh-Hant', 'en'],
    'hk': ['zh', 'zh-Hant', 'en'],
    'jp': ['ja', 'en'],
    'kr': ['ko', 'en'],
    'us': ['en', 'es'],
    'gb': ['en'],
    '001': ['en'] # 全球兜底品牌默认只提取英文
}

def get_allowed_langs(country):
    """获取该国家的白名单语言，如果不在配置中，则默认使用自身代码及英文"""
    return LANG_WHITELIST.get(country, [country, 'en'])

def generate_slug(display_name, wikidata):
    """生成合规的 slug (小写英数字符 + wikidata)"""
    slug = re.sub(r'[^a-zA-Z0-9]', '', display_name.lower())
    if wikidata:
        slug += f"_{wikidata.lower()}"
    return slug

def process():
    os.makedirs(BRANDS_OUT_DIR, exist_ok=True)

    # 读取 localbrand 下的 logo_manifest.json
    logo_manifest = {}
    logo_manifest_path = os.path.join(NSI_REPO_PATH, 'localbrand', 'logo_manifest.json')
    if os.path.exists(logo_manifest_path):
        try:
            with open(logo_manifest_path, 'r', encoding='utf-8') as f:
                logo_manifest = json.load(f)
        except Exception as e:
            print(f"Failed to read logo_manifest.json: {e}")

    # 嵌套字典：data[country_code][category_slug][brand_slug] = brand_json_object
    brand_data = {}

    # 优先扫描 localbrand 文件夹，若不存在则回退至标准的 brands 文件夹
    json_files = glob.glob(os.path.join(NSI_REPO_PATH, 'localbrand', '**', '*.json'), recursive=True)
    if not json_files:
        json_files = glob.glob(os.path.join(NSI_REPO_PATH, 'brands', '**', '*.json'), recursive=True)

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")
            continue

        props = data.get('properties', {})
        nsi_path = props.get('path', '')

        # 将 NSI 路径转为类别前缀 (例如 "brands/amenity/cafe" -> "amenity/cafe")
        nsi_type = nsi_path.replace('brands/', '').replace('localbrand/', '')

        # 判断是否在我们关心的业态中
        mapped = None
        for key, val in CATEGORY_MAP.items():
            if nsi_type.startswith(key):
                mapped = val
                break

        # 丢弃非生活/票务/快递领域的冗余数据（如银行、政府、修车厂）
        if not mapped:
            continue

        cat, sub_cat, default_color = mapped
        items = data.get('items', [])

        for item in items:
            display_name = item.get('displayName', '')
            if not display_name:
                continue

            tags = item.get('tags', {})
            # 提取它所属的国家列表，默认 001（全球）
            location_set = item.get('locationSet', {}).get('include', ['001'])
            wikidata = tags.get('brand:wikidata') or tags.get('name:wikidata') or ''

            slug = generate_slug(display_name, wikidata)

            item_id = item.get('id', '')
            icon_url = None
            if item_id in logo_manifest:
                icon_url = logo_manifest[item_id].get('github_logo_url')

            # 分发到对应的国家文件中
            for country in location_set:
                country = country.lower()
                allowed_langs = get_allowed_langs(country)

                aliases = set()
                keywords = set()

                # 默认把通用名字加进去
                if 'name' in tags: aliases.add(tags['name'])
                if 'brand' in tags: aliases.add(tags['brand'])

                # 基于白名单过滤多国语言
                for k, v in tags.items():
                    if k.startswith('name:') or k.startswith('brand:'):
                        lang_part = k.split(':', 1)[1]
                        if lang_part in allowed_langs:
                            aliases.add(v)

                keywords = list(aliases)
                aliases = list(aliases)

                # 提取网站域名，用于后续头像回源 (Unavatar)
                website = tags.get('website', '')
                domain = None
                if website:
                    match = re.search(r'https?://(?:www\.)?([^/]+)', website)
                    if match:
                        domain = match.group(1)

                brand_item = {
                    "slug": slug,
                    "title": display_name,
                    "short_name": display_name[:10],
                    "badge_text": display_name[:1].upper() if display_name else "",
                    "category": cat,
                    "sub_category": sub_cat,
                    "color": default_color,
                    "aliases": aliases,
                    "keywords": keywords,
                    "package_hints": [], # 预留给人工或其他 CI 后续补充
                    "icon_url": icon_url, # 将提取到的 logo 地址赋给 icon_url
                    "domain": domain,
                    "forces_pickup_scene": True,
                    "custom_metadata": {
                        "nsi_id": item.get('id', ''),
                        "wikidata": wikidata
                    }
                }

                # 初始化嵌套字典
                if country not in brand_data:
                    brand_data[country] = {}
                if cat not in brand_data[country]:
                    brand_data[country][cat] = {}

                brand_data[country][cat][slug] = brand_item

    # 按 国家 -> 业态 输出符合模板契约的 JSON 文件
    for country, cats in brand_data.items():
        country_dir = os.path.join(BRANDS_OUT_DIR, country)
        os.makedirs(country_dir, exist_ok=True)

        for cat, brands_dict in cats.items():
            out_file = os.path.join(country_dir, f"{cat}.json")

            out_json = {
                "type": "brand",
                "version": 6,
                "source": "nsi_auto_generated",
                "total_brands": len(brands_dict),
                "brand_aliases": brands_dict
            }

            # 使用缩进以确保 Git diff 可读性
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(out_json, f, ensure_ascii=False, indent=2)

        # 为每个国家生成一个总览的 index.json
        index_file = os.path.join(country_dir, "index.json")
        index_data = {
            "type": "brand_index",
            "country": country,
            "total_categories": len(cats),
            "manifest_files": []
        }

        # 收集该国家下的所有 manifest 链接（相对路径）
        for cat in cats.keys():
            index_data["manifest_files"].append(f"{cat}.json")

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"Data processing completed! Generated {len(brand_data)} country folders.")

if __name__ == "__main__":
    process()
