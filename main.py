
from binance import Client
from openai import OpenAI
from analyzer.base import Analyzer
from datetime import datetime
from jin10.load import Jin10Loader
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown
import textwrap
import time
import configparser
import sys
import threading

# 从配置文件中加载 API Key 和其他配置
config = configparser.ConfigParser()
config.read('config.ini')  # 请确保文件路径正确

# 读取 Binance API 配置
API_KEY = config.get("BINANCE", "API_KEY")
API_SECRET = config.get("BINANCE", "API_SECRET")
binance_client = Client(API_KEY, API_SECRET)

# 读取 OpenAI 配置
open_ai_api_key = config.get("GPT", "API_KEY")
# open_ai_base_url = config.get("OPENAI", "BASE_URL")
open_ai_client = OpenAI(api_key=open_ai_api_key)
def main():
    symbol = "BTCUSDT"
    days = 2
    now = datetime.now()
    end_date = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
 
    analyzer = Analyzer(binance_client)
    jin10 = Jin10Loader()
    def print_progress(stop_event):
        # Define a list of ANSI 256-color codes representing a rainbow spectrum
        rainbow_colors = [196, 202, 226, 46, 21, 93]
        i = 0
        while not stop_event.is_set():
            color_code = rainbow_colors[i % len(rainbow_colors)]
            # Set the text color using the ANSI escape code for 256 colors
            sys.stdout.write(f"\033[38;5;{color_code}m.\033[0m")
            sys.stdout.flush()
            i += 1
            time.sleep(2)

    def run_with_progress(func, desc, *args, **kwargs):
        # Print the description with a timestamp on the same line without a newline
        timestamp = datetime.now().strftime("%H:%M:%S")
        sys.stdout.write(f"[{timestamp}] {desc}")
        sys.stdout.flush()
        stop_event = threading.Event()
        progress_thread = threading.Thread(target=print_progress, args=(stop_event,))
        progress_thread.start()
        result = func(*args, **kwargs)
        stop_event.set()
        progress_thread.join()
        # End the progress line with a newline
        sys.stdout.write("\n")
        sys.stdout.flush()
        return result

    run_with_progress(analyzer.ohlcv, "获取K线数据", symbol, days, end_date)
    run_with_progress(analyzer.agg_trades, "获取订单数据", symbol, days, end_date)
    run_with_progress(analyzer.ticker_24hr, "获取24小时价格", symbol)
    run_with_progress(analyzer.other, "获取其他数据", symbol, days, end_date)
    run_with_progress(jin10.fetch_page, "获取经济日历", date_str)

    # 目标文件夹
    data_folder = "data"
    output_file = f"output/{date_str}.md"

    # 获取所有.md文件
    md_files = [f for f in os.listdir(data_folder) if f.endswith(".md")]

    # 按照文件名排序（可选）
    md_files.sort()

    # 逐个读取并合并内容
    with open(output_file, "w", encoding="utf-8") as outfile:
      for md_file in md_files:
        file_path = os.path.join(data_folder, md_file)
        with open(file_path, "r", encoding="utf-8") as infile:
          # outfile.write(f"# {md_file}\n\n")  # 添加文件名作为标题
          outfile.write(infile.read() + "\n\n")  # 追加文件内容
          outfile.write("---\n\n")  # 分隔符

    # 分割output_file成多段，每段以大标题（以'#'开头）开始，并生成[{ role: 'user', content: '' }, ...]格式
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()

    segments = []
    current_segment = ""
    lines = content.splitlines()
    titles = []
    for line in lines:
        # 遇到以'#'开头的大标题时，认为是新段落的开始
        if line.startswith("#") and (len(line) == 1 or line[1] != "#"):
            titles.append(line.strip())
            if current_segment.strip():
                segments.append({ "role": "user", "content": current_segment.strip() })
            current_segment = line + "\n"
        else:
            current_segment += line + "\n"

    if current_segment.strip():
        segments.append({ "role": "user", "content": current_segment.strip() })

    # 输出生成的段落列表（可以根据需要进一步处理）
    markdown_string = """
        # 角色设定
        你是一位专业的虚拟币市场分析师，熟悉市场趋势分析与交易策略，能为我生成基于以下数据的24小时BTC合约市场趋势分析报告。请根据提供的各类数据生成一个全面的分析报告，并给出相应的合约操作建议。

        ## 数据说明
        每次提交时，将提供以下各类数据，请确保每个部分对应正确的分析：

        1. **K线数据**：
        - 1小时与4小时K线数据。但是需要你自己分析价格走势、成交量、关键技术指标（如RSI、MACD等）。
        
        2. **鲸鱼交易监控数据**：
        - 大额买入和卖出数据，反映市场大资金流动。

        3. **恐慌与贪婪指数**：
        - 当前与历史的市场情绪数据。

        4. **合约数据**：
        - 合约持仓数据、资金费率、未平仓合约数、合约持仓量历史等。
        - 大户持仓量的多空比、大户账户数多空比、合约的主动买卖量。

        5. **市场价格波动**：
        - 24小时内的价格变动情况。

        6. **宏观经济事件数据**：
        - 即将发布或已发布的经济数据与事件，及其预期市场影响。

        ## 分析要求

        ### 1. 市场趋势预测：
        - **计算关键指标** 根据1小时与4小时K线数据。计算分析要用到的关键技术指标（如RSI、MACD等）。
        - **预测市场趋势**：基于K线数据、鲸鱼交易监控数据、恐慌与贪婪指数、资金费率等，判断未来24小时的市场走势（上涨、下跌或震荡）。
        - **关键指标分析**：分析关键技术指标（如RSI、MACD等）和大资金流动对市场趋势的影响，明确支撑位和阻力位。

        ### 2. 合约操作建议：
        - **操作建议**：基于市场趋势预测，给出具体的合约操作建议（买入/卖出时机、仓位安排、止损设置等）。
        - **数据依据**：提供明确的数据支持，并给出相应的风险管理措施。

        ### 3. 宏观经济与事件影响：
        - **经济事件分析**：分析即将发布的宏观经济数据与事件对市场可能产生的影响，并指出潜在的风险。"

        ## 输出要求
        ### 严格按照下面这些内容输出（100-200字左右）：
        - **走势总结**：包含市场趋势预测结果、关键指标分析、预测市场趋势，在达到什么价位时需要在次分析, 直接给出结果，不要生成根据、基于等相近词汇。
        - **合约操作建议**： 合约操作建议中，需要给出具体的做多/做空时机。
        - **宏观经济与事件影响**：需要注意的宏观经济事件对市场可能产生的影响。
    """
    messages = [
        { "role": 'assistant', "content": markdown_string }
    ]
    for idx, title in enumerate(titles):
        messages.append({"role": "assistant", "content": f"好的, 请提供{title.replace('#', '').strip()}数据"})
        messages.append(segments[idx])

    messages.append({"role": "assistant", "content": "数据是否已提交完整？"})
    messages.append({"role": "user", "content": "OK了，数据已提交完整，请帮我生成市场趋势分析报告"})
    print('开始分析')

    max_retries = 5
    delay = 2
    for attempt in range(max_retries):
        try:
            responses = open_ai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
            break
        except Exception as e:
            if "timeout" in str(e).lower():
                print(f"请求超时，正在重试 {attempt + 1}/{max_retries}，等待 {delay} 秒...")
                time.sleep(delay)
                delay *= 2  # 指数退避
            else:
                raise e
    else:
        raise Exception("重试次数已达上限，请检查网络或服务状态。")

    # 配置收件人列表和邮件发送账户
    mail_list = ["1072992047@qq.com"]  # 可添加更多邮箱
    sender_email = config.get("EMAIL", "SENDER_EMAIL")
    sender_password = config.get("EMAIL", "SENDER_PASSWORD")
    smtp_server = config.get("EMAIL", "SMTP_SERVER")
    smtp_port = 465

    # 邮件主题和内容
    markdown_content = textwrap.dedent(responses.choices[0].message.content)
    email_body = markdown.markdown(markdown_content)
    email_subject = f"{end_date} 市场趋势分析报告"

    # 构建邮件消息
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(mail_list)
    msg["Subject"] = email_subject
    msg.attach(MIMEText(email_body, 'html'))

    # 发送邮件
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.close()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

    # 订单深度，感觉没有用
    # order_book = analyzer.order_book(symbol)
    # print(order_book)

if __name__ == "__main__":
    main()
