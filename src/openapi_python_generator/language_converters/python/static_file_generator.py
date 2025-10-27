"""Generator for static files that are copied to the generated client."""

from typing import List

from ...models import StaticFile


def generate_static_files() -> List[StaticFile]:
    """
    Generate static files that will be copied to the generated client.

    Returns:
        List of StaticFile objects containing file names and content.
    """
    return []
