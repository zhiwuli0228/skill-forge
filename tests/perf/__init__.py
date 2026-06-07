"""Performance-campaign harness for skill-forge.

This package is the v0.6.x project-level evidence collection
asset extracted from the v0.6.0-remediation-campaign-001
monolithic script. The harness is stdlib-only, decoupled
from ``src/skill_forge/``, and invokable via
``python -m tests.perf._main``.

The ``_`` prefix on every module name prevents pytest's
default ``test_*.py`` / ``*_test.py`` collection pattern
from picking up the harness. Verified by
``uv run pytest --collect-only -q | grep -c "tests/perf/"`` == 0.
"""

__all__: list[str] = []
