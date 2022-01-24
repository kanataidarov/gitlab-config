# gitlab-config

Configures GitLab projects through usage of GitLab API

### Motivation 
---
Specifying configuration settings for every GitLab project required a lot of mouse clicking in my case. All settings were similar for all of the projects.

I looked for a way to automate the configuration of GitLab projects conveniently. Therefore, came to the idea of using GitLab API for this task.

### Usage
---
To start program, run `gitlab-config.sh` script.

```shell
Usage: gitlab-config.sh [-h] [--approval_settings] [--approval_rules] [--protected_branches] [--project_settings] base_url token namespace_paths

Updates configuration of all projects in specified groups within GitLab. 
You can specify which GitLab settings to configure using appropriate optional arguments. 
Currently 4 GibLab project configuration sections supported: Approval settings, Approval rules, Protected branches, General project settings. 

Written by Kanat Aidarov (https://github.com/kanataidarov)

positional arguments:
  base_url              URL of GitLab e.g `https://git.beeline.kz`
  token                 Personal Access Token, required to access GitLab API
  namespace_paths       List of Groups (comma separated) e.g `esb-gov,`

optional arguments:
  -h, --help            show this help message and exit
  --approval_settings   Project's approval settings (default: {"reset_approvals_on_push": true,
                        "disable_overriding_approvers_per_merge_request": true, "merge_requests_author_approval": false,
                        "merge_requests_disable_committers_approval": true})
  --approval_rules      Project's default approval rules (default: {"name": "Any name", "rule_type": "any_approver", "approvals_required":
                        1})
  --protected_branches  Project's protected branches (default:
                        [{"name":"master","push_access_levels":[{"access_level":0,"access_level_description":"No one"}],"merge_access_levels
                        ":[{"access_level":40,"access_level_description":"Maintainers"}],"allow_force_push":false,"code_owner_approval_requi
                        red":false},{"name":"dev","push_access_levels":[{"access_level":0,"access_level_description":"No one"}],"merge_acces
                        s_levels":[{"access_level":40,"access_level_description":"Maintainers"}],"allow_force_push":false,"code_owner_approv
                        al_required":false}])
  --project_settings    Project's global settings (default: {"allow_merge_on_skipped_pipeline":false,"only_allow_merge_if_all_discussions_ar
                        e_resolved":true,"only_allow_merge_if_pipeline_succeeds":true,"remove_source_branch_after_merge":true,"squash_option
                        ":"default_on"})

```
