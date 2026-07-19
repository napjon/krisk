from pathlib import Path

import pandas as pd
import pytest

from krisk.sources import FileSource, FrameSource, SourceError, validate_readonly_sql
from krisk.specs import ChartSpec, ClaimSpec
from krisk.storage import ArtifactStore


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM read_csv_auto('/etc/hosts')",
        "SELECT * FROM read_parquet('/tmp/private.parquet')",
        "SELECT pg_read_file('/etc/hosts')",
        "SELECT pg_read_binary_file('/etc/hosts')",
        "SELECT lo_import('/etc/hosts')",
        "SELECT * FROM postgres_scan('secret', 'public', 'users')",
        "SELECT * FROM glob('/etc/*')",
    ],
)
def test_sql_guard_rejects_external_and_admin_functions(sql):
    with pytest.raises(SourceError):
        validate_readonly_sql(sql)


@pytest.mark.parametrize(
    "source",
    [
        FrameSource({"sales": pd.DataFrame({"value": [1, 2]})}),
        FileSource(Path("krisk/tests/data")),
    ],
)
def test_local_sources_reject_relation_and_file_escape(source):
    with pytest.raises(SourceError):
        source.execute("SELECT count(*) FROM read_csv_auto('/etc/hosts')")
    with pytest.raises(SourceError, match="Relation"):
        source.execute("SELECT * FROM information_schema.tables")
    with pytest.raises(SourceError, match="Table functions"):
        source.execute("SELECT * FROM duckdb_secrets()")


def test_local_sources_allow_registered_relations_and_ctes():
    source = FrameSource({"sales": pd.DataFrame({"value": [1, 2]})})
    result = source.execute(
        "WITH totals AS (SELECT sum(value) AS value FROM sales) SELECT * FROM totals"
    )
    assert result.to_dict(orient="records") == [{"value": 3.0}]


@pytest.mark.parametrize(
    "override",
    [
        {"tooltip": {"formatter": "() => 1"}},
        {"series": {"renderItem": "return 1"}},
        {"color": "javascript:alert(1)"},
        {"custom": "function malicious() {}"},
    ],
)
def test_chart_overrides_reject_executable_strings(override):
    with pytest.raises(ValueError, match="Executable JavaScript"):
        ChartSpec(kind="bar", x="x", safe_overrides=override)


def test_artifact_size_rejection_never_unlinks_existing_digest(tmp_path):
    store = ArtifactStore(tmp_path / "artifacts")
    frame = pd.DataFrame({"value": range(100)})
    _, path, size = store.save_frame(frame)

    with pytest.raises(ValueError, match="snapshot exceeds"):
        store.save_frame(frame, max_bytes=size - 1)

    assert path.exists()
    assert store.load_frame(path).equals(frame)


def test_claim_kinds_enforce_operator_semantics():
    with pytest.raises(ValueError, match="Range claims"):
        ClaimSpec(label="bad range", kind="range", query_id="q", operator="gte", expected=1)
    with pytest.raises(ValueError, match="compare_column"):
        ClaimSpec(label="bad comparison", kind="comparison", query_id="q", operator="gte")
    with pytest.raises(ValueError, match="Equality claims"):
        ClaimSpec(
            label="bad warning",
            kind="threshold",
            query_id="q",
            operator="eq",
            expected=1,
            warning_tolerance=0.1,
        )
