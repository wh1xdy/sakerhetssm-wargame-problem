#! /bin/bash

PASS="92fe5438b7a109de83cc01f5563d2bb9ea60128f84c73d2e5a8418cbf6712ae4"

zip -0 -Z store --encrypt out.zip flag.jpeg -P $PASS
