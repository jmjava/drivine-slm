Read `k` from `query.json` and write the doc_vec vector query to `answer.txt`.

```answer.txt
CALL db.index.vector.queryNodes('doc_vec', 5, $embedding)
YIELD node
RETURN node
```
