# Python and PySpark conventions

Read before writing or reviewing Python. Routed from `AGENTS.md`.

## Style

- PEP 8, line length 120; format with `ruff format` (or `black`), lint with `ruff` (or `flake8`), imports sorted.
- Type hints on public function signatures; Google-style docstrings on public functions and classes.
- Imports: standard library, third party, local, separated by blank lines; absolute imports across packages; never `import *`.
- Functions are verbs (`load_orders`, `validate_schema`, `transform_silver`), under about 50 lines, guard clauses instead of deep nesting.

## Errors and logging

- Catch specific exceptions; never bare `except:`.
- `logging`, never `print()`, in pipeline and job code (test files may print).
- Re-raise with context: `raise ValueError("...") from err`.
- Retry transient failures with exponential backoff; fail fast on permanent ones.
- Never log PII or secrets; mask in error messages.

## PySpark

- Declarative first: in a Lakeflow pipeline use `from pyspark import pipelines as dp`, streaming tables, materialized views, AUTO CDC and expectations before reaching for DataFrame plumbing.
- DataFrame variables are `snake_case` nouns: `df_orders`, `df_customers`.
- No `collect()` or `toPandas()` on large frames; no `df.count()` for emptiness or logging (`df.isEmpty()`).
- No Python UDFs when a native function or `ai_*` SQL function exists; if unavoidable, `pandas_udf`.
- Order: filter, then join, then aggregate; broadcast small dimensions; cast join keys to matching types; handle NULL keys explicitly.
- Every stateful streaming operation has a watermark.
- Never build `spark.sql` strings with f-strings from variables; use `spark.sql(query, args={...})` or an allowlist regex such as `^[a-z0-9_.]+$` on identifiers.
- No `spark.conf.set` cluster tuning inside pipeline code; it is ignored on serverless. Use pipeline configuration.
- Serverless: no `.cache()`, `.persist()`, broadcast variables, or RDD APIs.

## Tests

- Mirror the source tree: `src/x/foo.py` to `tests/unit/test_foo.py`.
- Spark tests run in the workspace: pipeline unit tests in the Pipelines Editor, or `pytest.main([...])` in a notebook cell.
- `SparkSession.builder.getOrCreate()` only; never `.master(...)` or `spark.stop()`.
- Independent tests, no shared mutable state; build inputs with `spark.createDataFrame`; mock all external I/O.
- Tests are executed, and their summary pasted into `progress.md`, before a task is ticked.

## Entry points

- A module meant for `spark_python_task` or a wheel task has an `if __name__ == "__main__":` block that parses arguments, gets the session, calls the runner and `sys.exit()`s with a code.
- Library modules do not need one.
