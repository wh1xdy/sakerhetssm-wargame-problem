# Build main.exe with dune.
FROM debian:bookworm-slim AS build

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  dune \
  menhir \
  ocaml-nox \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY ast.ml dag.ml lexer.mll parser.mly regalloc.ml main.ml dune dune-project ./
RUN dune build ./main.exe

# Prepare nsjail chroot.
FROM debian:bookworm-slim AS chroot

RUN groupadd -g 1337 ctf && useradd -r -u 1337 -g ctf ctf
RUN mkdir -p /home/ctf/program

COPY --from=build /src/_build/default/main.exe /home/ctf/main.exe
COPY program/canonical.ssa /home/ctf/program/canonical.ssa
RUN chown -R ctf:ctf /home/ctf \
  && chmod 0555 /home/ctf/main.exe \
  && chmod 0444 /home/ctf/program/canonical.ssa

# Now setting up the actual container
FROM ghcr.io/google/nsjail/nsjail:latest

COPY --from=chroot / /chroot
ENV FLAG="SSM{pl3453_d0_y0ur_4n4ly515!!!_s0b}"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  netcat-traditional \
  && rm -rf /var/lib/apt/lists/*

ENTRYPOINT nsjail --port 1337 --chroot /chroot/ --user 1337 --group 1337 --cwd /home/ctf/ --keep_env --tmpfsmount /tmp --bindmount_ro /etc/resolv.conf:/etc/resolv.conf /home/ctf/main.exe

HEALTHCHECK --start-period=20s --start-interval=1s CMD sh -c '(wc -c < /chroot/home/ctf/program/canonical.ssa; cat /chroot/home/ctf/program/canonical.ssa) | nc -w 2 127.0.0.1 1337 | grep -q "hash_ok=true"'
