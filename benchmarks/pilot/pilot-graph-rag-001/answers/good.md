Read `index` and `k` from `query.json` and write the vector query to `answer.txt`.

```answer.txt
CALL db.index.vector.queryNodes('chunk_vec', 3, $embedding)
YIELD node, score
RETURN node, score
```
