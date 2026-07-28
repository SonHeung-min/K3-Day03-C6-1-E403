"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo các công cụ cho Cupid Agent: trợ lý ghép đôi và phân tích độ tương thích.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


def _normalize_text(value: str) -> str:
    """Chuẩn hóa chuỗi đầu vào bằng cách loại bỏ khoảng trắng thừa và chuyển về chữ thường."""
    return (value or "").strip().lower()


def _load_mock_profiles() -> list[Dict[str, Any]]:
    """Đọc dữ liệu hồ sơ từ mock_data.json trong cùng thư mục."""
    try:
        data_path = Path(__file__).resolve().with_name("mock_data.json")
        with data_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return []


def _resolve_profile(profile_input: Any) -> Optional[Dict[str, Any]]:
    """Chuyển đầu vào thành một hồ sơ từ mock_data nếu có thể."""
    if isinstance(profile_input, dict):
        return profile_input

    if not isinstance(profile_input, str):
        return None

    text = profile_input.strip()
    if not text:
        return None

    for profile in _load_mock_profiles():
        profile_id = str(profile.get("profile_id", "")).lower()
        profile_name = str(profile.get("name", "")).lower()
        if text.lower() in {profile_id, profile_name}:
            return profile

    return None


def _build_profile_summary(profile: Dict[str, Any]) -> str:
    """Tạo một đoạn mô tả ngắn từ hồ sơ để dùng cho fallback hoặc logging."""
    if not profile:
        return ""

    parts = []
    if profile.get("name"):
        parts.append(str(profile["name"]))
    if profile.get("age") is not None:
        parts.append(f"{profile['age']} tuổi")
    if profile.get("location"):
        parts.append(f"ở {profile['location']}")
    if profile.get("interests"):
        parts.append("sở thích: " + ", ".join(profile["interests"]))
    if profile.get("mbti"):
        parts.append(f"MBTI {profile['mbti']}")
    if profile.get("personal_traits"):
        parts.append("đặc điểm: " + ", ".join(profile["personal_traits"]))
    if profile.get("dealbreakers"):
        parts.append("dealbreakers: " + ", ".join(profile["dealbreakers"]))

    return "; ".join(parts)


