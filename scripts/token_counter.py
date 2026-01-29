#!/usr/bin/env python3
"""Token counting utility for cost tracking.

This module provides utilities for estimating token counts and API costs
for Claude models used in research-agents.

Usage:
    python scripts/token_counter.py <file_path> [--model sonnet]
    python scripts/token_counter.py --text "some text" [--model haiku]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Try to import tiktoken for accurate token counting
try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class TokenCounter:
    """Utility class for counting tokens and estimating API costs.

    This class provides methods for estimating token counts in text and
    calculating the associated API costs for different Claude models.

    Attributes:
        use_tiktoken: Whether tiktoken is available for accurate counting.
        encoding: The tiktoken encoding if available.

    Example:
        >>> counter = TokenCounter()
        >>> count = counter.count_tokens("Hello, world!")
        >>> cost = counter.estimate_cost("Hello, world!", model="sonnet")
    """

    # Default pricing based on model-routing.json cost_estimates
    # Prices are per 1K tokens
    DEFAULT_PRICING: dict[str, dict[str, float]] = {
        "haiku": {
            "input_per_1k": 0.00025,
            "output_per_1k": 0.00125,
            "typical_task_cost": 0.01,
        },
        "sonnet": {
            "input_per_1k": 0.003,
            "output_per_1k": 0.015,
            "typical_task_cost": 0.05,
        },
        "opus": {
            "input_per_1k": 0.015,
            "output_per_1k": 0.075,
            "typical_task_cost": 0.15,
        },
    }

    # Fallback estimation factor when tiktoken is not available
    # Average English word is approximately 1.3 tokens
    WORD_TO_TOKEN_RATIO: float = 1.3

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize the TokenCounter.

        Args:
            config_path: Optional path to model-routing.json for pricing.
                        If not provided, uses default pricing.
        """
        self.use_tiktoken = TIKTOKEN_AVAILABLE
        self.encoding = None

        if self.use_tiktoken:
            # Use cl100k_base encoding (used by Claude and GPT-4)
            try:
                self.encoding = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.use_tiktoken = False

        # Load pricing from config if provided
        self._pricing = self._load_pricing(config_path)

    def _load_pricing(
        self, config_path: str | Path | None
    ) -> dict[str, dict[str, float]]:
        """Load pricing configuration from model-routing.json.

        Args:
            config_path: Path to the configuration file.

        Returns:
            Dictionary containing pricing information per model.
        """
        if config_path is None:
            return self.DEFAULT_PRICING.copy()

        config_path = Path(config_path)
        if not config_path.exists():
            return self.DEFAULT_PRICING.copy()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            if "cost_estimates" in config:
                return config["cost_estimates"]
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not load config from {config_path}: {e}")

        return self.DEFAULT_PRICING.copy()

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in the given text.

        Uses tiktoken if available for accurate counting, otherwise
        falls back to word-based estimation (words * 1.3).

        Args:
            text: The text to count tokens for.

        Returns:
            Estimated number of tokens.

        Example:
            >>> counter = TokenCounter()
            >>> counter.count_tokens("Hello, world!")
            4  # Approximate, varies by method
        """
        if not text:
            return 0

        if self.use_tiktoken and self.encoding is not None:
            return len(self.encoding.encode(text))

        # Fallback: word-based estimation
        # Split on whitespace and multiply by average token ratio
        words = text.split()
        return int(len(words) * self.WORD_TO_TOKEN_RATIO)

    def estimate_cost(
        self,
        text: str,
        model: str = "sonnet",
        is_input: bool = True,
        output_ratio: float = 1.0,
    ) -> float:
        """Estimate the API cost for processing the given text.

        Args:
            text: The text to estimate cost for.
            model: The model to use for pricing ("haiku", "sonnet", or "opus").
            is_input: Whether this is input (True) or output (False) tokens.
            output_ratio: If is_input=True, multiply input tokens by this ratio
                         to estimate output tokens for total cost calculation.

        Returns:
            Estimated cost in USD.

        Raises:
            ValueError: If the model is not recognized.

        Example:
            >>> counter = TokenCounter()
            >>> counter.estimate_cost("Hello, world!", model="sonnet")
            0.000012  # Approximate
        """
        model = model.lower()
        if model not in self._pricing:
            raise ValueError(
                f"Unknown model: {model}. "
                f"Available models: {list(self._pricing.keys())}"
            )

        tokens = self.count_tokens(text)
        pricing = self._pricing[model]

        if is_input:
            # Calculate input cost
            input_cost = (tokens / 1000) * pricing["input_per_1k"]
            # Estimate output cost based on ratio
            estimated_output_tokens = int(tokens * output_ratio)
            output_cost = (estimated_output_tokens / 1000) * pricing["output_per_1k"]
            return input_cost + output_cost
        else:
            # Output only
            return (tokens / 1000) * pricing["output_per_1k"]

    def get_model_pricing(self) -> dict[str, dict[str, float]]:
        """Return the pricing information for all models.

        Returns:
            Dictionary mapping model names to their pricing details.
            Each model has 'input_per_1k', 'output_per_1k', and
            'typical_task_cost' keys.

        Example:
            >>> counter = TokenCounter()
            >>> pricing = counter.get_model_pricing()
            >>> pricing["sonnet"]["input_per_1k"]
            0.003
        """
        import copy

        return copy.deepcopy(self._pricing)

    def estimate_task_cost(self, model: str = "sonnet") -> float:
        """Get the typical task cost for a model.

        This returns a rough estimate based on typical usage patterns
        as defined in the model-routing.json configuration.

        Args:
            model: The model name ("haiku", "sonnet", or "opus").

        Returns:
            Typical task cost in USD.

        Raises:
            ValueError: If the model is not recognized.
        """
        model = model.lower()
        if model not in self._pricing:
            raise ValueError(
                f"Unknown model: {model}. "
                f"Available models: {list(self._pricing.keys())}"
            )

        return self._pricing[model]["typical_task_cost"]

    def format_cost_report(
        self,
        text: str,
        model: str = "sonnet",
        output_ratio: float = 1.0,
    ) -> str:
        """Generate a formatted cost report for the given text.

        Args:
            text: The text to analyze.
            model: The model to use for pricing.
            output_ratio: Ratio of output to input tokens for estimation.

        Returns:
            A formatted string containing the cost report.
        """
        tokens = self.count_tokens(text)
        cost = self.estimate_cost(text, model=model, output_ratio=output_ratio)
        method = "tiktoken" if self.use_tiktoken else "word-based estimation"

        lines = [
            "=" * 50,
            "Token Count and Cost Report",
            "=" * 50,
            f"Model: {model}",
            f"Counting method: {method}",
            f"Token count: {tokens:,}",
            f"Estimated cost: ${cost:.6f}",
            "-" * 50,
            "Pricing breakdown:",
            f"  Input: ${self._pricing[model]['input_per_1k']:.5f} per 1K tokens",
            f"  Output: ${self._pricing[model]['output_per_1k']:.5f} per 1K tokens",
            f"  Typical task: ${self._pricing[model]['typical_task_cost']:.2f}",
            "=" * 50,
        ]
        return "\n".join(lines)


def read_file(file_path: str | Path) -> str:
    """Read the contents of a file.

    Args:
        file_path: Path to the file to read.

    Returns:
        The file contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path.read_text(encoding="utf-8")


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command line arguments. If None, uses sys.argv.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = argparse.ArgumentParser(
        description="Count tokens and estimate API costs for Claude models.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/token_counter.py paper.tex --model sonnet
    python scripts/token_counter.py --text "Hello, world!" --model haiku
    python scripts/token_counter.py paper.tex --report
        """,
    )

    parser.add_argument(
        "file_path",
        nargs="?",
        help="Path to the file to analyze",
    )
    parser.add_argument(
        "--text",
        "-t",
        type=str,
        help="Text to analyze (instead of file)",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="sonnet",
        choices=["haiku", "sonnet", "opus"],
        help="Model to use for cost estimation (default: sonnet)",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to model-routing.json for custom pricing",
    )
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Print a detailed cost report",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--output-ratio",
        "-o",
        type=float,
        default=1.0,
        help="Ratio of output to input tokens for cost estimation (default: 1.0)",
    )

    parsed_args = parser.parse_args(args)

    # Validate arguments
    if parsed_args.file_path is None and parsed_args.text is None:
        parser.error("Either file_path or --text must be provided")

    if parsed_args.file_path is not None and parsed_args.text is not None:
        parser.error("Cannot specify both file_path and --text")

    try:
        # Get the text to analyze
        if parsed_args.text:
            text = parsed_args.text
            source = "text input"
        else:
            text = read_file(parsed_args.file_path)
            source = parsed_args.file_path

        # Create counter and analyze
        counter = TokenCounter(config_path=parsed_args.config)
        tokens = counter.count_tokens(text)
        cost = counter.estimate_cost(
            text,
            model=parsed_args.model,
            output_ratio=parsed_args.output_ratio,
        )

        # Output results
        if parsed_args.json:
            result: dict[str, Any] = {
                "source": source,
                "model": parsed_args.model,
                "tokens": tokens,
                "estimated_cost_usd": cost,
                "counting_method": "tiktoken" if counter.use_tiktoken else "word-based",
                "output_ratio": parsed_args.output_ratio,
            }
            print(json.dumps(result, indent=2))
        elif parsed_args.report:
            print(
                counter.format_cost_report(
                    text,
                    model=parsed_args.model,
                    output_ratio=parsed_args.output_ratio,
                )
            )
        else:
            print(f"Tokens: {tokens:,}")
            print(f"Estimated cost ({parsed_args.model}): ${cost:.6f}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
