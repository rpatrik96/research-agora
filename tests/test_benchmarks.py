"""
Tests for benchmark registry validation.
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_DIR = REPO_ROOT / "registry"


@pytest.fixture(scope="session")
def benchmarks_data():
    """Load registry/benchmarks.json."""
    path = REGISTRY_DIR / "benchmarks.json"
    if not path.exists():
        pytest.skip("registry/benchmarks.json not found")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def results_data():
    """Load registry/results.json."""
    path = REGISTRY_DIR / "results.json"
    if not path.exists():
        pytest.skip("registry/results.json not found")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def registry_skill_names():
    """Load all skill names from registry/index.json."""
    path = REGISTRY_DIR / "index.json"
    if not path.exists():
        pytest.skip("registry/index.json not found")
    with open(path) as f:
        data = json.load(f)
    names = set()
    for repo in data.get("repos", []):
        for skill in repo.get("skills", []):
            names.add(skill["name"])
    return names


class TestBenchmarksJson:
    """Tests for registry/benchmarks.json."""

    def test_has_version(self, benchmarks_data):
        assert "version" in benchmarks_data

    def test_has_benchmarks_array(self, benchmarks_data):
        assert "benchmarks" in benchmarks_data
        assert isinstance(benchmarks_data["benchmarks"], list)

    def test_benchmarks_have_required_fields(self, benchmarks_data):
        required = ["id", "name", "repo", "description", "task", "metrics", "primary-metric"]
        for bench in benchmarks_data["benchmarks"]:
            for field in required:
                assert field in bench, f"Benchmark '{bench.get('id', '?')}' missing '{field}'"

    def test_benchmark_ids_unique(self, benchmarks_data):
        ids = [b["id"] for b in benchmarks_data["benchmarks"]]
        assert len(ids) == len(set(ids)), f"Duplicate benchmark IDs: {ids}"

    def test_primary_metric_in_metrics(self, benchmarks_data):
        for bench in benchmarks_data["benchmarks"]:
            assert bench["primary-metric"] in bench["metrics"], (
                f"Benchmark '{bench['id']}': primary-metric '{bench['primary-metric']}' not in metrics"
            )

    def test_relevant_skills_exist(self, benchmarks_data, registry_skill_names):
        for bench in benchmarks_data["benchmarks"]:
            for skill in bench.get("relevant-skills", []):
                assert skill in registry_skill_names, (
                    f"Benchmark '{bench['id']}' references unknown skill: {skill}"
                )


class TestResultsJson:
    """Tests for registry/results.json."""

    def test_has_version(self, results_data):
        assert "version" in results_data

    def test_has_results_array(self, results_data):
        assert "results" in results_data
        assert isinstance(results_data["results"], list)

    def test_result_benchmark_ids_valid(self, results_data, benchmarks_data):
        valid_ids = {b["id"] for b in benchmarks_data["benchmarks"]}
        for result in results_data["results"]:
            assert result["benchmark-id"] in valid_ids, (
                f"Result references unknown benchmark: {result['benchmark-id']}"
            )
