import time
import random
from clearml import Task
from tqdm import tqdm


task = Task.init(
    project_name='Github CICD',
    task_name='dummy_task',
    reuse_last_task_id=False
)

for i in tqdm(range(10)):
    task.get_logger().report_scalar(
        title="Performance Metric",
        series="Series 1",
        iteration=i,
        value=random.randint(0, 100)
    )
    time.sleep(1)
