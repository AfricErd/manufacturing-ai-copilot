"""
Day9 手工 smoke check。

需要真实 LLM / Database 环境，
因此不作为自动单元测试执行。
"""


def main():

    from bootstrap import (
        workflow,
    )

    print(
        workflow.run(
            "销售订单有几个"
        )
    )

    print(
        workflow.run(
            "你好"
        )
    )


if __name__ == "__main__":

    main()