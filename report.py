# -*- coding: utf-8 -*-
"""
HTML可视化报告生成模块
"""
import os
import json
from datetime import datetime


def generate_report(stats: dict, evaluations: list, output_dir: str) -> str:
    """生成HTML可视化报告，返回文件路径"""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"kirkpatrick_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(output_dir, filename)

    if not stats:
        return ""

    n = stats["total"]
    l1 = stats.get("level1", {})
    l2 = stats.get("level2", {})
    l3 = stats.get("level3", {})
    l4 = stats.get("level4", {})

    # 雷达图数据（四级得分换算为百分制）
    radar_labels = ["反应层(L1)", "学习层(L2)", "行为层(L3)", "结果层(L4)"]
    l1_pct = round((l1.get("total_avg", 0) / 5) * 100, 1)
    l2_pct = round(l2.get("post_avg", 0), 1)
    l3_pct = round((l3.get("total_avg", 0) / 5) * 100, 1)
    roi_raw = l4.get("roi", 0)
    l4_pct = min(100, max(0, round(50 + roi_raw / 4, 1)))  # ROI映射到0~100

    radar_data = [l1_pct, l2_pct, l3_pct, l4_pct]

    # L1 各题目得分
    l1_q_labels = []
    l1_q_values = []
    from data.config import LEVEL1_QUESTIONS
    for q in LEVEL1_QUESTIONS:
        qid = q["id"]
        avg = l1.get("avg_by_question", {}).get(qid, 0)
        l1_q_labels.append(q["text"][:12] + "...")
        l1_q_values.append(avg)

    # L3 各题目得分
    l3_q_labels = []
    l3_q_values = []
    from data.config import LEVEL3_QUESTIONS
    for q in LEVEL3_QUESTIONS:
        qid = q["id"]
        avg = l3.get("avg_by_question", {}).get(qid, 0)
        l3_q_labels.append(q["text"][:12] + "...")
        l3_q_values.append(avg)

    # L4 各指标
    l4_metric_labels = ["效率提升%", "错误率降低%", "技能达标%", "留存率变化%"]
    l4_metric_values = [
        l4.get("metrics_avg", {}).get("L4M1", 0),
        l4.get("metrics_avg", {}).get("L4M2", 0),
        l4.get("metrics_avg", {}).get("L4M3", 0),
        l4.get("metrics_avg", {}).get("L4M4", 0),
    ]

    # 收集课程名称分布
    course_count = {}
    for e in evaluations:
        c = e.get("course_name", "未知")
        course_count[c] = course_count.get(c, 0) + 1
    pie_labels = list(course_count.keys())
    pie_data = list(course_count.values())

    roi = l4.get("roi", 0)
    roi_color = "#27ae60" if roi >= 0 else "#e74c3c"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>柯氏四级培训评估报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'PingFang SC','Microsoft YaHei',sans-serif; background: #f0f2f5; color: #333; }}
  .header {{ background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
    color: white; padding: 40px 60px; }}
  .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
  .header p {{ opacity: 0.85; font-size: 14px; }}
  .container {{ max-width: 1100px; margin: 30px auto; padding: 0 20px; }}

  /* KPI Cards */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px; }}
  .kpi-card {{ background: white; border-radius: 12px; padding: 24px; text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,.07); border-top: 4px solid; }}
  .kpi-card.l1 {{ border-color: #3498db; }}
  .kpi-card.l2 {{ border-color: #2ecc71; }}
  .kpi-card.l3 {{ border-color: #f39c12; }}
  .kpi-card.l4 {{ border-color: #9b59b6; }}
  .kpi-label {{ font-size: 12px; color: #888; margin-bottom: 8px; letter-spacing: 0.5px; }}
  .kpi-value {{ font-size: 36px; font-weight: 700; }}
  .kpi-sub {{ font-size: 12px; color: #aaa; margin-top: 4px; }}
  .kpi-card.l1 .kpi-value {{ color: #3498db; }}
  .kpi-card.l2 .kpi-value {{ color: #2ecc71; }}
  .kpi-card.l3 .kpi-value {{ color: #f39c12; }}
  .kpi-card.l4 .kpi-value {{ color: #9b59b6; }}

  /* Level Badges */
  .level-tag {{ display: inline-block; font-size: 11px; font-weight: 600;
    padding: 3px 10px; border-radius: 20px; margin-right: 8px; }}
  .tag-l1 {{ background: #dbeafe; color: #1d4ed8; }}
  .tag-l2 {{ background: #d1fae5; color: #065f46; }}
  .tag-l3 {{ background: #fef3c7; color: #92400e; }}
  .tag-l4 {{ background: #ede9fe; color: #5b21b6; }}

  /* Chart Sections */
  .section {{ background: white; border-radius: 12px; padding: 28px;
    box-shadow: 0 2px 12px rgba(0,0,0,.07); margin-bottom: 24px; }}
  .section-title {{ font-size: 16px; font-weight: 600; margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px; }}
  .charts-2col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
  .chart-wrap {{ position: relative; height: 280px; }}

  /* Pre/Post comparison */
  .compare-row {{ display: flex; align-items: center; gap: 16px; margin: 12px 0; }}
  .compare-label {{ width: 70px; font-size: 13px; color: #555; }}
  .bar-bg {{ flex: 1; background: #f0f0f0; border-radius: 6px; height: 28px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 6px; display: flex; align-items: center;
    padding-left: 10px; font-size: 13px; font-weight: 600; color: white; transition: width 0.8s; }}
  .bar-pre {{ background: linear-gradient(90deg, #94a3b8, #64748b); }}
  .bar-post {{ background: linear-gradient(90deg, #34d399, #10b981); }}

  /* ROI */
  .roi-big {{ font-size: 52px; font-weight: 800; text-align: center; padding: 20px 0; }}
  .insight-list {{ list-style: none; padding: 0; }}
  .insight-list li {{ padding: 10px 0; border-bottom: 1px dashed #eee; font-size: 14px;
    display: flex; align-items: flex-start; gap: 8px; }}
  .insight-list li::before {{ content: "💡"; flex-shrink: 0; }}

  .footer {{ text-align: center; padding: 30px; font-size: 12px; color: #aaa; }}

  @media(max-width: 768px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .charts-2col {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>📊 柯氏四级培训评估报告</h1>
  <p>Kirkpatrick Four-Level Training Evaluation &nbsp;|&nbsp;
     生成时间：{datetime.now().strftime("%Y年%m月%d日 %H:%M")} &nbsp;|&nbsp;
     参与人数：{n} 人</p>
</div>

<div class="container">

  <!-- KPI Cards -->
  <div class="kpi-grid">
    <div class="kpi-card l1">
      <div class="kpi-label"><span class="level-tag tag-l1">L1</span>反应层满意度</div>
      <div class="kpi-value">{l1.get("total_avg", 0)}<span style="font-size:18px">/5</span></div>
      <div class="kpi-sub">共 {n} 份反馈</div>
    </div>
    <div class="kpi-card l2">
      <div class="kpi-label"><span class="level-tag tag-l2">L2</span>学习层进步</div>
      <div class="kpi-value">+{l2.get("improvement", 0)}<span style="font-size:18px">%</span></div>
      <div class="kpi-sub">前测{l2.get("pre_avg",0)}% → 后测{l2.get("post_avg",0)}%</div>
    </div>
    <div class="kpi-card l3">
      <div class="kpi-label"><span class="level-tag tag-l3">L3</span>行为层应用度</div>
      <div class="kpi-value">{l3.get("total_avg", 0)}<span style="font-size:18px">/5</span></div>
      <div class="kpi-sub">30天后追踪均分</div>
    </div>
    <div class="kpi-card l4">
      <div class="kpi-label"><span class="level-tag tag-l4">L4</span>培训ROI</div>
      <div class="kpi-value" style="color:{roi_color}">{roi}<span style="font-size:18px">%</span></div>
      <div class="kpi-sub">投入¥{l4.get("total_invest",0):,} / 收益¥{l4.get("total_benefit",0):,}</div>
    </div>
  </div>

  <!-- 综合雷达图 + 课程分布 -->
  <div class="charts-2col">
    <div class="section">
      <div class="section-title">🕸️ 四级综合评估雷达图</div>
      <div class="chart-wrap">
        <canvas id="radarChart"></canvas>
      </div>
    </div>
    <div class="section">
      <div class="section-title">🥧 课程分布（参与比例）</div>
      <div class="chart-wrap">
        <canvas id="pieChart"></canvas>
      </div>
    </div>
  </div>

  <!-- L1 各题目得分 -->
  <div class="section">
    <div class="section-title">📋 <span class="level-tag tag-l1">L1</span>反应层 — 各维度详细得分</div>
    <div class="chart-wrap" style="height:260px">
      <canvas id="l1Chart"></canvas>
    </div>
  </div>

  <!-- L2 前测后测对比 -->
  <div class="section">
    <div class="section-title">📝 <span class="level-tag tag-l2">L2</span>学习层 — 前测 vs 后测对比</div>
    <div class="compare-row">
      <div class="compare-label">前测均分</div>
      <div class="bar-bg">
        <div class="bar-fill bar-pre" style="width:{l2.get('pre_avg',0)}%">{l2.get("pre_avg",0)}%</div>
      </div>
    </div>
    <div class="compare-row">
      <div class="compare-label">后测均分</div>
      <div class="bar-bg">
        <div class="bar-fill bar-post" style="width:{l2.get('post_avg',0)}%">{l2.get("post_avg",0)}%</div>
      </div>
    </div>
    <p style="margin-top:16px;font-size:13px;color:#666;">
      📈 平均进步幅度：<strong style="color:#10b981;font-size:16px">+{l2.get("improvement",0)}%</strong>
    </p>
  </div>

  <!-- L3 行为层 -->
  <div class="section">
    <div class="section-title">🔄 <span class="level-tag tag-l3">L3</span>行为层 — 工作中应用情况（30天追踪）</div>
    <div class="chart-wrap" style="height:260px">
      <canvas id="l3Chart"></canvas>
    </div>
  </div>

  <!-- L4 业务指标 + ROI -->
  <div class="charts-2col">
    <div class="section">
      <div class="section-title">📈 <span class="level-tag tag-l4">L4</span>结果层 — 业务指标改善</div>
      <div class="chart-wrap">
        <canvas id="l4Chart"></canvas>
      </div>
    </div>
    <div class="section">
      <div class="section-title">💰 <span class="level-tag tag-l4">L4</span>培训投入产出（ROI）</div>
      <div class="roi-big" style="color:{roi_color}">{roi}%</div>
      <p style="text-align:center;font-size:13px;color:#888">
        {"🎉 正向回报，培训效益良好" if roi >= 0 else "⚠️ 负向回报，建议优化方案"}</p>
      <ul class="insight-list" style="margin-top:16px">
        <li>累计培训投入：¥{l4.get("total_invest",0):,}</li>
        <li>估算培训收益：¥{l4.get("total_benefit",0):,}</li>
        <li>净收益：¥{l4.get("total_benefit",0) - l4.get("total_invest",0):,}</li>
      </ul>
    </div>
  </div>

  <!-- 智能建议 -->
  <div class="section">
    <div class="section-title">💡 AI智能分析建议</div>
    <ul class="insight-list">
      {"<li>反应层均分达到 " + str(l1.get("total_avg",0)) + "/5，" + ("学员满意度高，课程设计良好。" if l1.get("total_avg",0) >= 4 else "满意度有提升空间，建议收集具体改进意见。") + "</li>"}
      {"<li>学习层前后测进步 " + str(l2.get("improvement",0)) + "%，" + ("知识吸收效果显著，教学方法有效。" if l2.get("improvement",0) >= 15 else "知识转化有待加强，建议增加互动练习和案例讨论。") + "</li>"}
      {"<li>行为层均分 " + str(l3.get("total_avg",0)) + "/5，" + ("学员已将培训内容有效应用于工作，迁移效果好。" if l3.get("total_avg",0) >= 3.5 else "行为改变较弱，建议强化管理者支持和培训后辅导机制。") + "</li>"}
      {"<li>ROI为 " + str(roi) + "%，" + ("培训投资回报率达到预期，建议持续推进类似培训。" if roi >= 50 else "建议精细化评估培训项目设计，优化培训内容与业务目标对齐程度。") + "</li>"}
      {"<li>重点关注L3行为层：从'学会'到'用到工作中'是最大转化瓶颈，建议设置培训后30天行动计划和上级跟进机制。</li>"}
    </ul>
  </div>

</div>

<div class="footer">
  柯氏四级培训评估系统 · Kirkpatrick Model · 报告由 kirkpatrick-eval 自动生成<br>
  https://github.com/ASJ-Alita/kirkpatrick-eval
</div>

<script>
// ── 雷达图 ──────────────────────────────────────────────────────────────────
new Chart(document.getElementById('radarChart'), {{
  type: 'radar',
  data: {{
    labels: {json.dumps(radar_labels, ensure_ascii=False)},
    datasets: [{{
      label: '评估得分（百分制）',
      data: {radar_data},
      backgroundColor: 'rgba(57,73,171,0.2)',
      borderColor: '#3949ab',
      pointBackgroundColor: '#3949ab',
      pointRadius: 5,
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    scales: {{ r: {{ min: 0, max: 100, ticks: {{ stepSize: 20 }} }} }},
    plugins: {{ legend: {{ display: false }} }}
  }}
}});

// ── 饼图 ───────────────────────────────────────────────────────────────────
new Chart(document.getElementById('pieChart'), {{
  type: 'doughnut',
  data: {{
    labels: {json.dumps(pie_labels, ensure_ascii=False)},
    datasets: [{{
      data: {pie_data},
      backgroundColor: ['#3949ab','#2ecc71','#f39c12','#e74c3c','#9b59b6','#1abc9c','#e67e22'],
    }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
}});

// ── L1 柱状图 ──────────────────────────────────────────────────────────────
new Chart(document.getElementById('l1Chart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(l1_q_labels, ensure_ascii=False)},
    datasets: [{{
      label: '平均分（满分5）',
      data: {l1_q_values},
      backgroundColor: 'rgba(52,152,219,0.7)',
      borderColor: '#3498db',
      borderWidth: 1,
      borderRadius: 6,
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false, indexAxis: 'y',
    scales: {{ x: {{ min: 0, max: 5 }} }},
    plugins: {{ legend: {{ display: false }} }}
  }}
}});

// ── L3 柱状图 ──────────────────────────────────────────────────────────────
new Chart(document.getElementById('l3Chart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(l3_q_labels, ensure_ascii=False)},
    datasets: [{{
      label: '应用程度（满分5）',
      data: {l3_q_values},
      backgroundColor: 'rgba(243,156,18,0.7)',
      borderColor: '#f39c12',
      borderWidth: 1,
      borderRadius: 6,
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false, indexAxis: 'y',
    scales: {{ x: {{ min: 0, max: 5 }} }},
    plugins: {{ legend: {{ display: false }} }}
  }}
}});

// ── L4 业务指标 ────────────────────────────────────────────────────────────
new Chart(document.getElementById('l4Chart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(l4_metric_labels, ensure_ascii=False)},
    datasets: [{{
      label: '改善幅度（%）',
      data: {l4_metric_values},
      backgroundColor: ['rgba(155,89,182,.7)','rgba(52,73,94,.7)','rgba(26,188,156,.7)','rgba(230,126,34,.7)'],
      borderRadius: 6,
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }}
  }}
}});
</script>

</body>
</html>"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return filepath
