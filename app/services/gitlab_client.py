"""
GitLab API client with improved error handling
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
        """Fetch all groups from GitLab with better error handling"""
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

                # Better error handling for 401 and 403
                if response.status_code == 401:
                    print(f"❌ Authentication failed! Token is invalid or expired.")
                    print(f"   Please create a new token with 'api' scope at:")
                    print(f"   {self.gitlab_url}/-/profile/personal_access_tokens")
                    print(f"   Required scopes: api, read_api, read_repository")
                    return []
                elif response.status_code == 403:
                    print(f"❌ Access forbidden! Token doesn't have required permissions.")
                    print(f"   Required scopes: api, read_api, read_repository")
                    print(f"   Please create a new token at:")
                    print(f"   {self.gitlab_url}/-/profile/personal_access_tokens")
                    return []

                response.raise_for_status()
                groups = response.json()

                if not groups:
                    break

                all_groups.extend(groups)

                if len(groups) < per_page:
                    break

                page += 1

            print(f"✅ Successfully loaded {len(all_groups)} groups")
            return all_groups

        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error fetching groups: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Status code: {e.response.status_code}")
                print(f"   Response: {e.response.text[:200]}")
            return []
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: Unable to connect to {self.gitlab_url}")
            print(f"   Please check your GitLab URL and internet connection")
            return []
        except requests.exceptions.Timeout:
            print(f"❌ Timeout Error: Request took too long")
            return []
        except Exception as e:
            print(f"❌ Error fetching groups: {e}")
            return []

    def get_group_projects(self, group_id: str) -> List[Dict]:
        """Fetch all projects in a group with error handling"""
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

                # Handle errors
                if response.status_code == 401:
                    print(f"❌ Authentication failed while fetching projects")
                    return []
                elif response.status_code == 403:
                    print(f"❌ Access forbidden to group {group_id}")
                    return []
                elif response.status_code == 404:
                    print(f"❌ Group {group_id} not found")
                    return []

                response.raise_for_status()
                projects = response.json()

                if not projects:
                    break

                all_projects.extend(projects)

                if len(projects) < per_page:
                    break

                page += 1

            return all_projects

        except requests.exceptions.HTTPError as e:
            print(f"❌ Error fetching projects: {e}")
            return []
        except Exception as e:
            print(f"❌ Error fetching projects for group {group_id}: {e}")
            return []

    def get_project_branches(self, project_id: int) -> List[str]:
        """Get all branches for a project with error handling"""
        try:
            response = requests.get(
                f"{self.gitlab_url}/api/v4/projects/{project_id}/repository/branches",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 401:
                print(f"❌ Authentication failed while fetching branches")
                return []
            elif response.status_code == 403:
                print(f"❌ Access forbidden to project {project_id}")
                return []
            elif response.status_code == 404:
                print(f"❌ Project {project_id} not found or has no branches")
                return []

            response.raise_for_status()
            branches = response.json()
            return [b['name'] for b in branches]

        except Exception as e:
            print(f"❌ Error fetching branches: {e}")
            return []