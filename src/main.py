from args_parser import ArgsParser
from gitlab_config import GitlabConfig


def main(): 
    args = ArgsParser.parse_args()
    gconf = GitlabConfig(args)

    selected_pids = gconf.select_project_ids()

    if args["debug"]:
        debug_mode(gconf, selected_pids)
    else: 
        gconf.update_settings(selected_pids)
        gconf.print_response()


def debug_mode(gconf, selected_pids): 
    # gconf.select_projects_without_description()
    # selected_group_ids = gconf.select_group_ids()

    # branch_names = gconf.select_branch_names(selected_pids, active=False)
    # branches_n_their_commits = gconf.select_branch_names_with_commits(selected_pids, active=False)

    # gconf.duplicate_branches_with_new_names(selected_pids, branch_names, r"^.*?feature", "tz")

    # gconf.delete_branches_by_regex(selected_pids, branch_names, "^(?!tz|main).*")

    # gconf.ps.update_protected_branches(selected_pids)

    gconf.print_response()


if __name__ == "__main__":
    main()
