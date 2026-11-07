# Task 03 - Recursive JSON Path Explorer

def same_value(value, target):
    if isinstance(value, bool) or isinstance(target, bool):
        return type(value) == type(target) and value == target
    return value == target


def find_paths(data, target, path=""):
    paths = []

    if isinstance(data, dict):
        for key, value in data.items():
            if path:
                new_path = path + "." + str(key)
            else:
                new_path = str(key)

            if same_value(value, target):
                paths.append(new_path)
            elif isinstance(value, (dict, list)):
                paths.extend(find_paths(value, target, new_path))

    elif isinstance(data, list):
        for index in range(len(data)):
            value = data[index]
            new_path = path + "[" + str(index) + "]"

            if same_value(value, target):
                paths.append(new_path)
            elif isinstance(value, (dict, list)):
                paths.extend(find_paths(value, target, new_path))

    return paths


if __name__ == "__main__":
    data = {"a": [{"x": 5}, 5], "b": {"y": 5}}
    print(find_paths(data, 5))

    data2 = {"a": True, "b": 1}
    print(find_paths(data2, 1))
    print(find_paths(data2, True))
