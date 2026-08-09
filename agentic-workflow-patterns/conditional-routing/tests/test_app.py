"""Deterministic tests for the conditional-routing graph."""

import unittest
from unittest.mock import Mock, patch

import app


class ConditionalRoutingTests(unittest.TestCase):
    def test_graph_routes_low_energy(self) -> None:
        model = Mock()
        model.invoke.return_value = Mock(content="low")

        with patch.object(app, "get_model", return_value=model):
            result = app.graph.invoke({"input": "I am exhausted"})

        self.assertEqual(result["energy_level"], "low")
        self.assertIn("resting", result["response"])

    def test_classifier_normalizes_verbose_model_output(self) -> None:
        model = Mock()
        model.invoke.return_value = Mock(content="Energy: HIGH")

        with patch.object(app, "get_model", return_value=model):
            result = app.detect_energy_level({"input": "Ready to run"})

        self.assertEqual(result, {"energy_level": "high"})

    def test_classifier_rejects_unknown_route(self) -> None:
        model = Mock()
        model.invoke.return_value = Mock(content="unclear")

        with patch.object(app, "get_model", return_value=model):
            with self.assertRaisesRegex(ValueError, "supported energy level"):
                app.detect_energy_level({"input": "not sure"})


if __name__ == "__main__":
    unittest.main()
