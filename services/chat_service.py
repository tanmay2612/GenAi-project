"""Epic 5b: multi-turn construction engineering assistant."""
from __future__ import annotations

import logging
from typing import Dict, List, Tuple

from core.gemini_client import GeminiClient, GeminiError
from services.weather_service import advisory_summary

log = logging.getLogger(__name__)
MAX_HISTORY_TURNS = 12

SYSTEM_PROMPT = """You are a practical site engineering assistant for construction projects in India.
You help site engineers, supervisors and project managers with: concrete and curing practice (IS 456),
reinforcement and formwork, PPE and site safety (OSHA 1926, BOCW Act), crack and defect triage,
material quantities, scheduling and cost questions in INR.

Style: short, direct answers; use numbered steps for procedures; give units; state the code clause
when you are confident of it and say so when you are not. For anything that affects structural
safety, tell the user to confirm with a licensed structural engineer. Ask one clarifying question
if the request is too vague to answer safely.

Current site context: {weather}"""

# (keywords, answer) used when no API key is set. First match wins.
_KB: List[Tuple[Tuple[str, ...], str]] = [
    (("cur", "moist"), "Curing keeps concrete damp so it can gain strength. IS 456 cl. 13.5 asks for at least 7 days with ordinary Portland cement and at least 10 days with mineral admixtures or blended cement. Use 10 days or more in hot, dry weather. Ponding, wet hessian or curing compound all work; start as soon as the surface can take it without marring."),
    (("slump", "workability"), "IS 456 Table 7 gives typical slump ranges: about 25-75 mm for lightly reinforced sections, 50-100 mm for heavily reinforced sections, and 100-150 mm for trench fill. Do not add water on site to raise slump. Use a plasticiser instead."),
    (("cover",), "Nominal cover to reinforcement (IS 456 Table 16, all members): 20 mm mild exposure, 30 mm moderate, 45 mm severe, 50 mm very severe, 75 mm extreme. Use cover blocks of the same grade as the concrete and check cover before every pour."),
    (("crack",), "For cracks: measure the width with a crack gauge and record date and location. IS 456 cl. 35.3.2 uses 0.3 mm as the general limit. Under 0.3 mm is usually cosmetic; wider or diagonal cracks near supports, or cracks that keep growing, need a structural engineer. Fit tell-tales and re-read weekly."),
    (("formwork", "shuttering", "strip", "deshutter"), "Typical stripping times from IS 456 cl. 11.3 (OPC, about 15 C or above): vertical formwork 16-24 h; slab soffit 3 days with props left; props to slabs up to 4.5 m span 7 days; beam soffit 7 days; props to beams up to 6 m span 14 days. Extend in cold weather or with slower cements."),
    (("ppe", "helmet", "harness", "boot", "vest"), "Minimum PPE on an Indian building site: helmet with chin strap, high-visibility vest, safety boots, and gloves; add eye protection for cutting and grinding. Fall protection (guardrails or a harness on a rated anchor) is needed when working at about 1.8 m (6 ft) or more above the lower level under OSHA 1926.501."),
    (("scaffold",), "Scaffold checklist: sound base plates on firm ground, all standards plumb, ties at regular intervals, full-width platforms with toe boards, guardrails at open edges, safe ladder access, and a dated inspection tag. Inspect before each shift and after any storm."),
    (("trench", "excavat"), "For excavations, OSHA 1926.651-652 requires a protective system (sloping, shoring or a trench box) for trenches 1.5 m (5 ft) or deeper. Keep spoil and equipment back from the edge, provide a ladder within 7.5 m of any worker, and re-inspect after rain."),
    (("cement", "bag", "stack", "storage"), "Store cement on a raised, dry platform away from walls, covered against moisture. IS 4082 advises stacking no higher than 10 bags, and using older stock first. Do not use bags that have hardened into lumps."),
    (("steel", "rebar", "reinforcement", "kg"), "A common thumb rule for RCC buildings is about 3.5-4.5 kg of steel per sq ft of built-up area for houses and 4.5-5.5 kg for offices. Use the Planning tab to scale this for your project, and always take the final figure from the structural drawings and bar bending schedule."),
    (("cost", "budget", "estimate", "rate"), "Open the Planning and Valuation tab and enter the structure type, built-up area, city tier and completion percentage. It returns the budget, spend to date and current asset value in INR. Treat the rates as planning figures and replace them with local quotations before committing."),
    (("rain", "monsoon"), "In heavy rain: isolate temporary power in wet areas, re-inspect trenches before anyone enters, cover fresh concrete and stored cement, and stop work at height. Do not place concrete in heavy rain."),
    (("heat", "hot weather", "summer"), "In extreme heat: pour early morning or evening, keep concrete below roughly 35-38 C using chilled water or ice, start curing immediately, give workers shade, water and rest breaks, and watch for heat illness."),
    (("wind", "crane"), "Suspend crane lifts when wind reaches the manufacturer's limit, typically around 30-35 km/h. Lower the hook, set the jib to weathervane, tie down loose sheets and materials, and keep people off scaffold top decks."),
]

_FALLBACK = ("I'm running in demonstration mode, so I can answer from a built-in set of site-engineering topics: "
             "curing, slump, concrete cover, cracks, formwork stripping times, PPE, scaffolds, excavations, "
             "cement storage, steel quantities, costs and weather protocols. Try asking about one of those, "
             "or add a Gemini API key in the sidebar for open-ended answers.")


def _demo_reply(message: str, weather: str) -> str:
    text = message.lower()
    answer = next((a for keys, a in _KB if any(k in text for k in keys)), _FALLBACK)
    if weather != "Normal" and answer is not _FALLBACK:
        answer += f"\n\nNote: today's condition is set to **{weather}**, so check the weather protocols in this tab as well."
    return answer


def respond(client: GeminiClient, history: List[Dict[str, str]], message: str, weather: str) -> Tuple[str, str]:
    """Return (reply, mode). Falls back to the built-in knowledge base if the live call fails."""
    if client.enabled:
        try:
            system = SYSTEM_PROMPT.format(weather=advisory_summary(weather))
            reply = client.chat(system, history[-MAX_HISTORY_TURNS * 2:], message)
            return reply, "live"
        except GeminiError as exc:
            log.warning("Chat fallback: %s", exc)
            return f"_Live model unavailable ({exc}). Answering from built-in knowledge._\n\n" + _demo_reply(message, weather), "demo"
    return _demo_reply(message, weather), "demo"
