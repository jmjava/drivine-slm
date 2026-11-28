Match the Person from `status.json`, set status, and write the Cypher to `answer.txt`.

```answer.txt
MATCH (p:Person {name: 'Ada'})
SET p.status = 'active'
RETURN p
```
