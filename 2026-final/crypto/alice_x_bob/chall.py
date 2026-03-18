import secrets
from Crypto.Util.number import *
from love_story import story_template, flag

def gen_prime(bits, smoothness=40):
    while True:
        p = 2
        while (sz := p.bit_length()) < bits:
            p *= getPrime(min(bits - sz, smoothness))

        if isPrime(p + 1):
            return p + 1

p = gen_prime(512)
g = 2

alice_secret = bytes_to_long(flag)
bob_secret = secrets.randbelow(p)

alice_public = pow(g, alice_secret, p)
bob_public = pow(g, bob_secret, p)

story = story_template.substitute(
        prime=p,
        generator=g,
        alice_pk=alice_public,
        bob_pk=bob_public
    )

print(story)
