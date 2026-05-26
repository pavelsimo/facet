from __future__ import annotations

import numpy as np

import fascat as fc


def test_functional_api_wraps_asset_operations() -> None:
    mesh = fc.Mesh(
        points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=float),
        faces=np.array([[0, 1, 2], [2, 1, 3]], dtype=int),
    )
    asset = fc.Asset(
        root=fc.Node(id="root", name="root", children=[fc.Node(id="node", name="node", part_id="part")]),
        parts={"part": fc.Part(id="part", name="Part", mesh=mesh)},
    )

    repaired = fc.repair(asset)
    staged = fc.stage(repaired, uv0="box", uv1="box")
    optimized = fc.optimize(staged, target_triangles=1, preserve_instances=True)
    with_lods = fc.lods(optimized, ratios=(0.5,))

    part = with_lods.parts["part"]
    assert part.mesh is not None
    assert sorted(part.mesh.uvs) == [0, 1]
    assert len(part.lod_meshes) == 1


def test_node_to_dict_includes_transform() -> None:
    transform = np.eye(4, dtype=float)
    transform[0, 3] = 2.5
    node = fc.Node(id="node", name="node", transform=transform)

    assert node.to_dict()["transform"] == transform.tolist()
