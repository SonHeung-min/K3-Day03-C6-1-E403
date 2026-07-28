"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer / Integrator)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import re
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import (
    AVAILABLE_TOOLS,
    analyze_compatibility,
    suggest_date_idea,
    suggest_conversation_topics,
)
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()


def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")

    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}\n")

    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def parse_action(text: str):
    """
    Trích xuất tên tool và các tham số từ chuỗi 'Action: tool_name['arg1', 'arg2']'
    """
    pattern = r"Action:\s*([a-zA-Z0-9_]+)\[(.*?)\]"
    match = re.search(pattern, text)
    if not match:
        return None, []

    tool_name = match.group(1)
    raw_args = match.group(2)

    # Tách các tham số được bọc trong dấu ngoặc
    args = [
        arg.strip(" '\"")
        for arg in re.findall(
            r"'(?:\\'|[^'])*'|\"(?:\\\"|[^\"])*\"|[^,]+", raw_args
        )
        if arg.strip()
    ]
    return tool_name, args


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    step = 0
    history = f"User Query: {user_query}"

    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        # Gọi Provider với history
        response = provider.generate(history, system_prompt=REACT_SYSTEM_PROMPT)
        print(response)

        # Kiểm tra nếu Agent đã đưa ra câu trả lời cuối cùng
        if "Final Answer:" in response:
            print("\n✅ ReAct Agent đã hoàn thành suy luận.")
            return response

        # Kiểm tra xem Agent có gọi Tool (Action) hay không
        tool_name, args = parse_action(response)
        if tool_name:
            if tool_name in AVAILABLE_TOOLS:
                tool_func = AVAILABLE_TOOLS[tool_name]
                try:
                    observation = tool_func(*args)
                except Exception as e:
                    observation = f"LỖI THỰC THI TOOL: {str(e)}"
            else:
                observation = f"LỖI: Tool '{tool_name}' không tồn tại. Danh sách tool hợp lệ: {list(AVAILABLE_TOOLS.keys())}"

            obs_str = f"Observation: {observation}"
            print(f"👁️ {obs_str}")
            history += f"\n{response}\n{obs_str}"
        else:
            # Trường hợp không phát hiện Action hợp lệ và chưa có Final Answer
            history += (
                f"\n{response}\nObservation: Vui lòng đưa ra Action đúng cú pháp 'Action: tool_name['arg1', ...]' hoặc 'Final Answer: ...'"
            )

    if step >= MAX_ITERATIONS:
        print(
            f"\n🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!"
        )


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")

    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(
        f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})"
    )

    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")

    # Chạy thử câu test số 3 từ config/test_cases.json
    sample_query = tests[2]["question"]

    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    run_baseline_chatbot(sample_query, provider)

    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)

