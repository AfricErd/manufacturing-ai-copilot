// ============================================================
// DOM
// ============================================================

const questionInput =
    document.getElementById("questionInput");

const sendButton =
    document.getElementById("sendButton");

const clearButton =
    document.getElementById("clearButton");

const loadingPanel =
    document.getElementById("loadingPanel");

const errorPanel =
    document.getElementById("errorPanel");

const errorMessage =
    document.getElementById("errorMessage");

const resultArea =
    document.getElementById("resultArea");

const answerContent =
    document.getElementById("answerContent");

const taskList =
    document.getElementById("taskList");

const durationBadge =
    document.getElementById("durationBadge");

const workflowSummary =
    document.getElementById("workflowSummary");

const exampleButtons =
    document.querySelectorAll(
        ".example-button"
    );


// ============================================================
// 页面状态
// ============================================================

let isRunning = false;


// ============================================================
// 示例问题
// ============================================================

exampleButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                const question =
                    button.dataset.question;

                questionInput.value =
                    question;

                questionInput.focus();
            }
        );

    }
);


// ============================================================
// 点击发送
// ============================================================

sendButton.addEventListener(
    "click",
    runCopilot
);


// Ctrl + Enter 快速发送

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.ctrlKey
            &&
            event.key === "Enter"
        ) {

            event.preventDefault();

            runCopilot();
        }

    }
);


// ============================================================
// 清空
// ============================================================

clearButton.addEventListener(
    "click",
    function () {

        if (isRunning) {
            return;
        }

        questionInput.value = "";

        answerContent.textContent = "";

        taskList.innerHTML = "";

        workflowSummary.innerHTML = "";

        resultArea.classList.add(
            "hidden"
        );

        errorPanel.classList.add(
            "hidden"
        );

        questionInput.focus();
    }
);


// ============================================================
// 调用后端 API
// ============================================================

async function runCopilot() {

    if (isRunning) {
        return;
    }


    const question =
        questionInput.value.trim();


    if (!question) {

        showError(
            "请输入需要分析的问题。"
        );

        return;
    }


    setRunningState(true);


    errorPanel.classList.add(
        "hidden"
    );

    resultArea.classList.add(
        "hidden"
    );

    loadingPanel.classList.remove(
        "hidden"
    );


    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            question: question
                        })
                }
            );


        let data = null;


        try {

            data =
                await response.json();

        } catch (jsonError) {

            throw new Error(
                "后端返回的数据无法解析。"
            );
        }


        if (!response.ok) {

            let message =
                "执行失败，请查看后端日志。";


            if (
                data
                &&
                data.detail
            ) {

                message =
                    String(
                        data.detail
                    );
            }


            throw new Error(
                message
            );
        }


        renderResult(
            data
        );

    } catch (error) {

        console.error(
            error
        );


        showError(
            error.message
            ||
            "执行失败，请查看后端日志。"
        );

    } finally {

        loadingPanel.classList.add(
            "hidden"
        );

        setRunningState(false);
    }

}


// ============================================================
// 渲染完整执行结果
// ============================================================

