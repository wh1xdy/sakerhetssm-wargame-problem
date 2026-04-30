FROM ubuntu@sha256:ed1544e454989078f5dec1bfdabd8c5cc9c48e0705d07b678ab6ae3fb61952d2 AS chroot
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
  && rm -rf /var/lib/apt/lists/*
RUN groupadd -g 31338 ctf && useradd -r -u 31338 -g ctf ctf
RUN mkdir -p /home/ctf/
COPY main /home/ctf/
COPY flag.txt /home/ctf/
COPY libc.so.6 /home/ctf/
COPY libstdc++.so.6 /home/ctf/
COPY libm.so.6 /home/ctf/
COPY libgcc_s.so.1 /home/ctf/
COPY ld-2.40.so /home/ctf/
RUN chmod +x /home/ctf/main /home/ctf/ld-2.40.so

FROM ubuntu@sha256:ed1544e454989078f5dec1bfdabd8c5cc9c48e0705d07b678ab6ae3fb61952d2
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends socat ca-certificates \
  && rm -rf /var/lib/apt/lists/*
COPY --from=chroot / /chroot
RUN mkdir -p /chroot/etc && cp -f /etc/resolv.conf /chroot/etc/resolv.conf || true

# Write a wrapper script so socat EXEC gets a single argument
RUN printf '#!/bin/sh\nexec chroot --userspec=31338:31338 /chroot /bin/sh -c "cd /home/ctf && ./ld-2.40.so ./main"\n' \
    > /run_ctf.sh && chmod +x /run_ctf.sh

EXPOSE 31338
ENTRYPOINT ["socat", "-T60", "TCP-LISTEN:31338,reuseaddr,fork", "EXEC:/run_ctf.sh,stderr"]
