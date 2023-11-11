from argparse import ArgumentParser
from const import Optionals, Positionals
from custom_argparse import CustomArgparseFormatter

import json

class ArgsParser:
    """Parses Command Line arguments and replaces optional ones with default settings.
    """

    def parse_args(): 
        arg_parser = ArgumentParser(description=ArgsParser.description(), formatter_class=CustomArgparseFormatter)

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


    def description():
        return "Updates configuration of all projects in specified groups within GitLab. \
            \nYou can specify which GitLab settings to configure using appropriate optional arguments. \
            \nCurrently 4 GibLab project configuration sections supported: \
            \nApproval settings`, `Approval rules`, `Protected branches`, `General project settings`. \
            \n\nWritten by Kanat Aidarov (https://github.com/kanataidarov)"

