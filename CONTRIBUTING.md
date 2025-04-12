# Contributing a new task to ToolArena

Thank you for your interest in contributing a new task to ToolArena! This guide walks you through the steps to add a new task (tool) to this benchmark repository by opening a pull request.

## Overview

ToolArena is a benchmark for LLM-based agentic "tool creation." 

Specifically, the purpose of this benchmark is to assess how well LLM agents can create LLM-compatible "tools" from GitHub repositories.
You can think of a tool as a Python function that performs a given task: it has input arguments, and returns some sort of output.

> [!NOTE]  
> The terms "task" and "tool" are used interchangeably in this guide.

Each task in ToolArena consists of:
1. A **task definition** (`task.yaml`) containing basic metadata, inputs/outputs, test invocations, etc.
2. A **reference solution** (i.e. implementation), consisting of:
   - An **installation script** (`install.sh`) that installs all necessary dependencies to run the tool.
   - An **code implementation** (`implementation.py`) containing the Python implementation for the tool itself.
3. Any **data** files needed to invoke the tool (`data/` and `data/tests`).
4. Several **unit tests** to assess the correctness of a candidate implementation (`tests.py`).

When you create a new task, you place these files in a directory under `tasks/`. For example, if your task is named `my_nifty_task`, your files would live under `tasks/my_nifty_task/`.

> This guide will walk you through creating all the necessary files to define a task. At the end of this guide, you will have produced the following directory structure:
> ```
> tasks/
>  └─ my_nifty_task/
>      ├─ task.yaml
>      ├─ install.sh
>      ├─ implementation.py
>      ├─ tests.py
>      └─ data/
>          ├─ download.sh  # (optional script to download external data)
>          ├─ ...  # (your data files)
>          └─ tests/
>              └─ ...  # (optional additional data files for tests)

---

## Table of Contents

1. [Fork the repository](#1-fork-the-repository)
2. [Create a new task folder](#2-create-a-new-task-folder)
3. [Fill in your `task.yaml`](#3-fill-in-your-taskyaml)
4. [Write `install.sh`](#4-write-installsh)
5. [Write `implementation.py`](#5-write-implementationpy)
6. [Add test coverage (optional but recommended)](#6-add-test-coverage-optional-but-recommended)
7. [Run and verify your new task locally](#7-run-and-verify-your-new-task-locally)
8. [Submit a pull request](#8-submit-a-pull-request)
9. [Tips and best practices](#9-tips-and-best-practices)

---

## 1. Fork the repository

1. Click the "Fork" button in the GitHub UI to create your personal copy of ToolArena.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/ToolArena.git
   cd ToolArena
   ```

## 2. Install ToolArena
1. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/).
2. Install this project in a virtual environment:
   ```bash
   uv sync
   ```
   This will create a virtual environment at `.venv/`.
3. Activate the cirtual environment:
   ```bash
   ./venv/bin/activate
   ```
4. Check that the installation succeeded by verifyingn that the `toolarena` command exists:
   ```bash
   toolarena --help
   ```

## 3. Create a new task

Use the following command to create a new task:
```bash
toolarena init my_nifty_task
```
This will create a new task at `tasks/my_nifty_task` with the following files to get you started:
```
tasks/
 └─ my_nifty_task/
     ├─ task.yaml
     ├─ tests.py
     └─ data/
         └─ download.sh
```

## 4. Fill in your task definition (`task.yaml`)

You will find an automatically generated `task.yaml` file in your task folder (`tasks/my_nifty_task/task.yaml`). 
Edit the `task.yaml` file to define your task. 
Take special care to come up with a task `description`, and make sure all `arguments` and `returns` are specified.

> [!NOTE]  
> At any point, you can run the following command to see how the Python function signature of your task will look like:
> ```bash
> toolarena signature my_nifty_task
> ```

> [!TIP]  
> You can use an existing task in `tasks/` as a reference (for instance, [`tasks/conch_extract_features/task.yaml`](tasks/conch_extract_features/task.yaml)).

### Key sections to include
At this point, you should at least define the following parts:
1. **`name`**: matches the folder name (e.g., `mynifty_task`).
2. **`description`**: One or two sentences describing what your tool does.
3. **`repo`**: your should wrap functionality from a GitHub repository, so please specify:
   ```yaml
   repo:
     name: MyRepo
     url: "https://github.com/username/MyRepo"
     commit: abc123
     branch: main
     env:  # (optional)
       MY_TOKEN: "${env:MY_TOKEN}"
   ```
4. **`arguments`**: inputs your tool expects.
5. **`returns`**: outputs your tool produces.
