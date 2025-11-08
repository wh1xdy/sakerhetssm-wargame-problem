import frida

def on_message(message, data):
    print("[on_message] message:", message, "data:", data)

fd = frida.spawn('./ca_generator')
session = frida.attach(fd)

with open('hook.js', 'r') as fin:
    script_code = fin.read()

script = session.create_script(script_code)
script.on("message", on_message)
script.load()
frida.resume(fd)

input()
session.detach()
