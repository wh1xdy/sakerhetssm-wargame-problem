# autograph

Do you like collecting celebrities' autographs? Of course you have to keep
them safe. Store them in our encrypted vault!

Not sure if a seller's autograph is authentic? We will verify it for you! Our
state-of-the-art autograph-analysis algorithm never fails to spot a flawed
signature.

## How it works

We store `IV || ENC(HMAC(autograph) || pad)`, where `ENC` and `HMAC` are using
`AES-256` and `SHA-256` respectively.

## Try it out

We are running a special promotion today! Connect like so:

```
nc ... 40011
```

Have a look at our free collection! Only privileged users can access our
premium collection.

The code is in `autograph.go`

