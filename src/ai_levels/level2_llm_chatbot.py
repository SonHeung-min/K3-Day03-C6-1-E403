"""
CẤP ĐỘ 2: LLM CHATBOT
Chatbot baseline tư vấn tình cảm chung, không gọi tool và không tra hồ sơ.
"""

import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


CHATBOT_BASELINE_PROMPT = """Bạn là Cupid Chatbot. Hãy tư vấn giao tiếp/hẹn hò ở mức chung,
không giả vờ đã tra hồ sơ hoặc tính điểm tương thích."""


def llm_chatbot(user_input: str) -> str:
    text = user_input.lower()
    if "tìm" in text or "tương thích" in text or "hồ sơ" in text or "hợp nhau" in text:
        return (
            "🤖 [Cupid Chatbot]: Tôi chưa có quyền gọi tool tra hồ sơ, nên không thể kết luận có căn cứ. "
            "Bạn nên dùng Cupid ReAct Agent cho yêu cầu này."
        )
    return f"🤖 [Cupid Chatbot]: Đây là lời khuyên chung cho câu hỏi: '{user_input}'."


if __name__ == "__main__":
    print("=== DEMO CẤP ĐỘ 2: CUPID CHATBOT BASELINE ===")
    q = "An và Linh có hợp nhau không?"
    print(f"User: {q}")
    print(f"Bot : {llm_chatbot(q)}")
