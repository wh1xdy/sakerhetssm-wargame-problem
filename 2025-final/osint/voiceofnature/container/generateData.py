import random
import os
import math
from datetime import datetime

DB_SIZE = 50_000

with open(os.path.join(os.path.dirname(__file__), 'killar.csv')) as boys:
    firstNamesMDict = {}
    for nameStats in boys.read().split('\n'):
        if not nameStats: continue
        name, year, gender, num, order = nameStats.split(',')
        if name not in firstNamesMDict: firstNamesMDict[name] = 0
        firstNamesMDict[name] += int(num)
    numOccurrencesTotal = sum(firstNamesMDict.values())
    firstNamesM = []
    for name, occurrences in reversed(sorted(firstNamesMDict.items(), key=lambda item: item[1])):
        # print(name, occurrences, numOccurrencesTotal)
        firstNamesM += [name] * math.ceil(DB_SIZE * 1 / 2 * occurrences / numOccurrencesTotal)
with open(os.path.join(os.path.dirname(__file__), 'tjejer.csv')) as girls:
    firstNamesFDict = {}
    for nameStats in girls.read().split('\n'):
        if not nameStats: continue
        name, year, gender, num, order = nameStats.split(',')
        if name not in firstNamesFDict: firstNamesFDict[name] = 0
        firstNamesFDict[name] += int(num)
    numOccurrencesTotal = sum(firstNamesFDict.values())
    firstNamesF = []
    for name, occurrences in reversed(sorted(firstNamesFDict.items(), key=lambda item: item[1])):
        # print(name, occurrences, numOccurrencesTotal)
        firstNamesF += [name] * math.ceil(DB_SIZE * 1 / 2 * occurrences / numOccurrencesTotal)

# lastNames = ['Svensson', 'Johansson', 'Karlsson', 'Nilsson', 'Lindgren', 'Andersson']
with open(os.path.join(os.path.dirname(__file__), 'efternamn.csv')) as lastnames:
    lastNamesDict = {}
    for nameStats in lastnames.read().split('\n'):
        if not nameStats: continue
        name, num = nameStats.split(',')
        if name not in lastNamesDict: lastNamesDict[name] = 0
        lastNamesDict[name] += int(num)
    numOccurrencesTotal = sum(lastNamesDict.values())
    lastNames = []
    for name, occurrences in reversed(sorted(lastNamesDict.items(), key=lambda item: item[1])):
        # print(name, occurrences, numOccurrencesTotal)
        lastNames += [name] * math.ceil(DB_SIZE * 1 / 2 * occurrences / numOccurrencesTotal)

# print(firstNamesM[:100], firstNamesF[:100], lastNames[:100])

interests = [
    'reading', 'traveling', 'cooking', 'photography', 'hiking', 'painting',
    'music', 'sports', 'writing', 'gardening', 'gaming', 'dancing', 'fishing',
    'knitting', 'coding', 'gymnastics', 'running', 'cycling', 'swimming',
    'crafting', 'baking', 'drawing', 'watching movies', 'collecting', 'volunteering',
    'hunting', 'camping', 'surfing', 'skiing', 'snowboarding', 'scuba diving',
    'rock climbing', 'martial arts', 'history', 'science', 'technology', 'astronomy',
    'psychology', 'philosophy', 'politics', 'economics', 'environmentalism',
    'fashion', 'makeup', 'fitness', 'nutrition', 'home improvement', 'interior design',
    'animal care', 'pet training', 'language learning', 'public speaking', 'debating',
    'theater', 'comedy', 'magic', 'puzzles', 'board games', 'card games', 'video editing',
    'music production', 'blogging', 'podcasting', 'social media', 'entrepreneurship',
    'investing', 'real estate', 'cryptocurrency', 'self-improvement', 'mindfulness',
    'meditation', 'spirituality', 'astrology', 'mythology', 'cultural studies',
    'literature', 'poetry', 'graphic design', 'web development', 'app development',
    'data analysis', 'machine learning', 'artificial intelligence', 'robotics',
    'virtual reality', 'augmented reality', '3D printing', 'electronics', 'woodworking',
    'metalworking', 'leatherworking', 'upcycling', 'sustainability', 'minimalism',
    'travel photography', 'wildlife photography', 'street photography', 'mentoring',
    'portrait photography', 'food photography', 'event planning', 'party planning',
    'wedding planning', 'event hosting', 'networking', 'coaching', 'team sports',
    'individual sports', 'extreme sports', 'water sports', 'winter sports'
]

