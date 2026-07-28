"""
TOOL REGISTRY & SCHEMAS
Role 2: Tool Engineer for Cupid Agent.

Các tool dùng dữ liệu hồ sơ giả lập trong mock_data.json để chứng minh
ReAct Agent có thể tra cứu bằng chứng, quan sát kết quả tool và tránh bịa
hồ sơ hoặc điểm tương thích.
"""

import json
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional


ALIASES = {
    "female": "nu",
    "woman": "nu",
    "women": "nu",
    "girl": "nu",
    "male": "nam",
    "man": "nam",
    "men": "nam",
    "boy": "nam",
    "ho chi minh city": "tp.hcm",
    "hcm": "tp.hcm",
    "tp hcm": "tp.hcm",
    "tphcm": "tp.hcm",
    "tp.hcm": "tp.hcm",
    "sai gon": "tp.hcm",
    "saigon": "tp.hcm",
    "ha noi": "ha noi",
    "hanoi": "ha noi",
    "da nang": "da nang",
    "danang": "da nang",
    "sci-fi books": "sach khoa hoc vien tuong",
    "sci fi books": "sach khoa hoc vien tuong",
    "science fiction books": "sach khoa hoc vien tuong",
    "doc sach sci-fi": "sach khoa hoc vien tuong",
    "sach sci-fi": "sach khoa hoc vien tuong",
    "reptile keeping": "nuoi bo sat",
    "nuoi bo sat": "nuoi bo sat",
    "skydiving": "nhay du",
    "nhay du": "nhay du",
    "smokes": "hut thuoc",
    "smoking": "hut thuoc",
    "smoker": "hut thuoc",
    "non_smoker": "khong hut thuoc",
    "non-smoker": "khong hut thuoc",
    "non smoker": "khong hut thuoc",
    "khong hut thuoc": "khong hut thuoc",
    "quiet coffee": "ca phe yen tinh",
    "walking": "di dao",
    "bookstore": "nha sach",
    "medium": "trung binh",
    "low": "thap",
    "high": "cao",
    "serious": "nghiem tuc",
    "casual": "hen ho thoai mai",
    "casual dating": "hen ho thoai mai",
    "hoang": "hoang",
    "ho?ng": "hoang",
    "khanh": "khanh",
    "kh?nh": "khanh",
    "quan": "quan",
    "qu?n": "quan",
    "ha": "ha",
    "h?": "ha",
    "bao": "bao",
    "b?o": "bao",
}


def _normalize_text(value: Any) -> str:
    """Chuẩn hóa text để so khớp ổn định giữa tiếng Việt và tiếng Anh."""
    text = unicodedata.normalize("NFC", str(value or "").strip().casefold())
    ascii_text = "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    ascii_text = " ".join(ascii_text.replace("_", " ").replace("-", " ").split())
    return ALIASES.get(ascii_text, ascii_text)


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
    """Trả về bản tóm tắt hồ sơ dễ đọc cho Observation."""
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


def _normalized_set(values: List[Any]) -> set:
    return {_normalize_text(item) for item in values}


