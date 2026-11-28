Read `name` from `spec.json` and write the existence constraint to `answer.txt`.

```answer.txt
CREATE CONSTRAINT person_stamp IF NOT EXISTS FOR (p:Person) REQUIRE p.stamp IS NOT NULL
```
