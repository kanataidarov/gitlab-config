class clr: 
    HDRC = '\033[32m'
    SUBC = '\033[35m'
    DMPC = '\033[0m'
    RSTC = '\033[0m'

class Roles:
    TABLE = {0: "No access", 
        5: "Minimal access", 
        10: "Guest", 
        20: "Reporter",
        30: "Developer",
        40: "Maintainer", 
        50: "Owner"}

class Optionals:
    PROJECT_SETTINGS = {"name": "--project_settings", 
        "default": '{"allow_merge_on_skipped_pipeline":false,"only_allow_merge_if_all_discussions_are_resolved":true,"only_allow_merge_if_pipeline_succeeds":true,"remove_source_branch_after_merge":true,"squash_option":"default_on","merge_method":"ff"}', 
        "help": "Project's global settings"}
    PROTECTED_BRANCHES = {"name": "--protected_branches",
        "default": '[{"name":"master","push_access_levels":[{"access_level":0,"access_level_description":"No one"}],"merge_access_levels":[{"access_level":40,"access_level_description":"Maintainers"}],"allow_force_push":false,"code_owner_approval_required":false},{"name":"dev","push_access_levels":[{"access_level":0,"access_level_description":"No one"}],"merge_access_levels":[{"access_level":40,"access_level_description":"Maintainers"}],"allow_force_push":false,"code_owner_approval_required":false}]',
        "help": "Project's protected branches"}
    APPROVAL_RULES = {"name": "--approval_rules",
        "default": '{"name": "Any name", "rule_type": "any_approver", "approvals_required": 1}',
        "help": "Project's default approval rules"}
    APPROVAL_SETTINGS = {"name": "--approval_settings",
        "default": '{"reset_approvals_on_push": true, "disable_overriding_approvers_per_merge_request": true, "merge_requests_author_approval": false, "merge_requests_disable_committers_approval": true}',
        "help": "Project's approval settings"}
    PROJECT_IDS = {"name": "--project_ids", "default": '', "help": "List of Project Ids (comma separated) e.g `1,2,3`"}
    NAMESPACE_PATHS = {"name": "--namespace_paths", "default": '', "help": "List of Groups (comma separated) e.g `npd-gov,npd`"}

class Positionals:
    BASE_URL = {"name": "base_url", "help": "URL of GitLab  e.g `https://github.kz`"}
    TOKEN = {"name": "token", "help": "Personal Access Token, required to access GitLab API"}
