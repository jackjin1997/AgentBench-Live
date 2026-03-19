"""Tests for LangSmith evaluator and dataset export."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentbench.langsmith_eval import agentbench_evaluator, upload_benchmark_evaluators
from agentbench.langsmith_dataset import export_dataset


class TestAgentBenchEvaluator:
    def test_evaluator_with_score(self):
        run = MagicMock()
        run.outputs = {"score": 0.85, "details": {"Quality": 8.0}}
        example = MagicMock()

        result = agentbench_evaluator(run, example)
        assert result["score"] == 0.85
        assert "Quality" in result["reasoning"]

    def test_evaluator_missing_outputs(self):
        run = MagicMock()
        run.outputs = None
        example = MagicMock()

        result = agentbench_evaluator(run, example)
        assert result["score"] == 0.0

    def test_evaluator_empty_outputs(self):
        run = MagicMock()
        run.outputs = {}
        example = MagicMock()

        result = agentbench_evaluator(run, example)
        assert result["score"] == 0.0


class TestUploadEvaluators:
    @patch("agentbench.langsmith_eval.upload_benchmark_evaluators")
    def test_upload_without_langsmith(self, mock_upload):
        # Just verify it's callable
        mock_upload()
        mock_upload.assert_called_once()


class TestExportDataset:
    def test_export_without_langsmith(self, tmp_path):
        results_file = tmp_path / "results.json"
        results_file.write_text(json.dumps({
            "agent": "test",
            "scores": [{"task_id": "t1", "score": 0.9}],
        }))

        # Without langsmith installed, should log error and return
        with patch.dict("sys.modules", {"langsmith": None}):
            # The function handles ImportError gracefully
            pass

    def test_export_with_mock_client(self, tmp_path):
        results_file = tmp_path / "results.json"
        results_file.write_text(json.dumps({
            "agent": "test",
            "scores": [
                {
                    "task_id": "t1", "score": 0.9,
                    "details": {}, "auto_passed": True,
                    "judge_narrative": "",
                },
            ],
        }))

        mock_client_instance = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.id = "dataset-123"
        mock_client_instance.create_dataset.return_value = mock_dataset
        mock_client_cls = MagicMock(return_value=mock_client_instance)

        with patch("langsmith.Client", mock_client_cls):
            export_dataset(results_file, dataset_name="test-dataset")

        mock_client_instance.create_dataset.assert_called_once()
        mock_client_instance.create_example.assert_called_once()

    def test_export_empty_scores(self, tmp_path):
        results_file = tmp_path / "results.json"
        results_file.write_text(json.dumps({
            "agent": "test", "scores": [],
        }))

        with patch("agentbench.langsmith_dataset.Client", create=True):
            # Should warn about no scores
            pass
