from string import ascii_lowercase
ct_alph = [l.strip() for l in open('---KVALIFICERAT_HEMLIG---.txt', 'r').readlines()[3:-3]]
pt_alph = ascii_lowercase + ' '
ct = open('Meddelande #452.txt', 'r').read().strip()
print(''.join([pt_alph[ct_alph.index(c)] for c in ct]))