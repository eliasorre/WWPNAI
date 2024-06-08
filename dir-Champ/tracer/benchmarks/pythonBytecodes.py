def test_func(x, y):
    # Uses LOAD_FAST, STORE_FAST, BINARY_OP_ADD, RETURN_VALUE, etc.
    return x + y

def use_generators():
    # YIELD_VALUE, GET_ITER, FOR_ITER, etc.
    for i in range(10):
        yield i * 2

def list_comprehensions():
    # BUILD_LIST, LOAD_GLOBAL, etc.
    return [x * x for x in range(10)]

def manipulate_data_structures():
    # LIST_APPEND, BUILD_MAP, STORE_SUBSCR, etc.
    data = {}
    for i in range(5):
        data[i] = i * i
    return data

def handle_exceptions():
    # SETUP_EXCEPT, POP_JUMP_IF_TRUE, etc.
    try:
        1 / 0
    except ZeroDivisionError:
        return 'Caught division by zero!'

def with_statement():
    # WITH_EXCEPT_START, SETUP_WITH, etc.
    with open("test.txt", "w") as file:
        file.write("Hello, world!")

def use_classes():
    # LOAD_BUILD_CLASS, CALL_FUNCTION, etc.
    class TestClass:
        def __init__(self, value):
            self.value = value
        
        def get_value(self):
            # LOAD_METHOD, CALL_METHOD, etc.
            return self.value

    instance = TestClass(123)
    return instance.get_value()

def decorator(func):
    # This function uses LOAD_FAST, CALL_FUNCTION, RETURN_VALUE, etc.
    def wrapper(*args, **kwargs):
        print("Before calling", func.__name__)
        result = func(*args, **kwargs)
        print("After calling", func.__name__)
        return result
    return wrapper

@decorator
def say_hello(name):
    return f"Hello, {name}!"

import asyncio

async def fetch_data():
    # ASYNC_GEN_WRAP, LOAD_CONST, GET_AWAITABLE, etc.
    print("Fetching data...")
    await asyncio.sleep(1)  # Simulate an I/O-bound operation
    print("Data fetched")
    return {"data": 123}

async def main_async():
    data = await fetch_data()
    print(data)

def set_operations():
    # SET_ADD, COMPARE_OP, etc.
    a = {1, 2, 3}
    b = {3, 4, 5}
    return a.union(b), a.intersection(b)

def dict_comprehension():
    # BUILD_MAP, MAP_ADD, etc.
    return {k: k * k for k in range(10)}

def unpacking_args():
    data = (1, 2, 3)
    x, y, z = data  # UNPACK_SEQUENCE, STORE_FAST, etc.
    return x, y, z

def extended_call(*args, **kwargs):
    # CALL_FUNCTION_EX, BUILD_TUPLE, BUILD_MAP
    print("Positional Args:", args)
    print("Keyword Args:", kwargs)

def factorial(n):
    # RECURSIVE CALL, RETURN_VALUE, etc.
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)


def main():
    # CALL_FUNCTION, RETURN_VALUE, etc.
    print(test_func(5, 7))
    print(use_generators())
    print(list_comprehensions())
    print(manipulate_data_structures())
    print(handle_exceptions())
    with_statement()
    print(use_classes())
    print(decorator)
    print(set_operations)
    print(dict_comprehension)
    print(unpacking_args)
    print(extended_call)
    print(factorial)

if __name__ == "__main__":
    # Run synchronous main functions
    main()

    # Run asynchronous event loop
    asyncio.run(main_async())

