"""
TOOL REGISTRY & SCHEMAS
Role 2: Tool Engineer cho Cupid Agent.

Các tool trong file này dùng dữ liệu giả lập ở mock_data.json để minh họa
ReAct Agent biết tra cứu, quan sát kết quả và không bịa hồ sơ.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _normalize_text(value: Any) -> str:
    """Chuẩn hóa chuỗi để so khớp mềm."""
    return str(value or "").strip().lower()


def _load_mock_profiles() -> List[Dict[str, Any]]:
    """Đọc dữ liệu hồ sơ từ mock_data.json."""
    try:
        data_path = Path(__file__).resolve().with_name("mock_data.json")
        with data_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return []


def _resolve_profile(profile_input: Any) -> Optional[Dict[str, Any]]:
    """Tìm hồ sơ theo name hoặc profile_id."""
    if isinstance(profile_input, dict):
        return profile_input
    query = _normalize_text(profile_input)
    if not query:
        return None
    for profile in _load_mock_profiles():
        if query in {
            _normalize_text(profile.get("profile_id")),
            _normalize_text(profile.get("name")),
        }:
            return profile
    return None


def _profile_summary(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Rút gọn hồ sơ để Observation dễ đọc."""
    return {
        "profile_id": profile.get("profile_id"),
        "name": profile.get("name"),
        "age": profile.get("age"),
        "gender": profile.get("gender"),
        "location": profile.get("location"),
        "interests": profile.get("interests", []),
        "mbti": profile.get("mbti"),
        "personal_traits": profile.get("personal_traits", []),
        "dealbreakers": profile.get("dealbreakers", []),
        "relationship_goal": profile.get("relationship_goal"),
        "communication_style": profile.get("communication_style"),
        "preferred_date_style": profile.get("preferred_date_style", []),
        "green_flags": profile.get("green_flags", []),
        "red_flags": profile.get("red_flags", []),
    }


def _json(data: Any) -> str:
    """Serialize JSON tiếng Việt dễ đọc."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def search_profiles(
    gender: str = "",
    location: str = "",
    interest: str = "",
    mbti: str = "",
    exclude_trait: str = "",
) -> str:
    """
    Tìm hồ sơ theo bộ lọc cơ bản.

    Args:
        gender: Giới tính cần tìm, ví dụ "female" hoặc "male".
        location: Thành phố/khu vực.
        interest: Một sở thích bắt buộc.
        mbti: MBTI bắt buộc nếu có.
        exclude_trait: Trait cần loại trừ, ví dụ "smokes".

    Returns:
        str: JSON gồm danh sách hồ sơ phù hợp hoặc mảng rỗng, không tự tạo hồ sơ mới.
    """
    profiles = _load_mock_profiles()
    results = []

    for profile in profiles:
        if gender and _normalize_text(profile.get("gender")) != _normalize_text(gender):
            continue
        if location and _normalize_text(profile.get("location")) != _normalize_text(location):
            continue
        if mbti and _normalize_text(profile.get("mbti")) != _normalize_text(mbti):
            continue
        if interest:
            interests = [_normalize_text(item) for item in profile.get("interests", [])]
            if _normalize_text(interest) not in interests:
                continue
        if exclude_trait:
            traits = [_normalize_text(item) for item in profile.get("personal_traits", [])]
            red_flags = [_normalize_text(item) for item in profile.get("red_flags", [])]
            if _normalize_text(exclude_trait) in traits or _normalize_text(exclude_trait) in red_flags:
                continue
        results.append(_profile_summary(profile))

    return _json(
        {
            "count": len(results),
            "results": results,
            "note": "Không tìm thấy hồ sơ phù hợp; không được tự bịa ứng viên." if not results else "Kết quả lấy từ mock_data.json.",
        }
    )


def check_dealbreakers(person_a: Any, person_b: Any) -> str:
    """
    Kiểm tra trait/red flag của một người có đụng dealbreaker của người kia không.

    Args:
        person_a: Tên/profile_id người thứ nhất.
        person_b: Tên/profile_id người thứ hai.

    Returns:
        str: JSON mô tả xung đột dealbreaker.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "LỖI: Không tìm thấy đủ hồ sơ để kiểm tra dealbreaker."

    conflicts = []
    traits_a = set(profile_a.get("personal_traits", []) + profile_a.get("red_flags", []))
    traits_b = set(profile_b.get("personal_traits", []) + profile_b.get("red_flags", []))

    for breaker in profile_a.get("dealbreakers", []):
        if breaker in traits_b:
            conflicts.append(f"{profile_a['name']} không hợp với trait '{breaker}' của {profile_b['name']}")
    for breaker in profile_b.get("dealbreakers", []):
        if breaker in traits_a:
            conflicts.append(f"{profile_b['name']} không hợp với trait '{breaker}' của {profile_a['name']}")

    return _json(
        {
            "person_a": profile_a["name"],
            "person_b": profile_b["name"],
            "conflicts": conflicts,
            "safe_to_recommend": not conflicts,
        }
    )


