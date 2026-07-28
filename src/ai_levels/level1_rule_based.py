"""
CẤP ĐỘ 1: RULE-BASED BOT
Bot ghép đôi rất đơn giản, chỉ khớp keyword cố định và không dùng LLM/tool.
"""

import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def rule_based_bot(user_input: str) -> str:
    text = user_input.lower()
    if "chào" in text or "hi" in text or "hello" in text:
        return "Xin chào! Tôi là Cupid Rule-Based Bot. Tôi chỉ trả lời theo vài keyword cố định."
    if "icebreaker" in text or "mở đầu" in text:
        return "Bạn có thể bắt đầu bằng một câu hỏi nhẹ về sở thích trong bio."
    if "hợp nhau" in text or "tương thích" in text:
        return "Tôi chưa có tool phân tích hồ sơ, nên không thể chấm độ tương thích."
    if "riêng tư" in text or "theo dõi" in text:
        return "Tôi không hỗ trợ theo dõi hoặc xâm phạm quyền riêng tư."
    return "Xin lỗi, câu hỏi này nằm ngoài tập keyword được cài sẵn."


if __name__ == "__main__":
    print("=== DEMO CẤP ĐỘ 1: RULE-BASED CUPID BOT ===")
    for query in ["Chào bạn", "Gợi ý câu mở đầu", "An và Linh có hợp nhau không?"]:
        print(f"User: {query}")
        print(f"Bot : {rule_based_bot(query)}\n")
