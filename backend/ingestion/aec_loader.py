"""AEC data loading functions."""
import json
import logging
from pathlib import Path
from typing import Tuple

from backend.models.election import Election

logger = logging.getLogger(__name__)


def load_election_config(path: str) -> Election:
    """Load election configuration from JSON file."""
    with open(path, "r") as f:
        config_dict = json.load(f)
    return Election.from_dict(config_dict)


def validate_config(config_dict: dict) -> bool:
    """Validate election config has required fields."""
    required = [
        "election_id", "electorate", "state", "level",
        "election_date", "enrolled_voters", "tcp_candidates", "candidates"
    ]
    for field in required:
        if field not in config_dict:
            logger.error(f"Missing required field: {field}")
            return False
    if len(config_dict.get("tcp_candidates", [])) != 2:
        logger.error("tcp_candidates must have exactly 2 entries")
        return False
    if len(config_dict.get("candidates", [])) < 2:
        logger.error("Must have at least 2 candidates")
        return False
    return True


def parse_tcp_candidates(config: Election) -> Tuple[str, str]:
    """Return the two TCP candidate IDs."""
    if len(config.tcp_candidates) != 2:
        raise ValueError("Expected exactly 2 TCP candidates")
    return config.tcp_candidates[0], config.tcp_candidates[1]
