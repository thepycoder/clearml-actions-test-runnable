import os
from clearml import Task

from tag_as_master import get_clearml_task_of_current_commit


def compare_and_tag_task(commit_hash):
    current_task = Task.get_task(task_id=get_clearml_task_of_current_commit(commit_hash))
    best_task = Task.get_task(project_name='Github CICD', task_name='cicd_test', tags=['Best Performance'])
    if best_task:
        best_metric = max(
            best_task.get_reported_scalars().get('Performance Metric').get('Series 1').get('y')
        )
        current_metric = max(
            current_task.get_reported_scalars().get('Performance Metric').get('Series 1').get('y')
        )
        if current_metric >= best_metric:
            current_task.add_tags(['Best Performance'])
            # best_task.remove_tags(['Best Performance'])
    else:
        current_task.add_tags(['Best Performance'])


if __name__ == '__main__':
    print(f"Running on commit hash: {os.getenv('COMMIT_ID')}")
    compare_and_tag_task(os.getenv('COMMIT_ID'))
