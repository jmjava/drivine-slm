Read `index` from `query.json` and write the fulltext query to `answer.txt`.

```answer.txt
CALL db.index.fulltext.queryNodes('chunk_text', $q)
YIELD node, score
RETURN node, score
```
