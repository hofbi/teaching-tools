"""Create and manage Gitlab instances."""

import gitlab

from sel_tools.config import GITLAB_SERVER_URL


def create_gitlab_instance(gitlab_token: str) -> gitlab.Gitlab:
    """Create a gitlab instance."""
    return gitlab.Gitlab(GITLAB_SERVER_URL, private_token=gitlab_token)
