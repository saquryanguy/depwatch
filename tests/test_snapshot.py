"""Tests for depwatch.snapshot."""
import pytest

from depwatch.snapshot import (
    DependencySnapshot,
    diff_snapshots,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


@pytest.fixture()
def tmp_snap_dir(tmp_path):
    return str(tmp_path / "snaps")


def _snap(run_id="run1", ref="abc123", packages=None):
    return DependencySnapshot(
        run_id=run_id,
        ref=ref,
        packages=packages or {"requests": "2.28.0"},
    )


def test_save_creates_file(tmp_snap_dir):
    snap = _snap()
    path = save_snapshot(snap, snapshot_dir=tmp_snap_dir)
    assert path.exists()


def test_load_roundtrip(tmp_snap_dir):
    snap = _snap(packages={"flask": "2.3.0", "click": "8.1.0"})
    save_snapshot(snap, snapshot_dir=tmp_snap_dir)
    loaded = load_snapshot(snap.run_id, snapshot_dir=tmp_snap_dir)
    assert loaded is not None
    assert loaded.run_id == snap.run_id
    assert loaded.ref == snap.ref
    assert loaded.packages == snap.packages


def test_load_missing_returns_none(tmp_snap_dir):
    result = load_snapshot("nonexistent", snapshot_dir=tmp_snap_dir)
    assert result is None


def test_load_corrupt_returns_none(tmp_snap_dir):
    import pathlib
    pathlib.Path(tmp_snap_dir).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(tmp_snap_dir) / "bad.json").write_text("not json{{{")
    result = load_snapshot("bad", snapshot_dir=tmp_snap_dir)
    assert result is None


def test_list_snapshots_empty(tmp_snap_dir):
    assert list_snapshots(snapshot_dir=tmp_snap_dir) == []


def test_list_snapshots_returns_run_ids(tmp_snap_dir):
    save_snapshot(_snap(run_id="run_b"), snapshot_dir=tmp_snap_dir)
    save_snapshot(_snap(run_id="run_a"), snapshot_dir=tmp_snap_dir)
    ids = list_snapshots(snapshot_dir=tmp_snap_dir)
    assert ids == ["run_a", "run_b"]


def test_diff_snapshots_detects_upgrade():
    old = _snap(packages={"requests": "2.27.0"})
    new = _snap(packages={"requests": "2.28.0"})
    changes = diff_snapshots(old, new)
    assert "requests" in changes
    assert changes["requests"] == ("2.27.0", "2.28.0")


def test_diff_snapshots_no_change():
    snap = _snap(packages={"requests": "2.28.0"})
    changes = diff_snapshots(snap, snap)
    assert changes == {}


def test_diff_snapshots_new_package():
    old = _snap(packages={})
    new = _snap(packages={"flask": "3.0.0"})
    changes = diff_snapshots(old, new)
    assert changes["flask"] == (None, "3.0.0")


def test_diff_snapshots_unchanged_packages_excluded():
    old = _snap(packages={"requests": "2.28.0", "click": "8.0.0"})
    new = _snap(packages={"requests": "2.28.0", "click": "8.1.0"})
    changes = diff_snapshots(old, new)
    assert "requests" not in changes
    assert "click" in changes
