# uv: Create & Activate a Named Environment (Linux)

## 1. Create the environment

Give it a name (here `myenv`) instead of the default `.venv`:

```bash
uv venv myenv
```

Optional — pick a Python version:

```bash
uv venv myenv --python 3.12
```

## 2. Activate the environment

```bash
source myenv/bin/activate
```

## 3. Deactivate

```bash
deactivate
```

---

**Tip:** Once activated, install packages with `uv pip install <package>`.