streets = [
    'Storgatan', 'Lilla Vägen', 'Kungsleden', 'Björkgatan', 'Ängsgatan',
    'Huvudgatan', 'Skolgatan', 'Torggatan', 'Södra Vägen', 'Norra Gatan',
    'Östra Långgatan', 'Västra Allén', 'Rådgatan', 'Fågelvägen', 'Blomsterstigen',
    'Hälsovägen', 'Sjövägen', 'Bergsgatan', 'Granvägen', 'Tallgatan', 'Lindgatan',
    'Rosenlundsgatan', 'Kyrkogatan', 'Vintergatan', 'Sommargatan', 'Höstgatan',
    'Vårgatan', 'Fyrvägen', 'Häggvägen', 'Kastanjegatan', 'Aspgatan', 'Koppargatan',
    'Mästarvägen', 'Hantverksgatan', 'Industrigatan', 'Verkstadsgatan', 'Skogsvägen',
    'Havsgatan', 'Fjordgatan', 'Älvvägen', 'Bäckgatan', 'Källgatan', 'Vallgatan',
    'Bergvägen', 'Rådmansgatan', 'Smedjegatan', 'Köpmangatan', 'Fiskargatan',
    'Hamngatan', 'Väggagatan', 'Kyrkvägen', 'Röda Sten', 'Sundsgatan', 'Lövgatan',
    'Vitsippan', 'Krokusgatan', 'Sparvgatan', 'Falkgatan', 'Hönsgatan', 'Kattgatan',
    'Hundgatan', 'Fjärilsgatan', 'Björkvägen', 'Rönngatan', 'Plommonvägen',
    'Äppelvägen', 'Körsbärsgatan', 'Syrengatan', 'Rosengatan', 'Tulpanvägen',
    'Liljegatan', 'Magnoliagatan', 'Klematisgatan', 'Järnvägsgatan', 'Bussgatan',
    'Cykelvägen', 'Skidvägen', 'Golfvägen', 'Tennisgatan', 'Badgatan', 'Fritidsvägen',
    'Kulturvägen', 'Skapargatan', 'Drömvägen', 'Visiongatan', 'Framtidsgatan',
    'Hoppgatan', 'Lyckogatan', 'Samarbetsgatan', 'Vänskapsgatan', 'Gemenskapsgatan',
    'Kreativitetsgatan', 'Inspirationgatan', 'Motivationsgatan', 'Tacksamhetgatan'
]

cities = [
    'Stockholm', 'Göteborg', 'Malmö', 'Uppsala', 'Linköping'
]

personalNumbersTaken = set()

def generate_personalnumber(male=True):
    year = random.randint(1900, 2009)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    separator = '-' if (datetime.now().year - year) < 100 else '+'
    serial = random.randint(0, 99)
    genderNumber = random.randint(0, 4) * 2 + (1 if male else 0)
    validation = random.randint(0, 9)
    year %= 100
    personalNumber = f'{year:02}{month:02}{day:02}{separator}{serial:02}{genderNumber}{validation}'

    if personalNumber in personalNumbersTaken:
        print(f'{personalNumber = } is already taken! Generating new...')
        return generate_personalnumber(male)

    personalNumbersTaken.add(personalNumber)
    return personalNumber

def generate_address():
    street_number = random.randint(1, 100)
    postalCode = f'{random.randint(10000, 99999)}'
    return {
        'street': f'{random.choice(streets)} {street_number}',
        'postalCode': postalCode,
        'city': random.choice(cities)
    }

def generateData():
    people = []
    for _ in range(DB_SIZE):
        male = bool(random.randint(0,1))
        firstnameList = firstNamesM if male else firstNamesF
        name = f'{random.choice(firstnameList)} {random.choice(lastNames)}'
        personsInterests = []
        localInterests = interests.copy()
        for _ in range(random.randint(0, 10)):
            interestIndex = random.randint(0, len(localInterests) - 1)
            personsInterests.append(localInterests.pop(interestIndex))

        person = {
            'name': name,
            'personalnumber': generate_personalnumber(male),
            'gender': 'male' if male else 'female',
            'interests': personsInterests,
            'address': generate_address()
        }
        people.append(person)

    print('Done adding random people')
    # import json
    # json_data = json.dumps(people, indent=4, ensure_ascii=False)
    # print(json_data)

    return people
