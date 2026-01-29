#!/usr/bin/env python3
"""
Cache Manager for Research Agents Plugin

Provides persistent caching for arXiv queries, research state, and agent results
with configurable TTL and hash-based invalidation.

Usage:
    from scripts.cache_manager import CacheManager

    cache = CacheManager()
    cache.set_cached("arxiv/queries", key, data, ttl=86400)
    result = cache.get_cached("arxiv/queries", key)
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4


@dataclass
class CacheEntry:
    """Represents a cached entry with metadata."""

    version: str
    created_at: str
    expires_at: Optional[str]
    ttl_seconds: Optional[int]
    cache_key: str
    data_type: str
    content_hash: Optional[str]
    data: Any

    def is_expired(self) -> bool:
        """Check if the entry has expired based on TTL."""
        if self.expires_at is None:
            return False
        expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        return datetime.now(timezone.utc) > expiry

    def validate_hash(self, content: str) -> bool:
        """Validate content hash matches stored hash."""
        if self.content_hash is None:
            return True
        computed = hashlib.sha256(content.encode()).hexdigest()[:16]
        return computed == self.content_hash

    def to_dict(self) -> dict:
        """Convert entry to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "ttl_seconds": self.ttl_seconds,
            "cache_key": self.cache_key,
            "data_type": self.data_type,
            "content_hash": self.content_hash,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CacheEntry":
        """Create entry from dictionary."""
        return cls(
            version=d.get("version", "1.0.0"),
            created_at=d["created_at"],
            expires_at=d.get("expires_at"),
            ttl_seconds=d.get("ttl_seconds"),
            cache_key=d["cache_key"],
            data_type=d.get("data_type", "unknown"),
            content_hash=d.get("content_hash"),
            data=d["data"],
        )


@dataclass
class CacheConfig:
    """Configuration for cache manager."""

    cache_dir: Path = field(default_factory=lambda: Path(".research-cache"))
    max_size_mb: int = 100
    version: str = "1.0.0"
    ttl_defaults: dict = field(
        default_factory=lambda: {
            "arxiv_queries": 86400,  # 24 hours
            "arxiv_papers": 604800,  # 7 days
            "state": 0,  # Hash-based only
            "agents": 3600,  # 1 hour
        }
    )
    auto_cleanup: bool = True
    cleanup_threshold_percent: int = 90


