from tools.registry import ToolRegistry


def hello():

    return "hello"


def main():

    registry = ToolRegistry()

    registry.register(
        "hello",
        hello
    )

    print(
        registry.list_tools()
    )

    func = registry.get(
        "hello"
    )

    print(
        func()
    )

    print(
        registry.exists("hello")
    )

    print(
        registry.exists("world")
    )


if __name__ == "__main__":

    main()