from consts import Direction
import math, random

import agent_close_move_searchTree_dor_beliscão_peito_esquerdo





def agent_possible_moves_dor(digdug_pos):            #devolve dicio com todas as potenciais posições que o agente pode tomar e executar na próxima frame, ou apenas a posição consequente de um movimento
     #o digdug morre se a sua posição for igual à de um bicho (colisão).
     #quando morri no step 0 do 2º nível, tinha spawnado um Pooka em (0,1). O Digdug spawna em (1,1). As posições não eram a mesma, mas o Digdug fica com a tecla de parar '' quando a next_frame faz Update_Digdug, que por sua vez faz o movimento indicado pela tecla, e depois faz next_level se esse movimento matar o último inimigo, e mete o step a 0 e a última tecla a "", o que é irrelevante pois o movimento já foi feito e ainda estamos dentro da mesma função, e depois o Pooka mexe-se, e depois de se mexer, faz-se collision(), e se a posição de algum inimigo coincidir com o digdug, faz-se kill_digdug(), que faz self.digdug.kill(), que o faz morrer, tirando 1 vida e meter-lhe a posição no spawn (1,1). Basicamente no mesmo next_frame, o digdug clica na tecla, mata um inimigo com esse movimento, volta para (1,1), os inimigos dão spawn, e depois mexem-se, podendo mexerem-se para (1,1), e depois o next_frame termina. (O next_frame é chamado dentro de um while True no servidor, que começa por obter o info do jogo se step=0, depois envia-o e espera pelo envio, depois corre o next_frame; que em si faz um sleep assíncrono de 1/GAMESPEED, depois faz UpdateDigdug, que faz o next_level e mete a tecla a 0, e depois mexe os inimigos; e por fim envia o retorno do next_frame(), que é o state, ao client, e espera até que envie, assincronamente, podendo estar a executar código a seguir ao next_frame() antes de este acabar. Por sua vez, é enviada a tecla que o agente AI ou o utilizador selecionar do cliente, que também opera assíncronamente do servidor, e daí é independente se o algoritmo do agente AI dentro do client demora muito ou pouco a executar para o servidor e o next_frame() ser chamado igualmente e assim o jogo correr à mesma velocidade independentemente de se o agente AI é rápido ou lento a executar, se o servidor recebeu algures a tecla enquanto o ciclo While está a executar o next_frame e o update_digdug e a correr o jogo, esta é considerada quando o ciclo While executa o next_frame, caso contrário, o jogo continua a correr igual e o next_frame continua a correr igual e o updateDigdug corre igual)
     #a única maneira de o digdug não morrer mesmo é não jogar. Ou começar com o jogo parado, antes de fazer next_frame(), ou collision(), ou update_digdug(), mas sobretudo, antes de se fazer kill_digdug() ou pior ainda, digdug.kill(), ou indubitavelmente mau, digdug._lives-=1, que é mesmo bom

     dicio = {}
     x, y = digdug_pos
     dicio['w'] = [x,y-1] if digdug_pos[1]>0  else [x,y]
     dicio['s'] = [x,y+1] if digdug_pos[1]<23 else [x,y]
     dicio['a'] = [x-1,y] if digdug_pos[0]>0  else [x,y]
     dicio['d'] = [x+1,y] if digdug_pos[0]<47 else [x,y]
     dicio[' '] = [x,y]

     return dicio


'''          devolve a melhor opção de movimento do agente para não morrer, considerando todos os piores cenários em todas as seguintes frames,         '''
''' até o nível de recursão desejado, em qualquer situação, incluindo situações de perigo de morte (colisão com outro bicho -> ter a mesma posição que outro bicho -> morte) '''
#'''                 Esta função devolve o número de movimentos do Digdug possíveis que não resultem em posições que sejam iguais a alguma posição de algum bicho                '''
#'''Imagine-se o Digdug, a 2 unidades para a direita e 1 para baixo de algum bicho. E imagine-se um swarm ínumero de bichos, a partir das 10 posições abaixo do Digdug              '''
#'''No imediato, o Digdug pode mover-se para qualquer lado sem colidir com nenhum bicho. Mas na frame a seguir a essa, se o Digdug se mexeu para cima, e o bicho próximo para a esquerda, '''
#'''                 o Digdug pode colidir com o bicho próximo se se mexer para a direita e o bicho para a esquerda,                                                                  '''
'''                                                 o que o faria ficar com a mesma posição que o bicho, e portanto morrer e perder 1 vida, ou o jogo.                                 '''
#'''Se se fosse analisar o número de movimentos possível do Digdug, mover para baixo parece mais seguro, pois na próxima frame, pode mover-se para qualquer lado, sem o risco de colidir com o bicho próximo
#Se fossemos decidir que movimento fazer segundo a quantidade de movimentos que o Digdug pode fazer sem morrer para cada movimento que decidir, sem morrer, nas próximas 2 frames, para baixo seria sempre escolhido
#em detrimento de ir para cima, pois para cima (na 1ª frame), só poderia andar para cima e para a esquerda depois (2 movimentos possíveis sem morrer), enquanto que para baixo (na 1ª frame), poderia fazer os 5 movimentos
#(para cima, para baixo, para a esquerda, para a direita, e ficar na mesma posição).'''
#'''         No entanto, se se mexer para baixo vezes suficientes, eventualmente encontra o swarm de bichos, e não se pode mexer mais para baixo sem colidir com algum e morrer. Dependendo de como encontra o swarm,
#pode ficar sem movimentos possíveis sem risco de colisão, pelo que a partir de certa posição, o número de movimentos possíveis a partir dessa posição é 0, e o Digdug colide e morre.'''
#'''                                         Mas no caso de ir para cima, estaria sempre limitado a 2 ou 3 movimentos sem risco de colisão e morte em cada frame, mas poderia continuar indefinidamente em frente    '''
'''                                                     sem morrer e perder vida e sentir dor.      '''
#'''             No caso de ir para baixo, pode ter todos os 5 movimentos disponíveis a cada frame até certa posição, pelo que depois estes diminuiriam para 0.           '''
#'''                                 Ironicamente, neste cenário de ir para baixo, seria possível o Digdug sobreviver indefinidamente se o bicho próximo também continuasse a ir para baixo enquanto
#o Digdug fosse para baixo também, sendo que se o Digdug se move-se para cima depois de encontrar o swarm, e o bicho próximo para a esquerda, estaríamos num cenário idêntico ao de ir para cima desde o início'''
#'''     com a diferença de que o swarm ficaria muito mais perto do Digdug, e o Didgug só poderia fazer as mesmas 2 ou 3 movimentos (cima e esquerda) que podia fazer se começasse a ir para cima logo ao início,     '''
#'''                                                          mas mais perto de ter a sua posição igual à de um bicho e sentir '''

