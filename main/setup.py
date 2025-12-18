"""Setup paths and environment configuration."""

from pathlib import Path
import os
import sys


def setup_paths():
    """Setup project paths and environment variables."""
    ROOT = Path(__file__).parent.parent
    os.environ["PROJECT_ROOT"] = str(ROOT)
    
    # Add ormlib to path
    ormlib_path = ROOT.parent / "libs" / "grepx-orm-libs"
    if str(ormlib_path) not in sys.path:
        sys.path.insert(0, str(ormlib_path))
    
    return ROOT

