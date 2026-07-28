"""
CẤP ĐỘ 4: AUTONOMOUS AGENT
Minh họa Cupid Agent có planning và memory ở mức demo.
"""

import sys

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class AutonomousGoalAgent:
    def __init__(self, goal: str, max_steps: int = 4):
        self.goal = goal
        self.max_steps = max_steps
        self.memory = []

    def execute(self):
        print(f"🚀 === Bắt đầu Autonomous Goal: {self.goal} ===")

        plans = [
            ("Tìm hồ sơ phù hợp theo tiêu chí", "Call Tool: search_profiles(...)"),
            ("Phân tích độ tương thích", "Call Tool: analyze_compatibility(...)"),
            ("Kiểm tra dealbreaker", "Call Tool: check_dealbreakers(...)"),
            ("Gợi ý cách bắt chuyện", "Call Tool: suggest_conversation_topics(...)"),
        ]

        for step, (plan, action) in enumerate(plans[: self.max_steps], start=1):
            result = f"Hoàn thành bước {step}: {plan}"
            self.memory.append({"step": step, "plan": plan, "result": result})
            print(f"\n--- Planning Step {step}/{self.max_steps} ---")
            print(f"📋 [Planning]: {plan}")
            print(f"🛠️ [Execution]: {action}")
            print(f"💾 [Memory Saved]: {result}")

        print("\n🎯 [Goal Evaluation]: Đã có kế hoạch ghép đôi có căn cứ và không bịa dữ liệu.")


if __name__ == "__main__":
    agent = AutonomousGoalAgent("Tìm ứng viên phù hợp và gợi ý cách bắt chuyện an toàn")
    agent.execute()
