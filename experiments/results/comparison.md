# MySQL Connector Compatibility Comparison

This table contains only recorded experiment results. No missing target or case is inferred.

## Environments

| Target | Server version | Connector version | Python version | Evidence |
|---|---|---|---|---|
| oceanbase | 5.7.25-OceanBase_CE-v4.4.2.1 | 26.7.0 | 3.12.14 (main, Sep  1 2026, 14:16:52) [Clang 22.1.3 ] | `experiments/results/mysql_connector_compat.json` |
| mysql8 | 8.0.46 | 26.7.0 | 3.12.14 (main, Sep  1 2026, 14:16:52) [Clang 22.1.3 ] | `experiments/results/mysql8.json` |

## Results

Each result is `Connect / SELECT 1 / CRUD`.

| Case | oceanbase | mysql8 |
|---|---|---|
| C Extension / default | FAIL / - / - | PASS / PASS / PASS |
| Pure Python / default | PASS / PASS / PASS | PASS / PASS / PASS |
| C Extension / explicit | FAIL / - / - | PASS / PASS / PASS |
| Pure Python / explicit | PASS / PASS / PASS | PASS / PASS / PASS |
