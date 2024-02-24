from argparse import ArgumentParser
from const import Optionals, Positionals
from custom_argparse import CustomArgparseFormatter

import json


def parse_args():
    arg_parser = ArgumentParser(description=description(), formatter_class=CustomArgparseFormatter)

    # positional arguments
    arg_parser.add_argument(Positionals.BASE_URL["name"], help=Positionals.BASE_URL["help"])
    arg_parser.add_argument(Positionals.TOKEN["name"], help=Positionals.TOKEN["help"])
    arg_parser.add_argument(Positionals.DEBUG["name"], help=Positionals.DEBUG["help"])

    # optional arguments
    arg_parser.add_argument(Optionals.NAMESPACE_PATHS["name"], default=Optionals.NAMESPACE_PATHS["default"], type=str, help=Optionals.NAMESPACE_PATHS["help"])
    arg_parser.add_argument(Optionals.PROJECT_IDS["name"], default=Optionals.PROJECT_IDS["default"], type=str, help=Optionals.PROJECT_IDS["help"])
    arg_parser.add_argument(Optionals.PROJECT_SLUGS["name"], default=Optionals.PROJECT_SLUGS["default"], type=str, help=Optionals.PROJECT_SLUGS["help"])
    arg_parser.add_argument(Optionals.APPROVAL_SETTINGS["name"], default=Optionals.APPROVAL_SETTINGS["default"], type=str, help=Optionals.APPROVAL_SETTINGS["help"])
    arg_parser.add_argument(Optionals.APPROVAL_RULES["name"], default=Optionals.APPROVAL_RULES["default"], type=str, help=Optionals.APPROVAL_RULES["help"])
    arg_parser.add_argument(Optionals.PROTECTED_BRANCHES["name"], default=Optionals.PROTECTED_BRANCHES["default"], type=str, help=Optionals.PROTECTED_BRANCHES["help"])
    arg_parser.add_argument(Optionals.PROJECT_SETTINGS["name"], default=Optionals.PROJECT_SETTINGS["default"], type=str, help=Optionals.PROJECT_SETTINGS["help"])
    arg_parser.add_argument(Optionals.PUSH_RULES["name"], default=Optionals.PUSH_RULES["default"], type=str, help=Optionals.PUSH_RULES["help"])

    parsed_args = arg_parser.parse_args()

    args = {"base_url": parsed_args.base_url + "/api/v4",
            "headers": {"PRIVATE-TOKEN": parsed_args.token, "Content-Type": "application/json"},
            "debug": ArgsParser.to_bool(parsed_args.debug),
            "namespace_paths": list(filter(None, parsed_args.namespace_paths.split(","))),
            "project_ids": list(filter(None, parsed_args.project_ids.split(","))),
            "project_slugs": list(filter(None, parsed_args.project_slugs.split(","))),
            "approval_settings": json.loads(parsed_args.approval_settings),
            "approval_rules": json.loads(parsed_args.approval_rules),
            "protected_branches": json.loads(parsed_args.protected_branches),
            "project_settings": json.loads(parsed_args.project_settings),
            "push_rule_regex": parsed_args.push_rule_regex}

    if all(len(entries) > 0 for entries in (args["namespace_paths"], args["project_ids"])):
        arg_parser.error("Arguments `namespace_paths`, `project_ids` and `project_slugs` are mutually exclusive.")

    if args["project_slugs"] and not args["namespace_paths"]:
        arg_parser.error("Argument `project_slugs` should be specified with `namespace_paths` argument.")

    return args


def description():
    return "Updates configuration of all projects in specified groups within GitLab. \
        \nYou can specify which GitLab settings to configure using appropriate optional arguments. \
        \nCurrently 4 GibLab project configuration sections supported: \
        \nApproval settings`, `Approval rules`, `Protected branches`, `General project settings`. \
        \n\nWritten by Kanat Aidarov (https://github.com/kanataidarov)"


class ArgsParser:
    """Parses Command Line arguments and replaces optional ones with default settings.
    """

    def to_bool(self):
        """Convert string value to boolean. 
        """
        valid = {'true': True, 'false': False}

        if isinstance(self, bool):
            return self

        if not isinstance(self, str):
            raise ValueError('invalid literal for boolean. Not a string.')

        lower_value = self.lower()
        if lower_value in valid:
            return valid[lower_value]
        else:
            raise ValueError('invalid literal for boolean: "%s"' % self)
