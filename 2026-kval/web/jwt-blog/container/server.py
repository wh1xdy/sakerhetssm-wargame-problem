import flask
from flask import Flask, abort, render_template, make_response
import werkzeug.exceptions

import base64
import json
import hmac
import hashlib
from datetime import datetime

app = Flask(__name__)

flag = 'SSM{ba$e64_sh3n@n1gan$}'
secret = flag.encode()

def jwt_sign(data):
    if not isinstance(data, bytes):
        if not isinstance(data, str): data = json.dumps(data)
        data = data.encode()

    header = base64.urlsafe_b64encode(json.dumps({'typ': 'JWT', 'alg': 'HS256'}).encode()).strip(b'=')
    body = base64.urlsafe_b64encode(data).strip(b'=')
    signature = base64.urlsafe_b64encode(hmac.digest(secret, header + b'.' + body, hashlib.sha256)).strip(b'=')
    return f'{header.decode()}.{body.decode()}.{signature.decode()}'

def jwt_validate(token: str):
    try:
        header, _, signature = map(lambda s: base64.urlsafe_b64decode(s + '=='), token.split('.'))
        header = json.loads(header)

        assert header['typ'] == 'JWT'
        assert header['alg'] == 'HS256'

        string_to_compare = '.'.join(token.split('.')[:2]).encode()

        digest = hmac.digest(secret, string_to_compare, digest=hashlib.sha256)

        matches = hmac.compare_digest(digest, signature)
        return matches
    except:
        return False

admin_token = jwt_sign({'username': 'admin'})

