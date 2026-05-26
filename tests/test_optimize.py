from __future__ import annotations

import numpy as np

from fascat.asset import Asset, Node, Part
from fascat.mesh import Mesh
from fascat.options import OptimizeOptions


def test_optimize_can_duplicate_repeated_parts_per_occurrence() -> None:
    mesh = Mesh(
        points=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float),
        faces=np.array([[0, 1, 2]], dtype=int),
    )
    root = Node(
        id="root",
        name="root",
        children=[
            Node(id="node_a", name="A", part_id="part"),
            Node(id="node_b", name="B", part_id="part"),
        ],
    )
    asset = Asset(root=root, parts={"part": Part(id="part", name="Part", mesh=mesh)})

    optimized = asset.optimize(OptimizeOptions(simplify=False, optimize_buffers=False, preserve_instances=False))
    part_ids = [node.part_id for node in optimized.root.walk() if node.part_id is not None]

    assert optimized.part_count == 2
    assert len(set(part_ids)) == 2
    assert all(part_id is not None and part_id.startswith("part_") for part_id in part_ids)
    assert {part.metadata["source_part_id"] for part in optimized.parts.values()} == {"part"}


def test_target_triangles_wins_over_ratio() -> None:
    mesh = Mesh(
        points=np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0, 1, 0],
                [1, 1, 0],
                [0, 2, 0],
                [1, 2, 0],
            ],
            dtype=float,
        ),
        faces=np.array([[0, 1, 2], [2, 1, 3], [2, 3, 4], [4, 3, 5]], dtype=int),
    )
    asset = Asset(
        root=Node(id="root", name="root", children=[Node(id="node", name="node", part_id="part")]),
        parts={"part": Part(id="part", name="Part", mesh=mesh)},
    )

    optimized = asset.optimize(OptimizeOptions(target_triangles=3, ratio=0.25, simplify=True, optimize_buffers=False))
    optimized_mesh = optimized.parts["part"].mesh

    assert optimized_mesh is not None
    assert optimized_mesh.triangle_count == 3
