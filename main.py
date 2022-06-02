import asyncio
import utils
import random as rn
from typing import NamedTuple, Any


class Question(NamedTuple):
    question: str
    answer: Any


def questions():
    qs = utils.load_questions()
    while True:
        rn.shuffle(qs)
        for q in qs:
            yield q


async def local_main(player_count: int):
    t_timer = asyncio.create_task(asyncio.sleep(rn.randint(10, 15)), name="Countdown task")
    c_player = 0

    for question, answer in questions():
        print(question)
        while True:
            t_inp = asyncio.create_task(utils.input_async(f"{c_player + 1}: ", include_return=False), name="Async input task")
            while True:
                done, pending = await asyncio.wait({t_inp, t_timer}, timeout=0.1, return_when=asyncio.FIRST_COMPLETED)
                if t_timer in done:
                    t_inp.cancel()
                    print()
                    return c_player
                elif t_inp in done:
                    break
            resp = t_inp.result()
            utils.fwrite("\x9b999D\x9b2K")
            if answer == resp:
                utils.fwrite("\x9bA\x9b2K")
                c_player = (c_player + 1) % player_count
                break

is_local = utils.input_choice("Jak budeš hrát?", "local", "remote (nefunguje)") == "local"

if is_local:
    ply_count = int(input("Kolik hráčů: "))
    loser = asyncio.run(local_main(ply_count))
    print("Hráč č.", loser + 1, "prohrál")
else:
    print("Jsi retardovaný")
