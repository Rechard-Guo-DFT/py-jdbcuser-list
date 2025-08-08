import xml.etree.ElementTree as ET
import pandas as pd


def parse_xml_datasources(xml_file):
    """
    解析XML文件中的数据源配置，提取JNDI名称、用户名和URL
    正确处理XA数据源中的xa-datasource-property name="URL"
    """
    # 解析XML文件
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 存储结果的列表
    db_info = []

    # 查找所有数据源配置（datasource和xa-datasource）
    for elem in root.iter():
        # 处理普通数据源 (datasource)
        if 'datasource' in elem.tag and not 'xa-datasource' in elem.tag and 'jndi-name' in elem.attrib:
            jndi_name = elem.attrib.get('jndi-name', 'N/A')

            # 提取用户名
            username = 'N/A'
            for security in elem.iter():
                if 'security' in security.tag:
                    for user_elem in security.iter():
                        if 'user-name' in user_elem.tag and user_elem.text:
                            username = user_elem.text
                            break
                    if username != 'N/A':
                        break

            # 提取URL
            url = 'N/A'
            # 对于普通数据源，查找connection-url
            for url_elem in elem.iter():
                if 'connection-url' in url_elem.tag and url_elem.text:
                    url = url_elem.text.strip()
                    break

            db_info.append({
                'JNDI Name': jndi_name,
                'Username': username,
                'URL': url
            })

        # 处理XA数据源 (xa-datasource)
        elif 'xa-datasource' in elem.tag and 'jndi-name' in elem.attrib:
            jndi_name = elem.attrib.get('jndi-name', 'N/A')

            # 提取用户名
            username = 'N/A'
            for security in elem.iter():
                if 'security' in security.tag:
                    for user_elem in security.iter():
                        if 'user-name' in user_elem.tag and user_elem.text:
                            username = user_elem.text
                            break
                    if username != 'N/A':
                        break

            # 提取URL（XA数据源的URL在xa-datasource-property中）
            url = 'N/A'
            for prop in elem.iter():
                if 'xa-datasource-property' in prop.tag and prop.attrib.get('name') == 'URL':
                    # 获取property的文本内容
                    if prop.text:
                        url = prop.text.strip()
                    else:
                        # 如果直接文本为空，检查是否有子元素
                        for child in prop:
                            if child.text:
                                url = child.text.strip()
                                break
                    break

            db_info.append({
                'JNDI Name': jndi_name,
                'Username': username,
                'URL': url
            })

    return db_info


def find_specific_datasource(db_info, jndi_name):
    """
    在数据源列表中查找特定的JNDI名称
    """
    for db in db_info:
        if db['JNDI Name'] == jndi_name:
            return db
    return None


def generate_excel(db_info, filename='standalone_datasource_info.xlsx'):
    """
    将数据库信息生成Excel文件
    """
    df = pd.DataFrame(db_info)
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"Excel文件已生成: {filename}")
    return filename


def print_datasources(db_info):
    """
    打印数据源信息
    """
    print("数据库 JNDI 名称、用户名和 URL 列表:")
    print("-" * 120)
    print(f"{'JNDI Name':<50} {'Username':<15} {'URL':<50}")
    print("-" * 120)

    for info in db_info:
        print(f"{info['JNDI Name']:<50} {info['Username']:<15} {info['URL']:<50}")


def main():
    # 解析XML文件
    db_info = parse_xml_datasources('files/standalone-eap8.xml')

    if db_info:
        # 打印结果
        print_datasources(db_info)

        # 特别检查几个关键数据源
        critical_datasources = [
            'java:/jboss/jdbc/EPDatabase',
            'java:/jboss/jdbc/EPDatabaseDoc',
            'java:/jboss/jdbc/EPDatabaseID',
            'java:/jboss/jdbc/EPDatabaseIN'
        ]

        print(f"\n关键XA数据源检查:")
        print("-" * 120)
        for ds_name in critical_datasources:
            ds = find_specific_datasource(db_info, ds_name)
            if ds:
                print(f"✓ {ds_name:<50} {ds['Username']:<15} {ds['URL']:<50}")
            else:
                print(f"✗ {ds_name} 未找到")

        # 生成Excel文件
        generate_excel(db_info)

        print(f"\n总共找到 {len(db_info)} 个数据源配置。")
    else:
        print("未找到任何数据源配置。")


if __name__ == "__main__":
    main()
