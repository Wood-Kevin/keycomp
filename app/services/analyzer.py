import os
from groq import Groq

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set")
        _client = Groq(api_key=api_key)
    return _client


def _summarize_character(char: dict) -> str:
    name = char.get("name", "Unknown")
    cls = char.get("class", "Unknown")
    spec = char.get("active_spec_name", "Unknown")
    role = char.get("active_spec_role", "UNKNOWN").lower()
    realm = char.get("realm", "Unknown")
    region = char.get("region", "").upper()

    seasons = char.get("mythic_plus_scores_by_season", [])
    score = seasons[0].get("scores", {}).get("all", 0) if seasons else 0

    recent = char.get("mythic_plus_recent_runs", [])[:3]
    if recent:
        run_lines = []
        for run in recent:
            dungeon = run.get("dungeon", "Unknown")
            level = run.get("mythic_level", "?")
            run_score = run.get("score") or 0
            run_lines.append(f"    - {dungeon} +{level} (score {run_score:.1f})")
        runs_text = "\n".join(run_lines)
    else:
        runs_text = "    - No recent runs on record"

    return (
        f"{name} — {spec} {cls} ({role}) on {realm}-{region}\n"
        f"  Current M+ Score: {score}\n"
        f"  3 most recent runs:\n{runs_text}"
    )


_SYSTEM = (
    "You are a high-end Mythic+ analyst — think tournament realm veteran, "
    "not cheerleader. You give precise, tactically honest breakdowns. "
    "You do not hype groups up. You identify real strengths, real risks, "
    "and give a concrete recommendation. Be direct and specific. "
    "If a comp has a weakness, name it plainly. If a player is the weak "
    "link, say so. Use WoW-literate language — assume the reader knows "
    "what a kick, a stop, an immunity, and a lust are."
)


def analyze_party(characters_data: list[dict]) -> str:
    summaries = "\n\n".join(_summarize_character(c) for c in characters_data)

    prompt = (
        f"Analyze this Mythic+ party:\n\n{summaries}\n\n"
        "Give me a structured breakdown in exactly this format:\n\n"
        "**Composition verdict** (one sentence — is this comp strong, "
        "situational, or flawed for high keys?)\n\n"
        "**Role and utility breakdown** — tank, healer, each DPS. "
        "For each: what do they bring beyond their primary role? "
        "Kicks, immunities, externals, movement, battle rez. Be specific "
        "to the spec, not just the class.\n\n"
        "**Score analysis** — who is the carry, who is the carry candidate, "
        "who might be the ceiling. Be honest if someone is noticeably "
        "behind. What key range does this group realistically push "
        "based on their scores and recent run history?\n\n"
        "**Synergies** — name specific interactions that make this comp "
        "work or not work together. Aug Evoker buffing who? Which "
        "cooldowns stack? What's the kill order strategy?\n\n"
        "**Biggest risk** — one specific thing that could cause this "
        "group to time out or wipe. Not a generic warning — a concrete "
        "scenario based on this exact comp.\n\n"
        "**Recommendation** — one concrete suggested starting key level "
        "and one dungeon from the current pool to start with based on "
        "their recent runs and comp strengths."
    )
    response = _get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content
