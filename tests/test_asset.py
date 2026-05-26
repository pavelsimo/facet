from __future__ import annotations

from pathlib import Path

import pytest

from fascat.asset import Asset, Node
from fascat.material import Material


def test_material_copies_input_metadata() -> None:
    metadata = {"source": "cad"}

    material = Material(id="red", name="Red", base_color=(1.0, 0.0, 0.0, 1.0), metadata=metadata)
    metadata["source"] = "changed"

    assert material.metadata == {"source": "cad"}


def test_asset_copy_isolates_material_metadata() -> None:
    asset = Asset(
        root=Node(id="root", name="root"),
        materials={"red": Material(id="red", name="Red", base_color=(1.0, 0.0, 0.0, 1.0), metadata={"source": "cad"})},
    )

    copied = asset.copy()
    copied.materials["red"].metadata["source"] = "copy"

    assert asset.materials["red"].metadata == {"source": "cad"}
    assert copied.materials["red"].metadata == {"source": "copy"}


def test_asset_write_usd_records_report_step(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import fascat.io.usd as usd

    asset = Asset(root=Node(id="root", name="root"))
    output = tmp_path / "output.usda"
    calls: dict[str, object] = {}

    def fake_write_usd(written_asset: Asset, path: str | Path, *, debug: bool = False) -> None:
        calls["asset"] = written_asset
        calls["path"] = path
        calls["debug"] = debug

    monkeypatch.setattr(usd, "write_usd", fake_write_usd)

    asset.write_usd(output, debug=True)
    step = asset.report.steps[-1]

    assert calls == {"asset": asset, "path": output, "debug": True}
    assert step.name == "write"
    assert step.options == {"format": "OpenUSD", "debug": True}
    assert step.before == asset.stats()
    assert step.after == asset.stats()
    assert step.duration >= 0.0
    assert asset.report.finished_at is not None
    assert asset.report.output_stats == asset.stats()


def test_asset_write_usd_records_failure_report(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import fascat.io.usd as usd

    asset = Asset(root=Node(id="root", name="root"))

    def fail_write_usd(_asset: Asset, _path: str | Path, *, debug: bool = False) -> None:
        raise RuntimeError("disk full")

    monkeypatch.setattr(usd, "write_usd", fail_write_usd)

    with pytest.raises(RuntimeError, match="disk full") as error:
        asset.write_usd(tmp_path / "output.usda")

    step = asset.report.steps[-1]
    assert error.value.report is asset.report
    assert asset.report.errors == ["disk full"]
    assert step.name == "write"
    assert step.after == asset.stats()
    assert asset.report.finished_at is not None
    assert asset.report.output_stats == asset.stats()