class CacheManager:
    """
    Manages the .research-cache/ directory for research-agents plugin.

    Provides methods for caching arXiv queries, research state, and agent results
    with configurable TTL and hash-based invalidation.

    Attributes:
        config: CacheConfig instance with cache settings
        cache_dir: Path to the cache directory

    Example:
        >>> cache = CacheManager()
        >>> cache.set_cached("arxiv/queries", "abc123", {"papers": [...]}, ttl=86400)
        >>> result = cache.get_cached("arxiv/queries", "abc123")
        >>> if result and not result.is_expired():
        ...     print(result.data)
    """

    def __init__(
        self,
        cache_dir: Optional[str | Path] = None,
        config: Optional[CacheConfig] = None,
    ) -> None:
        """
        Initialize the cache manager.

        Args:
            cache_dir: Optional path to cache directory. Defaults to .research-cache/
            config: Optional CacheConfig instance. If not provided, loads from
                   config file or uses defaults.
        """
        if config:
            self.config = config
        else:
            self.config = CacheConfig()

        if cache_dir:
            self.config.cache_dir = Path(cache_dir)

        # Check environment variable override
        env_cache_dir = os.environ.get("RESEARCH_CACHE_DIR")
        if env_cache_dir:
            self.config.cache_dir = Path(env_cache_dir)

        self.cache_dir = self.config.cache_dir
        self._ensure_structure()
        self._load_config()

    def _ensure_structure(self) -> None:
        """Create cache directory structure if it doesn't exist."""
        directories = [
            self.cache_dir / "arxiv" / "queries",
            self.cache_dir / "arxiv" / "papers",
            self.cache_dir / "state" / "papers",
            self.cache_dir / "state" / "sessions",
            self.cache_dir / "agents" / "evidence",
            self.cache_dir / "agents" / "synthesis",
            self.cache_dir / "agents" / "validation",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> None:
        """Load configuration from config file if it exists."""
        config_path = self.cache_dir / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                config_data = json.load(f)
                if "max_size_mb" in config_data:
                    self.config.max_size_mb = config_data["max_size_mb"]
                if "ttl_defaults" in config_data:
                    self.config.ttl_defaults.update(config_data["ttl_defaults"])
                if "auto_cleanup" in config_data:
                    self.config.auto_cleanup = config_data["auto_cleanup"]

    def _get_cache_path(self, category: str, key: str) -> Path:
        """
        Get the full path for a cache entry.

        Args:
            category: Cache category (e.g., "arxiv/queries", "state/papers")
            key: Cache key (hash or identifier)

        Returns:
            Full path to the cache file
        """
        # Sanitize key for filesystem
        safe_key = re.sub(r"[^\w\-.]", "_", key)
        if not safe_key.endswith(".json"):
            safe_key += ".json"
        return self.cache_dir / category / safe_key

    def _get_default_ttl(self, category: str) -> Optional[int]:
        """Get default TTL for a category."""
        if "arxiv/queries" in category:
            return self.config.ttl_defaults.get("arxiv_queries", 86400)
        elif "arxiv/papers" in category:
            return self.config.ttl_defaults.get("arxiv_papers", 604800)
        elif "state" in category:
            return self.config.ttl_defaults.get("state", 0)
        elif "agents" in category:
            return self.config.ttl_defaults.get("agents", 3600)
        return 3600  # Default 1 hour

    @staticmethod
    def compute_hash(content: str) -> str:
        """
        Compute a hash key from content.

        Args:
            content: String content to hash

        Returns:
            First 16 characters of SHA-256 hash
        """
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @staticmethod
    def compute_query_hash(query: str, **params: Any) -> str:
        """
        Compute hash for an arXiv query with parameters.

        Args:
            query: Search query string
            **params: Additional query parameters

        Returns:
            Hash key for the query
        """
        normalized = query.lower().strip()
        param_str = json.dumps(params, sort_keys=True)
        return CacheManager.compute_hash(normalized + param_str)

    @staticmethod
    def generate_session_id() -> str:
        """Generate a new session ID."""
        return str(uuid4())

    def get_cached(
        self,
        category: str,
        key: str,
        validate_content: Optional[str] = None,
    ) -> Optional[CacheEntry]:
        """
        Retrieve a cached entry.

        Args:
            category: Cache category (e.g., "arxiv/queries", "state/papers")
            key: Cache key (hash or identifier)
            validate_content: Optional content to validate hash against

        Returns:
            CacheEntry if found and valid, None otherwise

        Example:
            >>> entry = cache.get_cached("arxiv/queries", "abc123")
            >>> if entry and not entry.is_expired():
            ...     return entry.data
        """
        cache_path = self._get_cache_path(category, key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                data = json.load(f)
            entry = CacheEntry.from_dict(data)

            # Check version compatibility
            if entry.version != self.config.version:
                self.invalidate(f"{category}/{key}")
                return None

            # Check expiration
            if entry.is_expired():
                self.invalidate(f"{category}/{key}")
                return None

            # Validate content hash if provided
            if validate_content and not entry.validate_hash(validate_content):
                self.invalidate(f"{category}/{key}")
                return None

            return entry

        except (json.JSONDecodeError, KeyError, OSError):
            return None

    def set_cached(
        self,
        category: str,
        key: str,
        data: Any,
        ttl: Optional[int] = None,
        content_hash: Optional[str] = None,
        data_type: Optional[str] = None,
    ) -> Path:
        """
        Store data in the cache.

        Args:
            category: Cache category (e.g., "arxiv/queries", "state/papers")
            key: Cache key (hash or identifier)
            data: Data to cache (must be JSON serializable)
            ttl: Time-to-live in seconds. If None, uses category default.
                 If 0, no time-based expiration (hash-based only).
            content_hash: Optional content hash for validation
            data_type: Optional data type identifier

        Returns:
            Path to the created cache file

        Example:
            >>> cache.set_cached(
            ...     "arxiv/queries",
            ...     query_hash,
            ...     {"papers": results},
            ...     ttl=86400
            ... )
        """
        if ttl is None:
            ttl = self._get_default_ttl(category)

        now = datetime.now(timezone.utc)
        expires_at = None
        if ttl and ttl > 0:
            expires_at = (now + timedelta(seconds=ttl)).isoformat().replace("+00:00", "Z")

        entry = CacheEntry(
            version=self.config.version,
            created_at=now.isoformat().replace("+00:00", "Z"),
            expires_at=expires_at,
            ttl_seconds=ttl if ttl and ttl > 0 else None,
            cache_key=f"sha256:{key}",
            data_type=data_type or category.replace("/", "_"),
            content_hash=content_hash,
            data=data,
        )

        cache_path = self._get_cache_path(category, key)
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        with open(cache_path, "w") as f:
            json.dump(entry.to_dict(), f, indent=2)

        # Auto cleanup if enabled and needed
        if self.config.auto_cleanup:
            self._maybe_cleanup()

        return cache_path

    def invalidate(self, cache_path: str) -> bool:
        """
        Invalidate (remove) a specific cache entry.

        Args:
            cache_path: Path relative to cache root (e.g., "arxiv/queries/abc123")

        Returns:
            True if entry was removed, False if it didn't exist

        Example:
            >>> cache.invalidate("arxiv/queries/abc123")
        """
        # Handle with or without .json extension
        if not cache_path.endswith(".json"):
            full_path = self.cache_dir / (cache_path + ".json")
        else:
            full_path = self.cache_dir / cache_path

        if full_path.exists():
            full_path.unlink()
            return True
        return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern.

        Args:
            pattern: Glob pattern relative to cache root (e.g., "arxiv/papers/2401.*")

        Returns:
            Number of entries invalidated

        Example:
            >>> count = cache.invalidate_pattern("arxiv/papers/2401.*")
        """
        count = 0
        for path in self.cache_dir.glob(pattern):
            if path.is_file():
                path.unlink()
                count += 1
        return count

    def clear_category(self, category: str) -> int:
        """
        Clear all entries in a category.

        Args:
            category: Category path (e.g., "arxiv/queries", "agents/evidence")

        Returns:
            Number of entries cleared

        Example:
            >>> cache.clear_category("agents/evidence")
        """
        category_path = self.cache_dir / category
        count = 0
        if category_path.exists():
            for path in category_path.rglob("*.json"):
                path.unlink()
                count += 1
        return count

    def clear_expired(self) -> int:
        """
        Remove all expired cache entries.

        Returns:
            Number of entries removed
        """
        count = 0
        for path in self.cache_dir.rglob("*.json"):
            if path.name == "config.json" or path.name == "index.json":
                continue
            try:
                with open(path) as f:
                    data = json.load(f)
                entry = CacheEntry.from_dict(data)
                if entry.is_expired():
                    path.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError, OSError):
                # Invalid entry, remove it
                path.unlink()
                count += 1
        return count

    def clear_older_than(self, days: int) -> int:
        """
        Remove entries older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of entries removed
        """
        threshold = datetime.now(timezone.utc) - timedelta(days=days)
        count = 0
        for path in self.cache_dir.rglob("*.json"):
            if path.name == "config.json" or path.name == "index.json":
                continue
            try:
                with open(path) as f:
                    data = json.load(f)
                created = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                )
                if created < threshold:
                    path.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError, OSError):
                continue
        return count

    def clear_all(self) -> None:
        """
        Remove all cache entries and recreate structure.

        Example:
            >>> cache.clear_all()
        """
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
        self._ensure_structure()

    def _maybe_cleanup(self) -> None:
        """Run cleanup if cache size exceeds threshold."""
        stats = self.get_stats()
        threshold_bytes = self.config.max_size_mb * 1024 * 1024
        threshold_used = threshold_bytes * (self.config.cleanup_threshold_percent / 100)

        if stats["total_bytes"] > threshold_used:
            # First clear expired
            self.clear_expired()
            # If still over, clear oldest entries
            stats = self.get_stats()
            if stats["total_bytes"] > threshold_used:
                self.clear_older_than(7)

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics including:
            - total_entries: Total number of cache entries
            - total_bytes: Total size in bytes
            - expired_entries: Number of expired entries
            - by_category: Breakdown by category
        """
        stats = {
            "total_entries": 0,
            "total_bytes": 0,
            "expired_entries": 0,
            "by_category": {},
        }

        for path in self.cache_dir.rglob("*.json"):
            if path.name == "config.json" or path.name == "index.json":
                continue

            stats["total_entries"] += 1
            stats["total_bytes"] += path.stat().st_size

            # Get category
            rel_path = path.relative_to(self.cache_dir)
            category = str(rel_path.parent)
            if category not in stats["by_category"]:
                stats["by_category"][category] = {"entries": 0, "bytes": 0}
            stats["by_category"][category]["entries"] += 1
            stats["by_category"][category]["bytes"] += path.stat().st_size

            # Check if expired
            try:
                with open(path) as f:
                    data = json.load(f)
                entry = CacheEntry.from_dict(data)
                if entry.is_expired():
                    stats["expired_entries"] += 1
            except (json.JSONDecodeError, KeyError, OSError):
                stats["expired_entries"] += 1

        return stats

    def list_entries(self, category: Optional[str] = None) -> list[dict]:
        """
        List cache entries with metadata.

        Args:
            category: Optional category to filter by

        Returns:
            List of entry metadata dictionaries
        """
        entries = []
        search_path = self.cache_dir / category if category else self.cache_dir

        for path in search_path.rglob("*.json"):
            if path.name == "config.json" or path.name == "index.json":
                continue

            try:
                with open(path) as f:
                    data = json.load(f)
                entries.append(
                    {
                        "path": str(path.relative_to(self.cache_dir)),
                        "key": data.get("cache_key", "unknown"),
                        "created_at": data.get("created_at"),
                        "expires_at": data.get("expires_at"),
                        "data_type": data.get("data_type"),
                        "size_bytes": path.stat().st_size,
                        "is_expired": CacheEntry.from_dict(data).is_expired(),
                    }
                )
            except (json.JSONDecodeError, KeyError, OSError):
                continue

        return entries


def _format_size(bytes_val: int) -> str:
    """Format bytes as human readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


def main() -> None:
    """CLI entry point for cache management."""
    parser = argparse.ArgumentParser(
        description="Manage research-agents cache",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear cache entries")
    clear_parser.add_argument("--all", action="store_true", help="Clear all cache")
    clear_parser.add_argument("--type", choices=["arxiv", "state", "agents"], help="Clear specific type")
    clear_parser.add_argument("--expired", action="store_true", help="Clear only expired entries")
    clear_parser.add_argument("--older-than", metavar="DAYS", help="Clear entries older than N days (e.g., 7d)")
    clear_parser.add_argument("--dry-run", action="store_true", help="Preview what would be cleared")

    # Invalidate command
    inv_parser = subparsers.add_parser("invalidate", help="Invalidate specific entry")
    inv_parser.add_argument("--key", required=True, help="Cache key to invalidate")

    # Stats command
    subparsers.add_parser("stats", help="Show cache statistics")

    # List command
    list_parser = subparsers.add_parser("list", help="List cache entries")
    list_parser.add_argument("--category", help="Filter by category")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cache = CacheManager()

    if args.command == "clear":
        if args.dry_run:
            if args.expired:
                stats = cache.get_stats()
                print(f"Would clear {stats['expired_entries']} expired entries")
            elif args.all:
                stats = cache.get_stats()
                print(f"Would clear {stats['total_entries']} entries ({_format_size(stats['total_bytes'])})")
            else:
                print("Use --all, --expired, --type, or --older-than")
        elif args.all:
            cache.clear_all()
            print("Cache cleared")
        elif args.type:
            count = cache.clear_category(args.type)
            print(f"Cleared {count} entries from {args.type}")
        elif args.expired:
            count = cache.clear_expired()
            print(f"Cleared {count} expired entries")
        elif args.older_than:
            days = int(args.older_than.rstrip("d"))
            count = cache.clear_older_than(days)
            print(f"Cleared {count} entries older than {days} days")
        else:
            print("Specify --all, --expired, --type, or --older-than")

    elif args.command == "invalidate":
        if cache.invalidate(args.key):
            print(f"Invalidated: {args.key}")
        else:
            print(f"Not found: {args.key}")

    elif args.command == "stats":
        stats = cache.get_stats()
        print("Cache Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Total size: {_format_size(stats['total_bytes'])}")
        print(f"  Expired entries: {stats['expired_entries']}")
        print("  By category:")
        for cat, cat_stats in sorted(stats["by_category"].items()):
            print(f"    {cat}: {cat_stats['entries']} entries ({_format_size(cat_stats['bytes'])})")

    elif args.command == "list":
        entries = cache.list_entries(args.category)
        if not entries:
            print("No entries found")
        else:
            for entry in entries:
                status = "[EXPIRED]" if entry["is_expired"] else ""
                print(f"{entry['path']} {status}")
                print(f"  Key: {entry['key']}")
                print(f"  Created: {entry['created_at']}")
                print(f"  Size: {_format_size(entry['size_bytes'])}")
                print()


if __name__ == "__main__":
    main()
