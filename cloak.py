import pandas as pd
import re
from collections import defaultdict


# 解析properties文件内容
def parse_cloak_properties(content):
    lines = content.split('\n')
    data = {}

    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            data[key.strip()] = value.strip()

    return data


# 提取数据库信息
def extract_database_info(data):
    db_list = []

    # 提取主数据库信息
    for key in data:
        url_match = re.match(r'mariadb\.tds\.db\.URL\.([A-Z.]+)', key)
        if url_match:
            region = url_match.group(1)
            url_key = f'mariadb.tds.db.URL.{region}'
            user_key = f'mariadb.tds.user.{region}'
            pass_key = f'mariadb.tds.pass.{region}'

            db_entry = {
                'Database Type': 'TDS Main',
                'Region': region,
                'URL': data.get(url_key, ''),
                'Username': data.get(user_key, ''),
                'Password': data.get(pass_key, '')
            }
            db_list.append(db_entry)

    # 提取从数据库信息
    for key in data:
        slave_url_match = re.match(r'mariadb\.tds\.slave\.db\.URL\.([A-Z]+)', key)
        if slave_url_match:
            region = slave_url_match.group(1)
            url_key = f'mariadb.tds.slave.db.URL.{region}'
            user_key = f'mariadb.tds.slave.user.{region}'
            pass_key = f'mariadb.tds.slave.pass.{region}'

            db_entry = {
                'Database Type': 'TDS Slave',
                'Region': region,
                'URL': data.get(url_key, ''),
                'Username': data.get(user_key, ''),
                'Password': data.get(pass_key, '')
            }
            db_list.append(db_entry)

    # 提取其他数据库信息
    if 'dbURL' in data:
        db_list.append({
            'Database Type': 'Main Database',
            'Region': 'SPARKDB',
            'URL': data.get('dbURL', ''),
            'Username': data.get('dbUser', ''),
            'Password': data.get('dbpassword', '')
        })

    if 'mariadb.ideal.slave.db.URL.SG' in data:
        db_list.append({
            'Database Type': 'IDEAL Slave',
            'Region': 'SG',
            'URL': data.get('mariadb.ideal.slave.db.URL.SG', ''),
            'Username': data.get('mariadb.ideal.slave.user.SG', ''),
            'Password': data.get('mariadb.ideal.slave.pass.SG', '')
        })

    return db_list


# 生成Excel文件
def generate_excel(db_info, filename='cloak_database_info.xlsx'):
    df = pd.DataFrame(db_info)
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"Excel文件已生成: {filename}")
    return filename


# 主程序
def main():
    # 读取cloak.properties文件
    with open('files/cloak.properties', 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析文件内容
    parsed_data = parse_cloak_properties(content)

    # 提取数据库信息
    db_info = extract_database_info(parsed_data)

    # 生成Excel文件
    generate_excel(db_info)


if __name__ == "__main__":
    main()
