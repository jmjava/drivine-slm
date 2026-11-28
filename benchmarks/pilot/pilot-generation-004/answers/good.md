Match the Person from `label.json`, remove the label, and write the Cypher to `answer.txt`.

```answer.txt
MATCH (p:Person {name: 'Ada'})
REMOVE p:Temp
RETURN p
```
