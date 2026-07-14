"""
Launch the Voron simulation view with project-local Python dependencies.

The workbench can run this file directly from .project.json. It creates a
project-local virtual environment, installs sim/requirements.txt when needed,
then starts the actual Qt/Plotly view in that environment.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import venv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIM_DIR = Path(__file__).resolve().parent
REQUIREMENTS = SIM_DIR / "requirements.txt"
VENV_DIR = PROJECT_ROOT / ".venv"
MARKER = VENV_DIR / ".mercurio-requirements.sha256"
VIEW_SCRIPT = SIM_DIR / "demo_qt.py"
LOG_PATH = SIM_DIR / "launch.log"


def log(message: str) -> None:
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def requirements_digest() -> str:
    return hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()


def ensure_venv() -> Path:
    python = venv_python()
    if not python.exists():
        log(f"creating virtual environment: {VENV_DIR}")
        venv.EnvBuilder(with_pip=True, clear=False).create(VENV_DIR)
    return python


def ensure_requirements(python: Path) -> None:
    if not REQUIREMENTS.exists():
        return

    digest = requirements_digest()
    if MARKER.exists() and MARKER.read_text(encoding="utf-8").strip() == digest:
        log("requirements already installed")
        return

    log(f"installing requirements: {REQUIREMENTS}")
    subprocess.check_call(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "-r",
            str(REQUIREMENTS),
        ],
        cwd=str(PROJECT_ROOT),
    )
    MARKER.write_text(digest, encoding="utf-8")
    log("requirements installed")


def main() -> None:
    LOG_PATH.write_text("", encoding="utf-8")
    log(f"launcher python: {sys.executable}")
    log(f"project root: {PROJECT_ROOT}")

    if os.environ.get("MERCURIO_SIM_BOOTSTRAPPED") == "1":
        log(f"already bootstrapped; executing view: {VIEW_SCRIPT}")
        os.execv(str(venv_python()), [str(venv_python()), "-X", "utf8", str(VIEW_SCRIPT)])

    python = ensure_venv()
    ensure_requirements(python)

    env = os.environ.copy()
    env["MERCURIO_SIM_BOOTSTRAPPED"] = "1"
    env.setdefault("MERCURIO_WORKSPACE", str(PROJECT_ROOT))
    env.setdefault("PYTHONIOENCODING", "utf-8")

    log(f"starting view with: {python}")
    subprocess.check_call(
        [str(python), "-X", "utf8", str(VIEW_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        env=env,
    )


if __name__ == "__main__":
    main()
