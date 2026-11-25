from __future__ import annotations

import argparse
import json

from drivine_lab.paths import DEFAULT_JSONL, INSTRUCT_PATH


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Export instruction JSON to JSONL for trainers.")
    parser.add_argument("--input", type=str, default=str(INSTRUCT_PATH))
    parser.add_argument("--output", type=str, default=str(DEFAULT_JSONL))
    args = parser.parse_args(argv)

    rows = json.loads(open(args.input, encoding="utf-8").read())
    with open(args.output, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(
                json.dumps(
                    {
                        "instruction": row["instruction"],
                        "response": row["response"],
                        "topic": row.get("topic"),
                        "id": row.get("id"),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
