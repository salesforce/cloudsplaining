import importlib.metadata

try:
    __version__ = importlib.metadata.version("cloudsplaining")
except Exception:
    # needed for local dev
    __version__ = "0.0.0"
