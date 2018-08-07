"""Utilities for creating test doubles (mocks, fakes, stubs, etc.)."""


class GenericNamespace(object):
    """Create a namespace with provided kwargs."""

    def __init__(self, **kwargs):
        """Set an instance attribute for each key/value pair in kwargs."""
        for key, value in kwargs.items():
            setattr(self, key, value)
