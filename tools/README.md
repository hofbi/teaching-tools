# Tools

Tools to automatically run repeating processes.

<!-- mdformat-toc start --slug=github --no-anchors --maxlevel=6 --minlevel=2 -->

- [File Export](#file-export)
- [GitLab Project Creation](#gitlab-project-creation)
- [Working with the GitLab Projects](#working-with-the-gitlab-projects)
  - [GitLab issue creation from homework slides](#gitlab-issue-creation-from-homework-slides)
  - [Comment Gitlab issues and change their state](#comment-gitlab-issues-and-change-their-state)
  - [Fetch the student code](#fetch-the-student-code)
  - [Evaluate the student code](#evaluate-the-student-code)
    - [Define Evaluation Jobs](#define-evaluation-jobs)
  - [Upload new files to the student code](#upload-new-files-to-the-student-code)
  - [Commit changes to the student code](#commit-changes-to-the-student-code)

<!-- mdformat-toc end -->

## File Export

Export files for student homework assignments and lecture templates.
This removes all solution code at stores the output in a destination directory.
You should have a file `.exportignore` (as defined by variable `EXPORT_IGNORE` in [sel_tools/file_export/config.py](sel_tools/file_export/config.py)) in your `source` folder, telling the function which file patterns to ignore.
Lines of `.exportignore` are forwarded to Python's `pathlib.Path.glob`, so the usual suspects such as `folder/*.cpp`, `**/*.cpp`, `folder/`, and `folder/specific_file.txt` work, similar to `.gitignore`.
Paths in `.exportignore`'s are interpreted relative to its location.

```shell
python3 export_files.py source --output-dir destination
```

Per default, file export removes solutions inside delimiters defined in [sel_tools/file_export/config.py](sel_tools/file_export/config.py).
You can disable removal of solutions by setting flag `-k` or `--keep-solutions` in the command above.

## GitLab Project Creation

Script [create_gitlab_projects.py](create_gitlab_projects.py) creates `-n`/`--homework-number` (default 1) repositories with contents from an export folder `-s`/`--source-path`, defaulting to `repository/export/homework`.
The script also creates a config file in folder `-r` or `--repo-info-dir` (default `config`) to contain the names and IDs of the newly created repos.
The json file's stem in that folder equals the `-g`/`--group-id`.
Existing files with identical file names will be overwritten.
Call

```shell script
python3 create_gitlab_projects.py repo_base_name -g group_id --gitlab-token your_token
```

to create one repo under the GitLab group with ID `group_id` using your [private access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).
Make sure that the token has `api` scope.
If your token cannot access the group and doesn't have project creation rights in the group, this script doesn't work.

## Working with the GitLab Projects

```shell script
python3 gitlab_projects.py <action>
```

See the sections below to get more information about the individual actions.
All actions require your private access token as defined [above](#gitlab-project-creation) and the student's repositories json config file produced by [gitlab project creation](#gitlab-project-creation).
Point to this file always with the first positional argument of the command.

### GitLab issue creation from homework slides

Create gitlab issues in students' repositories from the homework slides.
Call

```shell script
python3 gitlab_projects.py create_issues config/demo.json --issue-md-slides ../slides/homework/example/slide-deck.md --homework-number 1 --gitlab-token your_token
```

to create issues for the first homework.
The markdown slides can contain attachments in format `[attachment text](/path/to/file/relative/to/repo/root)` with the leading `/` as indicator for the link.
You can add optional parameter `-d`/`--due-date` to assign a due date to the issues created from one homework.
It consumes a date in format `YEAR MONTH DAY`, e.g. `-d 2020 1 31`: you don't need to look out for leading zeros.

### Comment Gitlab issues and change their state

Comment and optionally close/reopen gitlab issues in the students' repositories.
Call

```shell script
python3 gitlab_projects.py comment_issues config/demo.json --issue-number 42 --message "comment text" --gitlab-token your_token
```

to add a comment with _comment text_ to issue 42.
You can also use `-m`/`--message` with a path to a markdown file containing the issue comment in the markdown file.
Similar to the issue creation the message or markdown file can contain attachments with links to local files relative to the root project.
Call with `-s`/`--state-event` in `{close, reopen}`.

### Fetch the student code

Clone or pull all student repositories in the config file into workspace `-w`/`--workspace`.

```shell script
python3 gitlab_projects.py fetch_code config/demo.json --gitlab-token your_token
```

### Evaluate the student code

Clone or pull all student repositories in the config file into workspace `-w`/`--workspace`.
Provide the path to your `EvaluationJobFactory` python module with `-j`/`--job-factory`.
See how to [define evaluation jobs](#define-evaluation-jobs).
By default the factory defined in [`sel.py`](sel_tools/code_evaluation/jobs/sel.py) is used.
Provide a `-d`/`--date-last-homework` to additionally create a `git diff` patch file that shows the diff to the last homework.
By default where no date is provided, no diff is created.
Provide a `-e`/`--evaluation-date` to specify the evaluation deadline.
Only commits before that date will be considered for the evaluation.
By default where no date is provided, the latest commit will be used for the evaluation.
The date format is `YEAR MONTH DAY`, e.g. `-d 2020 1 31`
Call

```shell script
python3 gitlab_projects.py evaluate_code config/demo.json --homework-number 1 --gitlab-token your_token
```

#### Define Evaluation Jobs

See [`sel.py`](sel_tools/code_evaluation/jobs/sel.py) as an example to create your own `EvaluationJobFactory` and evaluation jobs.

1. Create a python file with a class that inherits from `EvaluationJobFactory`.
1. Implement the `EvaluationJobFactory.create` method to return the evaluation jobs you want to use for the respective homework number.

### Upload new files to the student code

Upload new files to the student code via a commit without cloning the repositories.
This command is only for adding new files.
For any other more complex modification, see the [commit changes module](#commit-changes-to-the-student-code).
Call

```shell script
python3 gitlab_projects.py upload_files config/demo.json --source-path your_source --gitlab-token your_token
```

### Commit changes to the student code

Commit changes to the student code by fetching the repos, copying the content from a source repo, and committing the changes.
The changes are copied using the [file export module](#file-export).
Clone or pull all student repositories in the config file into workspace `-w`/`--workspace`.

```shell script
python3 gitlab_projects.py commit_changes config/demo.json --source-path your_source --gitlab-token your_token
```
