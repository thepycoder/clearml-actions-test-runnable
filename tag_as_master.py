import json
import os

import pandas as pd
from clearml import Task
from github3 import login
from tabulate import tabulate


def create_output_tables(retrieve_scalars_dict):
    data = []
    for graph_title, graph_values in retrieve_scalars_dict.items():
        graph_data = []
        for series, series_values in graph_values.items():
            graph_data.append((graph_title, series, *series_values.values()))
        data += graph_data
    return sorted(data, key=lambda output: (output[0], output[1]))


def get_task_stats(task):
    task_status = task.get_status()
    # Try to get the task stats
    if task_status == "completed":
        table = create_comment_output(task, task_status)
        if table:
            return f"Results\n\n{table}\n\n" \
                    f"You can view full task results [here]({task.get_output_log_web_page()})"
        else:
            return f"Something went wrong when creating the task table. Check full task [here]({task.get_output_log_web_page()})"
    # Update the user about the task status, can not get any stats
    else:
        return f"Task is in {task_status} status, this should not happen!"


def create_comment_output(task, status):
    retrieve_scalars_dict = task.get_last_scalar_metrics()
    if retrieve_scalars_dict:
        scalars_tables = create_output_tables(retrieve_scalars_dict)
        df = pd.DataFrame(data=scalars_tables, columns=["Title", "Series", "Last", "Min", "Max"])
        df.style.set_caption(f"Last scalars metrics for task {task.task_id}, task status {status}")
        table = tabulate(df, tablefmt="github", headers="keys", showindex=False)
        return table


def create_stats_comment(project_stats):
    payload_fname = os.getenv('GITHUB_EVENT_PATH')
    with open(payload_fname, 'r') as f:
        payload = json.load(f)
    owner, repo = payload.get("repository", {}).get("full_name", "").split("/")
    if owner and repo:
        gh = login(token=os.getenv("GH_TOKEN"))
        if gh:
            pull_request = gh.pull_request(owner, repo, payload.get("pull_request", {}).get("number"))
            if pull_request:
                pull_request.create_comment(project_stats)
            else:
                print(f'Can not comment PR, {payload.get("issue", {}).get("number")}')
        else:
            print(f"Can not log in to gh, {os.getenv('GH_TOKEN')}")

def get_clearml_task_of_current_commit(commit_id):
    # Get the ID and Diff of all tasks based on the current commit hash, order by newest
    tasks = Task.query_tasks(
        task_filter={
            'order_by': ['-last_update'],
            '_all_': dict(fields=['script.version_num'],
                          pattern=commit_id
                          ),
            'status': ['completed']
        },
        additional_return_fields=['script.diff']
    )
    
    # If there are tasks, check which one has no diff: aka which one was run with the exact
    # code that is staged in this PR.
    if tasks:
        for task in tasks:
            if not task['script.diff']:
                return task['id']

    # If no task was run yet with the exact PR code, raise an error and block the PR.
    raise ValueError("No task based on this code was found in ClearML. Make sure to run it at least once before merging.")


if __name__ == '__main__':
    # Get the ClearML API Credentials
    os.environ["CLEARML_API_ACCESS_KEY"] = os.getenv('CLEARML_API_ACCESS_KEY')
    os.environ["CLEARML_API_SECRET_KEY"] = os.getenv('CLEARML_API_SECRET_KEY')
    os.environ["CLEARML_API_HOST"] = os.getenv('CLEARML_API_HOST')

    # Main check: Does a ClearML task exist for this specific commit?
    task_id = get_clearml_task_of_current_commit(os.getenv('GITHUB_SHA'))
    task = Task.get_task(task_id=task_id)

    # If the task exists, we can tag it as such, so we know in the interface which one it is.
    task.add_tags(['main_branch'])

    # Let's also add the task metrics to the PR automatically.
    # Get the metrics from the task and create a comment on the PR.
    stats = get_task_stats(task)
    create_stats_comment(stats)
