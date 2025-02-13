# 市场趋势预测系统产品需求文档

## 1. 项目概述

市场趋势预测系统旨在提供基于实时数据和情绪分析的 **BTC 未来趋势预测**。系统会每日早上7:30生成一份邮件报告，包含对当天BTC市场走势的预测，以及相关宏观经济事件的预警。

### 1.1 目标用户

- 虚拟币交易者
- 量化交易策略开发者
- 投资者和分析师

### 1.2 主要目标

- **每日市场趋势预测**：基于多维度数据，预测BTC市场未来24小时的走势（看涨/看跌）。
- **预测报告**：每个交易日早上7:30通过邮件自动发送市场趋势预测报告。
- **新闻预警**：通过宏观经济新闻和市场事件，预判对市场的影响，并给出预警或提示。

## 2. 功能需求

### 2.1 数据源

- **恐惧与贪婪指数**：通过 **Alternative.me API** 获取市场情绪数据。
- **市场交易数据**：通过 **Binance API** 获取市场交易量、价格波动、BTC订单数据等。
- **鲸鱼交易监控数据**：通过 **Binance API** 或其他第三方服务（如 Whale Alert）获取鲸鱼账户交易行为。
- **宏观经济新闻数据**：通过 **财经网站API** 或 **RSS** 获取未来7天内的重要经济新闻事件。

### 2.2 数据分析

- **市场情绪分析**：基于恐惧与贪婪指数，分析市场的情绪波动。
- **交易量分析**：分析BTC的交易量、波动率、市场深度等数据。
- **鲸鱼交易监控**：检测鲸鱼账户的资金流动和交易行为，评估市场趋势。
- **宏观经济事件影响**：分析未来7天的宏观经济新闻和数据，评估其对市场的潜在影响。

### 2.3 预测模型

- **时间序列预测模型**：利用市场历史数据（价格、成交量等）进行趋势预测。
- **基于情绪的预测模型**：结合市场情绪和鲸鱼交易监控数据，分析市场可能的趋势变化。
- **外部事件预测模型**：利用宏观经济数据和新闻发布预判市场的短期波动。

### 2.4 邮件报告

- **报告内容**：
  - 当日市场趋势预测（看涨/看跌）。
  - 影响市场的关键经济新闻事件（例如API原油库存数据发布、美国CPI数据等）。
  - 基于鲸鱼交易监控数据的市场动态。
  - 恐惧与贪婪指数的最新状态。
  
- **报告时间**：每日早上7:30发送。

### 2.5 用户界面

- **无用户界面**：系统通过自动化运行，生成每日预测报告并发送到用户邮箱。

## 3. 数据需求

### 3.1 恐惧与贪婪指数数据

- **API来源**：Alternative.me
- **API Endpoint**：`https://api.alternative.me/fng/`
- **数据内容**：
  - 恐惧与贪婪指数值
  - 数据更新时间（每天一次）
  
### 3.2 市场交易数据

- **API来源**：Binance API
- **API Endpoint**：`https://api.binance.com/api/v3/ticker/24hr`（获取24小时市场交易数据）
- **数据内容**：
  - BTC的当前价格、交易量、涨跌幅
  - 市场深度、历史价格数据

### 3.3 鲸鱼交易监控数据

- **API来源**：Binance API 或 Whale Alert
- **数据内容**：
  - 鲸鱼账户的交易行为数据（大宗交易、资金流入流出）

### 3.4 宏观经济新闻数据

- **数据来源**：财经网站（如 NewsBTC、Investing.com）
- **数据内容**：
  - 未来7天内重要的经济数据发布（如API原油库存、CPI数据等）
  - 相关新闻摘要和事件时间
  
## 4. 技术需求

### 4.1 数据获取与处理

- **API调用与数据提取**：定期从 **Binance API** 和 **Alternative.me** 获取最新的市场和情绪数据。
- **数据清洗与处理**：清洗数据，去除异常值，转换为适合分析的格式。
- **数据存储**：使用数据库（如MySQL或MongoDB）存储历史数据，确保数据的持久化和可查询性。

### 4.2 预测模型

- **机器学习模型**：使用如LSTM、ARIMA等模型对历史数据进行训练，预测BTC的短期市场趋势。
- **情绪分析**：基于恐惧与贪婪指数和鲸鱼交易监控数据，设计情绪分析算法来辅助市场预测。
  
### 4.3 邮件自动化

- **邮件发送**：使用邮件发送服务（如SMTP或第三方邮件API）定时发送报告。
  
## 5. 性能需求

- **实时性**：确保API数据更新及时，并在每日早上7:30前生成报告。
- **高准确性**：确保市场趋势预测的准确性，尽可能减少预测误差。
- **高可用性**：系统应具备较高的可用性，保证数据获取与报告生成无中断。

## 6. 风险与挑战

- **数据波动性**：市场情绪和宏观经济事件的变化会导致预测结果的波动，可能影响准确性。
- **数据源不稳定**：第三方API可能会遭遇访问限制或收费问题，需有备用方案。
- **模型准确性**：短期市场趋势预测本身具有较高的不确定性，需不断优化模型。
  
## 7. 时间计划

| 阶段       | 时间       | 任务内容                          |
|------------|------------|-----------------------------------|
| 需求分析   | 2025-02-08 | 确认数据源与需求，制定产品功能。     |
| 数据获取   | 2025-02-09 | 获取并测试API，整合所需数据。       |
| 模型构建   | 2025-02-15 | 搭建预测模型并进行训练与测试。     |
| 邮件系统   | 2025-02-18 | 设置邮件发送系统，测试报告生成。   |
| 系统集成   | 2025-02-20 | 完成系统集成与上线测试。           |
  
## 8. 结论

市场趋势预测系统将通过结合多源数据与机器学习模型，为用户提供准确的市场预测。通过每日早上的自动化报告，帮助交易者快速把握市场动向，并预警可能的风险和机会。
