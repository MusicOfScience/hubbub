"""CSV loading functions for election data."""
import logging
from pathlib import Path
from typing import List

import pandas as pd

from backend.models.candidate import Candidate
from backend.models.booth import Booth

logger = logging.getLogger(__name__)


def load_candidates(path: str) -> List[Candidate]:
    """Load candidates from CSV."""
    try:
        df = pd.read_csv(path)
        return [Candidate.from_dict(row) for _, row in df.iterrows()]
    except FileNotFoundError:
        logger.warning(f"Candidates file not found: {path}")
        return []
    except Exception as e:
        logger.error(f"Error loading candidates: {e}")
        return []


def load_booths(path: str) -> List[Booth]:
    """Load booths from CSV."""
    try:
        df = pd.read_csv(path)
        return [Booth.from_dict(row) for _, row in df.iterrows()]
    except FileNotFoundError:
        logger.warning(f"Booths file not found: {path}")
        return []
    except Exception as e:
        logger.error(f"Error loading booths: {e}")
        return []


def load_live_count(path: str) -> pd.DataFrame:
    """Load live count data from CSV."""
    try:
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        logger.warning(f"Live count file not found: {path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading live count: {e}")
        return pd.DataFrame()


def load_declaration_votes(path: str) -> pd.DataFrame:
    """Load declaration votes from CSV."""
    try:
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        logger.warning(f"Declaration votes file not found: {path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading declaration votes: {e}")
        return pd.DataFrame()


def load_historical_booths(path: str) -> pd.DataFrame:
    """Load historical booth results from CSV."""
    try:
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        logger.warning(f"Historical booths file not found: {path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading historical booths: {e}")
        return pd.DataFrame()
