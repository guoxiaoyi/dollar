import os
from playwright.sync_api import sync_playwright

class Jin10Loader:
    def __init__(self):
        pass
    def fetch_page(self, date):
        """
        传入日期字符串，例如 "2025-02-11"
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # 使用传入的日期动态构造 URL
            page.goto(f"https://rili.jin10.com/day/{date}", wait_until="networkidle")

            # 获取 calendar-main 中的内容
            content = page.query_selector('.index-page-content .calendar-main')
            table_headers = content.query_selector_all('.table-header')

            result = []
            for table_header in table_headers:
                title_element = table_header.query_selector('.table-header__title')
                title = title_element.inner_text() if title_element else "无标题"

                adjacent_div_handle = table_header.evaluate_handle("node => node.nextElementSibling")
                table = adjacent_div_handle.query_selector('.jin-table')
                header = table.query_selector("table") if table else None

                header_th_elements = [th.inner_text() for th in header.query_selector_all("th")] if header else []
                table_body = table.query_selector('.jin-table-body')

                rows = []
                if table_body:
                    groups = table_body.query_selector_all('.jin-table-row__group')
                    for group in groups:
                        wraps = group.query_selector_all('.jin-table-row__wrap')
                        if not wraps:
                            continue
                        first_wrap_columns = wraps[0].query_selector_all('.jin-table-column')
                        time = first_wrap_columns[0].inner_text() if first_wrap_columns else "无标题"
                        data = []
                        for wrap in wraps:
                            columns = wrap.query_selector_all('.jin-table-column')
                            if columns:
                                row_content = [col.inner_text() for col in columns[1:]]
                                data.append(row_content)
                        rows.append({
                            'time': time,
                            'data': data
                        })
                result.append({
                    'title': title,
                    'header': header_th_elements,
                    'body': rows
                })


            browser.close()
            markdown = self.remove_empty_columns_from_markdown(self.convert_to_markdown(result))
            os.makedirs("data", exist_ok=True)
            with open("data/jin10.md", "w") as file:
                file.write("# 经济日历\n\n")
                file.write(markdown)
            return markdown

    def convert_to_markdown(self, data):
        markdown = ""
        for section in data:
            title = section['title'].replace("\n", "")
            header = [item.replace("\n", "") for item in section['header']]
            body = section['body']

            markdown += f"## {title}\n\n"
            merged_data = []
            previous_time = None
            for entry in body:
                time = entry['time'].replace("\n", "")
                for row in entry['data']:
                    cleaned_row = [col.replace("\n", "") for col in row]
                    if time == previous_time:
                        merged_data.append([''] + cleaned_row)
                    else:
                        merged_data.append([time] + cleaned_row)
                    previous_time = time

            markdown += "| " + " | ".join(header) + " |\n"
            markdown += "| " + " | ".join(['---'] * len(header)) + " |\n"
            for row in merged_data:
                markdown += "| " + " | ".join(row) + " |\n"
            markdown += "\n"
        return markdown

    def process_table(self, table_lines):
        """
        处理一个 Markdown 表格，将数据行中全部为空的列（整列为空）删除，
        同时更新表头和分隔行。
        """
        rows = []
        for line in table_lines:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            rows.append(cells)

        if len(rows) <= 2:
            return table_lines

        ncols = len(rows[0])
        empty_cols = []
        for j in range(ncols):
            if all(row[j] == "" for row in rows[2:]):
                empty_cols.append(j)

        new_rows = []
        for row in rows:
            new_row = [cell for j, cell in enumerate(row) if j not in empty_cols]
            new_rows.append(new_row)

        new_table_lines = []
        for row in new_rows:
            new_line = "| " + " | ".join(row) + " |"
            new_table_lines.append(new_line)
        return new_table_lines

    def remove_empty_columns_from_markdown(self, md):
        """
        输入一个 Markdown 格式的字符串，查找其中所有的表格，
        并删除每个表格中数据行全为空的列（包括对应的表头和分隔行）。
        """
        lines = md.splitlines()
        output_lines = []
        table_lines = []
        in_table = False

        for line in lines:
            if line.strip().startswith("|"):
                table_lines.append(line)
                in_table = True
            else:
                if in_table:
                    output_lines.extend(self.process_table(table_lines))
                    table_lines = []
                    in_table = False
                output_lines.append(line)
        if in_table:
            output_lines.extend(self.process_table(table_lines))
        return "\n".join(output_lines)
