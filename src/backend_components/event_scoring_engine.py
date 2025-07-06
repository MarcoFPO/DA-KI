from typing import Dict, Any, List, Optional
import logging
import datetime

logger = logging.getLogger(__name__)

class EventScoringEngine:
    """
    Berechnet den Event-driven Score für Aktien basierend auf verschiedenen Event-Kategorien.
    """

    def __init__(self):
        # Event-Multiplikatoren aus technical_analysis_requirements.md (Abschnitt 8.8)
        self.multipliers = {
            'earnings': 3.0,
            'fda': 2.0,
            'product': 1.5,
            'ma': 2.0,
            'spinoff': 1.5,
            'conference': 1.0,
            'economic': 1.0
        }

    async def calculate_event_score(self, event_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Berechnet den gesamten Event-Score für eine Aktie.

        Args:
            event_data: Ein Dictionary, das Event-Kategorien auf Listen von Event-Daten abbildet.
                        Beispiel:
                        {
                            "earnings": [...],
                            "fda": [...],
                            # ...
                        }

        Returns:
            Ein Dictionary mit dem Gesamt-Event-Score, individuellen Scores und Details.
        """
        logger.info("Calculating event score...")

        base_scores = {
            'earnings': self._calculate_earnings_score(event_data.get('earnings', [])),
            'fda': self._calculate_fda_score(event_data.get('fda', [])),
            'product': self._calculate_product_score(event_data.get('product', [])),
            'ma': self._calculate_ma_score(event_data.get('ma', [])),
            'spinoff': self._calculate_spinoff_score(event_data.get('spinoff', [])),
            'conference': self._calculate_conference_score(event_data.get('conference', [])),
            'economic': self._calculate_economic_score(event_data.get('economic', []))
        }

        weighted_score = sum(
            base_scores[event] * self.multipliers.get(event, 0)
            for event in base_scores if base_scores[event] != 0
        )

        final_score = self._normalize_score_event_specific(weighted_score, base_scores)

        return {
            'total_event_score': round(final_score, 2),
            'individual_events': base_scores,
            'weighted_events': {k: base_scores[k] * self.multipliers.get(k, 0) for k in base_scores},
            'active_events': [k for k, v in base_scores.items() if v != 0]
        }

    # --- Private Methoden für individuelle Event-Scores ---

    def _calculate_earnings_score(self, earnings_data: List[Dict[str, Any]]) -> int:
        """Berechnet den Earnings Score (-5 bis +5)."""
        score = 0
        # Implementierung der Earnings Scoring-Logik
        # Berücksichtigt: Earnings Surprise History, Analyst Revision Trend, EPS Estimate Dispersion, Guidance Track Record, Preannouncement
        # Beispiel: for event in earnings_data: if event.get('surprise_percentage', 0) > 0: score += 1
        return max(-5, min(5, score))

    def _calculate_fda_score(self, fda_data: List[Dict[str, Any]]) -> int:
        """Berechnet den FDA/Regulatory Approvals Score (-3 bis +5)."""
        score = 0
        # Implementierung der FDA Scoring-Logik
        return max(-3, min(5, score))

    def _calculate_product_score(self, product_data: List[Dict[str, Any]]) -> int:
        """Berechnet den Product Launches Score (-3 bis +5)."""
        score = 0
        # Implementierung der Product Launches Scoring-Logik
        return max(-3, min(5, score))

    def _calculate_ma_score(self, ma_data: List[Dict[str, Any]]) -> int:
        """Berechnet den M&A Activity Score (-2 bis +5)."""
        score = 0
        # Implementierung der M&A Scoring-Logik
        return max(-2, min(5, score))

    def _calculate_spinoff_score(self, spinoff_data: List[Dict[str, Any]]) -> int:
        """Berechnet den Spin-offs/Divestitures Score (0 bis +5)."""
        score = 0
        # Implementierung der Spin-offs Scoring-Logik
        return max(0, min(5, score))

    def _calculate_conference_score(self, conference_data: List[Dict[str, Any]]) -> int:
        """Berechnet den Conference/Presentation Events Score (-1 bis +3)."""
        score = 0
        # Implementierung der Conference Scoring-Logik
        return max(-1, min(3, score))

    def _calculate_economic_score(self, economic_data: List[Dict[str, Any]]) -> int:
        """Berechnet den Economic/Sector Events Score (-2 bis +2)."""
        score = 0
        # Implementierung der Economic Scoring-Logik
        return max(-2, min(2, score))

    def _normalize_score_event_specific(self, value: float, base_scores: Dict[str, int]) -> float:
        """
        Normalisiert den gewichteten Event-Score auf den Bereich von -5 bis +5.
        Verwendet die spezifischen Max/Min-Werte der einzelnen Event-Kategorien.
        """
        # Theoretische Max/Min-Werte basierend auf technical_analysis_requirements.md
        theoretical_max_weighted = (
            5 * self.multipliers['earnings'] +
            5 * self.multipliers['fda'] +
            5 * self.multipliers['product'] +
            5 * self.multipliers['ma'] +
            5 * self.multipliers['spinoff'] +
            3 * self.multipliers['conference'] +
            2 * self.multipliers['economic']
        )
        theoretical_min_weighted = (
            -5 * self.multipliers['earnings'] +
            -3 * self.multipliers['fda'] +
            -3 * self.multipliers['product'] +
            -2 * self.multipliers['ma'] +
            0 * self.multipliers['spinoff'] +
            -1 * self.multipliers['conference'] +
            -2 * self.multipliers['economic']
        )

        if theoretical_max_weighted == theoretical_min_weighted:
            return 0.0

        clipped_value = max(theoretical_min_weighted, min(theoretical_max_weighted, value))
        normalized = (clipped_value - theoretical_min_weighted) / (theoretical_max_weighted - theoretical_min_weighted)
        final_score = normalized * (5 - (-5)) + (-5)

        return round(final_score, 2)

    async def get_status(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Status der EventScoringEngine zurück.
        """
        return {
            "status": "OK",
            "message": "EventScoringEngine ready",
            "last_checked": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "details": {}
        }
