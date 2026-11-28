Read `emails.json` and write a read-only Cypher query that returns each person name and optional email address to `answer.txt`.

```answer.txt
MATCH (p:Person)
OPTIONAL MATCH (p)-[:HAS_EMAIL]->(e)
RETURN p.name, e.address
```
