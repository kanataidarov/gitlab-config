import requests
import json
from argparse import ArgumentParser
from collections import defaultdict

from const import clr
from custom_argparse import CustomArgparseFormatter

class GitlabConfig:
    """Updates configuration of all projects in specified groups within GitLab

    Attributes: 
        updated (dict): Gathers all successful responses from GitLab API calls. 
        default_branch (str): Desired default branch (if exists) for every GitLab project. 
    """

    def __init__(self, default_branch="dev"):
        self.updated = defaultdict(dict)
        self.default_branch = default_branch


    def select_project_ids(self, args): 
        """Selects GitLab Ids of projects belonging to GitLab Groups specified in `namespace_paths` CL-argument.  
        :args Command Line arguments, includes defaults of optional arguments. 
        :return List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """
        projects_url = args["base_url"] + "/projects"
        response = requests.get(projects_url, headers=args["headers"])
        if not response.ok: 
            raise Exception("Undesired ({response.status_code}) response from `{projects_url}`")
        projects = response.json()

        return [entry["id"] for entry in projects if entry["path_with_namespace"].split("/")[0] in args["namespace_paths"]]


    def update_approval_settings(self, args, selected_project_ids): 
        """Updates Approval Settings subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_project_ids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """
        approvals_base_url = args["base_url"] + "/projects/{}/approvals"

        for project_id in selected_project_ids: 
            approvals_url = approvals_base_url.format(project_id)

            response = requests.post(approvals_url, headers=args["headers"], data=args["approval_settings"])
            
            self.dump_response(response, project_id, "Approval settings", {201})


    def update_approval_rules(self, args, selected_project_ids): 
        """Updates Approval Rules subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_project_ids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """
        approval_rules_base_url = args["base_url"] + "/projects/{}/approval_rules"

        for project_id in selected_project_ids: 
            approval_rules_url = approval_rules_base_url.format(project_id)

            response = requests.get(approval_rules_url, headers=args["headers"])
            default_rule = [entry for entry in response.json() if entry["rule_type"]=="any_approver"]
            if len(default_rule) == 1: 
                args["approval_rules"]["id"] = default_rule[0]["id"]
                response = requests.put(f'{approval_rules_url}/{args["approval_rules"]["id"]}', headers=args["headers"], data=args["approval_rules"])
            elif len(default_rule) == 0: 
                response = requests.post(approval_rules_url, headers=args["headers"], data=args["approval_rules"])
            else: 
                raise Exception("Project {project_id} cannot contain more than 1 default approval rule")
            
            self.dump_response(response, project_id, "Approval rules", {200, 201})


    def update_protected_branches(self, args, selected_project_ids):
        """Updates Protected Branches subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_project_ids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """
        protected_branches_base_url = args["base_url"] + "/projects/{}/protected_branches"

        for project_id in selected_project_ids: 
            protected_branches_url = protected_branches_base_url.format(project_id)

            response = requests.get(protected_branches_url, headers=args["headers"])
            protected_branches = response.json()

            for candidate in args["protected_branches"]: 
                if len( [branch for branch in protected_branches if branch["name"] == candidate["name"]] ) == 0:
                    protected_branches_url = f'{protected_branches_url}?name={candidate["name"]}\
                        &push_access_level={candidate["push_access_levels"][0]["access_level"]}\
                        &merge_access_level={candidate["merge_access_levels"][0]["access_level"]}\
                        &allow_force_push={candidate["allow_force_push"]}\
                        &code_owner_approval_required={candidate["code_owner_approval_required"]}'
                    response = requests.post(protected_branches_url, headers=args["headers"], data=candidate)
                    self.dump_response(response, project_id, "Protected branches", {201})


    def update_project_settings(self, args, selected_project_ids):
        """Updates overall Project Settings for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_project_ids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """
        project_settings_base_url = args["base_url"] + "/projects/{}"

        for project_id in selected_project_ids: 
            """ TODO: fix bug when defaulted branch does not exist
            default_branch_url = project_settings_base_url.format(str(project_id)+"/repository/branches/"+self.default_branch)
            response = requests.get(default_branch_url, headers=args["headers"])
            if response.status_code == 200:
                if response.json()["name"] == self.default_branch: 
                    args["project_settings"]["default_branch"] = self.default_branch
            """

            project_settings_url = project_settings_base_url.format(project_id)
            response = requests.put(project_settings_url, headers=args["headers"], data=args["project_settings"])

            self.dump_response(response, project_id, "Project settings", {200})


    def dump_response(self, response, project_id, config_name, desired_states={201}): 
        """Gathers successful response into `updated` attribute, otherwise throws errorneus response from GitLab. 
        :response Response obtained from last GitLab API call. 
        :project_id GitLab Id of the project currently being configured. 
        :config_name Name of the section being configured for the project. 
        :desired_states List of response status codes for which to accept dumps, otherwise errorneus response. 
        """
        if response.status_code in desired_states: 
            text = response.text 
            if config_name in self.updated[project_id].keys(): 
                text += f"\n{self.updated[project_id][config_name]}"
            self.updated[project_id][config_name] = text
        else: 
            raise Exception(f"Project {project_id} failed to update. Reason: \n{response.status_code} - {response.text}")

    def print_response(self): 
        """Prints all responses from `updated` attribute."""
        for project_id in self.updated.keys(): 
            print(f"{clr.HDRC}Project {project_id} successfully updated.{clr.DMPC} New configuration parameters are: {clr.RSTC}")
            for config_name in self.updated[project_id].keys(): 
                print(f"{clr.SUBC}{config_name}: \n{clr.DMPC}{self.updated[project_id][config_name]}{clr.RSTC}")


    def parse_args(self): 
        """Parses Command Line arguments and replaces optional ones with default settings."""
        arg_parser = ArgumentParser(description="Updates configuration of all projects in specified groups within GitLab. \
            \nYou can specify which GitLab settings to configure using appropriate optional arguments. \
            \nCurrently 4 GibLab project configuration sections supported: `Approval settings`, `Approval rules`, `Protected branches`, `General project settings`. \
            \n\nWritten by Kanat Aidarov (https://github.com/kanataidarov)", \
            formatter_class=CustomArgparseFormatter)

        # positional arguments
        arg_parser.add_argument("base_url", help="URL of GitLab  e.g `https://git.beeline.kz`")
        arg_parser.add_argument("token", help="Personal Access Token, required to access GitLab API")
        arg_parser.add_argument("namespace_paths", help="List of Groups (comma separated)  e.g `esb-gov,`")

        # optional arguments 
        arg_parser.add_argument("--approval_settings", 
            default='{"reset_approvals_on_push": true, "disable_overriding_approvers_per_merge_request": true, "merge_requests_author_approval": false, "merge_requests_disable_committers_approval": true}', 
            action="store_true", help="Project's approval settings")
        arg_parser.add_argument("--approval_rules", 
            default='{"name": "Any name", "rule_type": "any_approver", "approvals_required": 1}', 
            action="store_true", help="Project's default approval rules")
        arg_parser.add_argument("--protected_branches",
            default='[{"name":"master","push_access_levels":[{"access_level":0,"access_level_description":"No one"}],"merge_access_levels":[{"access_level":40,"access_level_description":"Maintainers"}],"allow_force_push":false,"code_owner_approval_required":false},{"name":"dev","push_access_levels":[{"access_level":0,"access_level_description":"No one"}],"merge_access_levels":[{"access_level":40,"access_level_description":"Maintainers"}],"allow_force_push":false,"code_owner_approval_required":false}]',
            action="store_true", help="Project's protected branches")
        arg_parser.add_argument("--project_settings", 
            default='{"allow_merge_on_skipped_pipeline":false,"only_allow_merge_if_all_discussions_are_resolved":true,"only_allow_merge_if_pipeline_succeeds":true,"remove_source_branch_after_merge":true,"squash_option":"default_on"}',
            action="store_true", help="Project's global settings")

        parsed_args = arg_parser.parse_args()
        
        args = {}
        args["base_url"] = parsed_args.base_url+"/api/v4" 
        args["headers"] = {"PRIVATE-TOKEN": parsed_args.token } 
        args["namespace_paths"] = parsed_args.namespace_paths.split(",") 
        args["approval_settings"] = json.loads(parsed_args.approval_settings)
        args["approval_rules"] = json.loads(parsed_args.approval_rules)
        args["protected_branches"] = json.loads(parsed_args.protected_branches)
        args["project_settings"] = json.loads(parsed_args.project_settings)
        
        return args
