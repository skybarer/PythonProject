"""
GitLab API client
"""

import requests
from typing import List, Dict


class GitLabClient:
    """GitLab API client"""

    def __init__(self, gitlab_url: str, private_token: str):
        self.gitlab_url = gitlab_url.rstrip('/')
        self.private_token = private_token
        self.headers = {"PRIVATE-TOKEN": private_token}

    def get_groups(self) -> List[Dict]:
        """Fetch all groups from GitLab"""
        try:
            all_groups = []
            page = 1
            per_page = 100

            while True:
                response = requests.get(
                    f"{self.gitlab_url}/api/v4/groups",
                    headers=self.headers,
                    params={
                        "per_page": per_page,
                        "page": page,
                        "all_available": True,
                        "top_level_only": False,
                        "owned": False,
                        "min_access_level": 10
                    },
                    timeout=30
                )
                response.raise_for_status()
                groups = response.json()

                if not groups:
                    break

                all_groups.extend(groups)

                if len(groups) < per_page:
                    break

                page += 1

            return all_groups
        except Exception as e:
            print(f"Error fetching groups: {e}")
            return []

    def get_group_projects(self, group_id: str) -> List[Dict]:
        """Fetch all projects in a group"""
        try:
            all_projects = []
            page = 1
            per_page = 100

            while True:
                response = requests.get(
                    f"{self.gitlab_url}/api/v4/groups/{group_id}/projects",
                    headers=self.headers,
                    params={
                        "per_page": per_page,
                        "page": page,
                        "include_subgroups": True,
                        "with_shared": True,
                        "archived": False
                    },
                    timeout=30
                )
                response.raise_for_status()
                projects = response.json()

                if not projects:
                    break

                all_projects.extend(projects)

                if len(projects) < per_page:
                    break

                page += 1

            return all_projects
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []

    def get_project_branches(self, project_id: int) -> List[str]:
        """Get all branches for a project"""
        try:
            response = requests.get(
                f"{self.gitlab_url}/api/v4/projects/{project_id}/repository/branches",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            branches = response.json()
            return [b['name'] for b in branches]
        except Exception as e:
            print(f"Error fetching branches: {e}")
            return []