def analyze_compatibility(person_a: Any, person_b: Any) -> str:
    """
    Phân tích mức độ tương thích giữa hai người bằng dữ liệu từ mock_data.json nếu có.

    Args:
        person_a: Hồ sơ người thứ nhất hoặc tên/profile_id.
        person_b: Hồ sơ người thứ hai hoặc tên/profile_id.

    Returns:
        str: Một bản tóm tắt độ tương thích, điểm số và gợi ý kết nối.
    """
    try:
        if not person_a or not person_b:
            return "LỖI: Vui lòng cung cấp thông tin của cả hai người để phân tích."

        profile_a = _resolve_profile(person_a)
        profile_b = _resolve_profile(person_b)

        if profile_a and profile_b:
            score = 50
            reasons = []

            shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))
            if shared_interests:
                score += min(20, len(shared_interests) * 8)
                reasons.append(f"cùng thích: {', '.join(shared_interests[:3])}")

            shared_traits = sorted(set(profile_a.get("personal_traits", [])) & set(profile_b.get("personal_traits", [])))
            if shared_traits:
                score += min(10, len(shared_traits) * 3)
                reasons.append(f"chia sẻ đặc điểm: {', '.join(shared_traits[:3])}")

            if profile_a.get("location") and profile_b.get("location") and profile_a.get("location") == profile_b.get("location"):
                score += 5
                reasons.append("cùng khu vực")

            age_diff = abs(int(profile_a.get("age", 0) or 0) - int(profile_b.get("age", 0) or 0))
            if age_diff <= 3:
                score += 4
                reasons.append("độ tuổi tương đồng")

            conflicts = []
            for breaker in profile_a.get("dealbreakers", []):
                if breaker in profile_b.get("personal_traits", []) or breaker in profile_b.get("dealbreakers", []):
                    conflicts.append(breaker)
            for breaker in profile_b.get("dealbreakers", []):
                if breaker in profile_a.get("personal_traits", []) or breaker in profile_a.get("dealbreakers", []):
                    conflicts.append(breaker)

            if conflicts:
                score -= min(20, len(set(conflicts)) * 8)
                reasons.append(f"có điểm xung khắc: {', '.join(sorted(set(conflicts))) }")

            score = max(0, min(100, score))

            if not reasons:
                reasons.append("có nền tảng giao tiếp khá phù hợp")

            return (
                f"Độ tương thích ước tính: {score}/100.\n"
                f"Điểm mạnh: {', '.join(reasons)}.\n"
                f"Gợi ý: Hãy thử bắt đầu bằng một chủ đề nhẹ như sở thích cá nhân hoặc kế hoạch cuối tuần."
            )

        text_a = _normalize_text(str(person_a))
        text_b = _normalize_text(str(person_b))

        score = 50
        reasons = []

        shared_keywords = [
            ("du lịch", "travel", "trip"),
            ("âm nhạc", "music", "nhạc"),
            ("ăn uống", "food", "cafe", "coffee"),
            ("game", "gaming", "video game"),
            ("sách", "book", "reading"),
            ("thể thao", "sport", "fitness"),
            ("cinema", "phim", "movie"),
        ]

        for keyword_group in shared_keywords:
            if any(term in text_a for term in keyword_group) and any(term in text_b for term in keyword_group):
                score += 8
                reasons.append(f"cùng thích {'/'.join(keyword_group)}")

        if "ngoài trời" in text_a and "ngoài trời" in text_b:
            score += 6
            reasons.append("cùng thích hoạt động ngoài trời")

        if "thân thiện" in text_a and "thân thiện" in text_b:
            score += 5
            reasons.append("có tính cách mở và thân thiện")

        score = max(0, min(100, score))

        if not reasons:
            reasons.append("có nền tảng giao tiếp khá phù hợp")

        return (
            f"Độ tương thích ước tính: {score}/100.\n"
            f"Điểm mạnh: {', '.join(reasons)}.\n"
            f"Gợi ý: Hãy thử bắt đầu bằng một chủ đề nhẹ như sở thích cá nhân hoặc kế hoạch cuối tuần."
        )
    except Exception as exc:
        return f"LỖI: Không thể phân tích độ tương thích. Chi tiết: {exc}"


def suggest_date_idea(person_a: Any, person_b: Any, budget: str = "trung bình") -> str:
    """
    Gợi ý một ý tưởng hẹn hò phù hợp với sở thích của cả hai người, ưu tiên dữ liệu mock_data nếu có.

    Args:
        person_a: Hồ sơ người thứ nhất hoặc tên/profile_id.
        person_b: Hồ sơ người thứ hai hoặc tên/profile_id.
        budget (str): Ngân sách dự kiến, ví dụ: 'thấp', 'trung bình', 'cao'.

    Returns:
        str: Một đề xuất hẹn hò cụ thể và phù hợp.
    """
    try:
        if not person_a or not person_b:
            return "LỖI: Vui lòng cung cấp thông tin của cả hai người để đề xuất ý tưởng hẹn hò."

        profile_a = _resolve_profile(person_a)
        profile_b = _resolve_profile(person_b)
        budget_text = _normalize_text(budget)

        if profile_a and profile_b:
            interests_a = set(profile_a.get("interests", []))
            interests_b = set(profile_b.get("interests", []))
            shared_interests = sorted(interests_a & interests_b)

            if any(term in " ".join(shared_interests).lower() for term in ["nhạc", "jazz", "cà phê", "cafe"]):
                idea = "hẹn hò tại quán cà phê có nhạc nền và trò chuyện nhẹ nhàng"
            elif any(term in " ".join(shared_interests).lower() for term in ["du lịch", "leo", "nhảy", "adventurous"]):
                idea = "đi dạo, chụp ảnh và thử một hoạt động ngoài trời thú vị"
            elif any(term in " ".join(shared_interests).lower() for term in ["gym", "chạy", "golf", "thể thao", "sport"]):
                idea = "đi chơi thể thao nhẹ hoặc đi bộ ở công viên"
            else:
                idea = "tổ chức một buổi trò chuyện thân thiện tại quán cà phê"
        else:
            text_a = _normalize_text(str(person_a))
            text_b = _normalize_text(str(person_b))
            if "âm nhạc" in text_a or "nhạc" in text_a or "âm nhạc" in text_b or "nhạc" in text_b:
                idea = "hẹn hò tại quán cà phê có biểu diễn acoustic"
            elif "du lịch" in text_a or "travel" in text_a or "du lịch" in text_b or "travel" in text_b:
                idea = "đi dạo và chụp ảnh ở một địa điểm đẹp"
            elif "thể thao" in text_a or "sport" in text_a or "thể thao" in text_b or "sport" in text_b:
                idea = "đi chơi thể thao nhẹ hoặc đi bộ ở công viên"
            else:
                idea = "tổ chức một buổi trò chuyện thân thiện tại quán cà phê"

        if "cao" in budget_text:
            budget_note = "phù hợp ngân sách cao"
        elif "thấp" in budget_text:
            budget_note = "phù hợp ngân sách thấp"
        else:
            budget_note = "phù hợp ngân sách trung bình"

        return f"Gợi ý hẹn hò: {idea}. {budget_note}."
    except Exception as exc:
        return f"LỖI: Không thể đề xuất ý tưởng hẹn hò. Chi tiết: {exc}"


