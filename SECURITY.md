# Security Policy

| Version | Supported |
| ------- | --------- |
| 0.x     | ✅        |

AURUM is a reference implementation — not a production service.

## Reporting a Concern

If you find code that could mislead practitioners into insecure patterns
(hardcoded credentials in examples, unsafe deserialization, injection-prone queries),
open a [GitHub Issue](../../issues) with label `security-concern`. Describe the file,
the pattern, and the safer alternative. Response within 7 days.

## Dependency Check

```bash
pip install pip-audit && pip-audit -r requirements.txt
```
