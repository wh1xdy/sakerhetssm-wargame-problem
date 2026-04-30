## Notes

### Deployed version

The deployed version is in
[`deploy/net-powpowpow.go`](./deploy/net-powpowpow.go). If
you prefer to look at it in a "non-net" way, have a look at
[`deploy/powpowpow.go`](./deploy/powpowpow.go)

### Solution

We want to find `enc(password)` but are not allowed to enter the admin
password. However, since `g^a^b = g^b^a`, and the transformation from string
to int is using chunks of 2 bytes, we can just change the order of some of
the bytes in the admin password.

Permuting `yes it is me the super important and secure admin with full
privil[eg][es]` into `yes it is me the super important and secure admin with
full privil[es][eg]` will give us the same result.
