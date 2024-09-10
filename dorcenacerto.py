"""Example client."""
import asyncio
import getpass
import json
import os, time

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame
import websockets

import copy
from consts import Direction

from agent_dor_cena_certo import agent_AI, agent_random_move

pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)


async def agent_loop(server_address="localhost:8000", agent_name="João"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        # Next 3 lines are not needed for AI agent
        #SCREEN = pygame.display.set_mode((299, 123))
        #SPRITES = pygame.image.load("data/pad.png").convert_alpha()
        #SCREEN.blit(SPRITES, (0, 0))

        key=""
        last_key=""
        digdug_dir=Direction.EAST
   

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                ##################################################### o que é preciso fazer, é só daqui até lá abaixo
                #Notas: o state é o dicio que contém toda a informação que precisamos para o agente inteligente usar. O state é o que a função assíncrona next_frame(self) de game.py retorna.
                #a chave "digdug" contém um par da posição do DigDug, e a chave "enemies" contém uma lista de dicionários da informação de cada inimigo {"name": str(e), "id": str(e.id), "pos": e.pos, "dir": e.lastdir}

                if 'digdug' not in state:
                    mapa = state['map']

                    oldstate = {}
                    stones_to_remove = set()
                    stones_clear = 0
                    stochastic_charger=0
                    last_pos = [1,1]
                    trapped_frames = 0
                    zoomed_frames = 0
                    closest_enemy_name = 'Fygar'
                else:

                    start = time.time()
                    key, digdug_dir, mapa, stones_to_remove, state, dor, stones_clear, last_pos, trapped_frames, closest_enemy_name, zoomed_frames = agent_AI(state, oldstate, digdug_dir, mapa, stones_to_remove, stones_clear, last_pos, trapped_frames, closest_enemy_name, zoomed_frames)

                    oldstate = copy.deepcopy(state)
                    

                    
                    if key== "A" and last_key!= 'A':
                        stochastic_charger=0
                    stochastic_charger += 1
                    if stochastic_charger >= 16 and dor!='dor':
                        key, digdug_dir = agent_random_move(state, digdug_dir, mapa)
                        stochastic_charger=0

                    last_key = key
                    stones_clear-=1
                    #last_pos = pos
                    
                    end = time.time()
                    time_diff_ms = round((end-start)*1000, 1)
                    if time_diff_ms >= 100:
                        print('\033[91m O agente precisou de mais de 100ms para fazer as suas computações:',time_diff_ms, '\033[0m')
                    elif time_diff_ms >= 10:
                        print('\033[93m',time_diff_ms, '\033[0m')
                    

                    await websocket.send(
                            json.dumps({"cmd": "key", "key": key})
                        )  # send key command to server - you must implement this send in the AI agent
                

################################################## o que é preciso fazer, é só daqui até lá cima

            
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

            # Next line is not needed for AI agent
            #pygame.display.flip()


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", 'Dor Cena Certo')
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
