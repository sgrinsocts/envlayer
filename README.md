# envlayer

> Lightweight env file manager that supports per-profile overrides and secret masking.

---

## Installation

```bash
pip install envlayer
```

---

## Usage

```python
from envlayer import EnvLayer

# Load base .env with a profile override and mask secrets in output
env = EnvLayer(profile="production", mask_secrets=True)
env.load()

# Access variables
db_url = env.get("DATABASE_URL")
print(env)  # Secrets like API keys are masked: sk-****

# Export merged env to a file
env.export(".env.merged")
```

**File structure example:**

```
.env                  # base config
.env.production       # production overrides (merged on top of base)
.env.development      # development overrides
```

Variables defined in `.env.<profile>` take precedence over `.env`.

---

## Features

- 🔀 Per-profile `.env` overrides
- 🔒 Automatic secret masking for sensitive keys (`SECRET`, `KEY`, `TOKEN`, `PASSWORD`)
- 📦 Zero dependencies
- 🐍 Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).