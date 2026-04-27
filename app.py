import streamlit as st
import time

st.set_page_config(page_title="Meituan Agent 真实执行版", layout="wide")
st.title("周末活动 Agent (动态执行版)")

# ==========================================
# 1. 真实的底层工具链 (Mock API) - 已加入家庭与朋友场景
# ==========================================
def tool_search_poi(intent_tags):
    """根据意图标签搜索真实(模拟)数据库"""
    mock_db = [
        # 家庭场景
        {"id": "A1", "name": "Meland 亲子乐园", "tags": ["家庭", "儿童", "5岁"], "distance": "2.0km", "action": "买 [2大1小] 家庭套票"},
        {"id": "R1", "name": "Wagas 沃歌斯 (轻食)", "tags": ["减肥", "健康", "家庭"], "distance": "500m", "action": "订3人位"},
        # 朋友场景 (4人，2男2女)
        {"id": "A3", "name": "沉浸式剧本杀体验馆", "tags": ["朋友", "聚会", "4人"], "distance": "1.8km", "action": "预订 4人情感本 (2男2女)"},
        {"id": "R3", "name": "Bistro 108 创意小酒馆", "tags": ["朋友", "聚餐", "氛围"], "distance": "2.1km", "action": "订4人位 (靠窗)"},
        # 兜底场景
        {"id": "A2", "name": "UCCA 现代艺术展", "tags": ["一个人", "city walk", "文艺"], "distance": "3.5km", "action": "买单人票"},
    ]
    
    results = []
    for item in mock_db:
        if any(tag in item["tags"] for tag in intent_tags):
            results.append(item)
    return results

def tool_check_queue(poi_name):
    """查询排队状态"""
    if "Meland" in poi_name:
        return "⚠️ 需排队 20 分钟"
    if "剧本杀" in poi_name:
        return "✅ 下午 14:00 场次有空位"
    return "✅ 当前无需排队"

# ==========================================
# 2. 模拟大模型的“规划与执行”中枢
# ==========================================
def execute_agent_pipeline(user_text):
    logs = []
    
    logs.append("🧠 **意图解析节点:** 正在分析你的输入...")
    tags = []
    # 动态匹配逻辑
    if "朋友" in user_text or "4个" in user_text:
        tags = ["朋友", "聚会", "4人", "聚餐", "氛围"]
        scenario = "friends"
    elif "孩子" in user_text or "老婆" in user_text or "家庭" in user_text:
        tags = ["家庭", "儿童", "5岁", "减肥", "健康"]
        scenario = "family"
    else:
        tags = ["一个人", "city walk", "文艺"]
        scenario = "solo"
        
    logs.append(f"🎯 **提取关键约束:** 匹配到标签 {tags}")
    
    logs.append("🛠️ **工具执行节点:** 调用 `tool_search_poi` 查询数据库...")
    pois = tool_search_poi(tags)
    for p in pois:
        logs.append(f"✅ 找到匹配地点: {p['name']}")
        
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
    # 默认放上赛题的朋友场景供测试
    default_prompt = "今天下午是空的，想和朋友出去玩几个小时，别离家太远。我们总共有4个人，2个男生2个女生，帮我安排一下。"
    user_input = st.text_area("发送给美团 Agent：", value=default_prompt, height=120)
    
    if st.button("运行 Agent (真执行)", type="primary"):
        st.session_state.order_executed = False
        st.session_state.run_result = None
        
        with st.status("Agent 正在规划及调用工具...", expanded=True) as status:
            logs, final_pois, scenario = execute_agent_pipeline(user_input)
            
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
                    st.markdown(f"🚩 距离: {poi['distance']} | {poi['status']}")
                    st.write(f"🏷️ **预订动作:** {poi['action']}")
            
            st.markdown("---")
            if not st.session_state.order_executed:
                if st.button("🚀 确认方案，一键安排！", type="primary", use_container_width=True):
                    with st.spinner("调用底层订单接口..."):
                        time.sleep(1.5)
                        st.session_state.order_executed = True
                        st.rerun()
            else:
                st.success("🎉 底层 API 下单已全部完成！")
                # 根据场景输出不同的分享文案
                if st.session_state.run_result["scenario"] == "friends":
                    st.info("📱 已自动发送微信给朋友群：'下午剧本杀和晚上法餐都订好啦，2点集合！'")
                elif st.session_state.run_result["scenario"] == "family":
                    st.info("📱 已自动发送微信给老婆：'搞定了，下午带娃去Meland放电，晚上吃Wagas减脂餐！'")
    else:
        st.info("👈 修改左侧文本并点击运行。直接测试赛题要求的两个场景吧！")
