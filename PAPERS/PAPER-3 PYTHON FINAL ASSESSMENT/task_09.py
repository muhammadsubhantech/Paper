# Task 09 - Streaming Log Inspector

from datetime import datetime


def read_errors(path):
    # This count is updated as the generator reads the file.
    read_errors.malformed_count = 0

    with open(path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            parts = line.strip().split("|")

            if len(parts) != 3:
                read_errors.malformed_count += 1
                continue

            timestamp = parts[0].strip()
            level = parts[1].strip()
            message = parts[2].strip()

            try:
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                read_errors.malformed_count += 1
                continue

            if not level or not message:
                read_errors.malformed_count += 1
                continue

            if level == "ERROR":
                yield line_number, timestamp, message


read_errors.malformed_count = 0


def summarize_errors(path):
    counts = {}

    for line_number, timestamp, message in read_errors(path):
        date = timestamp.split(" ")[0]

        if date not in counts:
            counts[date] = 0
        counts[date] += 1

    return {
        "errors_by_date": counts,
        "malformed_lines": read_errors.malformed_count
    }


if __name__ == "__main__":
    for error in read_errors("sample.log"):
        print(error)

    print(summarize_errors("sample.log"))
