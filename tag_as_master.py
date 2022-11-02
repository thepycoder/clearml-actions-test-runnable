from clearml import Task


def get_clearml_task_of_current_commit(commit_id):
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
    print(tasks)
    print([task['id'] for task in tasks])
    if tasks:
        for task in tasks:
            if not task['script.diff']:
                return task['id']

    raise ValueError("No task based on this code was found in ClearML. Make sure to run it at least once before merging.")


def tag_task(task_id):
    Task.get_task(task_id=task_id).add_tags(['main_branch'])


if __name__ == '__main__':
    task_id = get_clearml_task_of_current_commit('5fad8a5369ba42df95fd603083a58808e53ffeac')
    tag_task(task_id)