'''                                            dor de beliscão no peito, (digdug)  bom (mesmo bom)                                              '''                      
def agent_best_single_move_to_avoid_death_dor( digdug_pos, mapa, enemy_current_and_possible_positions, rocks_current_and_possible_positions, recursion=1, alive=0):
    if recursion == 0:
        return {}, 1, 1, 1            # devolve 1 se a recursão terminar, o que indica que a chamada que invocou a chamada que retornou isto, ainda continha movimentos que não resultavam em morte, após tanta recursão
    x_dor,y_beliscão = digdug_pos
    dicio_number_of_possible_moves_without_pain = {}
    dicio_number_of_possible_moves_without_pain[' '] = [0,0,math.dist([x_dor, y_beliscão], [0,0]),0, agent_digdug_proximity_pos((x_dor,y_beliscão), rocks_current_and_possible_positions)[1]]
    dicio_number_of_possible_moves_without_pain['w'] = [0,0,math.dist([x_dor,y_beliscão-1], [0,0]),0, agent_digdug_proximity_pos((x_dor,y_beliscão-1), rocks_current_and_possible_positions)[1]]
    dicio_number_of_possible_moves_without_pain['s'] = [0,0,math.dist([x_dor,y_beliscão+1], [0,0]),0, agent_digdug_proximity_pos((x_dor,y_beliscão+1), rocks_current_and_possible_positions)[1]]
    dicio_number_of_possible_moves_without_pain['a'] = [0,0,math.dist([x_dor-1,y_beliscão], [0,0]),0, agent_digdug_proximity_pos((x_dor-1,y_beliscão), rocks_current_and_possible_positions)[1]]
    dicio_number_of_possible_moves_without_pain['d'] = [0,0,math.dist([x_dor+1,y_beliscão], [0,0]),0, agent_digdug_proximity_pos((x_dor+1,y_beliscão), rocks_current_and_possible_positions)[1]]

    next_enemy_possible_positions = set()
    for pos in enemy_current_and_possible_positions:
        x,y = pos
        next_enemy_possible_positions.add((x,y))                #idealmente calcularia apenas o pior movimento, a pior posição que o bicho poderia tomar para mim, que poderia ser o movimento que o deixasse mais próximo de mim, mas também um movimento que o afastasse de mim, mas mais tarde me encurralásse. Se imaginarmos muitos bichos dispersos muito acima de mim, e um swarm em baixo, se os bichos todos tomassem o movimento que os aproximasse de mim, talvez conseguisse fugir numa diagonal para cima, ou sempre para cima. Mas se os bichos de cima fizerem uma linha distânciados a 2 unidades uns dos outros, eu não poderia escapar por cima, e os bichos de baixo eventualmente apanhariam-me. Como não vejo como poderia calcular esta pior jogada, calculo todas as jogadas, e aglomero-as numa super jogada malévola, em que a pior jogada está contida, bem como todas as outras. Isto pode tirar opções válidas para mim, visto que esta jogada é mais que ótima para o inimigo; que passado de um certo nível de recursão, 1 Pooka ocuparia o mapa inteiro como se tivesse a multiplicar a cada frame 
        next_enemy_possible_positions.add((x-1,y))
        next_enemy_possible_positions.add((x+1,y))
        next_enemy_possible_positions.add((x,y-1))
        next_enemy_possible_positions.add((x,y+1))
    next_enemy_possible_positions.discard((0,0))          #se o DigDug tiver nesta posição, ele não pode morrer para colisões com bichos (porque se os bichos também tiverem nesta posição, eles desaparecem primeiro do que é chamada a função collision() (que pode fazer digdug.kill(), que tirar uma vida ao digdug)

    next_rocks_possible_positions = set()
    for pos in rocks_current_and_possible_positions:
        x,y = pos
        next_rocks_possible_positions.add((x,y))
        if y+1<24 and mapa[x][y+1] != 1:
            next_rocks_possible_positions.add((x,y+1))

    pico_dor_mesmo_dor = 0
    digdug_dor = 0                                                            #retorna 0 se abaixo não se verificar nenhuma jogada que não pudesse resultar em morte, o que significa que fui encurralado e vou ter a mesma posição que um bicho, e morrer, e perder uma vida, e sentir no peito dor de beliscão aguda e mesmo 'dor' bom
    #dor = 0
    mamilo_abaixo = 0
    agent_moves_positions = agent_possible_moves_dor(digdug_pos)
    for move, position in agent_moves_positions.items():
        if (move == ' ' or tuple(position) != tuple(digdug_pos)) and (tuple(position) not in enemy_current_and_possible_positions) and (tuple(position) not in rocks_current_and_possible_positions):
            moves_sem_dor, dor, beliscão, mamilo = agent_best_single_move_to_avoid_death_dor( position, mapa, next_enemy_possible_positions, next_rocks_possible_positions, recursion-1, 1)
            if dor > pico_dor_mesmo_dor:
                pico_dor_mesmo_dor = dor
            digdug_dor += beliscão
            #dor += 1
            mamilo_abaixo += 1
            dicio_number_of_possible_moves_without_pain[move] = [ dor, beliscão, math.dist(position, [0,0]), mamilo, agent_digdug_proximity_pos(position, rocks_current_and_possible_positions)[1]]

    #print("moves válidas [recursion:", recursion,"]:", dor)
    return dicio_number_of_possible_moves_without_pain, 1+pico_dor_mesmo_dor, digdug_dor, mamilo_abaixo






def my_dark_dor(digdug_pos, bicho_pos):
    print("dor mesmo dor beliscão queimadura dor daquela das compulsões a imaginar e/ou fazer beliscão no peito pouco abaixo do mamilo esquerdo e para o centro. Bom")

    if digdug_pos[0] < bicho_pos[0]:
        return "a"
    if digdug_pos[0] > bicho_pos[0]:
        return "d"
    if digdug_pos[1] < bicho_pos[1]:
        return "w"
    if digdug_pos[0] > bicho_pos[0]:
        return "s"
    return ''
    






#############################################
def agent_possible_moves(state, chave='j'):            #devolve dicio com todas as potenciais posições que o agente pode tomar e executar na próxima frame, ou apenas a posição consequente de um movimento
     if 'digdug' in state:                             
        digdug_pos = state['digdug']                   
     else:                                             
        return ''
     dicio = {}
     x, y = digdug_pos
     dicio['w'] = [x,y-1] if digdug_pos[1]>0  else [x,y]
     dicio['s'] = [x,y+1] if digdug_pos[1]<23 else [x,y]
     dicio['a'] = [x-1,y] if digdug_pos[0]>0  else [x,y]
     dicio['d'] = [x+1,y] if digdug_pos[0]<47 else [x,y]
     dicio[' '] = [x,y]

     if chave in 'wsad ':
          return dicio[chave]
     return dicio








def all_enemies_current_and_possible_next_positions(state, mapa):                 #devolve lista com todas as posições de potencial morte na próxima frame devido a colisão com (quaisqueres) inimigos (ou com o fogo deles)
    possible_death_positions = []  
    possible_stone_death_positions = []  

    dicio = {}
    dicio_stones = {}

    digdug_proximity_zone, number_valid_moves = agent_digdug_proximity_pos(state['digdug'], [tuple[r['pos']] for r in state['rocks']])

    if 'enemies' in state:
        for enemy in state['enemies']:
            if math.dist(state['digdug'],enemy['pos']) <= 5:
                    enemy_name = enemy["name"]
                    enemy_id = enemy["id"]
                    enemy_pos = enemy["pos"]  

                    enemy_danger_zones = enemy_current_and_possible_next_positions(enemy_pos)
                    if enemy_name == "Fygar":
                        fygar_fire_zones = fygar_fire(enemy)
                        for fire_pos in fygar_fire_zones:
                            if not mapa_is_valid_position( fire_pos ):
                                continue
                            #elif (mapa[fire_pos[0]][fire_pos[1]] == 1) and (fire_pos not in digdug_proximity_zone) :  #possível fonte de mortes; retirar se o DigDug tiver mortes que não aparecem no terminal do cliente
                            #    continue
                            enemy_danger_zones.append( fire_pos )

                    dicio[enemy_id] = enemy_danger_zones

    if 'rocks' in state:
            for rock in state['rocks']:
                 rock_id = rock["id"]
                 rock_pos = rock["pos"]
                 x, y = rock_pos
                 rock_pos_below = [x, y+1]
                 if y+1<24 and mapa[x][y+1] != 1:
                    dicio_stones[rock_id] = [ rock_pos, rock_pos_below ]
                 else:
                    dicio_stones[rock_id] = [ rock_pos ]

    for values in dicio_stones.values():
        possible_stone_death_positions+=values

    for values in dicio.values():
        possible_death_positions+=values

    
   
    return possible_death_positions, possible_stone_death_positions
                         

                   





