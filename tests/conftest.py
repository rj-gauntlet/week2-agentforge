"""
Shared pytest fixtures for TDD.
- Use these in unit tests (tools) and integration tests (agent).
- Eval tests can use the same fixtures or load cases from data files.
"""
import os

import pytest
from dotenv import load_dotenv

# Load .env from project root so OPENAI_API_KEY etc. are visible to skipif and tests
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


@pytest.fixture(scope="session")
def project_root():
    """Project root (for loading data files like drug_interactions.json)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def sample_medications():
    """Sample medication lists for drug_interaction_check tests."""
    return [
        ["aspirin", "ibuprofen"],
        ["warfarin", "aspirin"],
        ["lisinopril"],
    ]
