import asyncio
from msvcrt import getch, kbhit


def safe_getch():
    c = getch()
    if c == b'\x03':
        raise KeyboardInterrupt
    return c


def modal_arrow_input():
    while True:
        c = safe_getch()
        if c == b'\xe0' or c == b'\x00':
            c = safe_getch()
            if c == b'H':
                return -1
            elif c == b'P':
                return 1
        elif c == b'\r':
            return 0


def fwrite(value):
    print(value, end="")


def input_choice(prompt, *choices):
    print(prompt)
    ptr = 0
    print('\n'.join([" " + str(x) for x in choices]))
    fwrite(f"\x9b{len(choices)}A>")
    fwrite(f"")
    while True:
        inp = modal_arrow_input()
        if inp == 0:
            fwrite(f"\x9b{len(choices) - ptr}E")
            return choices[ptr]
        elif inp == -1 and ptr > 0:
            ptr -= 1
            fwrite("\x9bD \x9bD\x9bA>")
        elif inp == 1 and ptr < len(choices) - 1:
            ptr += 1
            fwrite("\x9bD \x9bD\x9bB>")


async def input_async(prompt, include_return=True):
    print(prompt, end='')
    buf = []
    pos = 0
    while True:
        if not kbhit():
            await asyncio.sleep(0)
            continue
        c = chr(safe_getch()[0])
        if c == '\x00' or c == '\xe0':
            c = safe_getch()  # ignore next
            if c == b'K' and pos > 0:
                fwrite('\x9bD')
                pos -= 1
            if c == b'M' and pos < len(buf):
                fwrite('\x9bC')
                pos += 1
            if c == b'S' and pos < len(buf):
                del buf[pos]
                fwrite('\x9bK')
                fwrite(''.join(buf[pos:]))
                if len(buf) - pos > 0:  # Terminal replace 0 by 1
                    fwrite(f'\x9b{len(buf) - pos}D')
            continue
        elif c == '\x03':
            raise KeyboardInterrupt
        elif c == '\x08':
            if pos == 0:
                continue
            fwrite('\x9bD \x9bD')
            del buf[pos - 1]
            pos -= 1
        elif c == '\r':
            if include_return:
                print()
            break
        else:
            print(c, end='')
            buf.insert(pos, str(c[0]))
            pos += 1
    return ''.join(buf)


def load_questions():
    lst = []
    with open("questions.txt") as file:
        flag = False
        tmp = None
        lines = file.read().splitlines()
        for line in lines:
            if flag:
                lst.append((tmp, line))
            else:
                tmp = line
            flag = not flag
    return lst
