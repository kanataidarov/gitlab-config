import requests
import json
from argparse import ArgumentParser
from collections import defaultdict
import csv

from const import clr, Roles, Optionals, Positionals
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
        self.roles = defaultdict(str)


    def select_project_ids(self, args): 
        """Selects GitLab Ids of projects belonging to GitLab Groups specified in `namespace_paths` CL-argument.  
        :args Command Line arguments, includes defaults of optional arguments. 
        :return List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """
        result = []

        if len(args["namespace_paths"]) > 0: 
            result = [entry["id"] for entry in self.response_json(args, "projects") 
                if entry["path_with_namespace"].split("/")[0] in args["namespace_paths"]]
        elif len(args["project_ids"]) > 0:
            result = args["project_ids"]

        return result


    def update_approval_settings(self, args, selected_project_ids): 
        """Updates Approval Settings subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_project_ids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """

        for project_id in selected_project_ids: 
            approvals_url = f"{args['base_url']}/projects/{project_id}/approvals"

            response = requests.post(approvals_url, headers=args["headers"], data=args["approval_settings"])
            
            self.dump_response(response, project_id, "Approval settings", {201})


    def update_approval_rules(self, args, selected_project_ids): 
        """Updates Approval Rules subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_project_ids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """

        for project_id in selected_project_ids: 
            approval_rules_url = f"{args['base_url']}/projects/{project_id}/approval_rules"

            response = requests.get(approval_rules_url, headers=args["headers"])
            default_rule = [entry for entry in response.json() if entry["rule_type"]=="any_approver"]
            if len(default_rule) == 1: 
                args["approval_rules"]["id"] = default_rule[0]["id"]
                response = requests.put(f'{approval_rules_url}/{args["approval_rules"]["id"]}', headers=args["headers"], data=args["approval_rules"])
            elif len(default_rule) == 0: 
                response = requests.post(approval_rules_url, headers=args["headers"], data=args["approval_rules"])
            else: 
                raise Exception(f"Project {project_id} cannot contain more than 1 default approval rule")
            
            self.dump_response(response, project_id, "Approval rules", {200, 201})


    def update_protected_branches(self, args, selected_project_ids):
        """Updates Protected Branches subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_project_ids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """
        for project_id in selected_project_ids: 
            branches_url = f"{args['base_url']}/projects/{project_id}/repository/branches"
            protected_branches_url = f"{args['base_url']}/projects/{project_id}/protected_branches"

            response = requests.get(branches_url, headers=args["headers"])
            branches = response.json()

            response = requests.get(protected_branches_url, headers=args["headers"])
            protected_branches = response.json()

            for candidate in args["protected_branches"]:
                # if branch exists and its not protected them make candidate protected
                if len( [branch for branch in branches if branch["name"] == candidate["name"]] ) == 1 \
                        and len( [branch for branch in protected_branches if branch["name"] == candidate["name"]] ) == 0:
                    protected_branch_url = f'{protected_branches_url}?name={candidate["name"]}\
                        &push_access_level={candidate["push_access_levels"][0]["access_level"]}\
                        &merge_access_level={candidate["merge_access_levels"][0]["access_level"]}\
                        &allow_force_push={candidate["allow_force_push"]}\
                        &code_owner_approval_required={candidate["code_owner_approval_required"]}'
                    response = requests.post(protected_branch_url, headers=args["headers"], data=candidate)
                    self.dump_response(response, project_id, "Protected branches", {201})


    def update_project_settings(self, args, selected_project_ids):
        """Updates overall Project Settings for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_project_ids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """

        for project_id in selected_project_ids: 
            """ TODO: fix bug when defaulted branch does not exist
            default_branch_url = project_settings_base_url.format(str(project_id)+"/repository/branches/"+self.default_branch)
            response = requests.get(default_branch_url, headers=args["headers"])
            if response.status_code == 200:
                if response.json()["name"] == self.default_branch: 
                    args["project_settings"]["default_branch"] = self.default_branch
            """

            project_settings_url = f"{args['base_url']}/projects/{project_id}"
            response = requests.put(project_settings_url, headers=args["headers"], data=args["project_settings"])

            self.dump_response(response, project_id, "Project settings", {200})


    def csv_group_members(self, args, selected_group_ids, out_path="Members.csv"): 
        """Exports members of specified groups into csv. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_group_ids List of Ids for selected Gitlab Groups.
        :out_path Path to the output file in `csv` format.  
        """
        file = open(out_path, mode="w")
        writer = csv.writer(file, delimiter=";")
        for group_id in selected_group_ids: 
            members = self.response_json(args, f"groups/{group_id}/pending_members")
            
            print(len(members))
            for member in members: 
                writer.writerow([ member["username"], Roles.TABLE[int(member["access_level"])] ])

        file.close()

    
    def projects_without_description(self, args): 
        projects = self.response_json(args, "projects")

        for project in projects:
            if not project["description"]:
                print(project["path_with_namespace"])

    
    def select_group_ids(self, args): 
        """Selects GitLab Ids of groups specified in `namespace_paths` CL-argument.  
        :args Command Line arguments, includes defaults of optional arguments. 
        :return List of GitLab Ids of groups by their names. 
        """
        groups = self.response_json(args, "groups")

        return [entry["id"] for entry in groups if entry["path"] in args["namespace_paths"]]


    def response_json(self, args, path): 
        """Gets response as json by specified url.  
        :args Command Line arguments, includes defaults of optional arguments. 
        :path Subdirectory (section) with which to complete url. 
        :return response as json from specified url. 
        """
        final_url = f"{args['base_url']}/{path}"
        response = requests.get(final_url, headers=args["headers"])
        if not response.ok: 
            raise Exception(f"Undesired ({response.status_code}) response from `{final_url}`")
        return response.json()

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
        arg_parser.add_argument(Positionals.BASE_URL["name"], help=Positionals.BASE_URL["help"])
        arg_parser.add_argument(Positionals.TOKEN["name"], help=Positionals.TOKEN["help"])

        # optional arguments 
        arg_parser.add_argument(Optionals.NAMESPACE_PATHS["name"], default=Optionals.NAMESPACE_PATHS["default"], type=str, help=Optionals.NAMESPACE_PATHS["help"])
        arg_parser.add_argument(Optionals.PROJECT_IDS["name"], default=Optionals.PROJECT_IDS["default"], type=str, help=Optionals.PROJECT_IDS["help"])
        arg_parser.add_argument(Optionals.APPROVAL_SETTINGS["name"], default=Optionals.APPROVAL_SETTINGS["default"], type=str, help=Optionals.APPROVAL_SETTINGS["help"])
        arg_parser.add_argument(Optionals.APPROVAL_RULES["name"], default=Optionals.APPROVAL_RULES["default"], type=str, help=Optionals.APPROVAL_RULES["help"])
        arg_parser.add_argument(Optionals.PROTECTED_BRANCHES["name"], default=Optionals.PROTECTED_BRANCHES["default"], type=str, help=Optionals.PROTECTED_BRANCHES["help"])
        arg_parser.add_argument(Optionals.PROJECT_SETTINGS["name"], default=Optionals.PROJECT_SETTINGS["default"], type=str, help=Optionals.PROJECT_SETTINGS["help"])

        parsed_args = arg_parser.parse_args()
        
        args = {}
        args["base_url"] = parsed_args.base_url+"/api/v4"
        args["headers"] = {"PRIVATE-TOKEN": parsed_args.token }
        args["namespace_paths"] = list(filter(None, parsed_args.namespace_paths.split(",")))
        args["project_ids"] = list(filter(None, parsed_args.project_ids.split(",")))
        args["approval_settings"] = json.loads(parsed_args.approval_settings)
        args["approval_rules"] = json.loads(parsed_args.approval_rules)
        args["protected_branches"] = json.loads(parsed_args.protected_branches)
        args["project_settings"] = json.loads(parsed_args.project_settings)

        if all(len(entries)>0 for entries in (args["namespace_paths"], args["project_ids"])):
            arg_parser.error("Arguments `namespace_paths` and `project_ids` are mutually exclusive.")
        
        return args
