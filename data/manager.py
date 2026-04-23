# -*- coding: utf-8 -*-
"""
数据管理模块 - 存储与统计
"""
import json
import os
import csv
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "kirkpatrick_data.json")


def _load() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"evaluations": []}


def _save(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_evaluation(record: dict) -> str:
    """保存一条完整的四级评估记录，返回记录ID"""
    data = _load()
    record_id = f"KP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    record["id"] = record_id
    record["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["evaluations"].append(record)
    _save(data)
    return record_id


def get_all_evaluations() -> list:
    return _load().get("evaluations", [])


def delete_evaluation(record_id: str):
    data = _load()
    data["evaluations"] = [e for e in data["evaluations"] if e.get("id") != record_id]
    _save(data)


def clear_all():
    _save({"evaluations": []})


# ─── 统计计算 ──────────────────────────────────────────────────────────────────

def calc_stats(evaluations: list) -> dict:
    if not evaluations:
        return {}

    n = len(evaluations)

    # Level 1 平均分（每题1-5）
    l1_scores = {}
    for e in evaluations:
        for qid, val in e.get("level1", {}).items():
            l1_scores.setdefault(qid, []).append(val)
    l1_avg = {qid: round(sum(v) / len(v), 2) for qid, v in l1_scores.items()}
    l1_total = round(sum(l1_avg.values()) / len(l1_avg), 2) if l1_avg else 0

    # Level 2 前测/后测正确率
    pre_scores, post_scores = [], []
    for e in evaluations:
        l2 = e.get("level2", {})
        if l2.get("pre_score") is not None:
            pre_scores.append(l2["pre_score"])
        if l2.get("post_score") is not None:
            post_scores.append(l2["post_score"])
    l2_pre_avg = round(sum(pre_scores) / len(pre_scores), 1) if pre_scores else 0
    l2_post_avg = round(sum(post_scores) / len(post_scores), 1) if post_scores else 0
    l2_improvement = round(l2_post_avg - l2_pre_avg, 1)

    # Level 3 行为应用（每题1-5）
    l3_scores = {}
    for e in evaluations:
        for qid, val in e.get("level3", {}).items():
            l3_scores.setdefault(qid, []).append(val)
    l3_avg = {qid: round(sum(v) / len(v), 2) for qid, v in l3_scores.items()}
    l3_total = round(sum(l3_avg.values()) / len(l3_avg), 2) if l3_avg else 0

    # Level 4 ROI
    investments, benefits = [], []
    for e in evaluations:
        l4 = e.get("level4", {})
        inv = l4.get("L4M5", 0)
        ben = l4.get("L4M6", 0)
        if inv:
            investments.append(inv)
        if ben:
            benefits.append(ben)
    total_invest = sum(investments)
    total_benefit = sum(benefits)
    roi = round((total_benefit - total_invest) / total_invest * 100, 1) if total_invest else 0

    # 各业务指标平均
    l4_metrics = {}
    for e in evaluations:
        l4 = e.get("level4", {})
        for mid in ["L4M1", "L4M2", "L4M3", "L4M4"]:
            v = l4.get(mid)
            if v is not None:
                l4_metrics.setdefault(mid, []).append(v)
    l4_avg = {mid: round(sum(v) / len(v), 1) for mid, v in l4_metrics.items()}

    return {
        "total": n,
        "level1": {"avg_by_question": l1_avg, "total_avg": l1_total},
        "level2": {
            "pre_avg": l2_pre_avg,
            "post_avg": l2_post_avg,
            "improvement": l2_improvement,
        },
        "level3": {"avg_by_question": l3_avg, "total_avg": l3_total},
        "level4": {
            "metrics_avg": l4_avg,
            "total_invest": total_invest,
            "total_benefit": total_benefit,
            "roi": roi,
        },
    }


def export_csv(filepath: str):
    """导出所有评估数据为CSV"""
    evals = get_all_evaluations()
    if not evals:
        return False
    rows = []
    for e in evals:
        row = {
            "记录ID": e.get("id", ""),
            "填写时间": e.get("created_at", ""),
            "课程名称": e.get("course_name", ""),
            "部门": e.get("department", ""),
            "培训日期": e.get("train_date", ""),
            "学员姓名": e.get("trainee_name", "（匿名）"),
            "L1反应层均分": e.get("level1_avg", ""),
            "L2前测得分": e.get("level2", {}).get("pre_score", ""),
            "L2后测得分": e.get("level2", {}).get("post_score", ""),
            "L3行为层均分": e.get("level3_avg", ""),
            "L4投入(元)": e.get("level4", {}).get("L4M5", ""),
            "L4收益(元)": e.get("level4", {}).get("L4M6", ""),
        }
        rows.append(row)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return True