def enemy_current_and_possible_next_positions(enemy_pos):                 #Se a posição do digdug for igual à posição de um bicho, o digdug morre.
#o digdug só morre quando é chamada a função kill_digdug() do game.py. Esta função só é chamada na função collision(), em 3 situações distintas: (1) quando a posição (atual) do digdug é igual à posição de um bicho (digdug.pos == e.pos); (2) quando a posição do digdug é igual a uma das posições de fire dos fygars (if e.name == 'Fygar' and e.fire and digdug.pos in e.fire); (3) quando a posição do digdug é igual à posição de uma pedra (digdug.pos == r.pos)
#esta função devolve uma lista com a posição de um bicho, bem como a posição que ele terá de seguida na próxima frame, que é uma de todas as posições que ele pode ter de seguida.
    zone = []                               #estas são as posição adjacentes desse inimigo
    dicio = {}
    x,y = enemy_pos

    dicio['0'] = [x,y]                      #a ausência desta linha é que fazia o digdug colidir com os Pookas quando eles o perseguiam até o canto inferior direito do mapa. O digdug subia para cima, mas depois o primeiro if do flee é ir para baixo, para a posição do inimigo, que é o que acontecia e não era considerado perigoso sem esta linha. Pelo lado contrário, ir para a esquerda é o último if
    dicio['1'] = [x-1,y]
    dicio['2'] = [x+1,y]
    dicio['3'] = [x,y-1]
    dicio['4'] = [x,y+1]
                                             #os inimigos não se movem na diagonal, pelo que isto não ajuda a sobreviver colisões. Até prejudica, pois pode fazer o digdug parar sem reação quando poderia ter movimentos seguros se estas posições diagonais dos inimigos que eles não podem fazer não fossem consideradas

    for values in dicio.values():
         zone.append(values)
    return zone                             #devolve uma lista com todas as posições de potencial morte na próxima frame devido a colisão com um inimigo em particular








def fygar_fire(state_fygar):       #devolve lista com todas as posições de potencial morte devido a contacto doloroso com o fogo
    zone = []
    dicio = {}

   
    x,y = state_fygar['pos']

    
    dicio['1'] = [x+1, y]
    dicio['2'] = [x-1, y]
    dicio['3'] = [x+2, y]
    dicio['4'] = [x-2, y]
    dicio['5'] = [x+3, y]
    dicio['6'] = [x-3, y]
    dicio['7'] = [x+4, y]
    dicio['8'] = [x-4, y]


    for values in dicio.values():
         if values not in zone:
            zone.append(values)

    return zone












''' Precognition '''
#funções importadas, mas cuja lógica é básica e essencial, e que não deve ser alterada em testes que façam com outros mapas. Mesmo que se mude as dimensões do mapa e se adicionem novos tipos de Tile, isto deve-se manter em princípio
from consts import Tiles

#esta função olha para as dimensões e layout do mapa (os túneis e as pedras por escavar), e vê se é possível um bicho mover-se para um ponto x,y no mapa ou não.
#se esse ponto tiver fora dos bounds do mapa, ou se corresponder a uma pedra por escavar, não se pode mover para lá, e retorna True (is blocked). Se o ponto corresponder a um pocket vazio, ou outra coisa, retorna False (is not blocked).
def is_blocked(pos, mapa, traverse):
        x, y = pos
        if x not in range(len(mapa)) or y not in range(len(mapa[0])):   #ver se o ponto não está dentro das dimensões do mapa
            return True
        if mapa[x][y] == Tiles.PASSAGE:
            return False
        if mapa[x][y] == Tiles.STONE:
            if traverse:
                return False
            else:
                return True
        assert False, "Unknown tile type"

#esta função calcula a posição resultante de um movimento na direção escolhida a partir duma posição inicial. 
def calc_pos(cur, direction: Direction, mapa, traverse=True):
        cx, cy = cur
        npos = cur
        if direction == Direction.NORTH:
            npos = cx, cy - 1
        if direction == Direction.WEST:
            npos = cx - 1, cy
        if direction == Direction.SOUTH:
            npos = cx, cy + 1
        if direction == Direction.EAST:
            npos = cx + 1, cy

        # test blocked
        if is_blocked(npos, mapa, traverse):
            return cur

        return npos

#-também usar a próxima posição dos bichos para determinar se vamos estar numa posição de risco na próxima frame, além de verificar apenas nesta (como o comportamento dos Pookas smart é 100% previsível na próxima frame (porque a minha posição não muda até lá se premir 'A' ou '', e posso prevêr igualmente o que eles vão fazer para qualquer outro movimento que eu faça. Só tenho que avaliar isto no final do agent, e ver se é melhor prosseguir com esse movimento ou fugir; vale pouco a pena disparar apenas 1 ou 2 unidades de corda para depois ficar em situação de perigo e ter que fugir))

#predict their movements (get all of their expected positions, according to their smart behavior movement calculations, over n frames)
def precognition(digdug_pos, state, positions, mapa, recursion=3):
        if recursion<=0:
            return state, positions
        
        new_state = {'enemies': {}, 'rocks': state['rocks']}
        
        for id, bicho in state['enemies'].items():
                    a,b = bicho['pos']
                    if mapa[a][b] == 1:
                        positions.append(bicho['lastpos'])
                        new_state['enemies'][id] = {'pos': bicho['pos'], 'id': bicho['id'], 'dir': bicho['dir'], 'name': bicho['name'], 'lastpos': bicho['pos'] }
                        continue
                    enemies_pos = [e['pos'] for e in state['enemies'].values() if e['id'] != bicho['id'] ]
                    open_pos = [
                        [pos[0], pos[1]]
                        for pos in [
                            calc_pos(bicho['pos'], d, mapa, False) for d in Direction
                        ]
                        if [pos[0], pos[1]] not in [bicho['lastpos']] + enemies_pos
                        and [pos[0], pos[1]] not in [r['pos'] for r in state['rocks']]  # don't bump into rocks
                    ]
                    if open_pos == []:
                        positions.append(bicho['lastpos'])
                        new_state['enemies'][id] = {'pos': bicho['lastpos'], 'id':bicho['id'], 'dir':bicho['dir'], 'name': bicho['name'], 'lastpos': bicho['pos'] }
                    else:
                        next_pos = sorted(open_pos, key=lambda pos: math.dist(digdug_pos, pos))
                        positions.append(next_pos[0])
                        new_state['enemies'][id] = {'pos': next_pos[0], 'id':bicho['id'], 'dir':bicho['dir'], 'name': bicho['name'], 'lastpos': bicho['pos'] }
                    #if len(open_pos)<=1:
                #    print('open_pos:',open_pos, 'lastpos:', bicho['lastpos'], 'newpos:', next_pos[0], 'pos', bicho['pos'])
                #    for r in state['rocks']:
                #        print('rock:', r['pos'])
                #    print("\n")

        

        return precognition(digdug_pos, new_state, positions, mapa, recursion-1)








