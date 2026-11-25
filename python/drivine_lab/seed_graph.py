from __future__ import annotations

import argparse
import asyncio
import json
import os
from collections import defaultdict

from drivine_lab.paths import CONCEPTS_PATH, DEFAULT_GRAPH_DB, INSTRUCT_PATH


async def _seed(graph_path: str, concepts_path: str, instruct_path: str) -> None:
    from drivine import DatabaseType, DrivineAssembly

    from drivine_lab.models import Concept, ConceptBrief, DocChunk

    os.environ["DATABASE_TYPE"] = "SQLITE"
    os.environ["DATABASE_NAME"] = graph_path

    concepts = json.loads(open(concepts_path, encoding="utf-8").read())
    instruct = json.loads(open(instruct_path, encoding="utf-8").read())

    by_topic: dict[str, list[dict]] = defaultdict(list)
    for row in instruct:
        by_topic[row.get("topic", "overview")].append(row)

    async with DrivineAssembly() as drivine:
        # Touch registry type for clarity in logs / future multi-db setups.
        _ = DatabaseType.SQLITE
        gom = drivine.graph_object_manager()

        concept_ids = {c["id"] for c in concepts}
        for concept in concepts:
            related_ids = [rid for rid in concept.get("related", []) if rid in concept_ids]
            examples = [
                DocChunk(
                    uuid=row["id"],
                    topic=row.get("topic", "overview"),
                    instruction=row["instruction"],
                    response=row["response"],
                )
                for row in by_topic.get(concept["id"], [])[:3]
            ]
            # Also attach topic-matched examples when concept id != topic key.
            if not examples:
                examples = [
                    DocChunk(
                        uuid=row["id"],
                        topic=row.get("topic", "overview"),
                        instruction=row["instruction"],
                        response=row["response"],
                    )
                    for row in by_topic.get(concept["category"], [])[:2]
                ]

            related = [
                Concept(
                    uuid=other["id"],
                    title=other["title"],
                    category=other["category"],
                    summary=other["summary"],
                    detail=other["detail"],
                )
                for other in concepts
                if other["id"] in related_ids
            ]

            await gom.save(
                ConceptBrief(
                    concept=Concept(
                        uuid=concept["id"],
                        title=concept["title"],
                        category=concept["category"],
                        summary=concept["summary"],
                        detail=concept["detail"],
                    ),
                    related=related,
                    examples=examples,
                )
            )

        print(f"Seeded {len(concepts)} concepts into {graph_path}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Seed a SQLite Drivine investigation graph.")
    parser.add_argument("--graph", type=str, default=str(DEFAULT_GRAPH_DB))
    parser.add_argument("--concepts", type=str, default=str(CONCEPTS_PATH))
    parser.add_argument("--instruct", type=str, default=str(INSTRUCT_PATH))
    args = parser.parse_args(argv)
    asyncio.run(_seed(args.graph, args.concepts, args.instruct))


if __name__ == "__main__":
    main()
