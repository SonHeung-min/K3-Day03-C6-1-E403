"""
CẤP ĐỘ 3: REACTIVE AGENT
Minh họa Cupid ReAct Agent với chuỗi Thought -> Action -> Observation.
"""

import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def analyze_compatibility(person_a: str, person_b: str) -> str:
    return f"Độ tương thích ước tính giữa {person_a} và {person_b}: 68/100; có chung lối sống năng động."


def suggest_conversation_topics(person_a: str, person_b: str) -> str:
    return f"Chủ đề cho {person_a} và {person_b}: sở thích cuối tuần, đi bộ, cân bằng công việc-cuộc sống."


def reactive_agent_step(user_goal: str):
    print(f"🎯 Goal: {user_goal}")

    print("\n🧠 [Thought 1]: Cần phân tích độ tương thích dựa trên hồ sơ.")
    print("🛠️ [Action 1] : analyze_compatibility('An', 'Linh')")
    obs1 = analyze_compatibility("An", "Linh")
    print(f"👁️ [Observation 1]: {obs1}")

    print("\n🧠 [Thought 2]: Cần thêm chủ đề trò chuyện để câu trả lời hữu ích.")
    print("🛠️ [Action 2] : suggest_conversation_topics('An', 'Linh')")
    obs2 = suggest_conversation_topics("An", "Linh")
    print(f"👁️ [Observation 2]: {obs2}")

    print("\n🏁 [Final Answer]: An và Linh có nhiều điểm chung đủ để tìm hiểu thêm. Nên mở đầu bằng chủ đề sách khoa học viễn tưởng, cà phê cuối tuần hoặc một buổi đi bộ/nhà sách.")


if __name__ == "__main__":
    print("=== DEMO CẤP ĐỘ 3: CUPID REACT AGENT ===")
    reactive_agent_step("Phân tích An và Linh có hợp nhau không?")
