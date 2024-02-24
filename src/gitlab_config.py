from datetime import datetime, timedelta, timezone
from printer_utils import Printer
from project_settings import ProjectSettings
from urllib.parse import quote_plus

import const
import re
import requests


class GitlabConfig:
    """Updates configuration of all projects in specified groups within GitLab.

    Attributes: 
        args: Arguments object.
        default_branch (str): Desired default branch (if exists) for every GitLab project. 
        printer: Printer object from printer_utils.
        ps: ProjectSettings object.
    """

    def __init__(self, args, default_branch="dev"):
        self.args = args
        self.default_branch = default_branch
        self.printer = Printer()
        self.ps = ProjectSettings(self.args, self.printer)

    def select_project_ids(self):
        """Selects GitLab Ids of projects belonging to GitLab Groups specified in `namespace_paths` CL-argument.  
        :return List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """
        result = []

        if len(self.args["project_slugs"]) > 0:
            for project_slug in self.args["project_slugs"]:
                entry = self.printer.response_json(self.args, "projects/" + quote_plus(
                    f'{self.args["namespace_paths"][0]}/{project_slug}'))
                result.append(entry["id"])
        elif len(self.args["namespace_paths"]) > 0:
            result = [entry["id"] for entry in self.printer.response_json(self.args, "projects")
                      if entry["path_with_namespace"].split("/")[0] in self.args["namespace_paths"]]
        elif len(self.args["project_ids"]) > 0:
            result = self.args["project_ids"]

        return result

    def select_group_ids(self):
        """Selects GitLab Ids of groups specified in `namespace_paths` CL-argument.  
        :return List of GitLab Ids of groups by their names. 
        """
        groups = self.printer.response_json(self.args, "groups")

        return [entry["id"] for entry in groups if entry["path"] in self.args["namespace_paths"]]

    def select_projects_without_description(self):
        """Selects projects without description. 
        """
        projects = self.printer.response_json(self.args, "projects")

        for project in projects:
            if not project["description"]:
                print(project["path_with_namespace"])

    def select_branch_names(self, selected_pids, active=True):
        """Selects Branch names for given {:selected_pids}.
        :selected_pids List of Project Ids to operate on.
        :active If set selects only non-stale branches. Set by default.
        :return List of GitLab Branch names for given Project id.
        """
        response = {}
        for project_id in selected_pids:
            branch_names_url = f'projects/{project_id}/repository/branches'
            response_json = self.printer.response_json(self.args, branch_names_url)

            if active:
                result = [entry["name"] for entry in response_json if not self.__is_stale_branch(entry)]
            else:
                result = [entry["name"] for entry in response_json if self.__is_stale_branch(entry)]

            response[project_id] = result

        return response

    @staticmethod
    def __is_stale_branch(branch_entry, previous_days=const.STALE_BRANCH_DELTA, exclude_branches="dev,main"):
        """Checks if branch that has not had any commits in the previous {:previous_days} days.
        :branch_entry Object containing array of commit objects.
        :previous_days Number of days that branch should not have any new commits. 90 days by default.
        :exclude_branches Branch names to exclude from checking. Dev and main branches not checked by default.
        :return Boolean determining whether branch's last commit not older than specified number of days.
        """
        last_commit_dt = datetime.fromisoformat(branch_entry["commit"]["created_at"])
        previous_days_ago_dt = datetime.now(timezone(timedelta(hours=6))) - timedelta(days=previous_days)
        return previous_days_ago_dt > last_commit_dt and branch_entry["name"] not in exclude_branches.split(",")

    def duplicate_branches_with_new_names(self, selected_pids, branch_names, regex, replacement_str):
        """Creates new branches from {:selected_pids} and {:branch_names} using {:regex} and {:replacement_str}.
        :selected_pids List of Project Ids to operate on.
        :branch_names Names of the branches to duplicate. 
        :regex Regular expression which finds part of branch name to replace when duplicating.
        :replacement_str New part of a branch name. 
        """
        for project_id in selected_pids:
            for branch_name in branch_names:
                create_branch_url = f'{self.args["base_url"]}/projects/{project_id}/repository/branches'
                match = re.compile(regex).search(branch_name)
                if match:
                    new_branch_name = re.sub(regex, replacement_str, branch_name)
                    create_branch_url += f'?branch={new_branch_name}&ref={branch_name}'
                    response = requests.post(create_branch_url, headers=self.args["headers"])
                    self.printer.dump_response(response, project_id, "Duplicated branches", desired_states={201})

    def select_commits_by_branch(self, selected_pids, branch_name):
        """Selects all commits within given {:selected_pids} and {:branch_name}
        :selected_pids List of Project Ids to operate on.
        :branch_name Name of a branch with commits.
        :return Array of commit objects, containing id, message, creation datetime 
        """
        for project_id in selected_pids:
            select_commits_url = f'{self.args["base_url"]}/projects/{project_id}/repository/commits?ref_name={branch_name}'
            response = requests.get(select_commits_url, headers=self.args["headers"])
            return [{"id": entry["id"], "message": entry["message"], "created_at": entry["created_at"]} for entry in
                    response.json()]

    def select_branch_names_with_commits(self, selected_pids, active=False):
        """Selects Branch names for given {:selected_pids} including their commit objects.
        :selected_pids List of Project Ids to operate on.
        :active If set selects only non-stale branches. Unset by default.
        :return List of GitLab Branch names for given Project id and all commit objects within them.
        """
        branch_names = self.select_branch_names(selected_pids, active)
        branches_n_their_commits = {}
        for branch_name in branch_names:
            branches_n_their_commits[branch_name] = self.select_commits_by_branch(selected_pids, branch_name)

        return branches_n_their_commits

    def update_settings(self, selected_pids):
        self.ps.update_approval_settings(selected_pids)
        self.ps.update_approval_rules(selected_pids)
        self.ps.update_project_settings(selected_pids)
        self.ps.update_protected_branches(selected_pids)
        self.ps.update_push_rules(selected_pids)

    def delete_branches_by_regex(self, selected_pids, branch_names, regex):
        """Delete all branches with {:branch_names} within {:selected_pids} using {:regex}.
        :selected_pids List of Project Ids to operate on.
        :branch_names Names of the branches within {:selected_pids}. 
        :regex Regular expression which matches branch name to determine whether to delete given branch.
        """
        for project_id in selected_pids:
            for branch_name in branch_names:
                match = re.compile(regex).search(branch_name)
                if match:
                    delete_branch_url = f'{self.args["base_url"]}/projects/{project_id}/repository/branches/{quote_plus(branch_name)}'
                    response = requests.delete(delete_branch_url, headers=self.args["headers"])
                    print(response)

    def print_response(self):
        self.printer.print_response()

    def select_project_by_id(self, project_id):
        """Selects project's details by its {:project_id}.
        :project_id id of the project to select.
        :return Project's details.
        """
        select_project_url = f'{self.args["base_url"]}/projects/{project_id}'
        response = requests.get(select_project_url, headers=self.args["headers"])

        return response.json()
