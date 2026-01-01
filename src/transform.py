import json
import re
from docx import Document

def parse_maogai_docx(file_path, output_json):
    doc = Document(file_path)
    
    all_questions = []
    all_answers = []
    
    # 状态标记
    is_answer_section = False
    
    # 1. 遍历文档提取内容
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text or "共126题" in text or "共61题" in text: continue
        
        # 检测是否进入参考答案区域
        if "参考答案" in text or "一、单选题" in text and len(all_questions) > 0:
            is_answer_section = True
            continue

        if not is_answer_section:
            # 解析题目和行内选项
            # 正则：匹配题干 + A.选项 + B.选项 + C.选项 + D.选项
            parts = re.split(r'\s*([A-E]\s*[\.．])\s*', text)
            if len(parts) > 1:
                q_text = parts[0].strip()
                opts = []
                for i in range(1, len(parts), 2):
                    if i+1 < len(parts):
                        opts.append(f"{parts[i]}{parts[i+1]}".strip())
                
                all_questions.append({
                    "id": len(all_questions) + 1,
                    "question": q_text,
                    "options": opts,
                    "answer": "",
                    "analysis": ""
                })
        else:
            # 解析答案部分
            # 格式示例：B 。农民是中国革命的主力军 。
            ans_match = re.match(r'^([A-Z\s]+)[。\.．\s]+(.*)', text)
            if ans_match:
                all_answers.append({
                    "ans": ans_match.group(1).replace(" ", ""),
                    "ana": ans_match.group(2).strip()
                })

    # 2. 核心匹配逻辑：按顺序合并
    final_data = []
    for i in range(min(len(all_questions), len(all_answers))):
        q = all_questions[i]
        a = all_answers[i]
        q["answer"] = a["ans"]
        q["analysis"] = a["ana"]
        q["type"] = "单选" if len(a["ans"]) == 1 else "多选"
        final_data.append(q)

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    
    return len(final_data)

if __name__ == "__main__":
    count = parse_maogai_docx("毛概选择.docx", "maogai_data.json")
    print(f"✅ 处理完成！Dianana7mi，成功匹配了 {count} 道题目。")