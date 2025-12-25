"""
Pytest Configuration and Fixtures

This module provides shared fixtures for all tests.
"""

import pytest


@pytest.fixture
def sample_item() -> dict:
    """Provide a sample item for testing."""
    return {
        "id": "test-item-1",
        "name": "Test Item",
        "description": "A test item for unit tests",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_items() -> list[dict]:
    """Provide a list of sample items for testing."""
    return [
        {
            "id": "test-item-1",
            "name": "Test Item 1",
            "description": "First test item",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "id": "test-item-2",
            "name": "Test Item 2",
            "description": "Second test item",
            "created_at": "2024-01-02T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        },
    ]
