import sys
import re
from jinja2 import Template

def analyze_log_file(log_file_path):
    #re.compile 编译正则表达式后的对象可以重复使用，提高效率
    error_pattern = re.compile(r"ERROR: (.*)")
    errors = []

    try:
        with open(log_file_path,'r') as file:
            for line in file:
                # 匹配出来的值给到match
                match = error_pattern.search(line)
                if match:
                    # group(0)返回的是整个匹配的内容
                    # 包括前面的ERROR
                    # group(1)仅返回的是(.*)匹配的内容第一个
                    errors.append(match.group(1))
    except FileNotFoundError:
        print("日志文件未找到")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

    return errors


def generate_html_report(errors, report_file_path):
    template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>日志错误报告</title>
        <style>
            body { font-family: Arial, sans-serif; }
            h1 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { background-color: #f8d7da; margin: 5px 0; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>日志错误报告</h1>
        <ul>
        {% for error in errors %}
            <li>{{ error }}</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """)

    html_content = template.render(errors=errors)
    try:
        with open(report_file_path,'w') as report_file_path:
            report_file_path.write(html_content)
            print(f"报告已生成: {report_file_path}")
    except Exception as e:
        print(f"报告生成失败: {e}")
        sys.exit(1)


def main(log_file_path, report_file_path):
    errors = analyze_log_file(log_file_path)
    print(f"找到 {len(errors)} 个错误")
    generate_html_report(errors, report_file_path)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"用法: python script.py <日志文件路径> <报告文件路径>")
        sys.exit(1)

    log_file_path = sys.argv[1]
    report_file_path = sys.argv[2]

    main(log_file_path, report_file_path)