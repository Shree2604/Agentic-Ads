from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_feedback_insights(
    db: AsyncIOMotorDatabase,
    platform: str,
    tone: Optional[str] = None,
    limit: int = 15,
) -> Dict[str, Any]:
    """Aggregate recent feedback signals for a given platform/tone."""
    query: Dict[str, Any] = {"platform": platform}
    if tone:
        query["tone"] = tone

    cursor = (
        db.feedback.find(query)
        .sort("_id", -1)
        .limit(limit)
    )
    feedback_docs: List[Dict[str, Any]] = await cursor.to_list(length=limit)

    if not feedback_docs:
        return {
            "avg_rating": None,
            "total_samples": 0,
            "positive_highlights": [],
            "improvement_suggestions": [],
            "common_keywords": [],
            "summary": "No recent feedback available."
        }

    ratings = [doc.get("rating", 0) for doc in feedback_docs if isinstance(doc.get("rating", None), (int, float))]
    avg_rating = sum(ratings) / len(ratings) if ratings else None

    positive_highlights = [doc.get("message", "") for doc in feedback_docs if doc.get("rating", 0) >= 4][:3]
    improvement_suggestions = [doc.get("message", "") for doc in feedback_docs if doc.get("rating", 0) <= 2][:3]

    # Collect simple keyword signals from feedback tags/messages
    keyword_counter: Counter[str] = Counter()
    for doc in feedback_docs:
        message = doc.get("message", "")
        tags = doc.get("tags", [])
        words = []
        if isinstance(message, str):
            words.extend(
                word.lower()
                for word in message.split()
                if len(word) > 3
            )
        if isinstance(tags, list):
            words.extend(tag.lower() for tag in tags if isinstance(tag, str))
        keyword_counter.update(words)

    common_keywords = [word for word, _ in keyword_counter.most_common(5)]

    summary_parts = []
    if avg_rating is not None:
        summary_parts.append(f"Avg rating last {len(feedback_docs)} entries: {avg_rating:.1f}/5")
    if positive_highlights:
        summary_parts.append("Top praise: " + "; ".join(positive_highlights[:2]))
    if improvement_suggestions:
        summary_parts.append("Top fixes: " + "; ".join(improvement_suggestions[:2]))

    summary = " | ".join(summary_parts) if summary_parts else "Feedback captured for future refinement."

    return {
        "avg_rating": avg_rating,
        "total_samples": len(feedback_docs),
        "positive_highlights": positive_highlights,
        "improvement_suggestions": improvement_suggestions,
        "common_keywords": common_keywords,
        "summary": summary,
    }
