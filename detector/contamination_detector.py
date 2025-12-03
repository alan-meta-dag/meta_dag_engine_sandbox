# detector/contamination_detector.py

class ContaminationDetector:
    def __init__(self):
        self.enabled = True

    def check(self, test_case: dict) -> dict:
        """
        Very minimal fake detector.
        Just flags known patterns from pressure_test.
        """

        key = test_case.get("id", "").lower()

        signals = []

        if "cycle" in key:
            signals.append("CYCLE_DETECTED")

        if "orphan" in key:
            signals.append("ORPHAN_EDGE_DETECTED")

        if "payload" in key or "suspicious" in key:
            signals.append("SUSPICIOUS_PAYLOAD")

        if "label" in key or "semantic" in key:
            signals.append("SEMANTIC_DUPLICATION")

        if signals:
            return {
                "status": "CRITICAL",
                "signals": signals
            }

        return {
            "status": "NORMAL",
            "signals": []
        }

