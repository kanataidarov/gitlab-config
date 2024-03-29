from args_parser import parse_args
from gitlab_config import GitlabConfig


def debug_mode(gconf, selected_pids):
    print(gconf.ps.select_project_by_setting(selected_pids, {"merge_method": "merge"}))


def main():
    args = parse_args()
    gconf = GitlabConfig(args)

    selected_pids = gconf.select_project_ids()

    if args["debug"]:
        debug_mode(gconf, selected_pids)
    else:
        gconf.update_settings(selected_pids)
        gconf.print_response()


if __name__ == "__main__":
    main()
