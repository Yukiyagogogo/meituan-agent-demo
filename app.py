import streamlit as st
import time

st.set_page_config(page_title="Meituan Agent 真实执行版", layout="wide")
st.title("周末活动 Agent (动态执行版)")

# ==========================================
# 1. 真实的底层工具链 (Mock API)
# ==========================================
def tool_search_poi(intent_tags):
    """根据意图标签搜索真实(模拟)数据库"""
    mock_db = [
        {"id": "A1", "name": "Meland 亲子乐园", "tags": ["家庭", "儿童"], "distance": "2.0km", "action": "买套票"},
        {"id": "R1", "name": "Wagas 沃歌斯", "tags": ["减肥", "健康"], "distance": "500m", "action": "订3人位"},
        {"id": "A2", "name": "UCCA 现代艺术展", "tags": ["一个人", "city walk", "文艺"], "distance": "3.5km", "action": "买单人票"},
        {"id": "R2", "name": "Manner Coffee", "tags": ["一个人", "咖啡", "休息"], "distance": "100m", "action": "无需预订"}
    ]
    
    results = []
    for item in mock_db:
        if any(tag in item["tags"] for tag in intent_tags):
            results.append(item)
    return results

def tool_check_queue(poi_name):
    """查询排队状态"""
    if "Meland" in poi_name:
        return "需排队 20 分钟"
    return "当前无需排队"

# ==========================================
# 2. 模拟大模型的“规划与执行”中枢
# (未来这里将替换为 LangGraph + LLM API)
# ==========================================
def execute_agent_pipeline(user_text):
    logs = []
    
    # 节点 1: Intent Parser (意图解析)
    logs.append("🧠 **意图解析节点:** 正在分析你的输入...")
    tags = []
    if "一个人" in user_text or "city walk" in user_text.lower():
        tags = ["一个人", "city walk", "文艺", "咖啡"]
        scenario = "solo"
    else:
        tags = ["家庭", "儿童", "减肥", "健康"]
        scenario = "family"
    logs.append(f"🎯 **提取关键约束:** 匹配到标签 {tags}")
    
    # 节点 2: Tool Executor (工具调用)
    logs.append("🛠️ **工具执行节点:** 调用 `tool_search_poi` 查询数据库...")
    pois = tool_search_poi(tags)
    for p in pois:
        logs.append(f"✅ 找到匹配地点: {p['name']}")
        
    # 节点 3: Verifier (验证与状态查询)
    logs.append("⚖️ **状态校验节点:** 调用 `tool_check_queue` 检查可行性...")
    for p in pois:
        queue_status = tool_check_queue(p['name'])
        p['status'] = queue_status
        logs.append(f"📊 {p['name']} 状态: {queue_status}")
        
    return logs, pois, scenario

# ==========================================
# 3. 前端 UI 交互层
# ==========================================
if "order_executed" not in st.session_state:
    st.session_state.order_executed = False

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("💬 用户输入")
    user_input = st.text_area("发送给美团 Agent：", value="今天下午是空的，我一个人 city walk", height=100)
    
    if st.button("运行 Agent (真执行)", type="primary"):
        st.session_state.order_executed = False
        st.session_state.run_result = None
        
        with st.status("Agent 正在规划及调用工具...", expanded=True) as status:
            # 真实触发 Agent 核心逻辑
            logs, final_pois, scenario = execute_agent_pipeline(user_input)
            
            # 动态打印执行日志，模拟 LangGraph 状态流转
            for log in logs:
                st.write(log)
                time.sleep(0.5) 
                
            status.update(label="规划完毕！", state="complete", expanded=False)
            st.session_state.run_result = {"pois": final_pois, "scenario": scenario}

with col2:
    st.subheader("📋 动态生成方案")
    
    if "run_result" in st.session_state and st.session_state.run_result:
        pois = st.session_state.run_result["pois"]
        
        if not pois:
            st.error("抱歉，没有找到符合要求的方案。")
        else:
            for poi in pois:
                with st.container(border=True):
                    st.markdown(f"#### 📍 {poi['name']}")
                    st.markdown(f"🚩 距离: {poi['distance']} | ⏳ {poi['status']}")
                    st.write(f"🏷️ **预订动作:** {poi['action']}")
            
            st.markdown("---")
            if not st.session_state.order_executed:
                if st.button("🚀 确认方案，一键安排！", type="primary", use_container_width=True):
                    with st.spinner("调用底层订单接口..."):
                        time.sleep(1)
                        st.session_state.order_executed = True
                        st.rerun()
            else:
                st.success("🎉 底层 API 下单已全部完成！")
    else:
        st.info("👈 修改左侧文本并点击运行。试试输入 '家庭 减肥' 或 '一个人 city walk'")
        