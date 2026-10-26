__all__ = [
    "ManufacturingWorkflow",
]


def __getattr__(
    name: str,
):
    """
    Keep the workflow package lightweight.

    Importing pure workflow domain modules such as
    workflow.task must not eagerly import LangGraph.

    ManufacturingWorkflow remains available from the
    package root for backward compatibility and is
    loaded only when requested.
    """

    if name == "ManufacturingWorkflow":

        from workflow.langgraph_workflow import (
            ManufacturingWorkflow,
        )

        return ManufacturingWorkflow

    raise AttributeError(
        f"module 'workflow' has no "
        f"attribute {name!r}"
    )