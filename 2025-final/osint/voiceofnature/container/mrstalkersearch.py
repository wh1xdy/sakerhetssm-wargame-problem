import math
import generateData

def flatten(field):
    if isinstance(field, str):
        return field.lower()
    elif isinstance(field, list):
        return ' '.join([flatten(f) for f in field])
    elif isinstance(field, dict):
        return ' '.join([flatten(field[f]) for f in field])
    else:
        raise f'Unknown data type: {field = }'

def makeFlatDB(database: list[dict]):
    return [flatten(entry) for entry in database]

def search(database: list[dict], databaseFlat: list[str], query: str, page=1, pageSize=0):

    matchingResults = []

    for i, entry in enumerate(databaseFlat):
        for queryPart in query.split(' '):
            if not queryPart or not queryPart.lower() in entry: break
        else:
            matchingResults.append(database[i])

    pages = math.ceil(len(matchingResults) / pageSize) if pageSize > 0 else 1
    firstIndex = pageSize * (page - 1)
    try:
        result = matchingResults[firstIndex:firstIndex+pageSize] if pageSize > 0 else matchingResults
        return result, pages
    except ValueError:
        return [], 1

def getPerson(database: list[dict], personalnumber: str):
    for person in database:
        if person['personalnumber'] == personalnumber:
            return person
    return None

def generateDatabase():
    database = generateData.generateData()

    print('Database completed')

    results = search(database, makeFlatDB(database), 'Elin Andersson 96', pageSize=0)[0]
    print(f'Looking for Elin Andersson 1996: {len(results) = }')
    for result in results:
        database.remove(result)

    database.append({
        'name': 'Elin Andersson',
        'personalnumber': '960814-2284',
        'gender': 'female',
        'interests': [ 'photography', 'traveling', 'blogging', 'web development' ],
        'address': {
            'street': 'Storgatan 39',
            'postalCode': '11292',
            'city': 'Stockholm'
        }
    })

    return sorted(database, key=lambda item: item['address']['city'][0][-1])
