FROM pwn.red/jail

COPY --from=debian:trixie-slim@sha256:4bcb9db66237237d03b55b969271728dd3d955eaaa254b9db8a3db94550b1885 / /srv

RUN mkdir /srv/app
COPY life_simulator /srv/app/run

ENV JAIL_ENV_FLAG=SSM{the_lucky_shrimps_ate_all_the_crustaceans}
ENV JAIL_PORT=9301
