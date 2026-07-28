"""
TOOL REGISTRY & SCHEMAS
Role 2: Tool Engineer for Cupid Agent.

The tools use synthetic profiles from mock_data.json to demonstrate that the
ReAct Agent can retrieve evidence, observe tool results, and avoid fabricating
profiles or compatibility scores.
"""

import json
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional


ALIASES = {
    "tp.hcm": "ho chi minh city",
    "tphcm": "ho chi minh city",
    "tp hcm": "ho chi minh city",
    "sai gon": "ho chi minh city",
    "saigon": "ho chi minh city",
    "ha noi": "ha noi",
    "hà nội": "ha noi",
    "hanoi": "ha noi",
    "da nang": "da nang",
    "đà nẵng": "da nang",
    "danang": "da nang",
    "doc sach sci-fi": "sci-fi books",
    "đọc sách sci-fi": "sci-fi books",
    "nuoi bo sat": "reptile keeping",
    "nuôi bò sát": "reptile keeping",
    "nhay du": "skydiving",
    "nhảy dù": "skydiving",
    "khong hut thuoc": "non_smoker",
    "không hút thuốc": "non_smoker",
    "hoàng": "hoang",
    "ho?ng": "hoang",
    "khánh": "khanh",
    "kh?nh": "khanh",
    "hà": "ha",
    "h?": "ha",
    "bảo": "bao",
    "b?o": "bao",
}


def _normalize_text(value: Any) -> str:
    """Normalize text for stable matching."""
    text = unicodedata.normalize("NFC", str(value or "").strip().casefold())
    if text in ALIASES:
        return ALIASES[text]
    ascii_text = "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    return ALIASES.get(ascii_text, ascii_text)


def _load_mock_profiles() -> List[Dict[str, Any]]:
    """Load profile data from mock_data.json."""
    try:
        data_path = Path(__file__).resolve().with_name("mock_data.json")
        with data_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return []


def _resolve_profile(profile_input: Any) -> Optional[Dict[str, Any]]:
    """Resolve a profile by name or profile_id."""
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
    """Return a compact profile for readable observations."""
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
    """Serialize readable UTF-8 JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def search_profiles(
    gender: str = "",
    location: str = "",
    interest: str = "",
    mbti: str = "",
    exclude_trait: str = "",
) -> str:
    """
    Search profiles with simple filters.

    Args:
        gender: Target gender, e.g. "female" or "male".
        location: City or region.
        interest: Required interest.
        mbti: Required MBTI if provided.
        exclude_trait: Trait to exclude, e.g. "smokes".

    Returns:
        str: JSON containing matching profiles or an empty result set.
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
            "note": "No matching profile found; do not invent a new candidate."
            if not results
            else "Results are grounded in mock_data.json.",
        }
    )


