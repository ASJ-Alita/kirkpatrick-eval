<div align="center">

# 🏢 Training Toolkit

> 用 AI 重塑企业培训全流程

[![Training Toolkit](https://img.shields.io/badge/🧩-Training_Toolkit-2D9CDB?style=flat-square)](#)
[![Evaluation](https://img.shields.io/badge/🎓-Kirkpatrick_Model-E74C3C?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.6+-3776AB?style=flat-square&logo=python)](#)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#)
[![Zero Deps](https://img.shields.io/badge/Dependencies-Zero-success?style=flat-square)](#)

**柯氏四级培训评估系统** — 将经典评估模型落地为可执行的工具

反应层 → 学习层 → 行为层 → 结果层，四级问卷 + 自动分析报告 + ROI 计算，一站式完成。

🧩 **产品矩阵** → [知识库问答](https://github.com/ASJ-Alita/rag-knowledge-base) · [培训需求分析](https://github.com/ASJ-Alita/training-analyzer) · [效果追踪器](https://github.com/ASJ-Alita/training-tracker) · [智能出题](https://github.com/ASJ-Alita/quiz-generator) · [培训助手](https://github.com/ASJ-Alita/training-assistant)

</div>

---

# 柯氏四级培训评估系统

> **Kirkpatrick Four-Level Training Evaluation System**  
> 基于经典柯氏模型的企业培训效果评估工具，支持四级问卷收集 + 可视化分析报告自动生成

---

## 📷 功能截图

| 问卷填写 | 数据列表 | 分析报告 |
|:---:|:---:|:---:|
| 🖼️ 四层结构化问卷 | 🖼️ 历史数据管理 | 🖼️ HTML可视化大屏 |

---

## 🎯 什么是柯氏四级评估模型？

柯氏模型（Kirkpatrick Model）是全球最广泛应用的培训评估框架：

| 级别 | 维度 | 评估内容 | 评估时机 |
|------|------|----------|----------|
| **Level 1** | 反应层 | 学员对培训的满意度、对讲师/内容/组织的评价 | 培训结束后 |
| **Level 2** | 学习层 | 知识和技能的掌握程度（前测 vs 后测） | 培训前+培训后 |
| **Level 3** | 行为层 | 培训内容在工作中的实际应用程度 | 培训后30天 |
| **Level 4** | 结果层 | 业务指标改善、ROI投入产出比 | 培训后季度 |

---

## ✨ 系统功能

### 📝 Level 1 · 反应层问卷
- 8道李克特量表题（1~5分）
- 覆盖维度：内容价值 / 讲师表现 / 组织安排 / 教学资源 / 总体满意度

### 📝 Level 2 · 学习层测验
- 内置5道选择题，支持**前测**和**后测**
- 自动计算得分和进步幅度

### 📝 Level 3 · 行为层追踪（30天）
- 6道行为应用量表题
- 评估：知识应用 / 知识传播 / 行为改变 / 外部认可 / 持续学习

### 📝 Level 4 · 结果层 & ROI
- 4项业务指标（效率提升 / 错误率 / 技能达标率 / 留存率）
- 自动计算 ROI = (培训收益 - 培训投入) / 培训投入 × 100%

### 📊 智能分析报告
- **四级雷达图**：一图总览评估全貌
- **前后测对比图**：直观展示学习进步
- **业务指标柱状图**：量化培训产出
- **AI智能建议**：自动识别短板，给出改进方向
- 一键生成 HTML 报告，可分享给管理层

### 🗂️ 数据管理
- 本地 JSON 存储，零依赖
- 导出 CSV，兼容 Excel 分析
- 注入演示数据，即开即用

---

## 🚀 快速开始

### 环境要求
- Python 3.6+（无需安装任何第三方库）
- macOS / Windows / Linux

### 运行步骤

```bash
# 克隆仓库
git clone https://github.com/ASJ-Alita/kirkpatrick-eval.git
cd kirkpatrick-eval

# 直接运行（无需pip install）
python3 app.py
```

### 演示数据
1. 运行程序 → 切换到「📊 生成分析报告」Tab
2. 点击 **「🎭 注入演示数据」**（自动生成8条随机记录）
3. 点击 **「📊 生成并打开分析报告」**
4. 浏览器自动打开可视化报告 🎉

---

## 📁 项目结构

```
kirkpatrick-eval/
├── app.py              # GUI主程序（tkinter，3 Tab页签）
├── report.py           # HTML报告生成（Chart.js可视化）
├── data/
│   ├── config.py       # 问卷题目配置（四级题目定义）
│   └── manager.py      # 数据存储/统计/导出（JSON+CSV）
├── reports/            # 生成的报告文件（自动创建）
├── kirkpatrick_data.json  # 数据存储文件（运行后自动生成）
├── requirements.txt    # 依赖说明
└── README.md
```

---

## 🎯 面试亮点

这个项目充分体现了以下能力：

| 能力维度 | 体现点 |
|----------|--------|
| **培训专业知识** | 深度应用柯氏模型，覆盖评估全流程 |
| **产品思维** | 从用户场景出发，设计完整工作流 |
| **数据可视化** | Chart.js 动态图表，雷达图/柱状图/饼图 |
| **Python开发** | tkinter GUI + 模块化架构 |
| **实用性** | 零依赖，开箱即用，可直接在企业落地 |

---

## 🔮 下一步规划

- [ ] Web版本（FastAPI + Vue）
- [ ] 多课程对比分析
- [ ] AI自动生成培训改进建议（接入大模型API）
- [ ] 企业微信/钉钉问卷推送集成

---

## 📌 关于作者

**培训技术专家** | 12年IT教育经验 | AI应用爱好者  
关注：企业培训数字化 / AI辅助教学 / 学习与发展（L&D）

[![GitHub](https://img.shields.io/badge/GitHub-ASJ--Alita-blue?style=flat-square&logo=github)](https://github.com/ASJ-Alita)
