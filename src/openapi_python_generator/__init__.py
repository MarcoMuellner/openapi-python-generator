"""Python client from an OPENAPI 3.0+ specification in seconds."""

try:
    from importlib.metadata import (
        PackageNotFoundError,  # type: ignore
        version,
    )
except ImportError:  # pragma: no cover
    from importlib_metadata import (
        PackageNotFoundError,  # type: ignore
        version,  # type: ignore
    )

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
