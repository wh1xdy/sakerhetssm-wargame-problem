import os
import math
import random

flag = 'SSM{SEMAPHOREWARDTHINKING}'

flag = flag.upper().replace('{', '}').replace('}', ' BRACKET ').strip()

random.seed(flag)

semaphores = {
    'A': '07:30',
    'B': '09:30',
    'C': '11:30',
    'D': '12:30',
    'E': '06:08',
    'F': '06:15',
    'G': '06:22',
    'H': '09:38',
    'I': '07:52',
    'J': '12:15',
    'K': '07:00',
    'L': '07:08',
    'M': '07:15',
    'N': '07:22',
    'O': '09:52',
    'P': '09:00',
    'Q': '09:08',
    'R': '09:15',
    'S': '09:22',
    'T': '10:00',
    'U': '10:08',
    'V': '12:22',
    'W': '01:15',
    'X': '01:22',
    'Y': '10:15',
    'Z': '04:15',
    ' ': '06:30',
}

clocks = [semaphores[c] for c in flag]

# print(len(clocks), *clocks, sep='\n')

with open(os.path.join(os.path.dirname(__file__), 'flaggy-flag.svg'), 'w') as svg_file:

    width  = math.ceil((len(clocks) + 1 + 4) / 4)

    boat_scale = round((width - 2) * 100 * 0.8) / 100
    boat_offset_x = round(100 + 15 * boat_scale)
    boat_offset_y = round(100 + 20 * boat_scale)

    # print(f'{width = } {boat_scale = }')

    svg_file.write(f'''<svg viewBox="0 0 {width * 100} {width * 100}" style="background-color: navy" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <style>
        #boat path {{
            animation: ghi 4s infinite ease-in-out -3s;
            fill: none;
            stroke: white;
            stroke-linejoin: round;
        }}
        #boat {{
            animation: jkl 4s infinite ease-in-out -2s;
            transform: translate({boat_offset_x}px, {boat_offset_y}px) scale({boat_scale});
        }}

        @keyframes ghi {{
            from, to {{
                transform: translate(45px, 65px) rotate(-10deg) translate(-45px, -65px);
            }}
            50% {{
                transform: translate(45px, 65px) rotate(10deg) translate(-45px, -65px);
            }}
        }}

        @keyframes jkl {{
            from, to {{
                transform: translate({boat_offset_x}px, {round(boat_offset_y - 10 * boat_scale)}px) scale({boat_scale});
            }}
            50% {{
                transform: translate({boat_offset_x}px, {round(boat_offset_y + 10 * boat_scale)}px) scale({boat_scale});
            }}
        }}

        #clock {{
            transform: translate(calc(292800px * sqrt(var(--a) + 395856) / 2928), calc(27200px * sqrt(var(--c) - 2376236) / 272));
        }}
        #abc {{
            transform: translate(50px, 50px) rotate(calc(sqrt(var(--d) + 282) / 864 * 25920deg)) translate(-50px, -50px);
            animation: mno 1.5s;
        }}
        #def {{
            transform: translate(50px, 50px) rotate(calc(sqrt(var(--b) - 19234) / 160320 * 961920deg)) translate(-50px, -50px);
            animation: mno 1.5s;
        }}
        @keyframes mno {{
            from {{
                transform: translate(50px, 50px) rotate(0deg) translate(-50px, -50px);
            }}
        }}
    </style>

    <defs>
        <line id="tick" x1="50" x2="50" y1="4" y2="10" stroke="black" stroke-width="0.5" />

        <g id="clock">
            <circle cx="50" cy="50" r="50" fill="black" />
            <circle cx="50" cy="50" r="48" fill="white" />

            <use xlink:href="#tick" transform="rotate(  0 50 50)" />
            <use xlink:href="#tick" transform="rotate( 30 50 50)" />
            <use xlink:href="#tick" transform="rotate( 60 50 50)" />
            <use xlink:href="#tick" transform="rotate( 90 50 50)" />
            <use xlink:href="#tick" transform="rotate(120 50 50)" />
            <use xlink:href="#tick" transform="rotate(150 50 50)" />
            <use xlink:href="#tick" transform="rotate(180 50 50)" />
            <use xlink:href="#tick" transform="rotate(210 50 50)" />
            <use xlink:href="#tick" transform="rotate(240 50 50)" />
            <use xlink:href="#tick" transform="rotate(270 50 50)" />
            <use xlink:href="#tick" transform="rotate(300 50 50)" />
            <use xlink:href="#tick" transform="rotate(330 50 50)" />

            <line id="abc" x1="50" x2="50" y1="50" y2="25" stroke="black" stroke-width="1.5" />
            <line id="def" x1="50" x2="50" y1="50" y2="15" stroke="black" stroke-width="1" />

            <circle cx="50" cy="50" r="2" fill="black" />
            <circle cx="50" cy="50" r="1" fill="white" />
        </g>
    </defs>

''')
    for i, clock in sorted(list(enumerate(clocks)), key=lambda _: random.random()):
        h, m = map(int, clock.split(':'))

        if i < width:
            x, y = i, 0
        elif i < 2 * width - 1:
            x, y = width - 1, i - width + 1
        elif i < 3 * width - 2:
            x, y = (width - 1) * 3 - i, width - 1
        else:
            x, y = 0, (width - 1) * 4 - i

        svg_file.write(f'    <use xlink:href="#clock" style="{"; ".join(sorted([f"--d: {h**2 - 282}", f"--b: {m**2 + 19234}", f"--a: {x**2 - 395856}", f"--c: {y**2 + 2376236}"], key=lambda _: random.random()))}" />\n')

    svg_file.write('''
    <g id="boat">
        <path d="M 50,22 V 52 L 0,51 5,75 h 70 c 0,0 24,-31 15,-33 -3,-1 -6,0 -10,3 V 14 l 6,-2 -2,-6 -26,7 -2,-7 -6,2 2,7 -8,2 2,6 z M 72,47 58,52 V 28 c 1,-9 12,-10 14,-3 z" />
    </g>
</svg>
''')
