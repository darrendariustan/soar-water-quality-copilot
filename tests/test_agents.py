import os
import sys
import unittest

# Add src/backend to the Python path (same convention as test_cv_tool.py)
sys.path.append(os.path.join(os.path.dirname(__file__), "../src/backend"))

from schemas import (
    WaterQualityAnalysisRequest,
    WaterAppearancePayload,
    WaterTestStripPayload,
)
from agents.master_agent import run_pipeline


def _request(appearance_kwargs, strip_kwargs, location="Test Region"):
    appearance = WaterAppearancePayload(image_url="local://water.jpg", **appearance_kwargs)
    strip = WaterTestStripPayload(image_url="local://strip.jpg", **strip_kwargs)
    return WaterQualityAnalysisRequest(
        user_id="anon-1", location=location, appearance=appearance, test_strip=strip
    )


from unittest.mock import patch

def _mock_retrieve_guidance(contamination_type):
    if "nitrate" in contamination_type.lower() or "chemical" in contamination_type.lower():
        return {"title": "Mock", "summary": "Mock", "steps": ["Use another source"], "sources": ["Mock Source"], "sufficient": False}
    return {"title": "Mock", "summary": "Mock", "steps": ["Boil water for 1 minute", "Settle and filter"], "sources": ["Mock Source"], "sufficient": True}

@patch("agents.aws_retrieval_agent.retrieve_guidance", side_effect=_mock_retrieve_guidance)
class TestAgentGraph(unittest.TestCase):
    def test_safe_water(self, mock_rag):
        req = _request(
            {"clarity_classification": "Clear", "confidence_score": 0.95},
            {
                "ph": 7.2,
                "chlorine_residual_ppm": 1.0,
                "turbidity_ntu": 0.5,
                "nitrate_ppm": 5.0,
                "nitrite_ppm": 0.1,
                "hardness_ppm": 120.0,
                "iron_ppm": 0.05,
                "confidence_score": 0.95,
            },
        )
        result = run_pipeline(req, scenario="safe", scenario_label="Safe Water")
        self.assertEqual(result.overallRisk, "safe")
        self.assertEqual(len(result.parameters), 7)
        self.assertTrue(result.recommendations)
        self.assertTrue(result.sources)

    def test_microbial_outbreak(self, mock_rag):
        req = _request(
            {"clarity_classification": "Cloudy", "confidence_score": 0.8},
            {
                "ph": 7.0,
                "chlorine_residual_ppm": 0.0,
                "turbidity_ntu": 12.0,
                "nitrate_ppm": 5.0,
                "nitrite_ppm": 0.1,
                "hardness_ppm": 120.0,
                "iron_ppm": 0.05,
                "confidence_score": 0.85,
            },
        )
        result = run_pipeline(req, scenario="microbial", scenario_label="Microbiological Outbreak")
        self.assertEqual(result.overallRisk, "unsafe")
        # Boiling SHOULD be recommended for microbial contamination.
        self.assertTrue(any("boil" in r.lower() for r in result.recommendations), msg=f"Recommendations were: {result.recommendations}")

    def test_chemical_contamination_blocks_boiling(self, mock_rag):
        req = _request(
            {"clarity_classification": "Colored", "confidence_score": 0.8},
            {
                "ph": 7.0,
                "chlorine_residual_ppm": 1.0,
                "turbidity_ntu": 1.0,
                "nitrate_ppm": 90.0,  # above WHO 50 mg/L
                "nitrite_ppm": 0.1,
                "hardness_ppm": 120.0,
                "iron_ppm": 0.05,
                "confidence_score": 0.85,
            },
        )
        result = run_pipeline(req, scenario="chemical", scenario_label="Chemical Contamination")
        self.assertEqual(result.overallRisk, "unsafe")
        # No step may recommend boiling chemically contaminated water.
        recommends_boil = any(
            "boil" in r.lower() and not any(n in r.lower() for n in ("do not", "don't", "not "))
            for r in result.recommendations
        )
        self.assertFalse(recommends_boil)
        self.assertTrue(result.warnings)

    def test_low_confidence_flags_manual_entry(self, mock_rag):
        req = _request(
            {"clarity_classification": "Clear", "confidence_score": 0.4},
            {
                "ph": 7.2,
                "chlorine_residual_ppm": 1.0,
                "turbidity_ntu": 0.5,
                "nitrate_ppm": 5.0,
                "nitrite_ppm": 0.1,
                "hardness_ppm": 120.0,
                "iron_ppm": 0.05,
                "confidence_score": 0.4,
            },
        )
        result = run_pipeline(req)
        self.assertLess(result.confidence, 0.6)

    @patch("agents.exa_crawl_agent.search_trusted")
    def test_emergency_fallback_mode_part_8(self, mock_exa, mock_rag):
        mock_exa.return_value = {"used_live": False, "sources": [], "note": "EXA_API_KEY not set"}
        req = _request(
            {"clarity_classification": "Colored", "confidence_score": 0.8},
            {
                "ph": 7.0,
                "chlorine_residual_ppm": 1.0,
                "turbidity_ntu": 1.0,
                "nitrate_ppm": 90.0,
                "nitrite_ppm": 0.1,
                "hardness_ppm": 120.0,
                "iron_ppm": 0.05,
                "confidence_score": 0.85,
            },
        )
        result = run_pipeline(req)
        # Should flag as emergency fallback
        self.assertTrue(result.isEmergencyFallback)
        self.assertIn("exa", result.emergencyFallbackReason)
        # Verify it still returns a valid unsafe recommendation without crashing
        self.assertEqual(result.overallRisk, "unsafe")

if __name__ == "__main__":
    unittest.main()