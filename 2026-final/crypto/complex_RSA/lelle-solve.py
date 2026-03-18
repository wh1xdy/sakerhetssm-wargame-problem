from sage.all import *
from Crypto.Util.number import long_to_bytes

R = RealField(3334)
Z = ZZ["i"]
i = Z.gen()

#Zi2 = Z.quo(i**2 + 1)

n = 4059522918253284993687814387239029981707824515846267029031023876660011251733768277789191882826096923915420349555778548948735995255656672759032156493709485523166389039200686247504310292185538822338591684305369239073793745087531785971728440379181567847966205395805920929394968892323297835778595657917854138998 + 35343768297569037812903120448856135094494873474596365023614605663067352811153124489506331627072546401617939719631275583681981765695009674883291896858662957391228634313300567137283031780687614407767381736149469910942330185868675477426766509097356419347019419113956468535485785594136880206381335862883200480215*i
e = 65537
c = -3038950767734981138992058112711102158925439844145508011886120364966606897549619022902752205611523613847086554866245086470528950860387029283715930252259144956542179329486545275522836234727629313354294165366163896470385895072987633455665755187713326939778827905107465561666465536077096700794296163610149920021 - 132471565700527910445993204280569444237979007011750640670429577588141353551555891148897745317204667324391981029705517271572009426234733035655374845969587146235122046912096731357978123021102845943947731736701803012661702465655274812225361926468145984244144038564132467605478078237275573711918631757994149152*i
arg = R("0.97252384177105604660153119085002370813390021259362007279358516622842161237571727489296024223642835499585965081932082059916273069107684956560350637495288819710525965018511514050573234034649936547247767471165126303420409700773628822981575261767788092110003510907745737735764729819300000227191488156925796572739759783217806461156823010221735409317805729266949157429496999441270402565380453518120741445190418907404506483964712115095891458277084292397790808071645096495886687277209250684316450628596460540628226998071712277086157989100782123649580513372455764445218191222397632962063866597023473118342808981445645975839409327160807395702598729708875232436386515326847936383536038666233421614275125603168160634296550173592365940845903416673989632330493824110396789257846222648108904276715294170366583998597336114520479456509349064734284560154457554014181650653795726673322394118076203500393121943272584994360202865824867607007148828191395881195898001441123967388655451078711256904621534308578495567727291")

nnorm = sum(map(lambda x: x**2, n.coefficients()))
nnorm = ZZ(nnorm)
print(f"{nnorm = }")
for frac in continued_fraction(tan(arg)).convergents():
    b = frac.numer()
    a = frac.denom()
    if a**2 + b**2 <= 1:
        continue

    if nnorm / ZZ(a**2 + b**2) in ZZ:
        print(f"found! p.norm {a**2 + b**2}")
        pnorm = a**2 + b**2
        print(f"{(nnorm % pnorm, nnorm == pnorm) = }")
        break

qnorm = nnorm / pnorm
qnorm = ZZ(qnorm)
print(f"{(is_prime(qnorm), is_prime(pnorm)) = }")

phi = (pnorm - 1) * (qnorm - 1)
print(f"{phi = }")

class ComplexInteger:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __add__(self, other):
        return ComplexInteger(self.a + other.a, self.b + other.b)

    def __sub__(self, other):
        return ComplexInteger(self.a - other.a, self.b - other.b)

    def __mul__(self, other):
        return ComplexInteger(self.a * other.a - self.b * other.b, self.a * other.b + self.b * other.a)

    def __floordiv__(self, other):
        return self._divmod(other)[0]

    def __mod__(self, other):
        return self._divmod(other)[1]

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __str__(self):
        if self.a == self.b == 0:
            return "0"
        if self.a == 0:
            return f"{self.b}*i"
        if self.b == 0:
            return f"{self.a}"
        return f"{self.a} {'+' if self.b > 0 else '-'} {abs(self.b)}*i"

    def arg(self):
        mp.dps = 1000
        return atan(mpf(self.b) / mpf(self.a))

    def conjugate(self):
        """
        Returns the complex conjugate of this complex integer
        """
        return ComplexInteger(self.a, -self.b)

    def _divmod(self, other):
        """
        Returns the quotient and remainder from division with another complex
        integer. Remainder is always within the findamental domain of the
        lattice. (Not imporant, just means its well behaved)
        """
        assert not (other.a == 0 and other.b == 0), "Division by zero"

        denom = other.norm()
        b_conj = other.conjugate()
        num = self * b_conj  # Still a Gaussian integer

        # Divide real and imaginary parts of num by denom (an integer)
        # and round to nearest integer
        real = num.a
        imag = num.b

        def round_nearest(x, d):
            q, r = divmod(x, d)
            if 2 * r > d or (2 * r == d and q % 2 != 0):
                return q + 1
            return q

        q_real = round_nearest(real, denom)
        q_imag = round_nearest(imag, denom)

        q = ComplexInteger(q_real, q_imag)
        r = self - other * q
        return q, r

    def norm(self):
        """
        Returns the complex norm
        """
        return self.a ** 2 + self.b ** 2

    def is_prime(self):
        """
        Returns whether or not this is a gaussian prime
        """
        if self.b == 0:
            if self.a > 0 and self.a % 4 == 3 and isPrime(self.a):
                 return True
        
        if self.a == 0:
            if self.b > 0 and self.b % 4 == 3 and isPrime(self.b):
                 return True
                 
        return isPrime(self.norm())

def powmod(a, b, m):
    # Square and multiply algorithm
    result = ComplexInteger(1, 0)
    base = a % m

    while b > 0:
        if b % 2 == 1:
            result = (result * base) % m
        base = (base * base) % m
        b //= 2

    return result

#d = pow(e, -1, phi)
d = Zmod(phi)(e).inverse()
d = int(d)
print(f"{d = }")

ccoef = c.coefficients()
c = ComplexInteger(ccoef[0], ccoef[1])

ncoef = n.coefficients()
n = ComplexInteger(ncoef[0], ncoef[1])

flag = powmod(c, d, n)
#if flag.b == 0:
print(flag.a, flag.b)
m = lambda x: long_to_bytes(int(x)).decode()
print("".join(map(m, (flag.a, flag.b))))