def analyze_compatibility(person_a: Any, person_b: Any) -> str:
    """
    Phân tích độ tương thích ước tính giữa hai hồ sơ.

    Args:
        person_a: Tên/profile_id người thứ nhất.
        person_b: Tên/profile_id người thứ hai.

    Returns:
        str: JSON gồm điểm 0-100, band, evidence và lưu ý an toàn.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "LỖI: Không tìm thấy đủ hồ sơ để phân tích độ tương thích."

    score = 40
    evidence = []
    cautions = []

    shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))
    if shared_interests:
        score += min(20, len(shared_interests) * 8)
        evidence.append(f"Sở thích chung: {', '.join(shared_interests)}")

    if profile_a.get("relationship_goal") == profile_b.get("relationship_goal"):
        score += 15
        evidence.append(f"Cùng mục tiêu mối quan hệ: {profile_a.get('relationship_goal')}")

    shared_traits = sorted(set(profile_a.get("personal_traits", [])) & set(profile_b.get("personal_traits", [])))
    if shared_traits:
        score += min(10, len(shared_traits) * 4)
        evidence.append(f"Trait chung: {', '.join(shared_traits)}")

    if profile_a.get("location") == profile_b.get("location"):
        score += 10
        evidence.append("Cùng khu vực nên dễ gặp mặt")

    shared_date_styles = sorted(set(profile_a.get("preferred_date_style", [])) & set(profile_b.get("preferred_date_style", [])))
    if shared_date_styles:
        score += min(10, len(shared_date_styles) * 5)
        evidence.append(f"Kiểu hẹn phù hợp: {', '.join(shared_date_styles)}")

    dealbreaker_data = json.loads(check_dealbreakers(profile_a, profile_b))
    if dealbreaker_data["conflicts"]:
        score -= min(25, len(dealbreaker_data["conflicts"]) * 12)
        cautions.extend(dealbreaker_data["conflicts"])

    score = max(0, min(100, score))
    if score >= 85:
        band = "Rất tiềm năng"
    elif score >= 70:
        band = "Khá hợp"
    elif score >= 50:
        band = "Có điểm chung nhưng cần tìm hiểu thêm"
    elif score >= 30:
        band = "Khá nhiều khác biệt"
    else:
        band = "Không nên ưu tiên nếu không có thêm dữ liệu mới"

    if not evidence:
        evidence.append("Dữ liệu hiện có chưa cho thấy nhiều điểm chung rõ ràng")

    return _json(
        {
            "score": score,
            "band": band,
            "evidence": evidence,
            "cautions": cautions,
            "data_confidence": "medium",
            "note": "Đây là độ tương thích ước tính dựa trên dữ liệu hồ sơ hiện có, không phải kết luận tuyệt đối.",
        }
    )


def suggest_date_idea(person_a: Any, person_b: Any, budget: str = "trung bình") -> str:
    """
    Gợi ý ý tưởng hẹn hò dựa trên hai hồ sơ và ngân sách.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "LỖI: Không tìm thấy đủ hồ sơ để đề xuất ý tưởng hẹn hò."

    shared_styles = sorted(set(profile_a.get("preferred_date_style", [])) & set(profile_b.get("preferred_date_style", [])))
    shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))

    if shared_styles:
        idea = f"một buổi {shared_styles[0]}"
    elif shared_interests:
        idea = f"một buổi trò chuyện xoay quanh {shared_interests[0]}"
    else:
        idea = "một buổi cà phê nhẹ nhàng để tìm hiểu kỳ vọng của nhau"

    return _json(
        {
            "idea": idea,
            "budget": budget or "trung bình",
            "why": "Gợi ý dựa trên preferred_date_style và sở thích chung trong hồ sơ.",
        }
    )


def suggest_conversation_topics(person_a: Any, person_b: Any) -> str:
    """
    Gợi ý chủ đề trò chuyện dựa trên hai hồ sơ.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "LỖI: Không tìm thấy đủ hồ sơ để đề xuất chủ đề trò chuyện."

    shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))
    topics = [f"Sở thích chung: {item}" for item in shared_interests[:3]]
    topics.extend(
        [
            f"Hỏi nhẹ về kiểu hẹn yêu thích của {profile_b['name']}",
            "Một hoạt động cuối tuần khiến cả hai thấy thoải mái",
            "Cách hai người cân bằng công việc và đời sống cá nhân",
        ]
    )
    return _json({"topics": topics[:5], "tone": "tự nhiên, tôn trọng, không gây áp lực"})


AVAILABLE_TOOLS = {
    "search_profiles": search_profiles,
    "check_dealbreakers": check_dealbreakers,
    "analyze_compatibility": analyze_compatibility,
    "suggest_date_idea": suggest_date_idea,
    "suggest_conversation_topics": suggest_conversation_topics,
}
