import time
import random
from clearml import Task
from tqdm import tqdm


task = Task.init(
    project_name='Github CI/CD',
    task_name='dummy_task'
)

for i in tqdm(range(1000)):
    task.get_logger().report_scalar(
        title="Iteration Reporting",
        series="Series 1",
        iteration=i,
        value=random.randint(0, 100)
    )
    time.sleep(1)
