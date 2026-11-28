Read `label` from `query.json` and write the embedding filter query to `answer.txt`.

```answer.txt
MATCH (c:Chunk)
WHERE c.embedding IS NOT NULL
RETURN c
```
