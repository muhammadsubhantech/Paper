# Task 02 - Longest Valid Window

def longest_unique_window(text):
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    last_seen = {}
    start = 0
    best_start = 0
    best_length = 0

    for end in range(len(text)):
        character = text[end]

        if character in last_seen and last_seen[character] >= start:
            start = last_seen[character] + 1

        last_seen[character] = end
        current_length = end - start + 1

        # Use > so the earliest window wins when lengths are equal.
        if current_length > best_length:
            best_length = current_length
            best_start = start

    answer = text[best_start:best_start + best_length]
    return answer, best_start, best_length


if __name__ == "__main__":
    print(longest_unique_window("abcabcbb"))
    print(longest_unique_window(""))
    print(longest_unique_window("bbbbb"))
    print(longest_unique_window("pwwkew"))
    print(longest_unique_window("a b c"))