def agent_shooting_precognition(state, oldstate, mapa, digdug_pos, recursion=3):
    
    if 'enemies' not in oldstate:
        return [], []

    #predict positions of enemies and return them in the form of the last predicted state, and as a cumulative list of all predicted positions
    lastpos = {}
    for e in oldstate['enemies']:
        if math.dist(e['pos'], digdug_pos)<=6:
            id = e['id']
            lastpos[id] = e['pos']

    state_with_lastpos = {'enemies': {}, 'rocks': state['rocks']}
    for e in state['enemies']:
        id = e['id']
        if id in lastpos:
            state_with_lastpos['enemies'][id] = {'pos': e['pos'], 'id':e['id'], 'dir':e['dir'], 'name': e['name'], 'lastpos': lastpos[id]}
    
    return precognition(digdug_pos, state_with_lastpos, [], mapa, recursion)









def agent_shooting_conditions(state, oldstate, mapa, digdug_pos, digdug_dir, closest_enemy_name, zoomed_frames):
    x,y = digdug_pos
    rocks = [tuple(r['pos']) for r in state['rocks']]
    shooting_range_left = [[x-1,y], [x-2,y], [x-3,y]]
    shooting_range_right = [[x+1,y], [x+2,y], [x+3,y]]
    shooting_range_up = [[x,y-1], [x,y-2], [x,y-3]]
    shooting_range_down = [[x,y+1], [x,y+2], [x,y+3]]

    all_close_enemies_actual_and_predicted_positions = []

    close_enemy_pos = []
    if 'enemies' in state:
        for entry in state["enemies"]:
            if math.floor(math.dist(digdug_pos, entry["pos"])) <= 5:
                close_enemy_pos.append(entry["pos"])

    if zoomed_frames <= 80 or closest_enemy_name != 'Fygar' or (state['level']>=20 and state['step']<=840):
        precognition_sight = 2
    else:
        precognition_sight = 0
    precognition_state, precognition_positions = agent_shooting_precognition(state, oldstate, mapa, digdug_pos, precognition_sight)

    all_close_enemies_actual_and_predicted_positions += close_enemy_pos
    all_close_enemies_actual_and_predicted_positions += [[pre_pos[0], pre_pos[1]] for pre_pos in precognition_positions]

    if digdug_dir==Direction.WEST:
        for potential_target in shooting_range_left:
            a,b = potential_target
            if (not mapa_is_valid_position((a,b))) or (mapa[a][b]==1) or ((a,b) in rocks):
                break      
            if potential_target in all_close_enemies_actual_and_predicted_positions:
                return 'A',digdug_dir
    elif digdug_dir==Direction.EAST:
        for potential_target in shooting_range_right:
            a,b = potential_target
            if (not mapa_is_valid_position((a,b))) or (mapa[a][b]==1) or ((a,b) in rocks):
                break    
            if potential_target in all_close_enemies_actual_and_predicted_positions:
                return 'A',digdug_dir
    elif digdug_dir==Direction.NORTH:
        for potential_target in shooting_range_up:
            a,b = potential_target
            if (not mapa_is_valid_position((a,b))) or (mapa[a][b]==1) or ((a,b) in rocks):
                break    
            if potential_target in all_close_enemies_actual_and_predicted_positions:
                return 'A',digdug_dir
    elif digdug_dir==Direction.SOUTH:
        for potential_target in shooting_range_down:
            a,b = potential_target
            if (not mapa_is_valid_position((a,b))) or (mapa[a][b]==1) or ((a,b) in rocks):
                break    
            if potential_target in all_close_enemies_actual_and_predicted_positions:
                return 'A',digdug_dir
    return '', digdug_dir









def agent_random_move(state, digdug_dir, mapa, prefered_movements=''):        #para ver se desbloqueia o digdug em casos de impasse com algum inimigo
     possible_moves = agent_possible_moves(state)
     if possible_moves == '':
         return '', digdug_dir
     possible_death_positions, possible_stone_death_positions = all_enemies_current_and_possible_next_positions(state, mapa)
     safe_moves = ''
     for key, position in possible_moves.items():
          if (position not in possible_death_positions) and (position not in possible_stone_death_positions):
            safe_moves+=key

     if safe_moves == '':
         return '', digdug_dir
     
     prefered_potential_moves=''
     if len(prefered_movements)>0:
         for i in prefered_movements:
             if i in safe_moves:
                 prefered_potential_moves+=i

     if len(prefered_potential_moves) > 0:
        key = random.choice(prefered_potential_moves)
     else:
        key = random.choice(safe_moves)

     if key == 'w':
        return key, Direction.NORTH
     elif key == 'a':
        return key, Direction.WEST
     elif key == 'd':
        return key, Direction.EAST
     elif key == 's':
        return key, Direction.SOUTH
     return '', digdug_dir

    






def agent_dist_closest_enemy(state, swarm):                        #devolve as coordenadas do inimigo mais perto e a sua distância ao digdug
    if "digdug" in state:

        digdug_pos = state["digdug"]

        distancias = {}     #guardar as posições e distâncias de cada bicho ao digdug
        bichos_swarm = {}   #ver as posições dos bichos que estão a 'swarm' unidades de distância de mim (bichos que estão na mesma posição contam como 1)

        for key, values in state.items():
            if key == "enemies":
                for entry in values:
                    dist = math.dist(digdug_pos, entry["pos"])
                    priority = dist

                    if entry['name'] == 'Fygar':
                        priority -= 1
                    if entry['name'] == 'Fygar' and (state['step']>=1200 or state['level']<=18):
                        priority -= 2
                    if entry['name'] == 'Fygar' and state['step']>=2100:
                        priority -= 41
                    if entry['name'] == 'Fygar' and state['step']>=2700:
                        priority += 40

                    if state['level']>=20:
                        if (state['step'] > (400 + state['level']*20)) and entry['pos'][1]<24 / 4:
                            priority -= 4
                        elif (state['step'] > (400 + state['level']*20)) and (state['step'] < 2100) and entry['pos'][1] < 24 / 2:
                            priority -= 8
                        elif (state['step'] > (400 + state['level']*20)) and (state['step'] < 2100) and entry['pos'][1] < 24 * 3 / 4:
                            priority -= 16
                        elif (state['step'] > (400 + state['level']*20)) and (state['step'] < 2100) and entry['pos'][1] < 24:
                            priority -= 24
                    else:
                        if (state['step'] < 2100) and entry['pos'][1]<24 / 4:
                            priority -= 4
                        elif (state['step'] < 2100) and entry['pos'][1] < 24 / 2:
                            priority -= 8
                        elif (state['step'] < 2100) and entry['pos'][1] < 24 * 3 / 4:
                            priority -= 20
                        elif (state['step'] < 2100) and entry['pos'][1] < 24:
                            priority -= 28

                    if state['level'] >= 20 and state['step']<=840:         #a partir deste nível, isto substitui toda a prioridade acima para steps inferiores a 840
                        priority = dist
                        if entry['pos'][0]<=8:
                            priority -= 8

                        if entry['pos'][1]<=8:
                            priority -= 8

                        if entry['pos'][1]<=14 and state['step']>=400 and state['step']<=640:
                            priority -= 4
                        if entry['pos'][1]<=23 and state['step']>=400 and state['step']<=640:
                            priority -= 2

                        if entry['pos'][0]<=14 and state['step']>640:
                            priority -= 4
                        if entry['pos'][1]<=14 and state['step']>640:
                            priority -= 2

                        if dist <= 5 and entry['name'] == 'Fygar' and entry['pos'][0]<=8 and entry['pos'][1]<=8:
                            priority -= 8

                    if dist <= 3 and entry['name'] == 'Fygar' and state['step']<=840:
                        priority -= 40


                    if 'traverse' in entry and entry['traverse']==True:
                        traverse = True
                    else:
                        traverse = False

                    distancias[entry["name"]+entry["id"]] = [entry["pos"], dist,  entry["dir"], entry['name'], traverse, priority]     #cada entrada na dicio distâncias vai ser uma lista de 3 elementos: par de coordenadas do inimigo, distância entre o digdug e o inimigo, direção do inimigo
                    if dist <= swarm:
                        bichos_swarm[tuple(entry['pos'])] = entry['name']

        closest_enemy_dist = 100       
        closest_enemy_pos = [0,0]
        closest_enemy_name = 'Fygar'
        closest_enemy_traverse = False
        closest_enemy_priority = 100  
        for key, dists in distancias.items():
            if dists[5] < closest_enemy_priority:
                closest_enemy_dist = dists[1]
                closest_enemy_pos = dists[0]
                closest_enemy_name = dists[3]
                closest_enemy_priority = dists[5]
                if dists[4] == True:
                    closest_enemy_traverse = True
                else:
                    closest_enemy_traverse = False
                    
        return closest_enemy_pos, closest_enemy_dist, closest_enemy_name, closest_enemy_traverse, bichos_swarm
    return None, None, None, None, None
     


    




