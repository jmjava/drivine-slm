Read `label` and `prop` from `spec.json` and write the Cypher index statement to `answer.txt`.

```answer.txt
CREATE INDEX person_email IF NOT EXISTS FOR (p:Person) ON (p.email)
```
