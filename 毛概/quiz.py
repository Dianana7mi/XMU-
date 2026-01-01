import json
import os
import random

class MaoGaiQuiz:
    def __init__(self, data_path='maogai_data.json', mistake_path='mistakes.json'):
        self.data_path = data_path
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
        """处理用户输入：去空格、转大写、排序（解决多选顺序问题）"""
        return "".join(sorted(list(set(s.upper().strip()))))

    def play(self, q_list, mode_name="练习"):
        if not q_list:
            print(f"\n提示：{mode_name} 列表为空！")
            return

        score = 0
        total = len(q_list)
        print(f"\n>>> 开始 {mode_name} 模式 (输入 Q 退出)")

        for i, q in enumerate(q_list):
            print(f"\n【{i+1}/{total}】{q['question']}")
            for opt in q['options']:
                print(opt)
            
            user_input = input("\n请输入你的答案: ").strip()
            if user_input.upper() == 'Q': break

            # 核心判定逻辑
            u_ans = self.format_input(user_input)
            c_ans = self.format_input(q['answer'])

            if u_ans == c_ans:
                print("✅ 正确！")
                score += 1
            else:
                print(f"❌ 错误！正确答案是：{q['answer']}")
                # 错题收集：避免重复记录
                if q['id'] not in [m['id'] for m in self.mistakes]:
                    self.mistakes.append(q)
                    self._save_mistakes()

            print(f"【解析】：{q['analysis']}")
            print("-" * 30)

        print(f"\n{mode_name}结束！得分：{score}/{total}")
        input("按回车键返回主菜单...")

    def menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("="*40)
            print(f" 毛概刷题 By Dianana7mi and Gemini")
            print("="*40)
            print(f" 1. 顺序刷题 (总库: {len(self.questions)} 题)")
            print(f" 2. 随机乱序刷题")
            print(f" 3. 错题复习模式 (错题: {len(self.mistakes)} 题)")
            print(f" 4. 清空错题本")
            print(f" 5. 退出程序")
            print("="*40)
            
            choice = input("请选择 (1-5): ")
            if choice == '1':
                self.play(self.questions)
            elif choice == '2':
                random_qs = random.sample(self.questions, len(self.questions))
                self.play(random_qs, "随机练习")
            elif choice == '3':
                self.play(self.mistakes, "错题复习")
            elif choice == '4':
                self.mistakes = []
                self._save_mistakes()
                print("错题本已清空！")
                input()
            elif choice == '5':
                print("加油，祝你毛概高分过关！")
                break

if __name__ == "__main__":
    app = MaoGaiQuiz()
    app.menu()