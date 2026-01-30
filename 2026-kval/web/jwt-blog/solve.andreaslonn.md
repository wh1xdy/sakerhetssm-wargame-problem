# Solve

The token is blacklisted, so we can't use that exact one. However, base64 allows for padding and sometimes also changing the last characters without altering the content.

The JWT that we are given is:
```
eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJIUzI1NiJ9.eyJ1c2VybmFtZSI6ICJhZG1pbiJ9.do4Q8dUylbpDQ4hpD9RrjQWv-HetNeC1et2XFfoc4fc
```

Padding added to the end is removed (try appending `==`), but characters that decode to the same message works:

```
eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJIUzI1NiJ9.eyJ1c2VybmFtZSI6ICJhZG1pbiJ9.do4Q8dUylbpDQ4hpD9RrjQWv-HetNeC1et2XFfoc4fd
```

The `c` at the end is changed to a `d`, which decodes to the same signature, but is not the same when the strings are compared.
