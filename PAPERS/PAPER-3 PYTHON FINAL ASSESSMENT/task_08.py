# Task 08 - Cache Decorator with Expiration

import time
import functools
import inspect


def ttl_cache(seconds):
    if seconds < 0:
        raise ValueError("Cache time cannot be negative")

    def decorator(function):
        cache = {}
        signature = inspect.signature(function)

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            nonlocal cache

            # Bind arguments so x=2,y=3 and y=3,x=2 get the same key.
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            key = tuple(bound.arguments.items())

            try:
                hash(key)
            except TypeError:
                # Unhashable inputs are not cached.
                wrapper.cache_misses += 1
                return function(*args, **kwargs)

            now = time.monotonic()

            if key in cache:
                saved_time, saved_result = cache[key]

                if now - saved_time < seconds:
                    wrapper.cache_hits += 1
                    return saved_result

            wrapper.cache_misses += 1
            result = function(*args, **kwargs)
            cache[key] = (now, result)
            return result

        wrapper.cache_hits = 0
        wrapper.cache_misses = 0
        return wrapper

    return decorator


@ttl_cache(5)
def add_numbers(x, y):
    print("Calculating...")
    return x + y


if __name__ == "__main__":
    print(add_numbers(x=2, y=3))
    print(add_numbers(y=3, x=2))
    print("Hits:", add_numbers.cache_hits)
    print("Misses:", add_numbers.cache_misses)

# Note: unhashable arguments (such as lists or dictionaries) are calculated
# normally and are not stored in the cache.