def agent_stalk(state, oldstate, digdug_pos, digdug_dir, danger_zones, closest_enemy_pos, closest_enemy_name, closest_enemy_traverse, stones_to_remove, mapa, last_pos, clear_entrance_pathway, bichos_swarm, trapped_frames, zoomed_frames, remove_stone = False, possible_death_keys=''):                #Se a posição do digdug for igual à posição de um bicho, o digdug morre.
#mexer o agente de modo a que ele não considere ações que estão proibídas (que são as ações que o podem meter em perigos de vida)
#o digdug morre se a sua posição for igual à de um bicho (colisão).
    

        #dados necessários para as pesquisas abaixo
        key=''
        dist = math.dist(digdug_pos, closest_enemy_pos)
        rocks = [tuple(r['pos']) for r in state['rocks']]



        #caso os Pookas espertos estiverem a queimar tempo
        if state['step']>=state['timeout']-300:
            closest_enemy_pos = [44, 22]




        close_enemy_pos = []
        close_enemy_pos.append(closest_enemy_pos)
        close_enemy_dict = []
        close_enemy_dict.append({'pos': closest_enemy_pos, 'name': closest_enemy_name})
        for entry in state["enemies"]:
            if len(bichos_swarm.keys())>=2:
                new_dist = math.dist(digdug_pos, entry["pos"])
                if new_dist < dist:
                    if (entry['name'] == 'Fygar') or (entry['name'] == 'Pooka' and new_dist + 1 < dist):
                        dist = new_dist
                        closest_enemy_pos = entry['pos']
            if math.dist(digdug_pos, entry["pos"]) <= 8:
                close_enemy_pos.append(entry["pos"])
                close_enemy_dict.append({'pos': entry['pos'], 'name': entry['name']})




        #ver se o inimigo mais próximo está preso
        trap = enemy_trapped(closest_enemy_pos, mapa, rocks, closest_enemy_traverse)
        if closest_enemy_name == 'Pooka':
            trap_pooka, trapped_frames = pooka_trapped(closest_enemy_pos, mapa, rocks, trapped_frames)
        else:
            trap_pooka, trapped_frames = None, 0




        #ver que bichos estão encantaDORamente debaixo de rochas 
        dangerous_rocks = enemies_below_rocks(state, mapa, rocks)
        




        #se o inimigo mais próximo estiver preso, e a única maneira de chegar até ele for ao escavar as pedras à sua volta, ativar esta variável para permitir um movimento de possível morte
        dor = False




        #disparar se estiver algum bicho na linha de fogo
        key_s, digdug_dir_s = agent_shooting_conditions(state, oldstate, mapa, digdug_pos, digdug_dir, closest_enemy_name, zoomed_frames)
        if key_s == 'A':
            return key_s, digdug_dir_s, dor, trapped_frames
        
        


        if dist > 5 and clear_entrance_pathway != set() and trap[0]==False and len(bichos_swarm.keys())==0:
            #print('clear entrance pathway')
            state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'rocks': rocks, 'last_pos': tuple(last_pos), 'bichos_swarm': bichos_swarm}
            problem = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchProblem(agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchDomain_ClearEntrance(), state_initial, clear_entrance_pathway)            
            tree_search = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchTree(problem, 78, 'A*')
            path = tree_search.search()

            if path != None and len(path)>1:
                next_move = path[1]
                key = next_move['key']
                digdug_dir = next_move['dir']  




        elif dist >= 3 and dangerous_rocks != set() and trap[0]==False and trapped_frames <= 8 and len(bichos_swarm)<=1 and state['step']<=2100 and (state['step']>1000 or state['level']<20) and state['level']<29:
            #print('dangerous rocks', dangerous_rocks)
            state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'rocks': rocks, 'last_pos': tuple(last_pos), 'bichos_swarm': bichos_swarm}
            problem = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchProblem(agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchDomain_ClearEntrance(), state_initial, dangerous_rocks)            
            tree_search = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchTree(problem, 78, 'A*')
            path = tree_search.search()

            if path != None and len(path)>1:
                next_move = path[1]
                key = next_move['key']
                digdug_dir = next_move['dir']  
        



        #se estivermos perto do inimigo, e se tratar de um Pooka preso não entre rochas, mas sim na própria stone, desencravar, abdicando da segurança se estiver preso há mais de 80 frames
        elif dist <=8 and trapped_frames >= 8 and trapped_frames<=80:
            print("         Pooka preso em pedra")
            state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'rocks': rocks, 'enemies': close_enemy_dict,  'last_pos': tuple(last_pos), 'mapa': mapa,  'danger_zones': danger_zones, 'bichos_swarm': bichos_swarm}
            problem = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchProblem(agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchDomain_Stone_Remover(), state_initial, trap_pooka)            
            tree_search = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchTree(problem, 78, 'A*')
            path = tree_search.search()

            if path != None and len(path)>1:
                next_move = path[1]
                key = next_move['key']
                digdug_dir = next_move['dir']

        elif dist <=8 and trapped_frames > 80:
            print("         Pooka preso em pedra    dor")    
            state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'rocks': rocks, 'enemies': [],  'last_pos': tuple(last_pos), 'mapa': mapa,  'danger_zones': [], 'bichos_swarm': bichos_swarm}
            problem = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchProblem(agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchDomain_Stone_Remover(), state_initial, trap_pooka)            
            tree_search = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchTree(problem, 78, 'A*')
            path = tree_search.search()

            if path != None and len(path)>1:
                next_move = path[1]
                key = next_move['key']
                digdug_dir = next_move['dir']

            dor = True 




        #aproximar do inimigo
        elif  dist > 8:                 
            state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'rocks': rocks, 'last_pos': tuple(last_pos), 'mapa': mapa, 'bichos_swarm': bichos_swarm}
            problem = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchProblem(agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchDomain_Stalk(), state_initial, tuple(closest_enemy_pos))            
            tree_search = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchTree(problem, 78, 'A*')
            path = tree_search.search()

            if path != None and len(path)>1:
                next_move = path[1]
                key = next_move['key']
                digdug_dir = next_move['dir']   
            



        #se estivermos perto do inimigo, e ele estiver preso, tentar desencravá-lo
        elif dist <=8 and trap[0] != False:
            #se o inimigo estiver preso numa situação onde é possível desancravá-lo em segurança, com a remoção de uma pedra, ir para debaixo da pedra
            if trap[1] != 'dor':
                print("trapped sem dor")
                stone_to_fall = trap[1]

                state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'rocks': rocks, 'enemies': close_enemy_dict, 'last_pos': tuple(last_pos), 'mapa': mapa, 'danger_zones': danger_zones, 'bichos_swarm': bichos_swarm}
                problem = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchProblem(agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchDomain_Stone_Remover(), state_initial, stone_to_fall)            
                tree_search = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchTree(problem, 78, 'A*')
                path = tree_search.search()

                if path != None and len(path)>1:
                    next_move = path[1]
                    key = next_move['key']
                    digdug_dir = next_move['dir']

            #se estivermos perto do inimigo, e ele estiver preso, mas numa situação onde é impossível desancravá-lo em segurança, então tentemos aproximar dele, abdicando da segurança
            else:                   
                print('trapped dor') 
                state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'rocks': rocks, 'enemies': [],  'last_pos': tuple(last_pos), 'mapa': mapa,  'danger_zones': [], 'bichos_swarm': bichos_swarm}
                problem = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchProblem(agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchDomain_Stone_Remover(), state_initial, [tuple(closest_enemy_pos)])            
                tree_search = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchTree(problem, 78, 'A*')
                path = tree_search.search()

                if path != None and len(path)>1:
                    next_move = path[1]
                    key = next_move['key']
                    digdug_dir = next_move['dir']

                dor = True




        #se estivermos perto do inimigo e não há pedras no caminho, tentar posicionar-nos para disparar a corda não nele, mas nas premonições da posição dele (ou de outros inimigos próximos), se estivermos a persegui-lo à menos de zoomed_frames
        elif  dist <= 8 and (remove_stone == False or stones_to_remove == set()):
            #procurar enquadrar a posição de disparo não com a posição atual do inimigo, mas com a premonição de onde ele vai estar daqui a 1 frame
            #print('posicionar para matar inimigo')
            precognition_state, precognition_positions = agent_shooting_precognition(state, oldstate, mapa, digdug_pos, 1)
            precognition_dist = 100
            precognition_pos = None
            for pos in precognition_positions:
                dist = math.dist(digdug_pos, pos)
                if dist < precognition_dist:
                    precognition_dist = dist
                    precognition_pos = [pos[0], pos[1]]

            if precognition_positions != []:
                precognition_positions = [[p[0], p[1]] for p in precognition_positions]
            else:
                precognition_positions = close_enemy_pos
                precognition_pos = closest_enemy_pos
            
            if zoomed_frames <= 80 or (state['level'] >= 20 and state['step'] <= 840):
                state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'enemies': precognition_positions, 'closest_enemy': precognition_pos, 'closest_enemy_name': closest_enemy_name, 'rocks': rocks, 'mapa': mapa, 'danger_zones': danger_zones, 'state_info': {'level': state['level'], 'step': state['step']}, 'bichos_swarm': bichos_swarm, 'last_pos': tuple(last_pos)}
            else:
                state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'enemies': close_enemy_pos, 'closest_enemy': closest_enemy_pos, 'closest_enemy_name': closest_enemy_name, 'rocks': rocks, 'mapa': mapa, 'danger_zones': danger_zones, 'state_info': {'level': state['level'], 'step': state['step']}, 'bichos_swarm': bichos_swarm, 'last_pos': tuple(last_pos)}
            problem = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchProblem(agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchDomain(), state_initial, '')            
            tree_search = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchTree(problem, 78, 'A*')
            path = tree_search.search()

            if path!=None and len(path)>1:
                next_move = path[1]
                key = next_move['key']
                digdug_dir = next_move['dir']




        #se estivermos perto do inimigo, mas houver pedras na linha de disparo, remover uma delas
        elif dist<=8 and remove_stone == True:
            #print("há pedras na linha de disparo", stones_to_remove)

            state_initial = {'digdug': tuple(digdug_pos), 'dir': digdug_dir, 'key': '', 'rocks': rocks, 'enemies': close_enemy_dict, 'last_pos': tuple(last_pos), 'mapa': mapa, 'danger_zones': danger_zones, 'bichos_swarm': bichos_swarm}
            problem = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchProblem(agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchDomain_Stone_Remover(), state_initial, stones_to_remove)            
            tree_search = agent_close_move_searchTree_dor_beliscão_peito_esquerdo.SearchTree(problem, 78, 'A*')
            path = tree_search.search()

            if path != None and len(path)>1:
                next_move = path[1]
                key = next_move['key']
                digdug_dir = next_move['dir']



        return key, digdug_dir, dor, trapped_frames
                



