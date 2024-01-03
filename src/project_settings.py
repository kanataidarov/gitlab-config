import global_utils
import json
import requests


class ProjectSettings:
    """Accesses GitLab API to manipulate project settings. 

    Attributes: 
        args: Arguments object.
        printer: Printer object from printer_utils.
    """

    def __init__(self, args, printer):
        self.args = args
        self.printer = printer

    
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

            project_settings_url = f'{self.args["base_url"]}/projects/{project_id}'
            response = requests.put(project_settings_url, headers=self.args["headers"], data=json.dumps(self.args["project_settings"]))

            self.printer.dump_response(response, project_id, 'Project settings', {200})


    def update_approval_settings(self, selected_pids): 
        """Updates Approval Settings subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_pids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """

        for project_id in selected_pids: 
            approvals_url = f'{self.args["base_url"]}/projects/{project_id}/approvals'
            response = requests.post(approvals_url, headers=self.args["headers"], data=json.dumps(self.args["approval_settings"]))
            self.printer.dump_response(response, project_id, 'Approval settings', {201})


    def update_approval_rules(self, selected_pids): 
        """Updates Approval Rules subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_pids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """

        for project_id in selected_pids: 
            approval_rules_url = f'{self.args["base_url"]}/projects/{project_id}/approval_rules'

            response = requests.get(approval_rules_url, headers=self.args["headers"])
            default_rule = [entry for entry in response.json() if entry["rule_type"]=="any_approver"]
            if len(default_rule) == 1: 
                self.args["approval_rules"]["id"] = default_rule[0]["id"]
                response = requests.put(f'{approval_rules_url}/{self.args["approval_rules"]["id"]}', \
                                        headers=self.args["headers"], data=json.dumps(self.args["approval_rules"]))
            elif len(default_rule) == 0: 
                response = requests.post(approval_rules_url, headers=self.args["headers"], data=json.dumps(self.args["approval_rules"]))
            else: 
                raise Exception(f'Project {project_id} cannot contain more than 1 default approval rule')
            
            self.printer.dump_response(response, project_id, 'Approval rules', {200, 201})


    def update_protected_branches(self, selected_pids):
        """Updates Protected Branches subsection (in General section) for specified GitLab Ids. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_pids List of GitLab Ids of projects belonging to specified GitLab Groups. 
        """

        for project_id in selected_pids: 
            branches_url = f'{self.args["base_url"]}/projects/{project_id}/repository/branches'
            branches = requests.get(branches_url, headers=self.args["headers"]).json()

            protected_branches_url = f'{self.args["base_url"]}/projects/{project_id}/protected_branches'
            protected_branches = requests.get(protected_branches_url, headers=self.args["headers"]).json()

            for candidate in self.args["protected_branches"]:
                # if candidate branch exists and it's not protected, then add it to protected branches
                if len( [branch for branch in branches if branch["name"] == candidate["name"]] ) == 1 \
                        and len( [branch for branch in protected_branches if branch["name"] == candidate["name"]] ) == 0:
                    
                    self.__add_branch_to_protected(project_id, candidate)

                # if candidate branch exists and it's protected, then update its settings
                if len( [branch for branch in branches if branch["name"] == candidate["name"]] ) == 1 \
                        and len( [branch for branch in protected_branches if branch["name"] == candidate["name"]] ) == 1:
                    
                    self.__clear_all_access_levels(project_id, candidate["name"], protected_branches)
                    self.__update_protected_branch(project_id, candidate)

    def __add_branch_to_protected(self, project_id, candidate_branch):
        """Adds given branch to protected branches as well setting its protection settings.
        :project_id         Id of the project whose branch to update for.
        :candidate_branch   Object of the branch to remove all access levels.
        """
        protected_branch_url = f'{self.args["base_url"]}/projects/{project_id}/protected_branches\
                        ?name={candidate_branch["name"]}\
                        &push_access_level={candidate_branch["push_access_levels"][0]["access_level"]}\
                        &merge_access_level={candidate_branch["merge_access_levels"][0]["access_level"]}\
                        &allow_force_push={candidate_branch["allow_force_push"]}\
                        &code_owner_approval_required={candidate_branch["code_owner_approval_required"]}'.replace(' ', '')
        print(protected_branch_url)
        response = requests.post(protected_branch_url, headers=self.args["headers"])
        self.printer.dump_response(response, project_id, "Protected branches", {201})

    def __clear_all_access_levels(self, project_id, branch_name, protected_branches):
        """Removes all access_level records for a given protected branch.
        :project_id         Id of the project whose branch to update for.
        :branch_name        Name of the branch to remove all access levels.
        :protected_branches List of protected branch objects. 
        """
        protected_branch_url = f'{self.args["base_url"]}/projects/{project_id}/protected_branches/{branch_name}'
        candidate_branch = [branch for branch in protected_branches if branch["name"] == branch_name][0]

        data = '{'

        if candidate_branch["push_access_levels"]:
            allowed_to_push_removals = '['
            for level in candidate_branch["push_access_levels"]:
                allowed_to_push_removals += '{{"id": {level_id}, "_destroy": true}},'.format(level_id=level["id"])
            allowed_to_push_removals = allowed_to_push_removals[:-1] + ']'
            data += '"allowed_to_push": ' + allowed_to_push_removals + ','

        if candidate_branch["merge_access_levels"]:
            allowed_to_merge_removals = '['
            for level in candidate_branch["merge_access_levels"]:
                allowed_to_merge_removals += '{{"id": {level_id}, "_destroy": true}},'.format(level_id=level["id"])
            allowed_to_merge_removals = allowed_to_merge_removals[:-1] + ']'
            data += '"allowed_to_merge": ' + allowed_to_merge_removals + ','

        if candidate_branch["unprotect_access_levels"]:
            allowed_to_merge_removals = '['
            for level in candidate_branch["unprotect_access_levels"]:
                allowed_to_merge_removals += '{{"id": {level_id}, "_destroy": true}},'.format(level_id=level["id"])
            allowed_to_merge_removals = allowed_to_merge_removals[:-1] + ']'
            data += '"allowed_to_unprotect": ' + allowed_to_merge_removals + ','

        data = data[:-1] + '}'
                                    
        response = requests.patch(protected_branch_url, headers=self.args["headers"], data=data)

        if response.status_code != 200: 
            global_utils.fail(project_id, response)
       
        return response
    
    def __update_protected_branch(self, project_id, candidate_branch):
        """Updates protection settings for a given branch.
        :project_id         Id of the project whose branch to update for.
        :candidate_branch   Object of the branch to remove all access levels.
        """
        protected_branch_url = f'{self.args["base_url"]}/projects/{project_id}/protected_branches/{candidate_branch["name"]}'
        
        data = '{'

        if candidate_branch["push_access_levels"]:
            data += '"allowed_to_push": ' + json.dumps(candidate_branch["push_access_levels"]) + ','
        
        if candidate_branch["merge_access_levels"]:
            data += '"allowed_to_merge": ' + json.dumps(candidate_branch["merge_access_levels"]) + ','

        data += '"allow_force_push": false,'
        data += '"code_owner_approval_required": false,'
        
        data = data[:-1] + '}'

        response = requests.patch(protected_branch_url, headers=self.args["headers"], data=data)
        self.printer.dump_response(response, project_id, "Protected branches", {200})


    def select_project_by_setting(self, selected_pids, settings_filter):
        """Selects Project Id satisfying {:settings_filter} from list of {:selected_pids}
        :selected_pids      List of GitLab Ids of projects belonging to specified GitLab Groups.
        :settings_filter    Map of settings to filter from.
        :return             List of projects whose settings match for {:settings_filter}.
        """
        appropriate_projects = []
        for project_id in selected_pids: 
            select_project_url = f'{self.args["base_url"]}/projects/{project_id}'
            project = requests.get(select_project_url, headers=self.args["headers"]).json()

            if self.__is_appropriate_project(project, settings_filter):
                appropriate_projects.append((project["id"], project["path"]))

        return appropriate_projects
    
    def __is_appropriate_project(self, project, settings_filter):
        """Checks if projects settings correlate with {:settings_filter} values.
        :project            Json-object for the project whose settings to check.
        :settings_filter    Map of settings to filter from. Example: `{'merge_method': 'ff', 'squash_option': 'default_off'}`.
        :return             Boolean denoting, whether projects settings match with {:settings_filter} values or not.
        """
        for key, val in settings_filter.items():
            if not project[key] == val: 
                return False
            
        return True

