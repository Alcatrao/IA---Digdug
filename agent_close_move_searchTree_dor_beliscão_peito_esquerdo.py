from consts import Direction
import math

from abc import ABC, abstractmethod

#state deve ter a posição do DigDug, e o move que o meteu aí (exceto no primeiro estado de todos)
def agent_shooting_conditions(digdug_pos, digdug_dir, close_enemy_pos, closest_enemy_name):
    x,y = digdug_pos
    shooting_range_left = [ [x-2,y], [x-3,y]]
    shooting_range_right = [ [x+2,y], [x+3,y]]
    shooting_range_up = [ [x,y-2], [x,y-3]]
    shooting_range_down = [ [x,y+2], [x,y+3]]

    if digdug_dir==Direction.WEST and closest_enemy_name != 'Fygar':
        for potential_target in shooting_range_left:      
            if potential_target in close_enemy_pos:
                return True
    elif digdug_dir==Direction.EAST and closest_enemy_name != 'Fygar':
        for potential_target in shooting_range_right:
            if potential_target in close_enemy_pos:
                return True
    elif digdug_dir==Direction.NORTH:
        for potential_target in shooting_range_up:
            if potential_target in close_enemy_pos:
                return True
    elif digdug_dir==Direction.SOUTH:
        for potential_target in shooting_range_down:
            if potential_target in close_enemy_pos:
                return True
    return False




def smallest(lis):
    if len(lis)==1:
        return lis[0]
            
    meio = len(lis)//2
    metade1 = smallest(lis[:meio])
    metade2 = smallest(lis[meio:])

    if metade1 <= metade2:
        return metade1
    return metade2




def agent_digdug_proximity_pos(pos, rocks):
    dor = 0
    x,y = pos
    zone = [(x,y), (x-1,y), (x+1,y), (x,y-1), (x,y+1)]
    for pos in zone:
        x,y = pos
        if  (x>=0 and x<48 and y>=0 and y<24 and pos not in rocks):
            dor +=1
    return zone, dor 




def mapa_is_valid_position( pos ):
    x,y = pos
    if x>=0 and x<48 and y>=0 and y<24:
        return True
    return False




# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain:

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    def actions(self, state):
        x,y = state['digdug']
        a,b = state['closest_enemy']

        dicio = set()
        bicho = set()
        fygar = set()

        bicho.add((a,b))
        bicho.add((a-1,b))
        bicho.add((a+1,b))
        bicho.add((a,b-1))
        bicho.add((a,b+1))

        if state['closest_enemy_name'] == 'Fygar':
            fygar.add((a-1, b))
            fygar.add((a-2, b))
            fygar.add((a-3, b))
            fygar.add((a-4, b))
            fygar.add((a+1, b))
            fygar.add((a+2, b))
            fygar.add((a+3, b))
            fygar.add((a+4, b))


        if (x>0) and (math.dist((x-1,y), state['closest_enemy'])<=8) and ((x-1,y) not in fygar) and ((x-1,y) not in bicho) and ((x-1,y) not in state['rocks']) and ((x-1,y) not in state['danger_zones']):
            dicio.add(('a', (-1,0), Direction.WEST))
        if (x<47) and (math.dist((x+1,y), state['closest_enemy'])<=8) and ((x+1,y) not in fygar) and ((x+1,y) not in bicho) and ((x+1,y) not in state['rocks']) and ((x+1,y) not in state['danger_zones']):
            dicio.add(('d', (1,0), Direction.EAST))
        if (y>0) and (math.dist((x,y-1), state['closest_enemy'])<=8) and ((x,y-1) not in fygar) and ((x,y-1) not in bicho) and ((x,y-1) not in state['rocks']) and ((x,y-1) not in state['danger_zones']):
            dicio.add(('w', (0,-1), Direction.NORTH))
        if (y<23) and (math.dist((x,y+1), state['closest_enemy'])<=8) and ((x,y+1) not in fygar) and ((x,y+1) not in bicho) and ((x,y+1) not in state['rocks']) and ((x,y+1) not in state['danger_zones']):
            dicio.add(('s', (0,1), Direction.SOUTH))

        return dicio



    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        x,y = state['digdug']
        a,b = action[1]
        new_pos = (x+a,y+b)
        new_dir = action[2]
        new_key = action[0]
        new_state = {'digdug': new_pos, 'dir': new_dir, 'key': new_key, 'enemies': state['enemies'], 'closest_enemy': state['closest_enemy'], 'closest_enemy_name': state['closest_enemy_name'], 'rocks': state['rocks'], 'mapa': state['mapa'], 'danger_zones': state['danger_zones'], 'state_info': state['state_info'], 'bichos_swarm': state['bichos_swarm'], 'last_pos': (-1,-1) }
        return new_state
        

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal):
        if agent_shooting_conditions(state['digdug'], state['dir'], state['enemies'], state['closest_enemy_name']):
            return True
        return False

    # custo de uma accao num estado
    def cost(self, state, action):
        x,y = state['digdug']
        if state['mapa'][x][y] == 1:
            return 0.5            #para incentivar a criação de túneis (cria mais situações perigosas para mim, mas desbloqueia muitas situações de Fygares normais e causa a queda de mais pedras)
        return 1
              

    # custo estimado de chegar de um estado a outro
    def heuristic(self, state, goal):
        x,y = state['digdug']
        a,b = state['closest_enemy']

        default = math.dist((x,y), (a,b))+7
        dist_up = default
        dist_down = default
        dist_left = default
        dist_right = default


        if (a,b-3) not in state['rocks'] and mapa_is_valid_position((a,b-3)):
            dist_up = math.dist((x,y), (a,b-3))
        elif (a,b-2) not in state['rocks'] and mapa_is_valid_position((a,b-2)):
            dist_up = math.dist((x,y), (a,b-2))


        if (a,b+3) not in state['rocks'] and mapa_is_valid_position((a,b+3)):
            dist_down = math.dist((x,y), (a,b+3))
        elif (a,b+2) not in state['rocks'] and mapa_is_valid_position((a,b+2)):
            dist_down = math.dist((x,y), (a,b+2))
            



        if state['closest_enemy_name'] == 'Fygar':
            return smallest([dist_up, dist_down, default])
        



        if (a-3,b) not in state['rocks'] and mapa_is_valid_position((a-3,b)):
            dist_left = math.dist((x,y), (a-3,b))
        elif (a-2,b+1) not in state['rocks'] and mapa_is_valid_position((a-2,b+1)):
            dist_left = math.dist((x,y), (a-2,b+1))


        if (a+3,b) not in state['rocks'] and mapa_is_valid_position((a+3,b)):
            dist_right = math.dist((x,y), (a+3,b))
        elif (a+2,b+1) not in state['rocks'] and mapa_is_valid_position((a+2,b+1)):
            dist_right = math.dist((x,y), (a+2,b+1))

        if state['state_info']['step'] <= 1400 and state['state_info']['step']>=20:
            dist_left = 0.7 * dist_left


        return smallest([dist_up, dist_down, dist_left, dist_right, default])

        

        
        
    













