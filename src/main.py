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
    gconf.select_projects_without_description()
    
    gconf.print_response()


if __name__ == "__main__":
    main()
