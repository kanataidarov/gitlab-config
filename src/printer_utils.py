from collections import defaultdict
from const import clr, PER_PAGE_COUNT

import global_utils
import requests


class Printer:
    """Utility functions for printing http-responses.

    Attributes:
        updated: Object stores updated records. 
    """

    def __init__(self):
        self.updated = defaultdict(dict)

    @staticmethod
    def response_json(args, path):
        """Gets response as json by specified url.  
        :args Command Line arguments, includes defaults of optional arguments. 
        :path Subdirectory (section) with which to complete url. 
        :return response as json from specified url. 
        """
        final_url = f'{args["base_url"]}/{path}?&per_page={PER_PAGE_COUNT}&page=1'
        response = requests.get(final_url, headers=args["headers"])
        if not response.ok:
            raise Exception(f'Undesired ({response.status_code}) response from `{final_url}`')
        return response.json()

    def dump_response(self, response, project_id, config_name, desired_states={200, 201, 204}):
        """Gathers successful response into `updated` attribute, otherwise throws erroneous response from GitLab.
        :response       - Response obtained from last GitLab API call.
        :project_id     - GitLab id of the project being configured.
        :config_name    - Name of the section being configured for the project.
        :desired_states - List of response status codes for which to accept dumps, otherwise erroneous response.
        """
        if response.status_code in desired_states:
            text = response.text
            if config_name in self.updated[project_id].keys():
                text += f'\n{self.updated[project_id][config_name]}'
            self.updated[project_id][config_name] = text
        else:
            global_utils.fail(project_id, response)

    def print_response(self):
        """Prints all responses from `updated` attribute."""
        for project_id in self.updated.keys():
            print(
                f'{clr.HDRC}Project {project_id} successfully updated.{clr.DMPC} \nNew configuration parameters are: {clr.RSTC}')
            for config_name in self.updated[project_id].keys():
                print(f'{clr.SUBC}{config_name}: \n{clr.DMPC}{self.updated[project_id][config_name]}{clr.RSTC}')
