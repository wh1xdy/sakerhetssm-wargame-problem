import flask
from urllib import parse
import time
from collections import deque

import mrstalkersearch
from secret import flag

print('Generating database')
peopleDatabase = mrstalkersearch.generateDatabase()
print(f'Database generated {len(peopleDatabase)=}')

print('Generating flattened database')
peopleDatabaseFlat = mrstalkersearch.makeFlatDB(peopleDatabase)
print(f'Flattened database generated {len(peopleDatabaseFlat)=}')

ratelimitQueues: dict[deque] = {}

RL_TIME_SEC = 10
RL_NUM_REQ = 3

app = flask.Flask(__name__)

def ratelimit():
    ipAddr = flask.request.remote_addr

    if not ipAddr in ratelimitQueues:
        ratelimitQueues[ipAddr] = deque(maxlen=RL_NUM_REQ)

    q: deque = ratelimitQueues[ipAddr]

    if len(q) < RL_NUM_REQ or (q[0] + RL_TIME_SEC) < time.time():
        q.append(time.time())
        return True
    return False

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/search')
def search():
    if not ratelimit(): return flask.render_template('429.html'), 429

    # time.sleep(2 * random.random())
    q = flask.request.args.get('query')
    if not q: flask.abort(400, 'No search query supplied!')
    p = int(flask.request.args.get('page') or 1)

    results, numPages = mrstalkersearch.search(peopleDatabase, peopleDatabaseFlat, q, p, 20)
    # print(f'{results = }')
    return flask.render_template('search.html',
        query = q,
        results = results,
        prevPage = f'search?query={q}&page={p - 1}',
        nextPage = f'search?query={q}&page={p + 1}',
        pageNum = p,
        numPages = numPages
    )

@app.route('/person')
def person():
    if not ratelimit(): return flask.render_template('429.html'), 429
    # time.sleep(3 * random.random())
    pnr = flask.request.args.get('personalnumber')
    if not pnr: flask.abort(400, 'No personal number supplied!')
    person = mrstalkersearch.getPerson(peopleDatabase, pnr)
    if not person: flask.abort(404, 'Personal number not found')
    secretMessage = None
    if pnr == '960814-2284':
        secretMessage = flag
    return flask.render_template('person.html', pnr = pnr, person = person, flag = secretMessage)

@app.route('/aboutus')
def aboutus():
    return flask.render_template('aboutus.html')

@app.route('/remove', methods=['GET', 'POST'])
def remove():
    if flask.request.method == 'POST':
        print(flask.request.form)
        try:
            formData = flask.request.form.to_dict()
            a, b, c = map(lambda s: float(s.split('=')[1]), formData['captcha'].split(', '))
        except:
            flask.abort(400, 'Malformed request')
        if not (a.is_integer() and b.is_integer() and c.is_integer()):
            flask.abort(500, 'Invalid captcha: Not integers')
        a, b, c = int(a), int(b), int(c)
        if a**3 + b**3 + c**3 != 4:
            flask.abort(400, 'Invalid captcha: a^3 + b^3 + c^3 != 4')
        flask.abort(500, 'Unexpected error, perhaps you should get a Nobel prize for your discovery though')
    return flask.render_template('remove.html')

@app.route('/privacy')
def privacy():
    return flask.render_template('privacy.html')

app.jinja_env.filters['urlencode'] = parse.quote_plus

if __name__ == '__main__':
    app.run(debug=True, port=5000)
