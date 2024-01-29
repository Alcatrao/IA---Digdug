# --- My notes ---

# Grade: 20/20
The grading was done in conformity to the max and median scores of the class. Whoever had the best score, would receive top mark (20/20); those who had the median score, would get 16 (had previously been the mean, but everyone bar myself would have gotten a negative grade if that were still the case). We took a while to receive the grades (the teacher had to run the game 10 times for the agent of each student, and there were about 200 of us), but I knew this agent was special, and had little doubt it would perform the best.


# About the agent's algorithm
The agents objective vary in function of the level, the game step, the number of enemies immediately present, the presence of rocks neaby, and the proximity to the target to kill. I employed the A* search algorithm to find the next action to make at every step, for every goal I had, except one: the goal of keeping myself alive.

This is where my agent differed from everyone else's I think, since we were encouraged to use informed search techniques to approach our enemies, but had think for ourselves for every other goal beyond that. I initially figured the best way to keep myself alive when threatened, would be take a an action/move that would guarantee my survival in the next frame, if there was such a move. 

However, many times I would be left with an ample choice of moves to make that would result in me being alive in the next frame. Which one should I choose? Which one would you chose?

I moved from having that move being chosen randomly (keeping myself alive in the next frame was. at the beggining, good enough), to develop a recursive function that for each of the given movement options, would determine the number of frames I would be guaranteed to survive if I chose that move. It would check every possible action that would not result in me finding myself in collision with any enemy (which would result in death), and from each of those actions, it would compulsively do the same, until no more safe movements could be found. 

This solution can perhaps remind one of algorithms like minimax and expectimax, but it is actually very different; it's way faster, and it can provide movement choices better than these algorithms can do unless they have a pitch perfect evaluating funcion for determining the desirability of an action (however, it seems many are based on calculating the distance to the enemies, which can leave out certain trapping attemps that the same could do).

This was hard fueled by my OCD, which is why the code may look like incomprehensible alien gibberish at some points. The logic is all there though. Overall, apart from the grade, I think that on this project, I did very good. It was painful, but good.




# --- Teacher notes and installation guide ---

# ia-digdug
DigDug clone for AI teaching


## How to install

Make sure you are running Python 3.11.

`$ pip install -r requirements.txt`

*Tip: you might want to create a virtualenv first*

## How to play

open 3 terminals:

`$ python3 server.py`

`$ python3 viewer.py`

`$ python3 client.py`

to play using the sample client make sure the client pygame hidden window has focus

### Keys

Directions: arrows

*A*: 'a' - pump enemies

## Debug Installation

Make sure pygame is properly installed:

python -m pygame.examples.aliens

# Tested on:
- MacOS 13.6