def search_profiles(
    gender: str = "",
    location: str = "",
    interest: str = "",
    mbti: str = "",
    exclude_trait: str = "",
) -> str:
    """
    Tìm hồ sơ bằng các bộ lọc đơn giản.

    Args:
        gender: Giới tính cần tìm, ví dụ "nữ"/"female" hoặc "nam"/"male".
        location: Thành phố/khu vực, ví dụ "TP.HCM", "Ho Chi Minh City", "Hà Nội".
        interest: Sở thích bắt buộc.
        mbti: MBTI bắt buộc nếu có.
        exclude_trait: Đặc điểm cần loại trừ, ví dụ "hút thuốc"/"smokes".

    Returns:
        str: JSON chứa hồ sơ phù hợp hoặc tập kết quả rỗng.
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
        if interest and _normalize_text(interest) not in _normalized_set(profile.get("interests", [])):
            continue
        if exclude_trait:
            blocked = _normalize_text(exclude_trait)
            traits = _normalized_set(profile.get("personal_traits", []))
            red_flags = _normalized_set(profile.get("red_flags", []))
            if blocked in traits or blocked in red_flags:
                continue
        results.append(_profile_summary(profile))

    return _json(
        {
            "count": len(results),
            "results": results,
            "note": "Không tìm thấy hồ sơ phù hợp; không được bịa ứng viên mới."
            if not results
            else "Kết quả được lấy từ mock_data.json.",
        }
    )


def check_dealbreakers(person_a: str, person_b: str) -> str:
    """
    Kiểm tra liệu một người có vi phạm dealbreaker của người còn lại không.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "ERROR: Không tìm thấy đủ hồ sơ để kiểm tra dealbreaker."

    conflicts = []
    traits_a = _normalized_set(profile_a.get("personal_traits", []) + profile_a.get("red_flags", []))
    traits_b = _normalized_set(profile_b.get("personal_traits", []) + profile_b.get("red_flags", []))

    for breaker in profile_a.get("dealbreakers", []):
        if _normalize_text(breaker) in traits_b:
            conflicts.append(f"{profile_a['name']} có dealbreaker bị vi phạm bởi {profile_b['name']}: {breaker}")
    for breaker in profile_b.get("dealbreakers", []):
        if _normalize_text(breaker) in traits_a:
            conflicts.append(f"{profile_b['name']} có dealbreaker bị vi phạm bởi {profile_a['name']}: {breaker}")

    return _json(
        {
            "person_a": profile_a["name"],
            "person_b": profile_b["name"],
            "conflicts": conflicts,
            "safe_to_recommend": not conflicts,
        }
    )


def analyze_compatibility(person_a: str, person_b: str) -> str:
    """
    Ước tính độ tương thích giữa hai hồ sơ.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "ERROR: Không tìm thấy đủ hồ sơ để phân tích độ tương thích."

    score = 40
    evidence = []
    cautions = []

    shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))
    if shared_interests:
        score += min(20, len(shared_interests) * 8)
        evidence.append(f"Sở thích chung: {', '.join(shared_interests)}")

    if _normalize_text(profile_a.get("relationship_goal")) == _normalize_text(profile_b.get("relationship_goal")):
        score += 15
        evidence.append(f"Mục tiêu quan hệ tương đồng: {profile_a.get('relationship_goal')}")

    shared_traits = sorted(set(profile_a.get("personal_traits", [])) & set(profile_b.get("personal_traits", [])))
    if shared_traits:
        score += min(10, len(shared_traits) * 4)
        evidence.append(f"Đặc điểm chung: {', '.join(shared_traits)}")

    if _normalize_text(profile_a.get("location")) == _normalize_text(profile_b.get("location")):
        score += 10
        evidence.append("Cùng thành phố, dễ sắp xếp gặp mặt hơn")

    shared_date_styles = sorted(set(profile_a.get("preferred_date_style", [])) & set(profile_b.get("preferred_date_style", [])))
    if shared_date_styles:
        score += min(10, len(shared_date_styles) * 5)
        evidence.append(f"Kiểu hẹn hò phù hợp: {', '.join(shared_date_styles)}")

    dealbreaker_data = json.loads(check_dealbreakers(profile_a, profile_b))
    if dealbreaker_data["conflicts"]:
        score -= min(25, len(dealbreaker_data["conflicts"]) * 12)
        cautions.extend(dealbreaker_data["conflicts"])

    score = max(0, min(100, score))
    if score >= 85:
        band = "Rất triển vọng"
    elif score >= 70:
        band = "Khá phù hợp"
    elif score >= 50:
        band = "Có điểm chung, nên tìm hiểu thêm"
    elif score >= 30:
        band = "Có nhiều khác biệt"
    else:
        band = "Ưu tiên thấp nếu không có thêm dữ liệu mới"

    if not evidence:
        evidence.append("Dữ liệu hiện tại chưa cho thấy nhiều tín hiệu chung rõ ràng")

    missing_fields = [
        key
        for key in ("mbti", "communication_style", "relationship_goal")
        if not profile_a.get(key) or not profile_b.get(key)
    ]
    data_confidence = "trung bình" if missing_fields else "cao"

    return _json(
        {
            "score": score,
            "band": band,
            "evidence": evidence,
            "cautions": cautions,
            "data_confidence": data_confidence,
            "note": "Đây là điểm tương thích ước tính dựa trên dữ liệu hồ sơ hiện có, không phải kết luận chắc chắn.",
        }
    )


def suggest_conversation_topics(person_a: str, person_b: str) -> str:
    """
    Gợi ý chủ đề trò chuyện dựa trên hai hồ sơ.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "ERROR: Không tìm thấy đủ hồ sơ để gợi ý chủ đề trò chuyện."

    shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))
    topics = [f"Sở thích chung: {item}" for item in shared_interests[:3]]
    topics.extend(
        [
            f"Hỏi về kiểu buổi hẹn ít áp lực mà {profile_b['name']} thấy thoải mái",
            "Một hoạt động cuối tuần cả hai đều thấy dễ tham gia",
            "Cách mỗi người cân bằng công việc, sở thích và thời gian riêng",
        ]
    )
    return _json({"topics": topics[:5], "tone": "tự nhiên, tôn trọng, ít áp lực"})