class SearchDomain_Stone_Remover:

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    def actions(self, state):
        x,y = state['digdug']
    
        dicio = set()
        bicho = set()
        fygar = set()

        for enemy in state['enemies']:
            a,b = enemy['pos']
            bicho.add((a,b))
            bicho.add((a-1,b))
            bicho.add((a+1,b))
            bicho.add((a,b-1))
            bicho.add((a,b+1))
            if enemy['name'] == 'Fygar':
                fygar.add((a-1, b))
                fygar.add((a-2, b))
                fygar.add((a-3, b))
                fygar.add((a-4, b))
                fygar.add((a+1, b))
                fygar.add((a+2, b))
                fygar.add((a+3, b))
                fygar.add((a+4, b))

        if (y>0 and (x,y-1) not in state['rocks']) and ((x,y-1) not in bicho) and ((x,y-1) not in fygar) and ((x,y-1) != state['last_pos']) and ((x,y-1) not in state['danger_zones']):
            dicio.add(('w', (0,-1), Direction.NORTH))
        if (y<23 and (x,y+1) not in state['rocks']) and ((x,y+1) not in bicho) and ((x,y+1) not in fygar) and ((x,y+1) != state['last_pos']) and ((x,y+1) not in state['danger_zones']):
            dicio.add(('s', (0,1), Direction.SOUTH)) 
        if (x>0 and (x-1,y) not in state['rocks'])  and ((x-1,y) not in bicho) and ((x-1,y) not in fygar) and ((x-1,y) != state['last_pos']) and ((x-1,y) not in state['danger_zones']):
            dicio.add(('a', (-1,0), Direction.WEST))
        if (x<47 and (x+1,y) not in state['rocks'])  and ((x+1,y) not in bicho) and ((x+1,y) not in fygar) and ((x+1,y) != state['last_pos']) and ((x+1,y) not in state['danger_zones']):
            dicio.add(('d', (1,0), Direction.EAST))

        return dicio



    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        x,y = state['digdug']
        a,b = action[1]
        new_pos = (x+a,y+b)
        new_dir = action[2]
        new_key = action[0]
        new_state = {'digdug': new_pos, 'dir': new_dir, 'key': new_key, 'rocks': state['rocks'], 'enemies': state['enemies'], 'last_pos': state['last_pos'], 'mapa': state['mapa'], 'danger_zones': state['danger_zones'], 'bichos_swarm': state['bichos_swarm']}
        return new_state
        

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal):
        if state['digdug'] in goal:
            return True
        return False

    # custo de uma accao num estado
    def cost(self, state, action):
        x,y = state['digdug']
        if state['mapa'][x][y] == 1:
            return 0.5            #para incentivar a criação de túneis (cria mais situações perigosas para mim, mas desbloqueia muitas situações de Fygares normais e causa a queda de mais pedras)
        return 1

    # custo estimado de chegar de um estado a outro
    def heuristic(self, state, goal):
        x,y = state['digdug']
        dist_shortest = 100
        for stone in goal:
            dist = math.dist((x,y), stone)
            if dist < dist_shortest:
                dist_shortest = dist
        return dist_shortest




















