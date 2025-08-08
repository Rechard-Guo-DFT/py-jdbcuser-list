import os
import re
import codecs
import sys

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


def read_properties_file(directory, mapping):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".properties"):
                file_path = os.path.join(root, file)
                users = []
                urls = []
                with open(file_path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith("#"):
                            continue
                        # if match the pattern
                        if re.match(r'.*jdbc\.user=.*$', line):
                            users.append(line.strip())
                        elif re.match(r'.*jdbc\.URL=.*$', line):
                            urls.append(line.strip())

                if (len(users) > 0
                        and 'idealx-docker' not in file_path
                        and 'Deployment_Scripts' not in file_path
                        and 'build_property_replace' not in file_path
                ):
                    info = []
                    for i in range(len(users)):
                        info.append({"user": users[i], "url": urls[i]})
                    mapping[file_path] = info

            if os.path.isdir(file):
                read_properties_file(file, mapping)


def save_excel_file(mapping):
    import xlsxwriter
    workbook = xlsxwriter.Workbook('jdbc-list3.xlsx')
    worksheet = workbook.add_worksheet()

    # 定义格式
    border_format = workbook.add_format({'border': 1})
    # grey
    space_format = workbook.add_format({'border': 1, 'bg_color': '#DCDCDC'})
    header_format = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#DCDCDC'})

    # 写入excel标题
    worksheet.write_row(0, 0, ["File", "jdbc.user", "jdbc.URL"], header_format)

    row = 1
    file_count = 0
    for file, jdbc_info in mapping.items():

        length = len(jdbc_info)

        # 为不同文件添加间隔行（除了第一个文件）
        if file_count > 0:
            worksheet.write_row(row, 0, ["", "", ""], space_format)
            row += 1

        # 写入文件名
        if length > 1:
            worksheet.merge_range(row, 0, row + length - 1, 0, file, border_format)
        elif length == 1:
            worksheet.write(row, 0, file, border_format)

        # 写入jdbc信息
        for i in range(length):
            user = jdbc_info[i]['user']
            url = jdbc_info[i]['url']
            worksheet.write_row(row, 1, [user, url], border_format)
            row += 1
        file_count += 1

    workbook.close()


def main():
    directory = "D:/dbs-code/DBS_git/forkcode2/DBS_CB_SRC/DBS_OSS_SRC"
    mapping = {}
    read_properties_file(directory, mapping)
    save_excel_file(mapping)


# Main entry point
if __name__ == "__main__":
    main()