def agent_flee(state, mapa, digdug_dir, possible_death_positions, possible_stone_death_positions ):         #Se a posição do digdug for igual à posição de um bicho, o digdug morre.
    '''                                                        #agent_feel e agent_move fogem extremamente bem aos Pookas, só em casos de cerco em que literalmente todas as ações são perigosas é que o agente pode morrer. Com o Fygars é diferente, presumo eu a bug, pois eles matam-me na diagonal ocasionalmente (será que movem-se verticalmente e cospem fogo uma unidade para o lado dessa ao mesmo tempo?). Edit: os Fygars matavam-me porque as posições de chama deles não estavam a ser bem adicionadas à lista de posições perigosas 
    possibles_moves = agent_possible_moves(state)           #a função agent_move pode tomar qualquer movimento que não coloque o digdug em risco de vida, mas pode acontecer que ao fazê-la, o digdug fica vivo, mas pode ficar de seguida numa posição de risco. Esta função é usada para mover o digdug de uma posição de risco para uma segura 
    possible_death_keys = ''                                    #esta função move o digdug de uma posição de risco para uma segura, que pode tornar-se de seguida insegura. A agent_move move o digdug de uma posição segura para outra segura, que pode de seguida tornar-se insegura.
    for action, value in possibles_moves.items():           #o digdug só morre quando é chamada a função kill_digdug() do game.py. Esta função só é chamada na função collision(), em 3 situações distintas: (1) quando a posição (atual) do digdug é igual à posição de um bicho (digdug.pos == e.pos); (2) quando a posição do digdug é igual a uma das posições de fire dos fygars (if e.name == 'Fygar' and e.fire and digdug.pos in e.fire); (3) quando a posição do digdug é igual à posição de uma pedra (digdug.pos == r.pos)
        if value in possible_death_positions:                        
             possible_death_keys+=action
    if len(possible_death_keys)>=4:
        print("flee possible death keys:",possible_death_keys)
    key=''
    
    if 'w' not in possible_death_keys:
        key = 'w'
        digdug_dir = Direction.NORTH
    elif 'a' not in possible_death_keys:
        key = 'a'
        digdug_dir = Direction.WEST
    elif 'd' not in possible_death_keys:
        key = 'd'
        digdug_dir = Direction.EAST
    elif 's' not in possible_death_keys:
        key = 's'
        digdug_dir = Direction.SOUTH
    
    '''
    '''
    possible_moves = agent_possible_moves(state)        #o digdug morre se a sua posição for igual à de um bicho (colisão).
    
    key = ''
    closest_center_dist = 100

    possible_death_keys = '' 
    safe_moves = {}
    for move, pos in possible_moves.items():
        if pos not in possible_death_positions:
            dist = math.dist(pos, [23, 12])
            safe_moves[key] = [move, dist]       #preferir fugir mais para o perto do meio, se for seguro, para evitar ser encurralado numa parede, que retira um possível movimento, mesmo que fosse seguro se lá não estivesse
            if dist < closest_center_dist:
                key = move
                digdug_dir = key2direction(key, digdug_dir)
                closest_center_dist = dist
        else:
            possible_death_keys+=move
    if len(possible_death_keys)>4:
        print("flee possible death keys:",possible_death_keys)
                                                       
    return key, digdug_dir
    '''
    possible_death_positions_dor = set()
    for p in possible_death_positions:
        possible_death_positions_dor.add(tuple(p))
    possible_stone_death_positions_dor = set()
    for p in possible_stone_death_positions:
        possible_stone_death_positions_dor.add(tuple(p))


    dicio_moves, digdug_alive, digdug_dor, mamilo_abaixo = agent_best_single_move_to_avoid_death_dor( state['digdug'], mapa, possible_death_positions_dor, possible_stone_death_positions_dor, 3 )
    key = ' '
    dor, peito, pico_dor_mesmo_dor, mamilo, mesmo_dor =dicio_moves[' ']
    for queimadura, beliscão in dicio_moves.items():
        '''
        if beliscão[0] > dor:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[1] > peito and beliscão[4] >= 4:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[1] == peito and beliscão[4] >= 4 and beliscão[3] > mamilo:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[1] == peito and beliscão[4] >= 4 and beliscão[3] == mamilo and beliscão[4] > mesmo_dor:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[1] == peito and beliscão[4] >= 4 and beliscão[3] == mamilo and beliscão[4] == mesmo_dor and beliscão[2] < pico_dor_mesmo_dor:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        
        
        if beliscão[0] > dor:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[4] > mesmo_dor:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[4] == mesmo_dor and beliscão[2] < pico_dor_mesmo_dor:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[4] == mesmo_dor and beliscão[2] == pico_dor_mesmo_dor and beliscão[1] > peito:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[4] == mesmo_dor and beliscão[2] == pico_dor_mesmo_dor and beliscão[1] == peito and beliscão[3] > mamilo:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        '''
        
        if beliscão[0] > dor:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[4] > mesmo_dor:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[4] == mesmo_dor and beliscão[1] > peito:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[4] == mesmo_dor and beliscão[1] == peito and beliscão[2] < pico_dor_mesmo_dor:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
        elif beliscão[0] == dor and beliscão[4] == mesmo_dor and beliscão[1] == peito and beliscão[2] == pico_dor_mesmo_dor and beliscão[3] > mamilo:
            key = queimadura
            dor = beliscão[0]
            peito = beliscão[1]
            pico_dor_mesmo_dor = beliscão[2]
            mamilo = beliscão[3]
            mesmo_dor = beliscão[4]
    
        

        
    #print(dicio_moves)
    #print(key)
    if peito == 0 and beliscão != 0 and dor == 0 and pico_dor_mesmo_dor>=0 and mamilo >= 0 and mesmo_dor >= 0:
        key = ''
        print("beliscão:    ", dicio_moves)
        for dor_beliscão, peito_esquerdo in dicio_moves.items():
            if peito_esquerdo[2] == 0:
                key = dor_beliscão
    return key, key2direction(key, digdug_dir)
    


    




