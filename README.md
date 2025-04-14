# ToolArena

## Contributing
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to contribute a task to ToolArena.

## Installation
1. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/).
2. Install this project in a virtual environment:
   ```bash
   uv sync --all-groups
   ```
   This will create a virtual environment at `.venv/`.
3. Activate the virtual environment:
   ```bash
   ./venv/bin/activate
   ```
4. Check that the installation succeeded by verifying that the `toolarena` command exists:
   ```bash
   toolarena --help
   ```

### Environment setup
At the root of this repository, create a `.env` file with the following contents:
```bash
CUDA_VISIBLE_DEVICES=0 # If you have a GPU, set this to the device ID of the GPU you want to use, otherwise leave blank
HF_TOKEN=hf_abcdefghijklmnopqrstuvwxyz0123456789 # Replace with your HuggingFace token
```
Replace the `HF_TOKEN` variable with your [HuggingFace token](https://huggingface.co/settings/tokens).
You must request access to the following repositories on HuggingFace:
- [MahmoodLab/UNI](https://huggingface.co/MahmoodLab/UNI) (for [`uni_extract_features`](tasks/uni_extract_features/))
- [MahmoodLab/CONCH](https://huggingface.co/MahmoodLab/CONCH) (for [`conch_extract_features`](tasks/conch_extract_features/))
- [xiangjx/musk](https://huggingface.co/xiangjx/musk) (for [`musk_extract_features`](tasks/musk_extract_features/))

## Tasks
Tasks are defined in the [`tasks/`](tasks/) directory.
Each task is in a subfolder therein, and its task definition is available at `task.yaml`.

## Running a candidate implementation
A candidate implementation must consist of two files:
1. A bash script, `install.sh`, which installs all necessary dependencies for the tool (including cloning the associated repository)
2. A Python file, `implementation.py`, containing the Python implementation of the task. This file must define a function with the correct signature according to the task definition in `task.yaml`.
   > [!NOTE]
   > To see how the signature of the candidate implementation function should look like, simply run:
   > ```bash
   > toolarena signature $TASK
   > ```
   > where `$TASK` is the name of the task in question.

You should create an *implementation directory* where you store candidate implementations for the tasks. The directory structure will look as follows:
```
my_implementations/
  ├─ my_nifty_task/
  │   ├─ install.sh
  │   └─ implementation.py
  └─ ...  # more tasks (optional)
```

You can run your candidate implementation for a particular *invocation* using the following command:
```bash
TASK=my_nifty_task
INVOCATION=example
IMPLEMENTATION_DIR=my_implementations

toolarena run $TASK $INVOCATION --implementation $IMPLEMENTATION_DIR
```
Here, the `$INVOCATION` can either be `"example"` (referring to the example invocation provided in `task.yaml`), or it could be one of the names of the test invocations supplied in `task.yaml` in the `test_invocations` section.

> [!TIP]
> To run all invocations, you can simply omit the `$INVOCATION` from the `toolrarena run` command. In this case, ToolArena will run the example invocation as well as *all* test invocations.

> [!NOTE]
> The `toolarena run` command will cache the outputs of the command, so if you run the same invocation with the same implementation multiple times, the tool does not need to be invoked multiple times. 

## Running the benchmark
To run the benchmark on candidate implementations that you have created using your own agents, first ensure that you have stored the candidate implementations using the following directory structure:
```
my_implementations/
  ├─ conch_extract_features/
  │   ├─ install.sh
  │   └─ implementation.py
  └─ ...  # all other tasks defined in `tasks/`
```
You can run the unit tests which constitute the benchmark using the following command:
```bash
pytest tasks --implementation $IMPLEMENTATION_DIR
```

> [!TIP]
> If you only want to run the tests for invocations that are **already cached** (by running the `toolmaker run` command as described [above](#running-a-candidate-implementation)), use the following command:
> ```bash
> pytest tasks --implementation $IMPLEMENTATION_DIR --skip-uncached
> ```

> [!TIP]
> If you only want to run tests for a **specific task**, use the following command:
> ```bash
> pytest tasks/$TASK --implementation $IMPLEMENTATION_DIR
> ```

## Running the reference implementation
Each task provides a human-generated *reference implementation* to prove that the task is possible.
The reference implementations are supplied alongside the task definitions in the [`tasks/`](tasks/) directory.

To run these reference implementations, simply set `--implementation tasks/`, or remove the `--implementation` flag entirely, as follows:
- Running a specific invocation:
  ```bash
  toolarena run $TASK $INVOCATION
  ```
- Running the benchmark:
  ```bash
  pytest tasks
  ```
- Running the benchmark for a specific task:
  ```bash
  pytest tasks/$TASK
  ```

## Debugging candidate implementations
See [here](CONTRIBUTING.md#10-check-that-the-example-invocation-works).