TOOL_SCHEMAS = {
    "search_profiles": {
        "description": "Tìm hồ sơ ứng viên theo bộ lọc có căn cứ từ mock_data.json.",
        "inputs": {
            "gender": {"type": "str", "required": True, "examples": ["nữ", "nam"]},
            "location": {"type": "str", "required": True, "examples": ["TP.HCM", "Hà Nội", "Đà Nẵng"]},
            "interest": {"type": "str", "required": False, "examples": ["sách khoa học viễn tưởng", "nhảy dù"]},
            "mbti": {"type": "str", "required": False, "examples": ["INTJ", "ENFP"]},
            "exclude_trait": {"type": "str", "required": False, "examples": ["hút thuốc"]},
        },
        "output": "JSON gồm count, results và note. Nếu count=0, agent không được bịa ứng viên.",
    },
    "check_dealbreakers": {
        "description": "Kiểm tra xung đột dealbreaker giữa hai hồ sơ trước khi khuyến nghị.",
        "inputs": {
            "person_a": {"type": "str", "required": True, "examples": ["An", "USR-006"]},
            "person_b": {"type": "str", "required": True, "examples": ["Linh", "USR-001"]},
        },
        "output": "JSON gồm person_a, person_b, conflicts và safe_to_recommend.",
    },
    "analyze_compatibility": {
        "description": "Tính điểm tương thích ước tính dựa trên sở thích, mục tiêu, lifestyle, dealbreaker và độ đầy đủ dữ liệu.",
        "inputs": {
            "person_a": {"type": "str", "required": True, "examples": ["An", "USR-006"]},
            "person_b": {"type": "str", "required": True, "examples": ["Linh", "USR-001"]},
        },
        "output": "JSON gồm score, band, evidence, cautions, data_confidence và note.",
    },
    "suggest_conversation_topics": {
        "description": "Gợi ý chủ đề trò chuyện dựa trên hồ sơ thật và sở thích chung.",
        "inputs": {
            "person_a": {"type": "str", "required": True, "examples": ["An", "USR-006"]},
            "person_b": {"type": "str", "required": True, "examples": ["Linh", "USR-001"]},
        },
        "output": "JSON gồm topics và tone.",
    },
}


AVAILABLE_TOOLS = {
    "search_profiles": search_profiles,
    "check_dealbreakers": check_dealbreakers,
    "analyze_compatibility": analyze_compatibility,
    "suggest_conversation_topics": suggest_conversation_topics,
}
