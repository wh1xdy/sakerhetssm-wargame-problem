# gone-but-not-forgotten

July 2023, what a time to be alive! My friends had just let me borrow their
128-bit computer and I was testing out OpenFHE for the first time. Isn't it
amazing?! A brand new way to do encryption. It was a bit noisy of course,
both the encryption and the computer humming away. I got so distracted that
I forgot my key... Luckily I did save a few polynomials in `poly.txt`. Could
you help me recover the key? I'll give you a flag!

My memory isn't the best, but I do remember a few things...
 - I was using 128-bits of classic security
 - I was using the `FIXEDAUTO` scaling technique with mod size of 105 bits. The first mod size was 78 bits.
 - Their computer couldn't do any multiplications, so I had to resort to addition.
 - The execution mode was `EXEC\_EVALUATE` with desired precision 25, and I only allowed one adversarial query.

## Verify the key

Connect like so:

```
nc ... ...
```

Send one coefficient per line in base 10

