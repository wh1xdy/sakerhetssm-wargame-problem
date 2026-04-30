FROM ubuntu@sha256:ed1544e454989078f5dec1bfdabd8c5cc9c48e0705d07b678ab6ae3fb61952d2

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 socat ca-certificates \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 31337

# Create unprivileged user
RUN groupadd -g 31337 ctf && useradd -m -r -u 31337 -g 31337 ctf

WORKDIR /home/ctf

# Copy challenge + flag
COPY main /home/ctf/main
COPY flag.txt /home/ctf/flag.txt

# Lock down permissions:
# - /home/ctf: readable/executable only (no write)
# - main: executable but not writable
# - flag.txt: read-only
# - owned by root so the ctf user cannot chmod/chown them
RUN chown -R root:root /home/ctf \
    && chmod 0555 /home/ctf \
    && chmod 0555 /home/ctf/main \
    && chmod 0444 /home/ctf/flag.txt \
    # Ensure no accidental setuid/setgid bits on shipped files
    && find / -xdev -perm /6000 -type f -exec chmod a-s {} + || true

USER 31337:31337

# For each TCP connection: run /home/ctf/main with stdin/stdout on the socket
ENTRYPOINT ["socat", "-T", "120", "TCP-LISTEN:31337,reuseaddr,fork", "EXEC:/home/ctf/main,stderr"]
