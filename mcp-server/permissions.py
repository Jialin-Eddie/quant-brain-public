"""Permission control for quant-brain MCP server.

Core principle: Claude can READ everything, but can only WRITE to pending/.
Knowledge files are modified exclusively by humans.
"""

from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent

# Directories Claude can read
READABLE_DIRS = [
    "knowledge",
    "templates",
    "workflows",
    "prompts",
    "examples",
    "rules",
    "tools",
    "pending",
]

# Directory Claude can write to (suggestions only)
WRITABLE_DIR = "pending"


def validate_read_path(relative_path: str) -> Optional[Path]:
    """Validate and resolve a read path. Returns None if access denied."""
    full_path = (PROJECT_ROOT / relative_path).resolve()

    # Must be within project root
    if not full_path.is_relative_to(PROJECT_ROOT.resolve()):
        return None

    # Must be in a readable directory
    parts = Path(relative_path).parts
    if not parts or parts[0] not in READABLE_DIRS:
        return None

    if not full_path.exists():
        return None

    return full_path


def validate_write_path(relative_path: str) -> Optional[Path]:
    """Validate a write path. Only pending/ is writable. Returns None if denied."""
    full_path = (PROJECT_ROOT / relative_path).resolve()

    if not full_path.is_relative_to(PROJECT_ROOT.resolve()):
        return None

    parts = Path(relative_path).parts
    if not parts or parts[0] != WRITABLE_DIR:
        return None

    return full_path


def is_knowledge_path(relative_path: str) -> bool:
    """Check if a path points to the knowledge directory."""
    return Path(relative_path).parts[0] == "knowledge" if Path(relative_path).parts else False
