美团本地探索 Agent：周末闲时活动规划 🤖

这是一个基于自然语言的本地生活 Agent Demo。它能够解析用户意图（如家庭遛娃、朋友聚会），结合约束条件（如距离、排队状态），自动规划并执行本地服务预订。

🚀 在线体验 Demo
[👉 点击这里直接体验 Web UI 👈](https://meituan-agent-demo-e49gysxncujfletvvtpmef.streamlit.app/)**

💡 核心链路设计
1. Intent Parser (意图解析)**：提取关键约束（时间、人数、特殊限制等）。
2. Planner (全局规划)**：根据用户场景动态加载推荐策略。
3. Tool Executor (工具执行)**：调用 Mock API 进行查询（如 `search_poi`, `check_queue`）。
4. Human-in-the-loop (人类确认)**：方案生成后，等待用户一键确认并并发执行底层订单调度。
