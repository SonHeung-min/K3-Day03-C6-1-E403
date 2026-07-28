"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text or ""
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider (Cho bài test không cần kết nối API)"""
    def __init__(self):
        self.model_name = "Offline Mock Mode"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        text = prompt.lower()
        # Nếu là Chatbot Baseline
        if "baseline" in system_prompt.lower() or "chatbot" in system_prompt.lower():
            if "hãy tìm" in text or "tìm cho tôi" in text or "không hút thuốc" in text or "mbti" in text:
                return (
                    "Mình có thể tư vấn ở mức chung, nhưng không có quyền tra hồ sơ, lọc database hoặc xác nhận ứng viên thật. "
                    "Với yêu cầu này, bạn nên dùng Cupid ReAct Agent để gọi tool tìm hồ sơ và kiểm tra điều kiện."
                )
            if "nuôi bò sát" in text and "nhảy dù" in text:
                return (
                    "Gợi ý 3 câu mở đầu:\n"
                    "1. 'Bio của bạn làm mình phân vân: nên hỏi về bò sát trước hay chuẩn bị tinh thần nhảy dù trước?'\n"
                    "2. 'Bạn thích nuôi bò sát và nhảy dù, vậy chắc gu trò chuyện của bạn cũng không dành cho người yếu tim nhỉ?'\n"
                    "3. 'Mình chưa từng nhảy dù, nhưng nếu được nghe bạn kể về nó thì chắc cũng đủ làm tim rơi tự do rồi.'"
                )
            if "gắn kết lành mạnh" in text:
                return (
                    "Ba dấu hiệu khá tốt là: 1. Hai người giao tiếp rõ ràng và không ép nhau trả lời ngay; "
                    "2. Cả hai tôn trọng ranh giới cá nhân; "
                    "3. Mỗi người vẫn giữ đời sống riêng nhưng chủ động dành thời gian tìm hiểu nhau."
                )
            return (
                "Mình có thể tư vấn ở mức chung, nhưng không có quyền tra hồ sơ hoặc tính điểm tương thích. "
                "Nếu cần phân tích theo dữ liệu, hãy dùng Cupid ReAct Agent."
            )
        
        # Nếu là ReAct Agent và đã có Observation trong chat history
        if "observation:" in text:
            if '"count": 0' in text:
                return (
                    "Thought: Observation cho thấy không có hồ sơ phù hợp, tôi không được bịa ứng viên mới.\n"
                    "Final Answer: Mình chưa tìm thấy bạn nữ ở TP.HCM thỏa đồng thời các tiêu chí nhảy dù, nuôi bò sát, MBTI ENFP và không hút thuốc trong mock_data.json. Mình cũng không thể xác nhận nâng cấp VIP vì tool hiện tại không hỗ trợ thao tác tài khoản. Bạn có thể nới một tiêu chí như MBTI, sở thích hoặc địa điểm để hệ thống tìm được nhiều lựa chọn hơn."
                )
            if '"results"' in text:
                return (
                    "Thought: Observation đã trả về hồ sơ phù hợp và đã loại trừ người hút thuốc.\n"
                    "Final Answer: Dựa trên dữ liệu hiện có, Linh là lựa chọn hợp lý nhất vì ở TP.HCM, thích sách khoa học viễn tưởng và không có red flag hút thuốc. Bạn có thể bắt chuyện bằng một câu nhẹ như: 'Nếu được chọn một thế giới khoa học viễn tưởng để đi cà phê cuối tuần, bạn chọn nơi nào?'"
                )
            if '"topics"' in text:
                return (
                    "Thought: Tôi đã có Observation về độ tương thích và chủ đề trò chuyện.\n"
                    "Final Answer: An và Linh có nhiều điểm chung tốt để bắt đầu tìm hiểu, đặc biệt là mục tiêu nghiêm túc, sách khoa học viễn tưởng, cà phê cuối tuần và nhịp trò chuyện sâu. Chủ đề nên mở đầu nhẹ bằng sách, thói quen cuối tuần, hoặc một buổi cà phê yên tĩnh."
                )
            if '"score"' in text and "suggest_conversation_topics" not in text:
                return (
                    "Thought: Đã có điểm tương thích, cần thêm chủ đề trò chuyện để câu trả lời hữu ích hơn.\n"
                    "Action: suggest_conversation_topics['An', 'Linh']"
                )
            return (
                "Thought: Tôi đã có đủ Observation để đưa ra kết luận có căn cứ.\n"
                "Final Answer: Mình sẽ dựa trên Observation để trả lời, không tự bịa thêm hồ sơ hay điểm số."
            )
            
        # ReAct Agent bước đầu tiên: sinh Action
        if "gắn kết" in text or "câu mở đầu" in text:
            return (
                "Thought: Đây là câu hỏi tư vấn chung, không cần tra cứu hồ sơ.\n"
                "Final Answer: Đây là câu hỏi có thể trả lời trực tiếp bằng kiến thức giao tiếp chung, không cần gọi tool."
            )
        
        if "hút thuốc" in text and ("sách khoa học viễn tưởng" in text or "đọc sách sci-fi" in text):
            return (
                "Thought: Cần tìm nữ ở TP.HCM thích sách khoa học viễn tưởng và loại trừ người hút thuốc.\n"
                "Action: search_profiles['nữ', 'TP.HCM', 'sách khoa học viễn tưởng', '', 'hút thuốc']"
            )

        if "an" in text and "linh" in text:
            return (
                "Thought: Cần phân tích độ tương thích giữa An và Linh trước.\n"
                "Action: analyze_compatibility['An', 'Linh']"
            )

        if "nhảy dù" in text and "nuôi bò sát" in text and "enfp" in text:
            return (
                "Thought: Cần tìm hồ sơ nữ ở TP.HCM thỏa các tiêu chí chặt và loại trừ người hút thuốc.\n"
                "Action: search_profiles['nữ', 'TP.HCM', 'nhảy dù, nuôi bò sát', 'ENFP', 'hút thuốc']"
            )

        return (
            "Thought: Cần phân tích độ tương thích dựa trên hồ sơ có sẵn.\n"
            "Action: analyze_compatibility['An', 'Linh']"
        )


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
