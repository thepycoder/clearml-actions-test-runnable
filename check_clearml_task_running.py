import os
from clearml import Task


def check_task_status(task_id):
    task = Task.get_task(task_id=task_id)
    if task:
        task_status = task.get_status()
        # Try to get the task stats
        if task_status in ["completed", "published", "publishing", "in_progress", "stopped", "failed"]:
            pass
        elif task_status in ["created", "queued", "unknown"]:
            return f"Task is in {task_status} status, no stats yet."
    else:
        return f"Can not find task {task}.\n\n"
    

if __name__ == '__main__':
    # get credentials and login info
    os.environ["CLEARML_API_ACCESS_KEY"] = os.getenv('INPUT_CLEARML_API_ACCESS_KEY')
    os.environ["CLEARML_API_SECRET_KEY"] = os.getenv('INPUT_CLEARML_API_SECRET_KEY')
    os.environ["CLEARML_API_HOST"] = os.getenv('INPUT_CLEARML_API_HOST')
