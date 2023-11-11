from printer_utils import Printer

import requests

class ProjectSettings:
    """Accesses GitLab API to manipulate project settings. 

    Attributes: 
        args: Arguments object.
        printer: Printer object from printer_utils.
    """

    def __init__(self, args):
        self.args = args
        self.printer = Printer()

    
    def update_approval_settings(self, selected_pids): 
        """Updates Approval Settings subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_pids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """

        for project_id in selected_pids: 
            approvals_url = f"{self.args['base_url']}/projects/{project_id}/approvals"

            response = requests.post(approvals_url, headers=self.args["headers"], data=self.args["approval_settings"])
            
            self.printer.dump_response(response, project_id, "Approval settings", {201})


    def update_approval_rules(self, selected_pids): 
        """Updates Approval Rules subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_pids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """

        for project_id in selected_pids: 
            approval_rules_url = f"{self.args['base_url']}/projects/{project_id}/approval_rules"

            response = requests.get(approval_rules_url, headers=self.args["headers"])
            default_rule = [entry for entry in response.json() if entry["rule_type"]=="any_approver"]
            if len(default_rule) == 1: 
                self.args["approval_rules"]["id"] = default_rule[0]["id"]
                response = requests.put(f'{approval_rules_url}/{self.args["approval_rules"]["id"]}', headers=self.args["headers"], data=self.args["approval_rules"])
            elif len(default_rule) == 0: 
                response = requests.post(approval_rules_url, headers=self.args["headers"], data=self.args["approval_rules"])
            else: 
                raise Exception(f"Project {project_id} cannot contain more than 1 default approval rule")
            
            self.printer.dump_response(response, project_id, "Approval rules", {200, 201})


    def update_protected_branches(self, selected_pids):
        """Updates Protected Branches subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_pids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """
        for project_id in selected_pids: 
            branches_url = f"{self.args['base_url']}/projects/{project_id}/repository/branches"
            protected_branches_url = f"{self.args['base_url']}/projects/{project_id}/protected_branches"

            response = requests.get(branches_url, headers=self.args["headers"])
            branches = response.json()

            response = requests.get(protected_branches_url, headers=self.args["headers"])
            protected_branches = response.json()

            for candidate in self.args["protected_branches"]:
                # if branch exists and its not protected them make candidate protected
                if len( [branch for branch in branches if branch["name"] == candidate["name"]] ) == 1 \
                        and len( [branch for branch in protected_branches if branch["name"] == candidate["name"]] ) == 0:
                    protected_branch_url = f'{protected_branches_url}?name={candidate["name"]}\
                        &push_access_level={candidate["push_access_levels"][0]["access_level"]}\
                        &merge_access_level={candidate["merge_access_levels"][0]["access_level"]}\
                        &allow_force_push={candidate["allow_force_push"]}\
                        &code_owner_approval_required={candidate["code_owner_approval_required"]}'
                    response = requests.post(protected_branch_url, headers=self.args["headers"], data=candidate)
                    self.printer.dump_response(response, project_id, "Protected branches", {201})


    def update_project_settings(self, selected_pids):
        """Updates overall Project Settings for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_pids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """

        for project_id in selected_pids: 
            """ TODO: fix bug when defaulted branch does not exist
            default_branch_url = project_settings_base_url.format(str(project_id)+"/repository/branches/"+self.default_branch)
            response = requests.get(default_branch_url, headers=args["headers"])
            if response.status_code == 200:
                if response.json()["name"] == self.default_branch: 
                    args["project_settings"]["default_branch"] = self.default_branch
            """

            project_settings_url = f"{self.args['base_url']}/projects/{project_id}"
            response = requests.put(project_settings_url, headers=self.args["headers"], data=self.args["project_settings"])

            self.printer.dump_response(response, project_id, "Project settings", {200})
    