def check_dealbreakers(person_a: Any, person_b: Any) -> str:
    """
    Check whether either profile violates the other's dealbreakers.

    Args:
        person_a: Name/profile_id for the first person.
        person_b: Name/profile_id for the second person.

    Returns:
        str: JSON describing dealbreaker conflicts.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "ERROR: Not enough profiles found to check dealbreakers."

    conflicts = []
    traits_a = set(profile_a.get("personal_traits", []) + profile_a.get("red_flags", []))
    traits_b = set(profile_b.get("personal_traits", []) + profile_b.get("red_flags", []))

    for breaker in profile_a.get("dealbreakers", []):
        if breaker in traits_b:
            conflicts.append(f"{profile_a['name']} has a dealbreaker conflict with {profile_b['name']}: {breaker}")
    for breaker in profile_b.get("dealbreakers", []):
        if breaker in traits_a:
            conflicts.append(f"{profile_b['name']} has a dealbreaker conflict with {profile_a['name']}: {breaker}")

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
    Estimate compatibility between two profiles.

    Args:
        person_a: Name/profile_id for the first person.
        person_b: Name/profile_id for the second person.

    Returns:
        str: JSON with score, score band, evidence, cautions, and confidence.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "ERROR: Not enough profiles found to analyze compatibility."

    score = 40
    evidence = []
    cautions = []

    shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))
    if shared_interests:
        score += min(20, len(shared_interests) * 8)
        evidence.append(f"Shared interests: {', '.join(shared_interests)}")

    if profile_a.get("relationship_goal") == profile_b.get("relationship_goal"):
        score += 15
        evidence.append(f"Aligned relationship goal: {profile_a.get('relationship_goal')}")

    shared_traits = sorted(set(profile_a.get("personal_traits", [])) & set(profile_b.get("personal_traits", [])))
    if shared_traits:
        score += min(10, len(shared_traits) * 4)
        evidence.append(f"Shared traits: {', '.join(shared_traits)}")

    if profile_a.get("location") == profile_b.get("location"):
        score += 10
        evidence.append("Same city, easier to meet")

    shared_date_styles = sorted(set(profile_a.get("preferred_date_style", [])) & set(profile_b.get("preferred_date_style", [])))
    if shared_date_styles:
        score += min(10, len(shared_date_styles) * 5)
        evidence.append(f"Compatible date styles: {', '.join(shared_date_styles)}")

    dealbreaker_data = json.loads(check_dealbreakers(profile_a, profile_b))
    if dealbreaker_data["conflicts"]:
        score -= min(25, len(dealbreaker_data["conflicts"]) * 12)
        cautions.extend(dealbreaker_data["conflicts"])

    score = max(0, min(100, score))
    if score >= 85:
        band = "Very promising"
    elif score >= 70:
        band = "Good match"
    elif score >= 50:
        band = "Some common ground; learn more"
    elif score >= 30:
        band = "Several differences"
    else:
        band = "Low priority unless new data appears"

    if not evidence:
        evidence.append("The current profiles do not show many clear shared signals")

    missing_fields = [
        key
        for key in ("mbti", "communication_style", "relationship_goal")
        if not profile_a.get(key) or not profile_b.get(key)
    ]
    data_confidence = "medium" if missing_fields else "high"

    return _json(
        {
            "score": score,
            "band": band,
            "evidence": evidence,
            "cautions": cautions,
            "data_confidence": data_confidence,
            "note": "This is an estimated compatibility score based on available profile data, not a definitive conclusion.",
        }
    )


def suggest_date_idea(person_a: Any, person_b: Any, budget: str = "medium") -> str:
    """
    Suggest a date idea based on two profiles and a budget level.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "ERROR: Not enough profiles found to suggest a date idea."

    shared_styles = sorted(set(profile_a.get("preferred_date_style", [])) & set(profile_b.get("preferred_date_style", [])))
    shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))

    if shared_styles:
        idea = f"a {shared_styles[0]} date"
    elif shared_interests:
        idea = f"a relaxed conversation around {shared_interests[0]}"
    else:
        idea = "a low-pressure coffee date to learn about each other's expectations"

    return _json(
        {
            "idea": idea,
            "budget": budget or "medium",
            "why": "The suggestion is based on shared preferred_date_style and shared interests.",
        }
    )


def suggest_conversation_topics(person_a: Any, person_b: Any) -> str:
    """
    Suggest conversation topics based on two profiles.
    """
    profile_a = _resolve_profile(person_a)
    profile_b = _resolve_profile(person_b)
    if not profile_a or not profile_b:
        return "ERROR: Not enough profiles found to suggest conversation topics."

    shared_interests = sorted(set(profile_a.get("interests", [])) & set(profile_b.get("interests", [])))
    topics = [f"Shared interest: {item}" for item in shared_interests[:3]]
    topics.extend(
        [
            f"Ask about {profile_b['name']}'s ideal low-pressure date",
            "A weekend activity that feels comfortable for both people",
            "How each person balances work, hobbies, and personal time",
        ]
    )
    return _json({"topics": topics[:5], "tone": "natural, respectful, low-pressure"})


AVAILABLE_TOOLS = {
    "search_profiles": search_profiles,
    "check_dealbreakers": check_dealbreakers,
    "analyze_compatibility": analyze_compatibility,
    "suggest_date_idea": suggest_date_idea,
    "suggest_conversation_topics": suggest_conversation_topics,
}
