---
id: E-001
domain: engineering
title: "Asyncio: Silent Exception Swallowing in create_task"
summary: "Use this when using asyncio.create_task() to prevent silent exception swallowing that causes impossible-to-diagnose bugs in async Python code."
tags: [async, asyncio, exception, python, silent-failure]
keywords: [asyncio, create_task, exception swallowed, task exception ignored, coroutine error lost, done callback]
aliases: ["silent asyncio exception", "task exception lost", "asyncio create_task bug"]
triggers: [asyncio, create_task, concurrent tasks, coroutine, async exception, task exception]
severity: high
date_created: 2026-03-14
source_project: general
transferable: true
---

## Problem
When using `asyncio.create_task()`, exceptions raised inside the task are silently ignored unless the task result is explicitly awaited or retrieved. This leads to bugs that are extremely hard to diagnose.

## Root Cause
Python's asyncio stores the exception in the Task object but does not raise it unless:
1. The task is `await`ed
2. `task.result()` is called
3. The task is garbage collected (prints a warning, but doesn't crash)

## Solution
```python
# BAD: exception silently swallowed
task = asyncio.create_task(some_coroutine())

# GOOD: always await or add a callback
task = asyncio.create_task(some_coroutine())
task.add_done_callback(lambda t: t.result() if not t.cancelled() else None)

# BETTER: use TaskGroup (Python 3.11+)
async with asyncio.TaskGroup() as tg:
    tg.create_task(some_coroutine())
# exceptions propagate automatically
```

## Prevention
- Always use `asyncio.TaskGroup` for managing concurrent tasks (Python 3.11+)
- If using `create_task()`, always store the reference and await it
- Add a global exception handler: `loop.set_exception_handler(handler)`

## Related
- Python docs: asyncio Task
- PEP 654: Exception Groups
