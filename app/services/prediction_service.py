from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import func, select

from app.db.models import Outcome, Prediction, Transcript, TranscriptMatch
from app.db.repository import Repository


class PredictionService:
    def recompute(self) -> int:
        count = 0
        with Repository() as repo:
            outcomes = list(repo.session.scalars(select(Outcome)))
            total_transcripts = repo.session.scalar(select(func.count(Transcript.id)).where(Transcript.fetch_status == "ok")) or 0
            for o in outcomes:
                avg_mentions = (
                    repo.session.scalar(
                        select(func.avg(TranscriptMatch.adjusted_count)).where(TranscriptMatch.outcome_id == o.id)
                    )
                    or 0.0
                )
                baseline = min(1.0, avg_mentions / max(1, o.threshold_value + 1))
                recent = min(1.0, baseline * 1.2)
                threshold_penalty = max(0.1, 1.0 - (o.threshold_value - 1) * 0.12)
                coverage = min(1.0, total_transcripts / 10)
                model_probability = max(0.01, min(0.99, 0.4 * baseline + 0.25 * recent + 0.2 * threshold_penalty + 0.15 * coverage))
                confidence = max(0.1, min(0.95, 0.3 + coverage * 0.6))
                market_prob = o.implied_probability
                edge = model_probability - market_prob
                reason = (
                    f"baseline={baseline:.2f}, recent={recent:.2f}, threshold_penalty={threshold_penalty:.2f}, coverage={coverage:.2f}"
                )
                repo.replace_prediction(
                    o.id,
                    {
                        "related_event_id": None,
                        "market_probability": market_prob,
                        "model_probability": model_probability,
                        "edge": edge,
                        "confidence_score": confidence,
                        "component_scores_json": json.dumps(
                            {
                                "baseline_frequency_score": baseline,
                                "recent_frequency_score": recent,
                                "threshold_difficulty_score": threshold_penalty,
                                "transcript_coverage_score": coverage,
                            }
                        ),
                        "reason_summary": reason,
                        "predicted_at": datetime.utcnow(),
                    },
                )
                count += 1
        return count

    def list_predictions(self):
        with Repository() as repo:
            return list(repo.session.execute(select(Prediction, Outcome).join(Outcome, Outcome.id == Prediction.outcome_id)).all())
