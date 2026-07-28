"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer / Integrator)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
Hỗ trợ cả giao diện CLI Terminal (python src/app.py) và Giao diện Web Streamlit (streamlit run src/app.py).
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
    _load_mock_profiles,
)
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider, BaseLLMProvider

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


def run_baseline_chatbot(user_query: str, provider: BaseLLMProvider, show_prompt: bool = False):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ (Chỉ gọi API LLM).
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    if show_prompt:
        print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}\n")

    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def run_react_agent(user_query: str, provider: BaseLLMProvider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    step = 0
    history = f"User Query: {user_query}"
    react_steps = []

    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        # Gọi Provider với history
        response = provider.generate(history, system_prompt=REACT_SYSTEM_PROMPT) or ""
        print(response)

        # Kiểm tra nếu Agent đã đưa ra câu trả lời cuối cùng
        if "Final Answer:" in response:
            print("\n✅ ReAct Agent đã hoàn thành suy luận.")
            final_ans = response.split("Final Answer:")[-1].strip()
            thought_text = response.split("Final Answer:")[0].replace("Thought:", "").strip()
            react_steps.append({
                "step": step,
                "thought": thought_text,
                "action": None,
                "observation": None,
                "final_answer": final_ans
            })
            return response, react_steps

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

            thought_clean = response.replace(f"Action: {tool_name}[{', '.join(args)}]", "").replace("Thought:", "").strip()
            react_steps.append({
                "step": step,
                "thought": thought_clean,
                "action": f"{tool_name}[{', '.join([repr(a) for a in args])}]",
                "observation": observation,
                "final_answer": None
            })
        else:
            # Trường hợp không phát hiện Action hợp lệ và chưa có Final Answer
            history += (
                f"\n{response}\nObservation: Vui lòng đưa ra Action đúng cú pháp 'Action: tool_name['arg1', ...]' hoặc 'Final Answer: ...'"
            )
            react_steps.append({
                "step": step,
                "thought": response,
                "action": "Không nhận diện được Action",
                "observation": "Yêu cầu Agent định dạng lại cú pháp",
                "final_answer": None
            })

    if step >= MAX_ITERATIONS:
        fallback = (
            f"Thought: Tôi đã chạm giới hạn {MAX_ITERATIONS} bước nên cần dừng an toàn.\n"
            "Final Answer: Mình chưa có đủ bằng chứng để kết luận chắc chắn. "
            "Bạn có thể cung cấp thêm thông tin hoặc nới tiêu chí tìm kiếm để Cupid Agent phân tích tiếp."
        )
        print(f"\n🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")
        print(fallback)
        return fallback, react_steps
        
    return response, react_steps


def run_streamlit_gui():
    """Giao diện Web Streamlit trực tiếp trong app.py"""
    import streamlit as st

    st.set_page_config(
        page_title="Cupid Agent 💘 - Baseline vs Agentic",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ec4899, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
        }
        .sub-header {
            color: #6b7280;
            font-size: 1.05rem;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar Config
    st.sidebar.title("⚙️ Cấu hình Cupid App")

    chat_mode = st.sidebar.radio(
        "🎯 Chọn Chế độ Chat:",
        ["💬 Baseline Chatbot (Chỉ gọi API, không dùng Tool)", "🤖 Agentic ReAct (Có gọi Tools)"],
        index=1
    )
    is_agentic = "Agentic" in chat_mode

    provider_choice = st.sidebar.selectbox(
        "🔌 Chọn LLM Provider:",
        ["gemini", "openai", "anthropic", "openrouter", "mock"],
        index=0
    )
    os.environ["LLM_PROVIDER"] = provider_choice

    try:
        provider = get_llm_provider(provider_choice)
        model_name = getattr(provider, "model_name", "Default")
        st.sidebar.success(f"Active Provider: **{provider.__class__.__name__}** ({model_name})")
    except Exception as e:
        st.sidebar.error(f"Lỗi Provider: {e}")
        provider = get_llm_provider("mock")

    if is_agentic:
        st.sidebar.markdown("---")
        st.sidebar.markdown("🛠️ **Danh sách Tools khả dụng:**")
        for tname in AVAILABLE_TOOLS.keys():
            st.sidebar.markdown(f"- `{tname}`")

    if st.sidebar.button("🗑️ Xóa Lịch Sử Chat"):
        st.session_state.messages = []
        st.rerun()

    # Header
    st.markdown('<div class="main-header">💘 Cupid AI Chat App (Baseline vs Agentic)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Trợ lý ghép đôi AI (Lab 3: Baseline Chatbot vs ReAct Agent)</div>', unsafe_allow_html=True)

    if is_agentic:
        st.info("🤖 **Chế độ hiện tại: Agentic ReAct Agent** — Hệ thống có khả năng tự động gọi Tools để phân tích hồ sơ & tra cứu dữ liệu.")
    else:
        st.warning("💬 **Chế độ hiện tại: Baseline Chatbot** — Chỉ gọi API LLM tư vấn tổng quát, KHÔNG có khả năng sử dụng Tools.")

    # Target Profile Selector (Ngay phía trên khung Chat)
    profiles = _load_mock_profiles()
    profile_options = ["Chưa chọn đối tượng cụ thể"] + [
        f"{p['name']} ({p['profile_id']}) — {p['age']} tuổi, {p['location']}, MBTI: {p.get('mbti', 'N/A')}"
        for p in profiles
    ]

    st.markdown("### 🎯 Chọn Đối tượng Tìm Hiểu / Ghép Đôi:")
    selected_p_idx = st.selectbox(
        "Chọn một ứng viên từ Mock Data để AI tự động tập trung cá nhân hóa phân tích:",
        options=range(len(profile_options)),
        format_func=lambda i: profile_options[i],
        index=1 if len(profiles) > 0 else 0
    )

    selected_target = None
    if selected_p_idx > 0:
        selected_target = profiles[selected_p_idx - 1]
        t_name = selected_target.get("name")
        t_id = selected_target.get("profile_id")
        t_interests = ", ".join(selected_target.get("interests", []))
        t_traits = ", ".join(selected_target.get("personal_traits", []))
        t_dealbreakers = ", ".join(selected_target.get("dealbreakers", []))

        st.success(
            f"👤 **Đang tập trung phân tích đối tượng:** `{t_name}` (`{t_id}`)\n\n"
            f"- **Sở thích:** {t_interests} | **MBTI:** {selected_target.get('mbti', 'N/A')} | **Khu vực:** {selected_target.get('location')}\n"
            f"- **Đặc điểm:** {t_traits} | **Dealbreakers:** {t_dealbreakers}"
        )

    st.markdown("---")

    # Session State
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Xin chào! Tôi là Cupid AI Assistant. Hãy chọn một ứng viên ở trên và đặt câu hỏi, tôi sẽ cá nhân hóa và gọi Tools phân tích thông tin về người đó!",
                "mode_label": chat_mode,
                "steps": []
            }
        ]

    # Display History
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        steps = msg.get("steps", [])
        mode_label = msg.get("mode_label", "")

        with st.chat_message(role):
            if mode_label:
                st.caption(f"Mode: {mode_label}")

            if steps:
                with st.expander("🛠️ Chi tiết suy luận ReAct & Gọi Tools (Thought -> Action -> Observation)"):
                    for s in steps:
                        st.markdown(f"**Step {s['step']}**")
                        if s.get("thought"):
                            st.markdown(f"🧠 *Thought:* {s['thought']}")
                        if s.get("action"):
                            st.markdown(f"🛠️ *Action:* `{s['action']}`")
                        if s.get("observation"):
                            st.info(f"👁️ *Observation:* {s['observation']}")
                        st.markdown("---")
            st.write(content)

    # Quick prompts
    st.markdown("##### 💡 Gợi ý câu hỏi nhanh:")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("❓ (Tool) Phân tích độ tương thích & gợi ý hẹn hò"):
            if selected_target:
                tname = selected_target.get("name")
                st.session_state.sample_input = f"Hãy phân tích độ tương thích giữa tôi và {tname} trong hệ thống, sau đó gợi ý ý tưởng hẹn hò."
            else:
                st.session_state.sample_input = "Hãy phân tích độ tương thích giữa Linh và Hoàng trong hệ thống, sau đó gợi ý ý tưởng hẹn hò."
    with col_s2:
        if st.button("❓ (Tool) Gợi ý chủ đề trò chuyện phù hợp"):
            if selected_target:
                tname = selected_target.get("name")
                st.session_state.sample_input = f"Hãy gợi ý cho tôi 3 chủ đề trò chuyện dễ 'bắt sóng' nhất khi nhắn tin với {tname}."
            else:
                st.session_state.sample_input = "Nêu 3 dấu hiệu tâm lý cho thấy hai người đang có sự gắn kết lành mạnh trong giai đoạn đầu hẹn hò."

    user_input = st.chat_input("Nhập câu hỏi của bạn tại đây...")
    if "sample_input" in st.session_state and st.session_state.sample_input:
        user_input = st.session_state.sample_input
        st.session_state.sample_input = None

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "mode_label": chat_mode
        })
        with st.chat_message("user"):
            st.write(user_input)

        # Trộn ngữ cảnh Target Profile vào câu hỏi gửi tới Agent/LLM
        if selected_target:
            t_name = selected_target.get("name")
            t_id = selected_target.get("profile_id")
            t_interests = ", ".join(selected_target.get("interests", []))
            t_mbti = selected_target.get("mbti", "N/A")
            t_traits = ", ".join(selected_target.get("personal_traits", []))
            t_dealbreakers = ", ".join(selected_target.get("dealbreakers", []))

            context_query = (
                f"[HỒ SƠ ĐỐI TƯỢNG ĐANG TÌM HIỂU/GHÉP ĐÔI]\n"
                f"- Tên: {t_name} (Profile ID: {t_id})\n"
                f"- Tuổi: {selected_target.get('age')} | MBTI: {t_mbti} | Khu vực: {selected_target.get('location')}\n"
                f"- Sở thích: {t_interests}\n"
                f"- Đặc điểm: {t_traits}\n"
                f"- Dealbreakers: {t_dealbreakers}\n\n"
                f"LƯU Ý QUAN TRỌNG: Mọi câu hỏi của người dùng liên quan đến đối tượng này, hãy gọi các công cụ thực tế như analyze_compatibility['User', '{t_name}'], suggest_date_idea['User', '{t_name}', 'trung bình'], hoặc suggest_conversation_topics['User', '{t_name}'] để phân tích có căn cứ từ dữ liệu hệ thống.\n\n"
                f"Câu hỏi của người dùng: {user_input}"
            )
        else:
            context_query = user_input

        with st.chat_message("assistant"):
            if not is_agentic:
                with st.spinner("💬 Baseline Chatbot đang phản hồi..."):
                    res = run_baseline_chatbot(context_query, provider)
                    steps = []
                st.write(res)
            else:
                with st.spinner("🤖 Agentic ReAct đang suy luận & gọi tools..."):
                    res, steps = run_react_agent(context_query, provider)
                    final_ans = res.split("Final Answer:")[-1].strip() if "Final Answer:" in res else res

                if steps:
                    with st.expander("🛠️ Chi tiết suy luận ReAct & Gọi Tools (Thought -> Action -> Observation)", expanded=True):
                        for s in steps:
                            st.markdown(f"**Step {s['step']}**")
                            if s.get("thought"):
                                st.markdown(f"🧠 *Thought:* {s['thought']}")
                            if s.get("action"):
                                st.markdown(f"🛠️ *Action:* `{s['action']}`")
                            if s.get("observation"):
                                st.info(f"👁️ *Observation:* {s['observation']}")
                            st.markdown("---")
                st.write(final_ans)

        st.session_state.messages.append({
            "role": "assistant",
            "content": final_ans if is_agentic else res,
            "mode_label": chat_mode,
            "steps": steps if is_agentic else []
        })


if __name__ == "__main__":
    # Kiểm tra xem có đang chạy dưới Streamlit không
    try:
        import streamlit as st
        is_streamlit_running = st.runtime.exists()
    except Exception:
        is_streamlit_running = False

    if is_streamlit_running:
        run_streamlit_gui()
    else:
        print("==================================================")
        print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
        print("==================================================")

        provider = get_llm_provider()
        model_name = getattr(provider, "model_name", "Offline Mock Mode")
        print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")

        tests = load_test_cases()
        print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")

        sample_query = tests[2]["question"]

        print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
        run_baseline_chatbot(sample_query, provider, show_prompt=True)

        print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
        run_react_agent(sample_query, provider)
