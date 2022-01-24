from gitlab_config import GitlabConfig

def main(): 
    gconf = GitlabConfig()

    args = gconf.parse_args()

    selected_project_ids = gconf.select_project_ids(args)
    
    gconf.update_approval_settings(args, selected_project_ids)   
    gconf.update_approval_rules(args, selected_project_ids)
    gconf.update_protected_branches(args, selected_project_ids)
    gconf.update_project_settings(args, selected_project_ids)

    gconf.print_response()


if __name__ == "__main__":
    main()
