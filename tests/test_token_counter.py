"""Tests for the token counter utility.

This module contains tests for the TokenCounter class and CLI interface.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from token_counter import TokenCounter, main, read_file


class TestTokenCounter:
    """Tests for the TokenCounter class."""

    def test_init_default_pricing(self) -> None:
        """Test initialization with default pricing."""
        counter = TokenCounter()
        pricing = counter.get_model_pricing()

        assert "haiku" in pricing
        assert "sonnet" in pricing
        assert "opus" in pricing

    def test_init_with_config(self, tmp_path: Path) -> None:
        """Test initialization with custom config file."""
        config = {
            "cost_estimates": {
                "haiku": {
                    "input_per_1k": 0.001,
                    "output_per_1k": 0.002,
                    "typical_task_cost": 0.02,
                }
            }
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        counter = TokenCounter(config_path=config_path)
        pricing = counter.get_model_pricing()

        assert pricing["haiku"]["input_per_1k"] == 0.001

    def test_init_with_invalid_config(self, tmp_path: Path) -> None:
        """Test initialization with invalid config falls back to defaults."""
        config_path = tmp_path / "invalid.json"
        config_path.write_text("not valid json")

        counter = TokenCounter(config_path=config_path)
        pricing = counter.get_model_pricing()

        # Should fall back to defaults
        assert "haiku" in pricing
        assert "sonnet" in pricing

    def test_count_tokens_empty_string(self) -> None:
        """Test counting tokens for empty string."""
        counter = TokenCounter()
        assert counter.count_tokens("") == 0

    def test_count_tokens_simple_text(self) -> None:
        """Test counting tokens for simple text."""
        counter = TokenCounter()
        tokens = counter.count_tokens("Hello, world!")

        # Should return a positive number
        assert tokens > 0
        # For simple text, should be reasonable (not wildly large)
        assert tokens < 100

    def test_count_tokens_longer_text(self) -> None:
        """Test counting tokens for longer text."""
        counter = TokenCounter()
        short_text = "Hello"
        long_text = "Hello " * 100

        short_tokens = counter.count_tokens(short_text)
        long_tokens = counter.count_tokens(long_text)

        # Longer text should have more tokens
        assert long_tokens > short_tokens

    def test_estimate_cost_valid_models(self) -> None:
        """Test cost estimation for all valid models."""
        counter = TokenCounter()
        text = "This is a test sentence for cost estimation."

        for model in ["haiku", "sonnet", "opus"]:
            cost = counter.estimate_cost(text, model=model)
            assert cost >= 0
            assert isinstance(cost, float)

    def test_estimate_cost_invalid_model(self) -> None:
        """Test cost estimation raises error for invalid model."""
        counter = TokenCounter()
        text = "Test text"

        with pytest.raises(ValueError, match="Unknown model"):
            counter.estimate_cost(text, model="invalid_model")

    def test_estimate_cost_model_ordering(self) -> None:
        """Test that opus > sonnet > haiku in cost."""
        counter = TokenCounter()
        text = "This is a test sentence for comparing model costs."

        haiku_cost = counter.estimate_cost(text, model="haiku")
        sonnet_cost = counter.estimate_cost(text, model="sonnet")
        opus_cost = counter.estimate_cost(text, model="opus")

        # More expensive models should cost more
        assert opus_cost > sonnet_cost
        assert sonnet_cost > haiku_cost

    def test_estimate_cost_case_insensitive(self) -> None:
        """Test that model names are case-insensitive."""
        counter = TokenCounter()
        text = "Test text"

        lower_cost = counter.estimate_cost(text, model="sonnet")
        upper_cost = counter.estimate_cost(text, model="SONNET")
        mixed_cost = counter.estimate_cost(text, model="Sonnet")

        assert lower_cost == upper_cost == mixed_cost

    def test_estimate_cost_with_output_ratio(self) -> None:
        """Test cost estimation with different output ratios."""
        counter = TokenCounter()
        text = "Test text"

        cost_1x = counter.estimate_cost(text, model="sonnet", output_ratio=1.0)
        cost_2x = counter.estimate_cost(text, model="sonnet", output_ratio=2.0)

        # Higher output ratio should result in higher cost
        assert cost_2x > cost_1x

    def test_get_model_pricing_returns_copy(self) -> None:
        """Test that get_model_pricing returns a copy."""
        counter = TokenCounter()
        pricing1 = counter.get_model_pricing()
        pricing2 = counter.get_model_pricing()

        # Modifying one should not affect the other
        pricing1["haiku"]["input_per_1k"] = 999.0
        assert pricing2["haiku"]["input_per_1k"] != 999.0

    def test_estimate_task_cost_valid_models(self) -> None:
        """Test typical task cost estimation."""
        counter = TokenCounter()

        haiku_cost = counter.estimate_task_cost("haiku")
        sonnet_cost = counter.estimate_task_cost("sonnet")
        opus_cost = counter.estimate_task_cost("opus")

        assert haiku_cost == pytest.approx(0.01)
        assert sonnet_cost == pytest.approx(0.05)
        assert opus_cost == pytest.approx(0.15)

    def test_estimate_task_cost_invalid_model(self) -> None:
        """Test task cost estimation raises error for invalid model."""
        counter = TokenCounter()

        with pytest.raises(ValueError, match="Unknown model"):
            counter.estimate_task_cost("invalid")

    def test_format_cost_report(self) -> None:
        """Test cost report formatting."""
        counter = TokenCounter()
        report = counter.format_cost_report("Test text", model="sonnet")

        assert "Token Count and Cost Report" in report
        assert "sonnet" in report
        assert "Token count:" in report
        assert "Estimated cost:" in report


class TestReadFile:
    """Tests for the read_file function."""

    def test_read_existing_file(self, tmp_path: Path) -> None:
        """Test reading an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, world!")

        content = read_file(test_file)
        assert content == "Hello, world!"

    def test_read_nonexistent_file(self) -> None:
        """Test reading a nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/path/to/file.txt")

    def test_read_file_with_string_path(self, tmp_path: Path) -> None:
        """Test reading a file with string path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        content = read_file(str(test_file))
        assert content == "Test content"


