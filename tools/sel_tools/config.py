"""SEL Tools config"""

from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[2]

# File structure
CMAKE_MODULE_PATH = REPO_DIR / "cmake"
AVATAR_PATH = REPO_DIR / "assets" / "repo-avatar.png"
HW_BUILD_FOLDER = "hw_build"

# Git & GitLab Config
GITLAB_SERVER_URL = "https://gitlab.lrz.de/"
RUNNER_ID = 3666
GIT_MAIN_BRANCH = "master"
