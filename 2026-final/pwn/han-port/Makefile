CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -O2 -fno-inline -g -fno-stack-protector -no-pie -D_FORTIFY_SOURCE=0 -Icontainer/src
LDFLAGS = -lm

TARGET  = han-port
SRCS    = container/src/main.c container/src/han.c container/src/ports.c container/src/port_proc.c container/src/handler.c
OBJS    = $(SRCS:.c=.o)

# Same length as the real flag (SSM{r3act0r_l33k} = 17 chars)
PLACEHOLDER_FLAG = CTF{placeholder_}

DOCKER_IMAGE   = han-port-challenge
HANDOUT_IMAGE  = han-port-handout

.PHONY: all clean container handout

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -DFLAG='"$(PLACEHOLDER_FLAG)"' -o $@ $^ $(LDFLAGS)

container/src/%.o: container/src/%.c
	$(CC) $(CFLAGS) -DFLAG='"$(PLACEHOLDER_FLAG)"' -c -o $@ $<

# Builds the deployed container image. Pass FLAG= for the real flag.
container:
	docker build --network=host --build-arg FLAG='$(FLAG)' \
		-t $(DOCKER_IMAGE) container/

# Builds the handout: compiles with placeholder flag inside Docker (matching
# the server environment), then extracts the binary and libc for players.
handout:
	docker build --network=host --build-arg FLAG='$(PLACEHOLDER_FLAG)' \
		-t $(HANDOUT_IMAGE) container/
	docker create --name han-handout-tmp $(HANDOUT_IMAGE)
	docker cp han-handout-tmp:/chroot/home/ctf/han-port han-port
	docker cp han-handout-tmp:/chroot/lib/x86_64-linux-gnu/libc.so.6 libc.so.6
	docker rm han-handout-tmp
	sed 's/^ARG FLAG=.*/ARG FLAG/' container/Dockerfile > Dockerfile.handout
	mkdir -p handout/src
	cp han-port libc.so.6 handout.md Dockerfile.handout handout/
	cp container/src/main.c container/src/han.c container/src/han.h \
	   container/src/ports.c container/src/ports.h \
	   container/src/port_proc.c container/src/port_proc.h \
	   container/src/handler.c container/src/handler.h \
	   handout/src/
	zip -0 -r handout.zip handout/

clean:
	rm -f $(OBJS) $(TARGET) Dockerfile.handout
	rm -rf handout handout.zip container/src/*.o