def suggest_conversation_topics(person_a: Any, person_b: Any) -> str:
    """
    Gợi ý các chủ đề trò chuyện dựa trên hồ sơ trong mock_data.json khi có thể.

    Args:
        person_a: Hồ sơ người thứ nhất hoặc tên/profile_id.
        person_b: Hồ sơ người thứ hai hoặc tên/profile_id.

    Returns:
        str: Danh sách các chủ đề phù hợp để bắt đầu cuộc trò chuyện.
    """
    try:
        if not person_a or not person_b:
            return "LỖI: Vui lòng cung cấp thông tin của cả hai người để đề xuất chủ đề trò chuyện."

        profile_a = _resolve_profile(person_a)
        profile_b = _resolve_profile(person_b)

        if profile_a and profile_b:
            shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))
            topics = []
            if shared_interests:
                topics.extend([f"chủ đề chung: {item}" for item in shared_interests[:3]])
            topics.extend([
                "sở thích cuối tuần",
                "địa điểm ăn uống yêu thích",
                "một điều bất ngờ từng trải qua",
            ])
            return "Các chủ đề trò chuyện phù hợp: " + "; ".join(topics)

        topics = [
            "sở thích cuối tuần",
            "địa điểm ăn uống yêu thích",
            "bộ phim hoặc nhạc đang thích",
            "kế hoạch du lịch ngắn ngày",
            "một điều bất ngờ từng trải qua",
        ]
        return "Các chủ đề trò chuyện phù hợp: " + "; ".join(topics)
    except Exception as exc:
        return f"LỖI: Không thể đề xuất chủ đề trò chuyện. Chi tiết: {exc}"


# Danh sách các tool được đăng ký để Agent sử dụng
AVAILABLE_TOOLS = {
    "analyze_compatibility": analyze_compatibility,
    "suggest_date_idea": suggest_date_idea,
    "suggest_conversation_topics": suggest_conversation_topics,
}


###
# analyze_compatibility

# Dùng để phân tích độ tương thích giữa 2 người.
# Nhận vào thông tin về 2 người.
# Trả về điểm số tương thích, lý do tại sao phù hợp, và gợi ý bắt đầu trò chuyện.
# suggest_date_idea

# Dùng để gợi ý ý tưởng hẹn hò phù hợp.
# Nhận vào thông tin 2 người và ngân sách.
# Trả về một ý tưởng hẹn hò phù hợp với sở thích của cả hai.
# suggest_conversation_topics

# Dùng để gợi ý các chủ đề trò chuyện.
# Nhận vào thông tin 2 người.
# Trả về danh sách chủ đề nhẹ nhàng, tự nhiên để bắt đầu cuộc trò chuyện.
###