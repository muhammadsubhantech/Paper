# Task 04 - Dependency Execution Planner

def execution_order(tasks, dependencies):
    task_set = set(tasks)

    if len(task_set) != len(tasks):
        raise ValueError("Task names must be unique")

    next_tasks = {}
    waiting_count = {}

    for task in tasks:
        next_tasks[task] = []
        waiting_count[task] = 0

    for first, second in dependencies:
        if first not in task_set or second not in task_set:
            raise ValueError("Unknown task in dependency: " + str((first, second)))

        if second not in next_tasks[first]:
            next_tasks[first].append(second)
            waiting_count[second] += 1

    ready = []
    for task in tasks:
        if waiting_count[task] == 0:
            ready.append(task)

    ready.sort()
    result = []

    while ready:
        current = ready.pop(0)
        result.append(current)

        for following in next_tasks[current]:
            waiting_count[following] -= 1

            if waiting_count[following] == 0:
                ready.append(following)
                ready.sort()

    if len(result) != len(tasks):
        raise ValueError("Cycle detected: tasks cannot be completed")

    return result


if __name__ == "__main__":
    tasks = ["build", "test", "deploy"]
    dependencies = [("build", "test"), ("test", "deploy")]
    print(execution_order(tasks, dependencies))
