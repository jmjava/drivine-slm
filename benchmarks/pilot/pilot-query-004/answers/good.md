Read the `values` array in `nums.json` and write a read-only Cypher query that returns their sum to `answer.txt`.

```answer.txt
UNWIND [2, 4, 6] AS n
WITH n
RETURN sum(n)
```
