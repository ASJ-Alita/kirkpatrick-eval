# -*- coding: utf-8 -*-
"""
柯氏四级培训评估系统 - 主界面
Kirkpatrick Four-Level Training Evaluation System
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import webbrowser
from datetime import datetime

# 将项目根目录加入path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.config import (
    LEVEL1_QUESTIONS, LEVEL1_SCALE,
    LEVEL2_QUESTIONS,
    LEVEL3_QUESTIONS, LEVEL3_SCALE,
    LEVEL4_METRICS, COURSE_TEMPLATES, DEPARTMENT_LIST
)
from data.manager import save_evaluation, get_all_evaluations, delete_evaluation, clear_all, calc_stats, export_csv
from report import generate_report

# ── 主题色 ─────────────────────────────────────────────────────────────────────
BG = "#f0f2f5"
WHITE = "#ffffff"
PRIMARY = "#1a237e"
L1_COLOR = "#3498db"
L2_COLOR = "#2ecc71"
L3_COLOR = "#f39c12"
L4_COLOR = "#9b59b6"
TEXT = "#2c3e50"
GRAY = "#95a5a6"
DANGER = "#e74c3c"
SUCCESS = "#27ae60"
FONT = ("PingFang SC", 11)
FONT_BOLD = ("PingFang SC", 11, "bold")
FONT_TITLE = ("PingFang SC", 14, "bold")
FONT_BIG = ("PingFang SC", 18, "bold")


class KirkpatrickApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🎓 柯氏四级培训评估系统")
        self.root.configure(bg=BG)
        self.root.geometry("920x720")
        self.root.minsize(860, 640)

        # 预测题得分暂存
        self._pre_score_var = tk.IntVar(value=0)
        self._post_score_var = tk.IntVar(value=0)
        self._pre_answered = []
        self._post_answered = []

        self._build_ui()

    # ─── UI构建 ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # 顶部标题栏
        header = tk.Frame(self.root, bg=PRIMARY, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="🎓  柯氏四级培训评估系统", font=("PingFang SC", 16, "bold"),
                 fg="white", bg=PRIMARY).pack(side=tk.LEFT, padx=24, pady=14)
        tk.Label(header, text="Kirkpatrick Four-Level Evaluation", font=("PingFang SC", 10),
                 fg="#90caf9", bg=PRIMARY).pack(side=tk.LEFT, pady=20)

        # Notebook
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", font=("PingFang SC", 11, "bold"),
                         padding=[18, 8], background="#dde3f0", foreground=TEXT)
        style.map("TNotebook.Tab",
                  background=[("selected", WHITE)],
                  foreground=[("selected", PRIMARY)])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=(12, 4))

        self.tab_form = tk.Frame(self.notebook, bg=BG)
        self.tab_data = tk.Frame(self.notebook, bg=BG)
        self.tab_report = tk.Frame(self.notebook, bg=BG)

        self.notebook.add(self.tab_form, text="📝 填写评估问卷")
        self.notebook.add(self.tab_data, text="📋 已收集数据")
        self.notebook.add(self.tab_report, text="📊 生成分析报告")

        self._build_form_tab()
        self._build_data_tab()
        self._build_report_tab()

    # ─── Tab1: 问卷表单 ──────────────────────────────────────────────────────

    def _build_form_tab(self):
        # 外层滚动区
        canvas = tk.Canvas(self.tab_form, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_form, orient="vertical", command=canvas.yview)
        self.form_frame = tk.Frame(canvas, bg=BG)
        self.form_frame.bind("<Configure>",
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        p = self.form_frame
        pad = {"padx": 24, "pady": 6}

        # ── 基本信息 ─────────────────────────────────
        self._section_header(p, "📌 基本信息", L1_COLOR)

        row0 = tk.Frame(p, bg=BG)
        row0.pack(fill=tk.X, **pad)
        tk.Label(row0, text="课程名称：", font=FONT_BOLD, bg=BG, fg=TEXT, width=10, anchor="e").pack(side=tk.LEFT)
        self.course_var = tk.StringVar(value=COURSE_TEMPLATES[0])
        ttk.Combobox(row0, textvariable=self.course_var, values=COURSE_TEMPLATES,
                     font=FONT, width=22).pack(side=tk.LEFT, padx=6)
        tk.Label(row0, text="部门：", font=FONT_BOLD, bg=BG, fg=TEXT, width=6, anchor="e").pack(side=tk.LEFT, padx=(20,0))
        self.dept_var = tk.StringVar(value=DEPARTMENT_LIST[0])
        ttk.Combobox(row0, textvariable=self.dept_var, values=DEPARTMENT_LIST,
                     font=FONT, width=14).pack(side=tk.LEFT, padx=6)

        row1 = tk.Frame(p, bg=BG)
        row1.pack(fill=tk.X, **pad)
        tk.Label(row1, text="培训日期：", font=FONT_BOLD, bg=BG, fg=TEXT, width=10, anchor="e").pack(side=tk.LEFT)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(row1, textvariable=self.date_var, font=FONT, width=14).pack(side=tk.LEFT, padx=6)
        tk.Label(row1, text="姓名（可匿名）：", font=FONT_BOLD, bg=BG, fg=TEXT, width=14, anchor="e").pack(side=tk.LEFT, padx=(20,0))
        self.name_var = tk.StringVar(value="匿名")
        tk.Entry(row1, textvariable=self.name_var, font=FONT, width=14).pack(side=tk.LEFT, padx=6)

        # ── Level 1 反应层 ────────────────────────────
        self._section_header(p, "Level 1 · 反应层  —  培训结束后填写", L1_COLOR)
        tk.Label(p, text="请为以下各项评分（1=非常不同意  5=非常同意）",
                 font=("PingFang SC", 10), fg=GRAY, bg=BG).pack(anchor="w", padx=28, pady=(0, 6))

        self.l1_vars = {}
        for q in LEVEL1_QUESTIONS:
            self.l1_vars[q["id"]] = self._rating_row(p, q["text"], max_val=5, color=L1_COLOR)

        # ── Level 2 学习层 ────────────────────────────
        self._section_header(p, "Level 2 · 学习层  —  前测 & 后测", L2_COLOR)

        sub_frame = tk.Frame(p, bg=BG)
        sub_frame.pack(fill=tk.X, padx=28, pady=4)

        # 前测按钮
        tk.Button(sub_frame, text="▶ 开始前测（培训前）", font=FONT_BOLD,
                  bg=L2_COLOR, fg="white", relief="flat", bd=0, padx=12, pady=6,
                  cursor="hand2",
                  command=lambda: self._run_quiz("pre")).pack(side=tk.LEFT, padx=(0, 12))

        # 后测按钮
        tk.Button(sub_frame, text="▶ 开始后测（培训后）", font=FONT_BOLD,
                  bg="#27ae60", fg="white", relief="flat", bd=0, padx=12, pady=6,
                  cursor="hand2",
                  command=lambda: self._run_quiz("post")).pack(side=tk.LEFT, padx=(0, 20))

        # 得分显示
        self.l2_pre_label = tk.Label(sub_frame, text="前测：未完成", font=FONT, fg=GRAY, bg=BG)
        self.l2_pre_label.pack(side=tk.LEFT, padx=6)
        self.l2_post_label = tk.Label(sub_frame, text="后测：未完成", font=FONT, fg=GRAY, bg=BG)
        self.l2_post_label.pack(side=tk.LEFT, padx=6)

        # ── Level 3 行为层 ────────────────────────────
        self._section_header(p, "Level 3 · 行为层  —  培训结束30天后填写", L3_COLOR)
        tk.Label(p, text="请评估培训内容在实际工作中的应用情况（1=完全没有  5=总是）",
                 font=("PingFang SC", 10), fg=GRAY, bg=BG).pack(anchor="w", padx=28, pady=(0, 6))

        self.l3_vars = {}
        for q in LEVEL3_QUESTIONS:
            self.l3_vars[q["id"]] = self._rating_row(p, q["text"], max_val=5, color=L3_COLOR)

        # ── Level 4 结果层 ────────────────────────────
        self._section_header(p, "Level 4 · 结果层  —  培训完成后业务指标变化", L4_COLOR)
        tk.Label(p, text="请填写培训前后的业务指标变化（%），以及培训总投入与估算收益",
                 font=("PingFang SC", 10), fg=GRAY, bg=BG).pack(anchor="w", padx=28, pady=(0, 6))

        self.l4_vars = {}
        for m in LEVEL4_METRICS:
            self.l4_vars[m["id"]] = self._metric_row(p, m["text"], m["unit"])

        # ── 提交按钮 ──────────────────────────────────
        btn_frame = tk.Frame(p, bg=BG)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="✅  提交评估数据", font=("PingFang SC", 13, "bold"),
                  bg=PRIMARY, fg="white", relief="flat", bd=0,
                  padx=32, pady=10, cursor="hand2",
                  command=self._submit).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="🔄 重置表单", font=FONT,
                  bg=GRAY, fg="white", relief="flat", bd=0,
                  padx=16, pady=10, cursor="hand2",
                  command=self._reset_form).pack(side=tk.LEFT, padx=10)

    def _section_header(self, parent, title: str, color: str):
        f = tk.Frame(parent, bg=color, height=36)
        f.pack(fill=tk.X, padx=16, pady=(14, 4))
        f.pack_propagate(False)
        tk.Label(f, text=title, font=FONT_BOLD, fg="white", bg=color).pack(
            side=tk.LEFT, padx=16, pady=6)

    def _rating_row(self, parent, text: str, max_val: int, color: str) -> tk.IntVar:
        f = tk.Frame(parent, bg=WHITE, pady=6)
        f.pack(fill=tk.X, padx=28, pady=2)
        tk.Label(f, text=text, font=FONT, bg=WHITE, fg=TEXT,
                 wraplength=440, justify="left", width=38, anchor="w").pack(side=tk.LEFT, padx=8)
        var = tk.IntVar(value=3)
        for i in range(1, max_val + 1):
            tk.Radiobutton(f, text=str(i), variable=var, value=i,
                           font=("PingFang SC", 10), bg=WHITE,
                           activebackground=WHITE, fg=color,
                           selectcolor=WHITE).pack(side=tk.LEFT, padx=6)
        return var

    def _metric_row(self, parent, text: str, unit: str) -> tk.StringVar:
        f = tk.Frame(parent, bg=WHITE, pady=6)
        f.pack(fill=tk.X, padx=28, pady=2)
        tk.Label(f, text=text, font=FONT, bg=WHITE, fg=TEXT,
                 wraplength=440, width=38, anchor="w").pack(side=tk.LEFT, padx=8)
        var = tk.StringVar(value="0")
        tk.Entry(f, textvariable=var, font=FONT, width=10).pack(side=tk.LEFT, padx=6)
        tk.Label(f, text=unit, font=FONT, fg=GRAY, bg=WHITE).pack(side=tk.LEFT)
        return var

    # ─── 前/后测答题窗口 ─────────────────────────────────────────────────────

    def _run_quiz(self, mode: str):
        title = "📝 前测题目（培训前）" if mode == "pre" else "📝 后测题目（培训后）"
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("640x500")
        win.configure(bg=BG)
        win.grab_set()

        tk.Label(win, text=title, font=FONT_TITLE, fg=PRIMARY, bg=BG).pack(pady=14)

        answers = {}
        correct_answers = {q["id"]: q["answer"] for q in LEVEL2_QUESTIONS}

        scroll_frame = tk.Frame(win, bg=BG)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        for q in LEVEL2_QUESTIONS:
            qf = tk.Frame(scroll_frame, bg=WHITE, pady=8, padx=10,
                          relief="solid", bd=1)
            qf.pack(fill=tk.X, pady=6)
            tk.Label(qf, text=q["text"], font=FONT_BOLD, fg=TEXT,
                     bg=WHITE, wraplength=540, justify="left").pack(anchor="w", pady=(4, 6))
            var = tk.StringVar()
            answers[q["id"]] = var
            for opt in q["options"]:
                tk.Radiobutton(qf, text=opt, variable=var, value=opt[0],
                               font=FONT, bg=WHITE, activebackground=WHITE).pack(anchor="w", padx=10)

        def submit_quiz():
            score = sum(1 for qid, var in answers.items()
                        if var.get() == correct_answers.get(qid))
            pct = round(score / len(LEVEL2_QUESTIONS) * 100, 1)
            win.destroy()
            if mode == "pre":
                self._pre_score_var.set(pct)
                self.l2_pre_label.config(
                    text=f"前测：{score}/{len(LEVEL2_QUESTIONS)}题  ({pct}%)",
                    fg=L2_COLOR, font=FONT_BOLD)
            else:
                self._post_score_var.set(pct)
                self.l2_post_label.config(
                    text=f"后测：{score}/{len(LEVEL2_QUESTIONS)}题  ({pct}%)",
                    fg=SUCCESS, font=FONT_BOLD)
            messagebox.showinfo("答题完成",
                                f"{'前测' if mode=='pre' else '后测'}得分：{pct}%\n({score}/{len(LEVEL2_QUESTIONS)} 题正确)")

        tk.Button(win, text="✅ 提交答案", font=FONT_BOLD,
                  bg=L2_COLOR, fg="white", relief="flat", bd=0,
                  padx=20, pady=8, cursor="hand2",
                  command=submit_quiz).pack(pady=12)

    # ─── 提交表单 ────────────────────────────────────────────────────────────

    def _submit(self):
        # 计算L1均分
        l1_vals = {qid: var.get() for qid, var in self.l1_vars.items()}
        l1_avg = round(sum(l1_vals.values()) / len(l1_vals), 2)

        # L2
        l2_data = {
            "pre_score": self._pre_score_var.get(),
            "post_score": self._post_score_var.get(),
        }

        # 计算L3均分
        l3_vals = {qid: var.get() for qid, var in self.l3_vars.items()}
        l3_avg = round(sum(l3_vals.values()) / len(l3_vals), 2)

        # L4 数值转换
        l4_data = {}
        for mid, var in self.l4_vars.items():
            try:
                l4_data[mid] = float(var.get())
            except ValueError:
                l4_data[mid] = 0.0

        record = {
            "course_name": self.course_var.get(),
            "department": self.dept_var.get(),
            "train_date": self.date_var.get(),
            "trainee_name": self.name_var.get() or "匿名",
            "level1": l1_vals,
            "level1_avg": l1_avg,
            "level2": l2_data,
            "level3": l3_vals,
            "level3_avg": l3_avg,
            "level4": l4_data,
        }

        record_id = save_evaluation(record)
        messagebox.showinfo("提交成功",
                            f"✅ 评估数据已保存！\n记录ID：{record_id}\n"
                            f"\n  反应层均分：{l1_avg}/5"
                            f"\n  学习层进步：{round(l2_data['post_score'] - l2_data['pre_score'], 1)}%"
                            f"\n  行为层均分：{l3_avg}/5")
        self._refresh_data_tab()

    def _reset_form(self):
        if messagebox.askyesno("重置确认", "确定要清空所有填写内容吗？"):
            for var in self.l1_vars.values():
                var.set(3)
            self._pre_score_var.set(0)
            self._post_score_var.set(0)
            self.l2_pre_label.config(text="前测：未完成", fg=GRAY)
            self.l2_post_label.config(text="后测：未完成", fg=GRAY)
            for var in self.l3_vars.values():
                var.set(3)
            for var in self.l4_vars.values():
                var.set("0")

    # ─── Tab2: 数据列表 ──────────────────────────────────────────────────────

    def _build_data_tab(self):
        toolbar = tk.Frame(self.tab_data, bg=BG)
        toolbar.pack(fill=tk.X, padx=16, pady=10)
        tk.Button(toolbar, text="🔄 刷新", font=FONT, bg=PRIMARY, fg="white",
                  relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
                  command=self._refresh_data_tab).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(toolbar, text="📤 导出CSV", font=FONT, bg=L2_COLOR, fg="white",
                  relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
                  command=self._export_csv).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(toolbar, text="🗑️ 删除选中", font=FONT, bg=DANGER, fg="white",
                  relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
                  command=self._delete_selected).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(toolbar, text="⚠️ 清空所有", font=FONT, bg="#c0392b", fg="white",
                  relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
                  command=self._clear_all).pack(side=tk.LEFT)

        self.count_label = tk.Label(toolbar, text="共 0 条记录",
                                    font=FONT, fg=GRAY, bg=BG)
        self.count_label.pack(side=tk.RIGHT, padx=16)

        cols = ("记录ID", "课程名称", "部门", "培训日期", "L1均分", "L2前测%", "L2后测%", "L3均分")
        self.tree = ttk.Treeview(self.tab_data, columns=cols, show="headings", selectmode="browse")
        col_widths = [110, 160, 110, 100, 70, 75, 75, 70]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(self.tab_data, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0), pady=4)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=4)

        self._refresh_data_tab()

    def _refresh_data_tab(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        evals = get_all_evaluations()
        self.count_label.config(text=f"共 {len(evals)} 条记录")
        for e in reversed(evals):
            l2 = e.get("level2", {})
            self.tree.insert("", "end", iid=e["id"], values=(
                e.get("id", ""),
                e.get("course_name", ""),
                e.get("department", ""),
                e.get("train_date", ""),
                e.get("level1_avg", ""),
                l2.get("pre_score", ""),
                l2.get("post_score", ""),
                e.get("level3_avg", ""),
            ))

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV文件", "*.csv")],
            initialfile=f"kirkpatrick_data_{datetime.now().strftime('%Y%m%d')}.csv")
        if path:
            if export_csv(path):
                messagebox.showinfo("导出成功", f"✅ 数据已导出到：\n{path}")
            else:
                messagebox.showwarning("暂无数据", "还没有评估数据，请先填写问卷。")

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先选中要删除的记录")
            return
        if messagebox.askyesno("确认删除", f"确定要删除记录 {sel[0]} 吗？"):
            delete_evaluation(sel[0])
            self._refresh_data_tab()

    def _clear_all(self):
        if messagebox.askyesno("危险操作", "⚠️ 确定要清空所有评估数据吗？此操作不可恢复！"):
            clear_all()
            self._refresh_data_tab()

    # ─── Tab3: 报告生成 ──────────────────────────────────────────────────────

    def _build_report_tab(self):
        # 顶部说明卡片
        info_card = tk.Frame(self.tab_report, bg=WHITE, pady=20)
        info_card.pack(fill=tk.X, padx=20, pady=(16, 8))

        tk.Label(info_card, text="📊 智能分析报告", font=FONT_BIG,
                 fg=PRIMARY, bg=WHITE).pack()
        tk.Label(info_card, text="基于收集的评估数据，自动生成包含四级雷达图、前后测对比、ROI分析的HTML报告",
                 font=("PingFang SC", 11), fg=GRAY, bg=WHITE).pack(pady=6)

        # 统计概览
        self.stats_frame = tk.Frame(self.tab_report, bg=BG)
        self.stats_frame.pack(fill=tk.X, padx=20, pady=8)
        self._refresh_stats()

        # 按钮区
        btn_area = tk.Frame(self.tab_report, bg=BG)
        btn_area.pack(pady=20)

        tk.Button(btn_area, text="🔄 刷新统计", font=FONT, bg=GRAY, fg="white",
                  relief="flat", bd=0, padx=16, pady=10, cursor="hand2",
                  command=self._refresh_stats).pack(side=tk.LEFT, padx=8)

        tk.Button(btn_area, text="📊  生成并打开分析报告", font=("PingFang SC", 13, "bold"),
                  bg=PRIMARY, fg="white", relief="flat", bd=0,
                  padx=28, pady=12, cursor="hand2",
                  command=self._gen_report).pack(side=tk.LEFT, padx=8)

        # 演示数据按钮
        tk.Button(btn_area, text="🎭 注入演示数据", font=FONT, bg=L4_COLOR, fg="white",
                  relief="flat", bd=0, padx=16, pady=10, cursor="hand2",
                  command=self._inject_demo).pack(side=tk.LEFT, padx=8)

        # 最近生成的报告列表
        self.report_label = tk.Label(self.tab_report,
                                     text="", font=("PingFang SC", 10), fg=GRAY, bg=BG)
        self.report_label.pack()

    def _refresh_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        evals = get_all_evaluations()
        stats = calc_stats(evals)

        cards = [
            ("L1反应层", f"{stats.get('level1', {}).get('total_avg', '—')}/5", L1_COLOR),
            ("L2学习进步", f"+{stats.get('level2', {}).get('improvement', '—')}%", L2_COLOR),
            ("L3行为层", f"{stats.get('level3', {}).get('total_avg', '—')}/5", L3_COLOR),
            ("ROI", f"{stats.get('level4', {}).get('roi', '—')}%", L4_COLOR),
            ("参与人数", str(stats.get("total", 0)) + " 人", PRIMARY),
        ]
        for label, val, color in cards:
            c = tk.Frame(self.stats_frame, bg=WHITE, pady=14, padx=14,
                         relief="solid", bd=0, width=140)
            c.pack(side=tk.LEFT, padx=8, pady=4)
            c.pack_propagate(False)
            tk.Label(c, text=label, font=("PingFang SC", 10), fg=GRAY, bg=WHITE).pack()
            tk.Label(c, text=val, font=("PingFang SC", 20, "bold"),
                     fg=color, bg=WHITE).pack()
            tk.Frame(c, bg=color, height=3).pack(fill=tk.X, pady=(6, 0))

    def _gen_report(self):
        evals = get_all_evaluations()
        if not evals:
            messagebox.showwarning("暂无数据", "还没有评估数据！\n请先填写问卷，或点击「注入演示数据」查看效果。")
            return
        stats = calc_stats(evals)
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
        path = generate_report(stats, evals, reports_dir)
        if path:
            webbrowser.open(f"file://{path}")
            self.report_label.config(
                text=f"✅ 报告已生成：{os.path.basename(path)}", fg=SUCCESS)
        else:
            messagebox.showerror("生成失败", "报告生成失败，请检查数据。")

    def _inject_demo(self):
        """注入演示数据（8条记录）"""
        import random
        courses = ["管理技能提升培训", "Python/AI技术培训", "沟通表达培训", "销售技巧培训"]
        depts = ["人力资源部", "技术研发部", "销售部", "市场营销部"]
        for i in range(8):
            l1_vals = {q["id"]: random.randint(3, 5) for q in LEVEL1_QUESTIONS}
            l3_vals = {q["id"]: random.randint(2, 5) for q in LEVEL3_QUESTIONS}
            record = {
                "course_name": random.choice(courses),
                "department": random.choice(depts),
                "train_date": f"2026-04-{random.randint(10, 22):02d}",
                "trainee_name": f"学员{i+1:02d}",
                "level1": l1_vals,
                "level1_avg": round(sum(l1_vals.values()) / len(l1_vals), 2),
                "level2": {
                    "pre_score": random.randint(40, 65),
                    "post_score": random.randint(70, 95),
                },
                "level3": l3_vals,
                "level3_avg": round(sum(l3_vals.values()) / len(l3_vals), 2),
                "level4": {
                    "L4M1": round(random.uniform(8, 20), 1),
                    "L4M2": round(random.uniform(10, 25), 1),
                    "L4M3": round(random.uniform(15, 30), 1),
                    "L4M4": round(random.uniform(3, 8), 1),
                    "L4M5": random.randint(20000, 80000),
                    "L4M6": random.randint(50000, 200000),
                },
            }
            save_evaluation(record)

        messagebox.showinfo("演示数据注入完成", "✅ 已注入8条演示数据！\n现在可以点击「生成并打开分析报告」查看效果。")
        self._refresh_stats()
        self._refresh_data_tab()


# ─── 入口 ──────────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    app = KirkpatrickApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