posts = [
    {
        'author': 'admin',
        'title': 'Welcome to my blog',
        'summary': 'I have just created a blog',
        'content': \
     '''<p>
            This is my new beautiful blog! I have made it myself, in Flask!
        </p>
        <p>
            I have not yet figured out how to make a login system, but I have heard a lot of interesting things about JSON Web Tokens.
        </p>''',
    },
    {
        'author': 'admin',
        'title': 'JSON Web Tokens implemented',
        'summary': 'I have now successfully implemented JSON Web Tokens on this blog',
        'content': \
     '''<p>
            I could not find any simple and easy to use resources for it, so I created it myself.
        </p>
        <p>
            I have not yet figured out how to make a login system, but I have heard a lot of interesting things about JSON Web Tokens.
        </p>
        <div style="overflow: auto;padding: 1em;border-radius: 0.5em;color: #cccccc;background-color: #1f1f1f;font-family: 'Roboto Mono', Consolas, 'Cascadia Code', 'Courier New', monospace;font-weight: normal;font-size: 14px;line-height: 19px;white-space: pre;"><div><span style="color: #569cd6;">def</span><span style="color: #cccccc;"> </span><span style="color: #dcdcaa;">jwt_sign</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">data</span><span style="color: #cccccc;">):</span></div><div><span style="color: #cccccc;">    </span><span style="color: #c586c0;">if</span><span style="color: #cccccc;"> </span><span style="color: #569cd6;">not</span><span style="color: #cccccc;"> </span><span style="color: #dcdcaa;">isinstance</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">data</span><span style="color: #cccccc;">, </span><span style="color: #4ec9b0;">bytes</span><span style="color: #cccccc;">):</span></div><div><span style="color: #cccccc;">        </span><span style="color: #c586c0;">if</span><span style="color: #cccccc;"> </span><span style="color: #569cd6;">not</span><span style="color: #cccccc;"> </span><span style="color: #dcdcaa;">isinstance</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">data</span><span style="color: #cccccc;">, </span><span style="color: #4ec9b0;">str</span><span style="color: #cccccc;">): </span><span style="color: #9cdcfe;">data</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #4ec9b0;">json</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">dumps</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">data</span><span style="color: #cccccc;">)</span></div><div><span style="color: #cccccc;">        </span><span style="color: #9cdcfe;">data</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #9cdcfe;">data</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">encode</span><span style="color: #cccccc;">()</span></div><br><div><span style="color: #cccccc;">    </span><span style="color: #9cdcfe;">header</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #4ec9b0;">base64</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">urlsafe_b64encode</span><span style="color: #cccccc;">(</span><span style="color: #4ec9b0;">json</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">dumps</span><span style="color: #cccccc;">({</span><span style="color: #ce9178;">'typ'</span><span style="color: #cccccc;">: </span><span style="color: #ce9178;">'JWT'</span><span style="color: #cccccc;">, </span><span style="color: #ce9178;">'alg'</span><span style="color: #cccccc;">: </span><span style="color: #ce9178;">'HS256'</span><span style="color: #cccccc;">}).</span><span style="color: #dcdcaa;">encode</span><span style="color: #cccccc;">()).</span><span style="color: #dcdcaa;">strip</span><span style="color: #cccccc;">(</span><span style="color: #569cd6;">b</span><span style="color: #ce9178;">'='</span><span style="color: #cccccc;">)</span></div><div><span style="color: #cccccc;">    </span><span style="color: #9cdcfe;">body</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #4ec9b0;">base64</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">urlsafe_b64encode</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">data</span><span style="color: #cccccc;">).</span><span style="color: #dcdcaa;">strip</span><span style="color: #cccccc;">(</span><span style="color: #569cd6;">b</span><span style="color: #ce9178;">'='</span><span style="color: #cccccc;">)</span></div><div><span style="color: #cccccc;">    </span><span style="color: #9cdcfe;">signature</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #4ec9b0;">base64</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">urlsafe_b64encode</span><span style="color: #cccccc;">(</span><span style="color: #4ec9b0;">hmac</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">digest</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">secret</span><span style="color: #cccccc;">, </span><span style="color: #9cdcfe;">header</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">+</span><span style="color: #cccccc;"> </span><span style="color: #569cd6;">b</span><span style="color: #ce9178;">'.'</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">+</span><span style="color: #cccccc;"> </span><span style="color: #9cdcfe;">body</span><span style="color: #cccccc;">, </span><span style="color: #4ec9b0;">hashlib</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">sha256</span><span style="color: #cccccc;">)).</span><span style="color: #dcdcaa;">strip</span><span style="color: #cccccc;">(</span><span style="color: #569cd6;">b</span><span style="color: #ce9178;">'='</span><span style="color: #cccccc;padding-right: 1em;">)</span></div><div><span style="color: #cccccc;">    </span><span style="color: #c586c0;">return</span><span style="color: #cccccc;"> </span><span style="color: #569cd6;">f</span><span style="color: #ce9178;">'</span><span style="color: #569cd6;">{</span><span style="color: #9cdcfe;">header</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">decode</span><span style="color: #cccccc;">()</span><span style="color: #569cd6;">}</span><span style="color: #ce9178;">.</span><span style="color: #569cd6;">{</span><span style="color: #9cdcfe;">body</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">decode</span><span style="color: #cccccc;">()</span><span style="color: #569cd6;">}</span><span style="color: #ce9178;">.</span><span style="color: #569cd6;">{</span><span style="color: #9cdcfe;">signature</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">decode</span><span style="color: #cccccc;">()</span><span style="color: #569cd6;">}</span><span style="color: #ce9178;">'</span></div><br><div><span style="color: #569cd6;">def</span><span style="color: #cccccc;"> </span><span style="color: #dcdcaa;">jwt_validate</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">token</span><span style="color: #cccccc;">: </span><span style="color: #4ec9b0;">str</span><span style="color: #cccccc;">):</span></div><div><span style="color: #cccccc;">    </span><span style="color: #c586c0;">try</span><span style="color: #cccccc;">:</span></div><div><span style="color: #cccccc;">        </span><span style="color: #9cdcfe;">header</span><span style="color: #cccccc;">, </span><span style="color: #9cdcfe;">_</span><span style="color: #cccccc;">, </span><span style="color: #9cdcfe;">signature</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #4ec9b0;">map</span><span style="color: #cccccc;">(</span><span style="color: #569cd6;">lambda</span><span style="color: #cccccc;"> </span><span style="color: #9cdcfe;">s</span><span style="color: #cccccc;">: </span><span style="color: #4ec9b0;">base64</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">urlsafe_b64decode</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">s</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">+</span><span style="color: #cccccc;"> </span><span style="color: #ce9178;">'=='</span><span style="color: #cccccc;">), </span><span style="color: #9cdcfe;">token</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">split</span><span style="color: #cccccc;">(</span><span style="color: #ce9178;">'.'</span><span style="color: #cccccc;">))</span></div><div><span style="color: #cccccc;">        </span><span style="color: #9cdcfe;">header</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #4ec9b0;">json</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">loads</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">header</span><span style="color: #cccccc;">)</span></div><br><div><span style="color: #cccccc;">        </span><span style="color: #c586c0;">assert</span><span style="color: #cccccc;"> </span><span style="color: #9cdcfe;">header</span><span style="color: #cccccc;">[</span><span style="color: #ce9178;">'typ'</span><span style="color: #cccccc;">] </span><span style="color: #d4d4d4;">==</span><span style="color: #cccccc;"> </span><span style="color: #ce9178;">'JWT'</span></div><div><span style="color: #cccccc;">        </span><span style="color: #c586c0;">assert</span><span style="color: #cccccc;"> </span><span style="color: #9cdcfe;">header</span><span style="color: #cccccc;">[</span><span style="color: #ce9178;">'alg'</span><span style="color: #cccccc;">] </span><span style="color: #d4d4d4;">==</span><span style="color: #cccccc;"> </span><span style="color: #ce9178;">'HS256'</span></div><br><div><span style="color: #cccccc;">        </span><span style="color: #9cdcfe;">string_to_compare</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #ce9178;">'.'</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">join</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">token</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">split</span><span style="color: #cccccc;">(</span><span style="color: #ce9178;">'.'</span><span style="color: #cccccc;">)[:</span><span style="color: #b5cea8;">2</span><span style="color: #cccccc;">]).</span><span style="color: #dcdcaa;">encode</span><span style="color: #cccccc;">()</span></div><br><div><span style="color: #cccccc;">        </span><span style="color: #9cdcfe;">digest</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #4ec9b0;">hmac</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">digest</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">secret</span><span style="color: #cccccc;">, </span><span style="color: #9cdcfe;">string_to_compare</span><span style="color: #cccccc;">, </span><span style="color: #9cdcfe;">digest</span><span style="color: #d4d4d4;">=</span><span style="color: #4ec9b0;">hashlib</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">sha256</span><span style="color: #cccccc;">)</span></div><br><div><span style="color: #cccccc;">        </span><span style="color: #9cdcfe;">matches</span><span style="color: #cccccc;"> </span><span style="color: #d4d4d4;">=</span><span style="color: #cccccc;"> </span><span style="color: #4ec9b0;">hmac</span><span style="color: #cccccc;">.</span><span style="color: #dcdcaa;">compare_digest</span><span style="color: #cccccc;">(</span><span style="color: #9cdcfe;">digest</span><span style="color: #cccccc;">, </span><span style="color: #9cdcfe;">signature</span><span style="color: #cccccc;">)</span></div><div><span style="color: #cccccc;">        </span><span style="color: #c586c0;">return</span><span style="color: #cccccc;"> </span><span style="color: #9cdcfe;">matches</span></div><div><span style="color: #cccccc;">    </span><span style="color: #c586c0;">except</span><span style="color: #cccccc;">:</span></div><div><span style="color: #cccccc;">        </span><span style="color: #c586c0;">return</span><span style="color: #cccccc;"> </span><span style="color: #569cd6;">False</span></div></div>
        <p>
            I'm actually quite proud of it! You can then take a token, like this one:
        </p>
        <div style="overflow: auto;padding: 1em;border-radius: 0.5em;color: #cccccc;background-color: #1f1f1f;font-family: 'Roboto Mono', Consolas, 'Cascadia Code', 'Courier New', monospace;font-weight: normal;font-size: 14px;line-height: 19px;white-space: pre;"><div><span style="color: #ce9178;padding-right: 1em;">{{ TOKEN }}</span></div></div>
        <p>
            And put it as a "token" cookie. Of course, I have added some code to make sure that this specific JWT is not able to be used.
        </p>
        '''.replace('{{ TOKEN }}', admin_token),
    },
    {
        'author': 'admin',
        'title': 'Admin page implemented',
        'summary': 'I have now successfully implemented an admin page on this blog',
        'content': \
     '''<p>
            Now that JWTs are working, I have been able to implement an admin page!
        </p>
        <p>
            <a href="/admin">Here is a link to the admin page.</a>
        </p>
        <p>
            I have also added a fun error page for when you are not logged in!
        </p>
        ''',
    },
]

@app.route('/')
def index():
    return render_template('index.html', posts=posts, year=datetime.now().year)

@app.route('/post')
def post():
    postId = flask.request.args.get('id')
    if not postId:
        return flask.abort(400, 'No post ID provided')
    try:
        postId = int(postId)
    except ValueError:
        return abort(400, 'Invalid post ID')
    if postId < 0 or postId >= len(posts):
        return abort(404, 'Post ID not found')
    return render_template('post.html', post=posts[postId], year=datetime.now().year)

@app.route('/admin')
def admin():
    try:
        token = flask.request.cookies.get('token', '').strip('=')

        if not token:
            return abort(403, 'No key no admin')

        if not jwt_validate(token):
            return abort(403, 'Invalid token')

        if token == admin_token:
            return abort(403, 'Blacklisted token')

        _, data, _ = token.split('.')

        data = json.loads(base64.urlsafe_b64decode(data))

        if data['username'] != 'admin':
            return abort(403)

        return flag

    except SyntaxError:
        return abort(403, "You can't do that")

@app.errorhandler(werkzeug.exceptions.Forbidden)
def handle_forbidden(e: werkzeug.exceptions.Forbidden):
    r = make_response(render_template('403.html', desc=e.description))
    r.status_code = 403
    return r

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
