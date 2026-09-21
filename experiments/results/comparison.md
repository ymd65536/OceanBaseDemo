# MySQL Connector Compatibility Comparison

This report contains recorded experiment facts only. No missing result or root cause is inferred.

## Environments

| Target | Server version | Connector version | Python version | Platform | Experiment runner | Evidence |
|---|---|---|---|---|---|---|
| mysql57 | 5.7.44 | 26.7.0 | 3.12.14 (main, Sep  1 2026, 14:16:52) [Clang 22.1.3 ] | Linux-6.8.0-1064-azure-x86_64-with-glibc2.43 | `experiments/mysql_connector_compat.py` | `experiments/results/mysql57.json` |
| mysql8 | 8.0.46 | 26.7.0 | 3.12.14 (main, Sep  1 2026, 14:16:52) [Clang 22.1.3 ] | Linux-6.8.0-1064-azure-x86_64-with-glibc2.43 | `experiments/mysql_connector_compat.py` | `experiments/results/mysql8.json` |
| oceanbase | 5.7.25-OceanBase_CE-v4.4.2.1 | 26.7.0 | 3.12.14 (main, Sep  1 2026, 14:16:52) [Clang 22.1.3 ] | Linux-6.8.0-1064-azure-x86_64-with-glibc2.43 | `experiments/mysql_connector_compat.py` | `experiments/results/mysql_connector_compat.json` |

## Recorded Results (FACT)

Each result is `Connect / SELECT 1 / CRUD`.

| Case | mysql57 | mysql8 | oceanbase |
|---|---|---|---|
| C Extension / default | PASS / PASS / PASS | PASS / PASS / PASS | FAIL / - / - |
| Pure Python / default | PASS / PASS / PASS | PASS / PASS / PASS | PASS / PASS / PASS |
| C Extension / explicit | PASS / PASS / PASS | PASS / PASS / PASS | FAIL / - / - |
| Pure Python / explicit | PASS / PASS / PASS | PASS / PASS / PASS | PASS / PASS / PASS |
