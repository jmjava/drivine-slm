Read `people.json` and write a read-only Cypher query that counts Person nodes to `answer.txt`.

```answer.txt
MATCH (p:Person)
RETURN count(p)
```