class TestCLI:
    """Tests for the CLI interface."""

    def test_cli_with_text(self, capsys: pytest.CaptureFixture) -> None:
        """Test CLI with --text argument."""
        result = main(["--text", "Hello, world!"])

        assert result == 0
        captured = capsys.readouterr()
        assert "Tokens:" in captured.out
        assert "Estimated cost" in captured.out

    def test_cli_with_file(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test CLI with file argument."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("This is test content.")

        result = main([str(test_file)])

        assert result == 0
        captured = capsys.readouterr()
        assert "Tokens:" in captured.out

    def test_cli_with_model(self, capsys: pytest.CaptureFixture) -> None:
        """Test CLI with --model argument."""
        result = main(["--text", "Test", "--model", "opus"])

        assert result == 0
        captured = capsys.readouterr()
        assert "opus" in captured.out

    def test_cli_json_output(self, capsys: pytest.CaptureFixture) -> None:
        """Test CLI with JSON output."""
        result = main(["--text", "Test", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert "tokens" in output
        assert "estimated_cost_usd" in output
        assert "model" in output

    def test_cli_report_output(self, capsys: pytest.CaptureFixture) -> None:
        """Test CLI with report output."""
        result = main(["--text", "Test", "--report"])

        assert result == 0
        captured = capsys.readouterr()
        assert "Token Count and Cost Report" in captured.out

    def test_cli_no_input_error(self, capsys: pytest.CaptureFixture) -> None:
        """Test CLI error when no input provided."""
        with pytest.raises(SystemExit):
            main([])

    def test_cli_both_inputs_error(self, capsys: pytest.CaptureFixture) -> None:
        """Test CLI error when both file and text provided."""
        with pytest.raises(SystemExit):
            main(["file.txt", "--text", "some text"])

    def test_cli_nonexistent_file(self, capsys: pytest.CaptureFixture) -> None:
        """Test CLI with nonexistent file."""
        result = main(["/nonexistent/file.txt"])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_cli_invalid_model(self, capsys: pytest.CaptureFixture) -> None:
        """Test CLI with invalid model."""
        with pytest.raises(SystemExit):
            main(["--text", "test", "--model", "invalid"])

    def test_cli_output_ratio(self, capsys: pytest.CaptureFixture) -> None:
        """Test CLI with output ratio."""
        result = main(["--text", "Test", "--output-ratio", "2.0", "--json"])

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["output_ratio"] == 2.0


class TestTiktokenFallback:
    """Tests for tiktoken availability and fallback behavior."""

    def test_word_based_estimation_without_tiktoken(self) -> None:
        """Test word-based estimation when tiktoken is not available."""
        counter = TokenCounter()

        # Force word-based estimation
        counter.use_tiktoken = False
        counter.encoding = None

        text = "one two three four five"  # 5 words
        tokens = counter.count_tokens(text)

        # Should be approximately 5 * 1.3 = 6.5, rounded to 6
        assert tokens == 6

    def test_tiktoken_vs_word_estimation(self) -> None:
        """Test that both methods give reasonable results."""
        counter = TokenCounter()

        text = "This is a sample sentence for testing token counting."

        # Get tiktoken result if available
        tiktoken_result = None
        if counter.use_tiktoken:
            tiktoken_result = counter.count_tokens(text)

        # Force word-based estimation
        counter.use_tiktoken = False
        counter.encoding = None
        word_result = counter.count_tokens(text)

        # Both should give positive results
        assert word_result > 0
        if tiktoken_result:
            assert tiktoken_result > 0
            # Results should be in the same ballpark (within 2x)
            ratio = max(tiktoken_result, word_result) / min(tiktoken_result, word_result)
            assert ratio < 2.0


class TestIntegration:
    """Integration tests using actual model-routing.json."""

    @pytest.fixture
    def model_routing_path(self) -> Path:
        """Get the path to the model-routing.json file."""
        return (
            Path(__file__).parent.parent
            / "plugins"
            / "research-agents"
            / "config"
            / "model-routing.json"
        )

    def test_load_from_model_routing(self, model_routing_path: Path) -> None:
        """Test loading pricing from actual model-routing.json."""
        if not model_routing_path.exists():
            pytest.skip("model-routing.json not found")

        counter = TokenCounter(config_path=model_routing_path)
        pricing = counter.get_model_pricing()

        # Verify expected structure
        assert "haiku" in pricing
        assert "sonnet" in pricing
        assert "opus" in pricing

        # Verify pricing values match expected
        assert pricing["haiku"]["typical_task_cost"] == 0.01
        assert pricing["sonnet"]["typical_task_cost"] == 0.05
        assert pricing["opus"]["typical_task_cost"] == 0.15
