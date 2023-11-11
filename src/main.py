from args_parser import ArgsParser
from gitlab_config import GitlabConfig

def main(): 
    args = ArgsParser.parse_args()
    gconf = GitlabConfig(args)

    selected_project_ids = gconf.select_project_ids()

    # gconf.update_settings(selected_project_ids)
    
    # gconf.select_projects_without_description(args)
    # selected_group_ids = gconf.select_group_ids(args)

    # branch_names = gconf.select_branch_names(args, selected_project_ids, active=True)
    branches_n_their_commits = gconf.select_branch_names_with_commits(selected_project_ids, active=False)
    print(branches_n_their_commits)

    # gconf.duplicate_branches_with_new_names(args, selected_project_ids, branch_names, r"^.*?feature", "tz")

    # gconf.print_response()


if __name__ == "__main__":
    main()
