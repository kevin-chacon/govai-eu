"""govai — EU AI Act compliance inventory from a software list."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("govai-eu")
except PackageNotFoundError:
    __version__ = "0.0.0"  # fallback when running from source