class SearchDomain_Stalk:

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    def actions(self, state):
        x,y = state['digdug']
        dicio = set()
    
        if (y>0 and (x,y-1) not in state['rocks']) and ((x,y-1) != state['last_pos']):
            dicio.add(('w', (0,-1), Direction.NORTH))
        if (y<23 and (x,y+1) not in state['rocks']) and ((x,y+1) != state['last_pos']):
            dicio.add(('s', (0,1), Direction.SOUTH)) 
        if (x>0 and (x-1,y) not in state['rocks'])  and ((x-1,y) != state['last_pos']):
            dicio.add(('a', (-1,0), Direction.WEST))
        if (x<47 and (x+1,y) not in state['rocks']) and ((x+1,y) != state['last_pos']):
            dicio.add(('d', (1,0), Direction.EAST))
        return dicio


    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        x,y = state['digdug']
        a,b = action[1]
        new_pos = (x+a,y+b)
        new_dir = action[2]
        new_key = action[0]
        new_state = {'digdug': new_pos, 'dir': new_dir, 'key': new_key, 'rocks': state['rocks'], 'last_pos': state['last_pos'], 'mapa': state['mapa'], 'bichos_swarm': state['bichos_swarm']}
        return new_state
        

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal):
        if state['digdug'] == goal:
            return True
        return False

    # custo de uma accao num estado
    def cost(self, state, action):
        x,y = state['digdug']
        if state['mapa'][x][y] == 1:
            return 0.5            #para incentivar a criação de túneis (cria mais situações perigosas para mim, mas desbloqueia muitas situações de Fygares normais e causa a queda de mais pedras)
        return 1
        

    # custo estimado de chegar de um estado a outro
    def heuristic(self, state, goal):
        x,y = state['digdug']
        return math.dist((x,y), goal)
    










class SearchDomain_ClearEntrance:

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    def actions(self, state):
        x,y = state['digdug']
        dicio = set()
    
        if (y>0 and (x,y-1) not in state['rocks']) and ((x,y-1) != state['last_pos']):
            dicio.add(('w', (0,-1), Direction.NORTH))
        if (y<23 and (x,y+1) not in state['rocks']) and ((x,y+1) != state['last_pos']):
            dicio.add(('s', (0,1), Direction.SOUTH)) 
        if (x>0 and (x-1,y) not in state['rocks'])  and ((x-1,y) != state['last_pos']):
            dicio.add(('a', (-1,0), Direction.WEST))
        if (x<47 and (x+1,y) not in state['rocks']) and ((x+1,y) != state['last_pos']):
            dicio.add(('d', (1,0), Direction.EAST))
        return dicio


    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        x,y = state['digdug']
        a,b = action[1]
        new_pos = (x+a,y+b)
        new_dir = action[2]
        new_key = action[0]
        new_state = {'digdug': new_pos, 'dir': new_dir, 'key': new_key, 'rocks': state['rocks'], 'last_pos': state['last_pos'], 'bichos_swarm': state['bichos_swarm']}
        return new_state
        

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal):
        if state['digdug'] in goal:
            return True
        return False

    # custo de uma accao num estado
    def cost(self, state, action):
        custo = 1
        dist_agora = 0
        dist_prev = 0
        for bicho in state['bichos_swarm'].keys():
            a,b = bicho
            dist_agora += math.dist(state['digdug'], (a,b))
            dist_prev += math.dist(state['last_pos'], (a,b))

        if dist_agora > dist_prev:
            custo -= 0.1
        return custo
            


    # custo estimado de chegar de um estado a outro
    def heuristic(self, state, goal):
        x,y = state['digdug']
        dist_shortest = 100
        for stone in goal:
            dist = math.dist((x,y), stone)
            if dist < dist_shortest:
                dist_shortest = dist
        return dist_shortest












        



# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent): 
        self.state = state
        self.parent = parent
        self.cost = 0
        self.heuristic = 0
        self.eval = 0
    def __str__(self):
        return "no(" + str(self.state) + ")"
    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self,problem, limit, strategy='A*'): 
        self.problem = problem
        root = SearchNode(problem.initial, None)
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.non_terminals = 0
        self.expanded_nodes = 0
        self.limit = limit

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)

    # procurar a solucao
    def search(self):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            self.expanded_nodes += 1
            if self.problem.goal_test(node.state) or self.expanded_nodes >= self.limit:
                self.solution = node
                self.terminals = len(self.open_nodes)+1
                return self.get_path(node)
            self.non_terminals += 1
            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                if newstate not in self.get_path(node):
                    newnode = SearchNode(newstate,node)
                    newnode.cost = node.cost + self.problem.domain.cost( newnode.state, (newnode.state, newnode.parent.state) )    
                    newnode.heuristic = self.problem.domain.heuristic ( newnode.state, self.problem.goal )                          
                    newnode.eval = newnode.cost + newnode.heuristic
                    lnewnodes.append(newnode)
            self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'A*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes = sorted(self.open_nodes, key=lambda node : node.eval) 
        elif self.strategy == 'gulosa':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes = sorted(self.open_nodes, key=lambda node : node.heuristic) 


