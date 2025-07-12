import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========== 配置页面 ===========
st.set_page_config(page_title="POMS Mood State Analyzer", page_icon="🏋️", layout="wide")

# =========== 标题 ===========
st.markdown("<h1 style='text-align: center; color: #2E86C1;'>🏋️‍♂️ POMS Mood State Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Developed by Dr. Hu from Capital University of Physical Education and Sports.</h4>", unsafe_allow_html=True)
st.markdown("---")

# =========== 分值映射 ===========
score_map = {
    "几乎没有": 0,
    "有一点": 1,
    "适中": 2,
    "相当多": 3,
    "非常地": 4
}

# 分量表题目编号
subscale_questions = {
    "紧张": [1, 8, 15, 21, 28, 35],
    "愤怒": [2, 9, 16, 22, 29, 36, 37],
    "疲劳": [3, 10, 17, 23, 30],
    "抑郁": [4, 11, 18, 24, 31, 38],
    "精力": [5, 12, 19, 25, 32, 39],
    "慌乱": [6, 13, 20, 26, 33],
    "自尊感": [7, 14, 27, 34, 40]
}

# =========== 文件上传 ===========
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("Upload your POMS Excel file (.xlsx)", type=["xlsx"])
with col2:
    order_file = st.file_uploader("Optional: Name order file (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    name_order = None

    if order_file is not None:
        order_df = pd.read_excel(order_file)
        name_order = order_df["姓名"].tolist()

    results = []

    for idx, row in df.iterrows():
        result = {"姓名": row["姓名"]}
        scores = {}

        for scale, questions in subscale_questions.items():
            total = 0
            for q_num in questions:
                match_cols = [c for c in df.columns if c.strip().startswith(str(q_num))]
                if match_cols:
                    value = row[match_cols[0]]
                    score = score_map.get(str(value).strip(), 0)
                    total += score
            scores[scale] = total
            result[scale] = total

        negative = scores["紧张"] + scores["愤怒"] + scores["疲劳"] + scores["抑郁"] + scores["慌乱"]
        positive = scores["精力"] + scores["自尊感"]
        TMD = negative - positive + 100
        result["TMD"] = TMD

        results.append(result)

    results_df = pd.DataFrame(results)

    # 排序
    if name_order:
        results_df["姓名"] = pd.Categorical(results_df["姓名"], categories=name_order, ordered=True)
        results_df = results_df.sort_values("姓名")

    st.success("✅ Analysis completed!")

    st.subheader("📄 Individual Scores")
    st.dataframe(results_df, use_container_width=True)

    # 计算均值 & SD
    summary_df = results_df.drop(columns=["姓名"]).agg(['mean', 'std']).T
    summary_df = summary_df.rename(columns={'mean': 'Mean', 'std': 'SD'})
    st.subheader("📊 Overall Mean and SD")
    st.dataframe(summary_df, use_container_width=True)

    # 下载结果
    csv = results_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("💾 Download CSV", csv, "POMS_results.csv", "text/csv")

    st.markdown("---")

    # =========== 图表交互 ===========
    st.subheader("🎨 Interactive Charts")
    chart_type = st.selectbox("Select Chart Type", ["Radar Chart (Mean)", "Bar Chart (Mean)", "Box Plot (Individuals)", "Scatter Plot (Individuals)"])
    selected_scales = st.multiselect("Select Scales", list(subscale_questions.keys()) + ["TMD"], default=["TMD"])

    plot_df = pd.melt(results_df, id_vars=["姓名"], value_vars=selected_scales, var_name="Scale", value_name="Score")

    if chart_type == "Radar Chart (Mean)":
        mean_df = plot_df.groupby("Scale")["Score"].mean().reset_index()
        mean_df = pd.concat([mean_df, mean_df.iloc[[0]]], ignore_index=True)  # 使用 pd.concat 替代 append
        fig = px.line_polar(mean_df, r="Score", theta="Scale", line_close=True, title="Mean Scores Radar Chart")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Bar Chart (Mean)":
        mean_df = plot_df.groupby("Scale")["Score"].mean().reset_index()
        fig = px.bar(mean_df, x="Scale", y="Score", color="Scale", title="Mean Scores Bar Chart")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Box Plot (Individuals)":
        fig = px.box(plot_df, x="Scale", y="Score", points="all", color="Scale", title="Individual Scores Distribution")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter Plot (Individuals)":
        fig = px.scatter(plot_df, x="姓名", y="Score", color="Scale", symbol="Scale", title="Individual Scores Scatter Plot")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray;'>Developed by Dr. Hu from Capital University of Physical Education and Sports.</p>", unsafe_allow_html=True)
