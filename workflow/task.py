from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import re

class TaskStatus(str, Enum):
    """
一个工作流子任务的生命周期状态。
任务状态可供后续调度分发器、调度器、追踪模块以及工作流状态共用。
    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class SubTask:
    """
工作流计划中不可变的工作单元。

子任务用于描述：
1. 需要执行的内容；
2. 具备对应能力的智能体；
3. 必须先行完成的上游任务。

运行时执行状态不属于本范畴。
    """

    task_id: str

    description: str

    agent_name: str

    dependencies: tuple[str, ...] = field(
        default_factory=tuple
    )


    def __post_init__(
        self,
    ) -> None:
        """
        校验并规范化 SubTask 的基础字段。

        这里负责 SubTask 自身边界：
        - 字段类型
        - 空字符串
        - task_id 格式
        - dependency 基础格式

        dependency 是否真实存在、
        DAG 是否有环，
        仍由 TaskPlan 统一负责。
        """

        # ====================================================
        # 1. 基础类型校验
        # ====================================================

        if not isinstance(
            self.task_id,
            str,
        ):
            raise TypeError(
                "SubTask.task_id must be a string."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise TypeError(
                "SubTask.description must be a string."
            )

        if not isinstance(
            self.agent_name,
            str,
        ):
            raise TypeError(
                "SubTask.agent_name must be a string."
            )

        if not isinstance(
            self.dependencies,
            (list, tuple),
        ):
            raise TypeError(
                "SubTask.dependencies must be a list or tuple."
            )

        # ====================================================
        # 2. 字符串规范化
        # ====================================================

        task_id = self.task_id.strip()

        description = (
            self.description.strip()
        )

        agent_name = (
            self.agent_name.strip()
        )

        dependencies = []

        for dependency in self.dependencies:

            if not isinstance(
                dependency,
                str,
            ):
                raise TypeError(
                    "SubTask.dependencies must contain "
                    "only string task ids."
                )

            dependency_id = (
                dependency.strip()
            )

            if not dependency_id:

                raise ValueError(
                    "SubTask.dependencies must not "
                    "contain empty task ids."
                )

            dependencies.append(
                dependency_id
            )

        dependencies = tuple(
            dependencies
        )

        # ====================================================
        # 3. 非空校验
        # ====================================================

        if not task_id:

            raise ValueError(
                "SubTask.task_id must not be empty."
            )

        if not description:

            raise ValueError(
                "SubTask.description must not be empty."
            )

        if not agent_name:

            raise ValueError(
                "SubTask.agent_name must not be empty."
            )

        # ====================================================
        # 4. task_id 格式
        #
        # 合法：
        # T1
        # T2
        # T10
        #
        # 非法：
        # task1
        # 1
        # T0
        # ====================================================

        if (
            re.fullmatch(
                r"T[1-9]\d*",
                task_id,
            )
            is None
        ):

            raise ValueError(
                "SubTask.task_id must use format "
                "'T1', 'T2', 'T3'..."
            )

        # ====================================================
        # 5. dependency 去重校验
        # ====================================================

        if (
            len(set(dependencies))
            != len(dependencies)
        ):

            raise ValueError(
                f"SubTask '{task_id}' contains "
                "duplicate dependencies."
            )

        # ====================================================
        # 6. 写回规范化结果
        # ====================================================

        object.__setattr__(
            self,
            "task_id",
            task_id,
        )

        object.__setattr__(
            self,
            "description",
            description,
        )

        object.__setattr__(
            self,
            "agent_name",
            agent_name,
        )

        object.__setattr__(
            self,
            "dependencies",
            dependencies,
        )


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "task_id": self.task_id,
            "description": self.description,
            "agent_name": self.agent_name,
            "dependencies": list(
                self.dependencies
            ),
        }


@dataclass(frozen=True)
class TaskPlan:
    """
经过结构验证的工作流方案。

任务计划仅持有计划不变量。

