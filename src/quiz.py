import json
import os
import random
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
# 修复：使用 ttkbootstrap 最新的 ScrolledText 导入路径
from ttkbootstrap.widgets.scrolled import ScrolledText

def resource_path(relative_path):
    """ 获取资源绝对路径，适配 PyInstaller 的临时目录 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MaoGaiQuiz:
    """逻辑处理类：负责数据加载、保存、搜索和答案格式化"""

    def __init__(self, data_path='maogai_data.json', mistake_path='mistakes.json'):
        # 使用 resource_path 处理题库文件（它是只读的，打包在exe内部）
        self.data_path = resource_path(data_path)
        # 错题本文件建议保留在 exe 同级目录（它是要写的），不需要用 resource_path
        self.mistake_path = mistake_path
        self.questions = self._load_json(self.data_path)
        self.mistakes = self._load_json(self.mistake_path)

    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_mistakes(self):
        with open(self.mistake_path, 'w', encoding='utf-8') as f:
            json.dump(self.mistakes, f, ensure_ascii=False, indent=4)

    def format_input(self, s):
        """处理用户输入：去重、转大写、排序（解决多选顺序不同导致的误判）"""
        return "".join(sorted(list(set(s.upper().strip()))))

    def search_questions(self, keyword):
        """根据关键词在题干、选项和解析中进行模糊搜索"""
        if not keyword: return []
        results = []
        for q in self.questions:
            content = q['question'] + "".join(q['options']) + q['analysis']
            if keyword.lower() in content.lower():
                results.append(q)
        return results


class ModernQuizGUI:
    def __init__(self, root):
        self.logic = MaoGaiQuiz()
        self.root = root
        self.root.title("毛概智能刷题系统 - 终极美化版")
        self.root.geometry("900x800")

        # 设置现代深色主题
        self.style = ttk.Style(theme='superhero')

        self.current_q_list = []
        self.current_idx = 0
        self.score = 0

        self.setup_menu()

    def clear_frame(self):
        """清空当前窗口的所有组件，用于切换界面"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_menu(self):
        """主菜单界面"""
        self.clear_frame()
        main_frame = ttk.Frame(self.root, padding=50)
        main_frame.pack(expand=True, fill=BOTH)

        ttk.Label(main_frame, text="毛概智能刷题系统", font=("微软雅黑", 28, "bold"), bootstyle=INFO).pack(pady=20)

        # 数据统计卡片
        stats_frame = ttk.Labelframe(main_frame, text="题库概览", padding=20)
        stats_frame.pack(fill=X, pady=10)
        ttk.Label(stats_frame, text=f"📚 总题数: {len(self.logic.questions)}").pack(side=LEFT, padx=30)
        ttk.Label(stats_frame, text=f"❌ 错题本: {len(self.logic.mistakes)}", bootstyle=DANGER).pack(side=RIGHT, padx=30)

        # 按钮网格
        btn_grid = ttk.Frame(main_frame)
        btn_grid.pack(pady=20)

        ttk.Button(btn_grid, text="🔍 搜索与查题", command=self.show_search_view, width=22, bootstyle=INFO).grid(row=0,
                                                                                                                column=0,
                                                                                                                padx=10,
                                                                                                                pady=10)
        ttk.Button(btn_grid, text="📝 顺序刷题", command=lambda: self.start_quiz(self.logic.questions), width=22,
                   bootstyle=PRIMARY).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(btn_grid, text="🎲 随机乱序",
                   command=lambda: self.start_quiz(random.sample(self.logic.questions, len(self.logic.questions))),
                   width=22, bootstyle=SUCCESS).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(btn_grid, text="📖 错题复习", command=lambda: self.start_quiz(self.logic.mistakes), width=22,
                   bootstyle=WARNING).grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(main_frame, text="清空错题本", command=self.clear_mistakes, width=48,
                   bootstyle="outline-danger").pack(pady=10)

    def show_search_view(self):
        """查题搜索界面"""
        self.clear_frame()
        search_frame = ttk.Frame(self.root, padding=30)
        search_frame.pack(fill=BOTH, expand=True)

        top_bar = ttk.Frame(search_frame)
        top_bar.pack(fill=X, pady=10)

        ttk.Label(top_bar, text="关键词:").pack(side=LEFT, padx=5)
        search_entry = ttk.Entry(top_bar, font=("微软雅黑", 12))
        search_entry.pack(side=LEFT, fill=X, expand=True, padx=5)

        # 结果列表表格
        columns = ("ID", "类型", "题干预览")
        # selectmode='extended' 允许用户按住 Ctrl/Shift 进行多选
        tree = ttk.Treeview(search_frame, columns=columns, show='headings', height=15, selectmode='extended')
        tree.heading("ID", text="ID")
        tree.heading("类型", text="类型")
        tree.heading("题干预览", text="题干预览")
        tree.column("ID", width=60, anchor=CENTER)
        tree.column("类型", width=80, anchor=CENTER)
        tree.column("题干预览", width=650)
        tree.pack(fill=BOTH, expand=True, pady=10)

        def run_search(event=None):
            word = search_entry.get()
            results = self.logic.search_questions(word)
            for item in tree.get_children(): tree.delete(item)
            for q in results:
                tree.insert('', END, values=(q['id'], q['type'], q['question'][:50] + "..."))

        ttk.Button(top_bar, text="搜索", command=run_search, bootstyle=INFO).pack(side=LEFT, padx=5)
        search_entry.bind("<Return>", run_search)

        # 底部按钮栏
        btn_bar = ttk.Frame(search_frame)
        btn_bar.pack(fill=X)

        def view_selected():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning("提示", "请先选中至少一道题！")
                return

            # 批量提取选中题目的 ID
            selected_ids = [tree.item(item)['values'][0] for item in selected_items]
            practice_list = [q for q in self.logic.questions if q['id'] in selected_ids]
            self.start_quiz(practice_list)

        ttk.Label(search_frame, text="* 提示：按住 Ctrl 或 Shift 键可一次性选择多道题进行练习", font=("微软雅黑", 9),
                  foreground="gray").pack(side=LEFT)
        ttk.Button(btn_bar, text="练习选中题目", command=view_selected, bootstyle=SUCCESS).pack(side=RIGHT, padx=5)
        ttk.Button(btn_bar, text="返回主菜单", command=self.setup_menu, bootstyle=SECONDARY).pack(side=RIGHT, padx=5)

    def start_quiz(self, q_list):
        """开始练习逻辑"""
        if not q_list:
            messagebox.showwarning("提示", "练习列表为空！")
            return
        self.current_q_list = q_list
        self.current_idx = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        """显示题目页面（核心：单多选自动切换逻辑）"""
        self.clear_frame()
        q = self.current_q_list[self.current_idx]

        # 顶部进度条
        progress_frame = ttk.Frame(self.root, padding=10)
        progress_frame.pack(fill=X)
        current_progress = ((self.current_idx + 1) / len(self.current_q_list)) * 100
        ttk.Progressbar(progress_frame, value=current_progress, bootstyle=INFO).pack(fill=X, pady=5)
        ttk.Label(progress_frame, text=f"第 {self.current_idx + 1} 题 / 共 {len(self.current_q_list)} 题").pack()

        # 题干区域
        q_card = ttk.Labelframe(self.root, text=f"[{q['type']}] - ID: {q['id']}", padding=20)
        q_card.pack(fill=BOTH, expand=True, padx=30, pady=10)

        q_display = ScrolledText(q_card, height=6, font=("微软雅黑", 12), autohide=True)
        q_display.pack(fill=BOTH, expand=True)
        q_display.insert(END, q['question'])
        # 修复：必须访问 .text 属性来设置 DISABLED，否则会报 TclError
        q_display.text.configure(state=DISABLED)

        # 选项区域：根据题目类型动态生成组件
        opts_frame = ttk.Frame(self.root, padding=20)
        opts_frame.pack(fill=X, padx=50)

        is_single = (q['type'] == "单选")

        if is_single:
            # 单选题：使用 Radiobutton，绑定同一个 StringVar 实现物理互斥（禁止多选）
            self.single_var = ttk.StringVar()
            for opt in q['options']:
                opt_code = opt[0].upper()
                ttk.Radiobutton(opts_frame, text=opt, variable=self.single_var,
                                value=opt_code, bootstyle="toolbutton-info", padding=10).pack(fill=X, pady=5)
        else:
            # 多选题：使用 Checkbutton，每个选项独立
            self.check_vars = {}
            for opt in q['options']:
                opt_code = opt[0].upper()
                var = ttk.BooleanVar()
                self.check_vars[opt_code] = var
                ttk.Checkbutton(opts_frame, text=opt, variable=var,
                                bootstyle="toolbutton-info", padding=10).pack(fill=X, pady=5)

        # 操作栏
        bottom_frame = ttk.Frame(self.root, padding=20)
        bottom_frame.pack(fill=X)
        ttk.Button(bottom_frame, text="提交答案", command=self.check_answer, width=15, bootstyle=SUCCESS).pack(
            side=RIGHT, padx=10)
        ttk.Button(bottom_frame, text="退出练习", command=self.setup_menu, width=15, bootstyle=SECONDARY).pack(
            side=RIGHT)

    def check_answer(self):
        """判定答案"""
        q = self.current_q_list[self.current_idx]

        # 根据题目类型获取答案
        if q['type'] == "单选":
            u_ans = self.single_var.get()
        else:
            user_ans_list = [code for code, var in self.check_vars.items() if var.get()]
            u_ans = self.logic.format_input("".join(user_ans_list))

        if not u_ans:
            messagebox.showwarning("提示", "请先选择答案！")
            return

        c_ans = self.logic.format_input(q['answer'])
        is_correct = (u_ans == c_ans)

        result_title = "✅ 正确" if is_correct else "❌ 错误"
        result_msg = f"正确答案: {q['answer']}\n\n解析: {q['analysis']}"

        if is_correct:
            self.score += 1
        else:
            if q['id'] not in [m['id'] for m in self.logic.mistakes]:
                self.logic.mistakes.append(q)
                self.logic._save_mistakes()

        messagebox.showinfo(result_title, result_msg)

        # 翻页
        self.current_idx += 1
        if self.current_idx < len(self.current_q_list):
            self.show_question()
        else:
            messagebox.showinfo("结束", f"练习结束！\n本次得分: {self.score}/{len(self.current_q_list)}")
            self.setup_menu()

    def clear_mistakes(self):
        """清空错题本"""
        if messagebox.askyesno("确认", "确定清空所有错题记录吗？"):
            self.logic.mistakes = []
            self.logic._save_mistakes()
            self.setup_menu()


if __name__ == "__main__":
    # 初始化主题窗口
    root = ttk.Window(themename="superhero")
    app = ModernQuizGUI(root)
    root.mainloop()