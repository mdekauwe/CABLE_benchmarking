from pathlib import Path
import tempfile
import os

from benchcab.scripts import benchtree

def test_create_minbenchtree():
    """Test the min. directory tree is created"""

    mydir = Path.cwd()
    with tempfile.TemporaryDirectory() as td:
        # Get into the temporary directory to test creating the directory structure
        os.chdir(td)

        print(f"In the directory: {td}")
        tb = benchtree.BenchTree(Path(td))
        tb.create_minbenchtree()

        cwd=Path.cwd()
        print(f"cwd path: {cwd}")
        paths_to_create=[
            (cwd/"src").is_dir(),
            (cwd/"runs").is_dir(),
        ]
        assert all(paths_to_create)
    