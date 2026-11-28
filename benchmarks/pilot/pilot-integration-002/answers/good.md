Read `label` and `prop` from `spec.json` and write the uniqueness constraint to `answer.txt`.

```answer.txt
CREATE CONSTRAINT person_email IF NOT EXISTS FOR (p:Person) REQUIRE p.email IS UNIQUE
```
