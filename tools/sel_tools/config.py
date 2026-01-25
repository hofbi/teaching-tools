"""SEL Tools config."""

from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[2]

# Git & GitLab Config (this is all you need if you want to customize the config)
GITLAB_SERVER_URL = "https://gitlab.lrz.de/"
RUNNER_ID = 3666
GIT_MAIN_BRANCH = "master"
