# Task 12 - Custom Iterable Range Toolkit

class ReversibleRange:
    def __init__(self, start, stop, step=1):
        if step == 0:
            raise ValueError("Step cannot be zero")

        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        current = self.start

        if self.step > 0:
            while current < self.stop:
                yield current
                current += self.step
        else:
            while current > self.stop:
                yield current
                current += self.step

    def __reversed__(self):
        length = len(self)

        if length == 0:
            return iter(())

        last = self.start + (length - 1) * self.step
        return iter(ReversibleRange(last, self.start - self.step, -self.step))

    def __len__(self):
        if self.step > 0:
            if self.start >= self.stop:
                return 0
            return (self.stop - self.start - 1) // self.step + 1

        if self.start <= self.stop:
            return 0
        return (self.start - self.stop - 1) // (-self.step) + 1

    def __contains__(self, value):
        if not isinstance(value, int):
            return False

        if self.step > 0:
            if value < self.start or value >= self.stop:
                return False
        else:
            if value > self.start or value <= self.stop:
                return False

        return (value - self.start) % self.step == 0


if __name__ == "__main__":
    numbers = ReversibleRange(2, 11, 3)

    print(list(numbers))
    print(list(reversed(numbers)))
    print(len(numbers))
    print(5 in numbers)