调度与执行逻辑特意
不归属此处。
    """

    question: str

    tasks: tuple[SubTask, ...]


    def __post_init__(
        self,
    ) -> None:
        """
        校验 TaskPlan 最外层输入边界，
        再执行 dependency / DAG 结构校验。
        """

        # ====================================================
        # 1. 基础类型
        # ====================================================

        if not isinstance(
            self.question,
            str,
        ):

            raise TypeError(
                "TaskPlan.question must be a string."
            )

        if not isinstance(
            self.tasks,
            (list, tuple),
        ):

            raise TypeError(
                "TaskPlan.tasks must be a list or tuple."
            )

        question = (
            self.question.strip()
        )

        tasks = tuple(
            self.tasks
        )

        # ====================================================
        # 2. question / tasks 非空
        # ====================================================

        if not question:

            raise ValueError(
                "TaskPlan.question must not be empty."
            )

        if not tasks:

            raise ValueError(
                "TaskPlan must contain at least "
                "one subtask."
            )

        # ====================================================
        # 3. tasks 必须都是 SubTask
        # ====================================================

        for task in tasks:

            if not isinstance(
                task,
                SubTask,
            ):

                raise TypeError(
                    "TaskPlan.tasks must contain "
                    "only SubTask objects."
                )

        object.__setattr__(
            self,
            "question",
            question,
        )

        object.__setattr__(
            self,
            "tasks",
            tasks,
        )

        # ====================================================
        # 4. dependency / DAG 等结构校验
        # ====================================================

        self._validate_structure()


    @property
    def task_ids(
        self,
    ) -> tuple[str, ...]:

        return tuple(
            task.task_id
            for task in self.tasks
        )


    def get_task(
        self,
        task_id: str,
    ) -> SubTask:

        for task in self.tasks:

            if task.task_id == task_id:
                return task

        raise KeyError(
            f"Task '{task_id}' not found in plan."
        )


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "question": self.question,
            "tasks": [
                task.to_dict()
                for task in self.tasks
            ],
        }


    def _validate_structure(
        self,
    ) -> None:

        task_ids = self.task_ids

        task_id_set = set(
            task_ids
        )

        # ====================================================
        # 1. Task ID must be unique
        # ====================================================

        if (
            len(task_id_set)
            != len(task_ids)
        ):
            raise ValueError(
                "任务计划包含重复的任务编号。"
            )

        # ====================================================
        # 2. Dependency validation
        # ====================================================

        for task in self.tasks:

            for dependency in task.dependencies:

                if dependency == task.task_id:

                    raise ValueError(
                        f"Task '{task.task_id}' "
                        "cannot depend on itself."
                    )

                if dependency not in task_id_set:

                    raise ValueError(
                        f"Task '{task.task_id}' depends "
                        f"on unknown task "
                        f"'{dependency}'."
                    )

        # ====================================================
        # 3. DAG validation
        # ====================================================

        self._validate_acyclic()


    def _validate_acyclic(self) -> None:
        """
        验证依赖图为有向无环图（DAG）。
        这属于结构规划验证，而非调度。
        """
        # 1. 构建字典 key:task_id value:任务依赖集合
        dependencies_by_task = {}
        for task in self.tasks:
            dependencies_by_task[task.task_id] = set(task.dependencies)

        # 2. remaining：还没有处理完成的任务id集合
        remaining = set(dependencies_by_task)
        # 3. resolved：已经全部处理完成的任务id集合，类型注解：存放字符串的集合
        resolved: set[str] = set()

        while remaining:
            # ========== 原来集合推导式改成普通for ==========
            ready = set()
            for task_id in remaining:
                task_deps = dependencies_by_task[task_id]
                if task_deps.issubset(resolved):
                    ready.add(task_id)
            # ===============================================

            if not ready: # ready是空集合，找不到任何可以执行的任务 → 循环依赖
                cycle_tasks = ", ".join(sorted(remaining))
                raise ValueError(
                    "TaskPlan contains a cyclic dependency involving: "
                    f"{cycle_tasks}."
                )
            
            resolved.update(ready)
            remaining.difference_update(ready)
    def validate_agents(
        self,
        available_agents:set[str]
    ):

        for task in self.tasks:

            if task.agent_name not in available_agents:

                raise ValueError(
                    f"Unknown agent: {task.agent_name}"
                )



@dataclass(frozen=True)
class TaskResult:
    """
    一个工作流子任务的终端执行结果。

    结果通过 task_id 识别，而不是通过 agent_name 识别，
    因为同一个 Agent 可以在同一工作流中执行多个子任务。
    """

    task_id: str

    agent_name: str

    status: TaskStatus

    answer: str = ""

    data: dict[str, Any] = field(
        default_factory=dict
    )

    error: str | None = None


    def __post_init__(
        self,
    ) -> None:
        """
        校验 TaskResult 自身的数据边界。

        TaskResult 只允许表示终态：
        - SUCCEEDED
        - FAILED
        - SKIPPED
        """

        # ====================================================
        # 1. 类型校验
        # ====================================================

        if not isinstance(
            self.task_id,
            str,
        ):
            raise TypeError(
                "TaskResult.task_id must be a string."
            )

        if not isinstance(
            self.agent_name,
            str,
        ):
            raise TypeError(
                "TaskResult.agent_name must be a string."
            )

        if not isinstance(
            self.status,
            TaskStatus,
        ):
            raise TypeError(
                "TaskResult.status must be a TaskStatus."
            )

        if not isinstance(
            self.answer,
            str,
        ):
            raise TypeError(
                "TaskResult.answer must be a string."
            )

        if not isinstance(
            self.data,
            dict,
        ):
            raise TypeError(
                "TaskResult.data must be a dict."
            )

        if (
            self.error is not None
            and not isinstance(
                self.error,
                str,
            )
        ):
            raise TypeError(
                "TaskResult.error must be "
                "a string or None."
            )

        # ====================================================
        # 2. Normalize
        # ====================================================

        task_id = (
            self.task_id.strip()
        )

        agent_name = (
            self.agent_name.strip()
        )

        error = (
            self.error.strip()
            if self.error is not None
            else None
        )

        # ====================================================
        # 3. 基础值校验
        # ====================================================

        if not task_id:

            raise ValueError(
                "TaskResult.task_id must not be empty."
            )

        if (
            re.fullmatch(
                r"T[1-9]\d*",
                task_id,
            )
            is None
        ):

            raise ValueError(
                "TaskResult.task_id must use format "
                "'T1', 'T2', 'T3'..."
            )

        if not agent_name:

            raise ValueError(
                "TaskResult.agent_name must not "
                "be empty."
            )

        # ====================================================
        # 4. TaskResult 必须是终态
        # ====================================================

        if self.status in {
            TaskStatus.PENDING,
            TaskStatus.RUNNING,
        }:

            raise ValueError(
                "TaskResult must represent a "
                "terminal task status."
            )

        # ====================================================
        # 5. 状态和 error 必须一致
        # ====================================================

        if (
            self.status
            == TaskStatus.SUCCEEDED
            and error is not None
        ):

            raise ValueError(
                "A succeeded TaskResult cannot "
                "contain an error."
            )

        if (
            self.status
            in {
                TaskStatus.FAILED,
                TaskStatus.SKIPPED,
            }
            and not error
        ):

            raise ValueError(
                f"A {self.status.value} TaskResult "
                "must contain a reason."
            )

        # ====================================================
        # 6. 写回规范化数据
        # ====================================================

        object.__setattr__(
            self,
            "task_id",
            task_id,
        )

        object.__setattr__(
            self,
            "agent_name",
            agent_name,
        )

        object.__setattr__(
            self,
            "data",
            dict(
                self.data
            ),
        )

        object.__setattr__(
            self,
            "error",
            error,
        )


    @property
    def success(
        self,
    ) -> bool:

        return (
            self.status
            == TaskStatus.SUCCEEDED
        )


    @classmethod
    def succeeded(
        cls,
        task: SubTask,
        answer: str,
        data: dict[str, Any] | None = None,
    ) -> "TaskResult":

        return cls(
            task_id=task.task_id,
            agent_name=task.agent_name,
            status=TaskStatus.SUCCEEDED,
            answer=answer,
            data=data or {},
        )


    @classmethod
    def failed(
        cls,
        task: SubTask,
        error: str,
    ) -> "TaskResult":

        return cls(
            task_id=task.task_id,
            agent_name=task.agent_name,
            status=TaskStatus.FAILED,
            error=error,
        )


    @classmethod
    def skipped(
        cls,
        task: SubTask,
        reason: str,
    ) -> "TaskResult":

        return cls(
            task_id=task.task_id,
            agent_name=task.agent_name,
            status=TaskStatus.SKIPPED,
            error=reason,
        )


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "success": self.success,
            "answer": self.answer,
            "data": dict(
                self.data
            ),
            "error": self.error,
        }