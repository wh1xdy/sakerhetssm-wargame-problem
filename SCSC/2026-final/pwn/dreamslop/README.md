# DreamSlop

OpenChallSpec layout for [challtools](https://github.com/mateuszdrwal/challtools):

- `challenge.yml` — challenge metadata and service definition
- `interpreter/` — **handout** source (also listed in `downloadable_files`)
- `container/` — Docker image for the remote service (sources staged here by the build script)
- `scripts/build-challenge.sh` — copies `interpreter/` into `container/` and writes `container/flag.txt` from the build flag
- `solve/` — reference solution (organizers)

## Organizer workflow

```bash
chmod +x scripts/build-challenge.sh
pip install challtools   # or pipx
challtools validate
challtools build
challtools start
```

## Local dev (no Docker)

```bash
make -C interpreter test
```

## Local solve

```bash
pip install pwntools
make -C interpreter
python3 solve/solve.py
```
