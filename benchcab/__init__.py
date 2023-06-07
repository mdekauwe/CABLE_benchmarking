import importlib.metadata

try:
    __version__ = importlib.metadata.version("benchcab")
except importlib.metadata.PackageNotFoundError:
    __version__ = ""
    print("Warning: unable to interrogate version string from installed distribution.")
    # Note: cannot re-raise exception here as this will break pytest
    # when running without first installing the package
