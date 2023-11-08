from gitlab_config import GitlabConfig

def main(): 
    gconf = GitlabConfig()

    args = gconf.parse_args()

    selected_project_ids = gconf.select_project_ids(args)

    gconf.update_approval_settings(args, selected_project_ids)   
    gconf.update_approval_rules(args, selected_project_ids)
    gconf.update_project_settings(args, selected_project_ids)
    gconf.update_protected_branches(args, selected_project_ids)
    
    # selected_group_ids = gconf.select_group_ids(args)
    # gconf.csv_group_members(args, selected_group_ids, out_path="Members.csv")

    # branch_names = gconf.select_branch_names(args, selected_project_ids, active=True)
    # gconf.duplicate_branches_with_new_names(args, selected_project_ids, branch_names, r"^.*?feature", "tz")

    gconf.print_response()


if __name__ == "__main__":
    main()