def key2direction(key, digdug_dir):
    if key == "w":
        return Direction.NORTH
    elif key == "a":
        return Direction.WEST
    elif key == "s":
        return Direction.SOUTH
    elif key == "d":
        return Direction.EAST
    return digdug_dir








#caso tentemos disparar num inimigo, se o caminho não estiver desimpedido, temos de o desimpedir
def stone_remover(state, digdug_pos, enemy_pos, mapa, stones_to_remove, stones_clear, rocks):
    
    stones_start = len(stones_to_remove)

    for stone_pos in stones_to_remove:
        dis = math.dist(digdug_pos, stone_pos)
        if dis > 4:
            stones_to_remove = set()


    x,y = digdug_pos
    a,b = enemy_pos

    if x==a:            #coluna é a mesma, o digdug e o bicho estão alinhados na vertical
        dist = y-b      #se o valor for negativo, o bicho está abaixo do digdug. Se for positivo, o bicho está acima
        if dist < 0:
            for i in range(1, -dist):
                if y+i<24 and mapa[x][y+i]==1:
                    stones_to_remove.add((x, y+i))
                elif (x,y+i) in rocks:
                    rock = position_below_stone( (x,y+i), rocks )
                    if rock != None:
                        stones_to_remove.add(rock)

        else:
            for i in range(1, dist):
                if y-i>=0 and mapa[x][y-i]==1:
                    stones_to_remove.add((x, y-i))
                elif (x,y-i) in rocks:
                    rock = position_below_stone( (x,y-i), rocks )
                    if rock != None:
                        stones_to_remove.add(rock)

    if y==b:        #linha é a mesma, o digdug e o bicho estão alinhados na horizontal
        dist = x-a  #se o valor for negativo, o bicho está à direita do digdug
        if dist < 0:
            for i in range(1, -dist):
                if x+i<48 and mapa[x+i][y]==1:
                    stones_to_remove.add((x+i, y))
                elif (x+i,y) in rocks:
                    rock = position_below_stone( (x+i,y), rocks )
                    if rock != None:
                        stones_to_remove.add(rock)
 
        else:
            for i in range(1, dist):
                if x-i>=0 and mapa[x-i][y]==1:
                    stones_to_remove.add((x-i, y))
                elif (x-i,y) in rocks:
                    rock = position_below_stone( (x-i,y), rocks )
                    if rock != None:
                        stones_to_remove.add(rock)


    stones_end = len(stones_to_remove)

    if len(stones_to_remove)!=0:
        if stones_start < stones_end:
            stones_clear = 10
        else:
            stones_clear-=1
    else:
        stones_clear = 0    #não há pedra
    return stones_to_remove, stones_clear       








#para não ter que fazer tantas verificações sobre a validade de uma posição no mapa
def mapa_is_valid_position( pos ):
    x,y = pos
    if x>=0 and x<48 and y>=0 and y<24:
        return True
    return False








#calcula a posição do mapa abaixo de uma (pilha de) pedra
def position_below_stone(rock, rocks):
    a,b = rock

    if b >= 23:
        print("can't remove this rock", rock)
        return None

    if (a,b+1) not in rocks:
        return (a,b+1)
    
    return position_below_stone((a,b+1), rocks)
    








#ver se o inimigo que estamos a tentar exterminar está preso e não se pode mexer
def enemy_trapped(closest_enemy, mapa, stones_positions, traverse):

    if traverse == True:
        return False, None
    
    rocks_to_clear = []

    x,y = closest_enemy
    enemy_proximity_pos = [(x,y), (x+1,y), (x-1,y), (x,y+1), (x,y-1)]
    stone = 0
    if (mapa_is_valid_position((x-1,y)) and mapa[x-1][y]==1) or ((x-1,y) in stones_positions) or (not mapa_is_valid_position([x-1,y])):
        stone += 1
    if (mapa_is_valid_position((x+1,y)) and mapa[x+1][y]==1) or ((x+1,y) in stones_positions) or (not mapa_is_valid_position([x+1,y])):
        stone += 1
    if (mapa_is_valid_position((x,y-1)) and mapa[x][y-1]==1) or ((x,y-1) in stones_positions) or (not mapa_is_valid_position([x,y-1])):
        stone += 1
    if (mapa_is_valid_position((x,y+1)) and mapa[x][y+1]==1) or (not mapa_is_valid_position((x,y+1))):
        stone += 1

    if stone == 4:
        print("enemy trapped", closest_enemy)
        for rock in stones_positions:
            if math.dist(rock, closest_enemy)<=4 and rock[1]:
                r = position_below_stone(rock, stones_positions)
                if r!=None and r[1]<=21:
                    rocks_to_clear.append( r )
        if rocks_to_clear != []:
            return True, rocks_to_clear
        return True, 'dor'
    return False, None








