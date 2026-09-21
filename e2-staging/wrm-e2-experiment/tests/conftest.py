import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pytest
from wrm_e2.e2_bundle import load_e1_replay_bundle, ROOT


@pytest.fixture(scope="session")
def e1_bundle():
    return load_e1_replay_bundle()