function renderResult(data) {

    const answer =
        data.answer
        ||
        "工作流未返回最终回答。";


    answerContent.textContent =
        answer;


    renderDuration(
        data.duration_ms
    );


    const tasks =
        Array.isArray(data.tasks)
            ? data.tasks
            : [];


    renderWorkflowSummary(
        tasks
    );


    renderTasks(
        tasks
    );


    resultArea.classList.remove(
        "hidden"
    );


    resultArea.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


// ============================================================
// 执行耗时
// ============================================================

function renderDuration(
    durationMs
) {

    if (
        durationMs === undefined
        ||
        durationMs === null
    ) {

        durationBadge.textContent =
            "执行耗时：-";

        return;
    }


    const seconds =
        Number(durationMs)
        / 1000;


    durationBadge.textContent =
        "执行耗时："
        +
        seconds.toFixed(2)
        +
        " 秒";

}


// ============================================================
// 工作流统计
// ============================================================

function renderWorkflowSummary(
    tasks
) {

    workflowSummary.innerHTML = "";


    const counters = {

        succeeded: 0,
        failed: 0,
        skipped: 0,
        other: 0

    };


    tasks.forEach(
        function (task) {

            const status =
                normalizeStatus(
                    task.status
                );


            if (
                status === "succeeded"
            ) {

                counters.succeeded += 1;

            } else if (
                status === "failed"
            ) {

                counters.failed += 1;

            } else if (
                status === "skipped"
            ) {

                counters.skipped += 1;

            } else {

                counters.other += 1;
            }

        }
    );


    appendSummaryChip(
        "任务 "
        +
        tasks.length
    );


    if (
        counters.succeeded > 0
    ) {

        appendSummaryChip(
            "成功 "
            +
            counters.succeeded
        );
    }


    if (
        counters.failed > 0
    ) {

        appendSummaryChip(
            "失败 "
            +
            counters.failed
        );
    }


    if (
        counters.skipped > 0
    ) {

        appendSummaryChip(
            "跳过 "
            +
            counters.skipped
        );
    }

}


function appendSummaryChip(
    text
) {

    const chip =
        document.createElement(
            "span"
        );


    chip.className =
        "summary-chip";


    chip.textContent =
        text;


    workflowSummary.appendChild(
        chip
    );

}


// ============================================================
// 渲染任务列表
// ============================================================

function renderTasks(
    tasks
) {

    taskList.innerHTML = "";


    if (
        tasks.length === 0
    ) {

        const empty =
            document.createElement(
                "div"
            );


        empty.className =
            "task-description";


        empty.textContent =
            "当前工作流没有返回任务执行信息。";


        taskList.appendChild(
            empty
        );


        return;
    }


    tasks.forEach(
        function (task) {

            const card =
                createTaskCard(
                    task
                );


            taskList.appendChild(
                card
            );

        }
    );

}


// ============================================================
// 创建任务卡片
// ============================================================

function createTaskCard(
    task
) {

    const card =
        document.createElement(
            "article"
        );


    card.className =
        "task-card";


    // --------------------------------------------------------
    // 任务主信息
    // --------------------------------------------------------

    const main =
        document.createElement(
            "div"
        );


    main.className =
        "task-main";


    const taskId =
        document.createElement(
            "div"
        );


    taskId.className =
        "task-id";


    taskId.textContent =
        task.task_id
        ||
        "任务";


    const agent =
        document.createElement(
            "div"
        );


    agent.className =
        "agent-name";


    agent.textContent =
        formatAgentName(
            task.agent_name
        );


    const description =
        document.createElement(
            "div"
        );


    description.className =
        "task-description";


    description.textContent =
        task.description
        ||
        "暂无任务描述";


    const status =
        createStatusBadge(
            task.status
        );


    main.appendChild(
        taskId
    );

    main.appendChild(
        agent
    );

    main.appendChild(
        description
    );

    main.appendChild(
        status
    );


    card.appendChild(
        main
    );


    // --------------------------------------------------------
    // 执行详情
    // --------------------------------------------------------

    const details =
        document.createElement(
            "details"
        );


    details.className =
        "task-details";


    const summary =
        document.createElement(
            "summary"
        );


    summary.textContent =
        "查看执行详情";


    details.appendChild(
        summary
    );


    const content =
        document.createElement(
            "div"
        );


    content.className =
        "detail-content";


    appendDetailRow(
        content,
        "执行智能体",
        formatAgentName(
            task.agent_name
        )
    );


    appendDetailRow(
        content,
        "原始 Agent 标识",
        task.agent_name
        || "-"
    );


    appendDetailRow(
        content,
        "依赖任务",
        formatDependencies(
            task.dependencies
        )
    );


    appendDetailRow(
        content,
        "执行结果",
        task.success
            ? "成功"
            : "未成功"
    );


    if (
        task.error
    ) {

        appendDetailRow(
            content,
            "错误信息",
            String(
                task.error
            )
        );
    }


    if (
        task.answer
    ) {

        const answerRow =
            document.createElement(
                "div"
            );


        answerRow.className =
            "detail-row";


        const label =
            document.createElement(
                "div"
            );


        label.className =
            "detail-label";


        label.textContent =
            "智能体执行结果";


        const answer =
            document.createElement(
                "div"
            );


        answer.className =
            "detail-answer";


        // 不使用 innerHTML，
        // 防止模型返回内容被浏览器当作 HTML 执行。
        answer.textContent =
            String(
                task.answer
            );


        answerRow.appendChild(
            label
        );

        answerRow.appendChild(
            answer
        );


        content.appendChild(
            answerRow
        );
    }


    details.appendChild(
        content
    );


    card.appendChild(
        details
    );


    return card;
}


// ============================================================
// 执行详情行
// ============================================================

function appendDetailRow(
    container,
    labelText,
    valueText
) {

    const row =
        document.createElement(
            "div"
        );


    row.className =
        "detail-row";


    const label =
        document.createElement(
            "span"
        );


    label.className =
        "detail-label";


    label.textContent =
        labelText
        +
        "：";


    const value =
        document.createElement(
            "span"
        );


    value.textContent =
        valueText;


    row.appendChild(
        label
    );

    row.appendChild(
        value
    );


    container.appendChild(
        row
    );

}


// ============================================================
// 任务状态
// ============================================================

function createStatusBadge(
    statusValue
) {

    const status =
        normalizeStatus(
            statusValue
        );


    const badge =
        document.createElement(
            "span"
        );


    badge.className =
        "status-badge "
        +
        "status-"
        +
        status;


    badge.textContent =
        getStatusText(
            status
        );


    return badge;
}


// 后端状态保持英文。
// 页面只负责转换为中文显示。

function getStatusText(
    status
) {

    const mapping = {

        succeeded:
            "执行成功",

        failed:
            "执行失败",

        skipped:
            "已跳过",

        running:
            "执行中",

        pending:
            "等待执行",

        missing:
            "状态未知"

    };


    return (
        mapping[status]
        ||
        "状态未知"
    );
}


function normalizeStatus(
    status
) {

    const value =
        String(
            status
            ||
            "missing"
        )
            .toLowerCase();


    const supported = [
        "succeeded",
        "failed",
        "skipped",
        "running",
        "pending",
        "missing"
    ];


    if (
        supported.includes(
            value
        )
    ) {

        return value;
    }


    return "missing";
}


// ============================================================
// Agent 中文名称
// ============================================================

function formatAgentName(
    agentName
) {

    const value =
        String(
            agentName
            ||
            "unknown"
        )
            .toLowerCase();


    const mapping = {

        llm:
            "通用 LLM 智能体",

        database:
            "数据库智能体",

        knowledge:
            "知识库智能体",

        production:
            "生产 MES 智能体"

    };


    return (
        mapping[value]
        ||
        agentName
        ||
        "未知智能体"
    );
}


// ============================================================
// Dependency
// ============================================================

function formatDependencies(
    dependencies
) {

    if (
        !Array.isArray(
            dependencies
        )
        ||
        dependencies.length === 0
    ) {

        return "无";
    }


    return dependencies.join(
        "、"
    );
}


// ============================================================
// 错误提示
// ============================================================

function showError(
    message
) {

    errorMessage.textContent =
        message;


    errorPanel.classList.remove(
        "hidden"
    );
}


// ============================================================
// 运行状态
// ============================================================

function setRunningState(
    running
) {

    isRunning =
        running;


    sendButton.disabled =
        running;


    clearButton.disabled =
        running;


    questionInput.disabled =
        running;


    exampleButtons.forEach(
        function (button) {

            button.disabled =
                running;

        }
    );


    if (running) {

        sendButton.textContent =
            "正在分析...";

    } else {

        sendButton.textContent =
            "开始分析";
    }

}