def pooka_trapped(enemy_pos, mapa, rocks, trapped_frames):
    x,y = enemy_pos
    if x<0 or x>47 or y<0 or y>23:
        return None, 0
    temp = []
    position_to_clear = []
    if mapa[x][y] == 1:
        trapped_frames+=1
        #if trapped_frames > 10:
        #    print(trapped_frames)
        for r in rocks:
            if math.dist(enemy_pos, r) <= 4:
                temp.append(position_below_stone(r, rocks))
    for p in temp:
        if p != None:
            position_to_clear.append(p)
    if len(position_to_clear)>=1:
        return position_to_clear, trapped_frames
    return None, 0








#ver todas as posições que o DigDug pode ter em n frames
def agent_digdug_proximity_pos(pos, rocks):
    dor = 0
    x,y = pos
    zone = [(x,y), (x-1,y), (x+1,y), (x,y-1), (x,y+1)]
    for pos in zone:
        x,y = pos
        if  (x>=0 and x<48 and y>=0 and y<24 and pos not in rocks) or (x<=2 and y<=2):
            dor +=1
    return zone, dor       








#criar um caminho largo ao início para os inimigos com smart.Normal escaparem (só costumo perder antes de nível 20 por timeouts)
def clear_entrance_pathway(rocks, mapa, level, step):
    if level <= 4 or step > 1400:
        return set()
    zone = set()
    rocks_pos = set()
    for r in rocks:
        rocks_pos.add(tuple(r))

    for y in range(2, 18):
        if mapa[4][y] == 1 and agent_digdug_proximity_pos((4,y), rocks)[1]>=3:
            zone.add((4,y))
    for y in range(2, 20):
        if mapa[5][y] == 1 and agent_digdug_proximity_pos((5,y), rocks)[1]>=3:
            zone.add((5,y))
    for y in range(2, 24):
        if mapa[6][y] == 1 and agent_digdug_proximity_pos((6,y), rocks)[1]>=3:
            zone.add((6,y))
    for y in range(2, 24):
        if mapa[0][y] == 1 and agent_digdug_proximity_pos((0,y), rocks)[1]>=3:
            zone.add((0,y))

    return zone








def enemies_below_rocks(state, mapa, rocks):
    stones_to_clear = set()
    contaDor = 0
    for enemy in state['enemies']:
        a,b = enemy['pos']  
        if abs(state['digdug'][0] - a) <= 7 and (b<20 or (mapa_is_valid_position((a,b-1)) and mapa[a][b-1] != 1)):
            for r in rocks:
                contaDor+=1
                if contaDor >= 180:
                    return stones_to_clear
                x,y = r
                if abs(a-x)<=2 and b-y >= 3:
                    for p in range(y+1, b-2):
                        contaDor+=1
                        if mapa[x][p] == 1:
                            stones_to_clear.add((x,p))
                            if len(stones_to_clear) >= 7:
                                return stones_to_clear
    return stones_to_clear

          






def zoomed_enemy(prev_enemy_name, current_enemy_name, zoomed_frames):
    if prev_enemy_name == current_enemy_name:
        return zoomed_frames+1
    return 0
    







def agent_AI(state, oldstate, digdug_dir, mapa, stones_to_remove, stones_clear, last_pos, trapped_frames, prev_enemy_name, zoomed_frames):
    #ver se estamos em jogo e se o DigDug tem posição e vida e pode morrer
    if 'digdug' not in state:
        return '', digdug_dir
    digdug_pos = state['digdug']




    #calcular quais as posições proibídas:
    possible_death_positions, possible_stone_death_positions = all_enemies_current_and_possible_next_positions(state, mapa)




    #calcular posição do inimigo mais próximo, a distância a que está de nós, o seu nome, e quantos bichos estão na nossa iminência
    closest_enemy_pos, closest_enemy_dist, closest_enemy_name, closest_enemy_traverse, bichos_swarm = agent_dist_closest_enemy(state, 3)




    #atualizar mapa e tempo para limpar as pedras a remover
    x,y = digdug_pos
    if mapa[x][y] == 1:
        if (x,y) in stones_to_remove:
            stones_to_remove=set()
        mapa[x][y] = 0

    stones_clear -= 1
    if stones_clear <= 0:
        stones_clear = 0
        stones_to_remove = set()




    #ver número de movimentos imediatamente válidos
    rocks = [tuple(r['pos']) for r in state['rocks']]
    zone, valid_moves = agent_digdug_proximity_pos( digdug_pos, rocks )


    

    #verificar se estamos numa posição em que os bichos possam estar na próxima frame, e mover para a posição que leva a mais possibilidades de escape possível se estivermos
    if (digdug_pos in possible_death_positions) or (digdug_pos in possible_stone_death_positions) or ((len(bichos_swarm.keys())>=3 or (valid_moves<=4 and len(bichos_swarm.keys())>=2) or (valid_moves<=2)) and (state['step'])<=1200):
        key, digdug_dir = agent_flee(state, mapa, digdug_dir, possible_death_positions, possible_stone_death_positions)
        return key, digdug_dir, mapa, stones_to_remove, state, 'dor', stones_clear, digdug_pos, trapped_frames-1, closest_enemy_name, zoomed_frames
    



    #atualizar caminho à entrada para os Pookas normais poderem fugir
    entrance_pathway = clear_entrance_pathway(state['rocks'], mapa, state['level'], state['step'])




    #ver há quantas frames estamos a perseguir o mesmo tipo de bicho
    zoomed_frames = zoomed_enemy(prev_enemy_name, closest_enemy_name, zoomed_frames)
    



    #ver as possíveis jogadas que podemos fazer que não asseguram que não morremos assim que as façamos
    possibles_moves = agent_possible_moves(state)
    possible_death_keys = ''
    for action, value in possibles_moves.items():
        if (value in possible_death_positions) or (value in possible_stone_death_positions):
             possible_death_keys+=action

    


    #set das posições de perigo
    possible_death_positions_set=set()
    for p in possible_death_positions:
        possible_death_positions_set.add(tuple(p))
    for p in possible_stone_death_positions:
        possible_death_positions_set.add(tuple(p))





    #abordar os bichos, consoante a distância ao mais perto, se o bicho está preso ou não, se há stones para remover ou não, se estamos há muito tempo ocupados com este bicho ou não
    stones_to_remove, clear_time = stone_remover(state, digdug_pos, closest_enemy_pos, mapa, stones_to_remove, stones_clear, rocks)
 
    key, digdug_dir, dor, trapped_frames = agent_stalk(state, oldstate, digdug_pos, digdug_dir, possible_death_positions_set, closest_enemy_pos, closest_enemy_name, closest_enemy_traverse, stones_to_remove, mapa, last_pos, entrance_pathway, bichos_swarm, trapped_frames, zoomed_frames, True, possible_death_keys)
    if key in possible_death_keys and dor != True:
        key, digdug_dir = agent_random_move(state, digdug_dir, mapa)
    return key, digdug_dir, mapa, stones_to_remove, state, ' ', clear_time, digdug_pos, trapped_frames, closest_enemy_name, zoomed_frames        #os bichos muitas vezes matam-me logo assim que removo a parede. Remover parede apenas quando os bichos estão verdadeiramente presos (numa só posição), e preferir retirar a parede quando os bichos deixam de estar na posição para a qual estive a disparar em vão
      
