---
layout: default
title: Status
---

## Project Summary: 
Project Pac-Mo is an AI agent that plays a modified version of the Pac-Man by Bandai Namco Games. The AI of Pac-Mo will be developed based on Minecraft Malmo. The player is named after 'Robot'. The goal of this game is to get the highest score from each stage, while the agent should avoid a monster in the closed map(14 by 14 for now) that kills the player at once if contacted. The dots, which gives a score in the original game, will be replaced by the 'gold_ingot' in Minecraft. 

The monster in Pac-Mo, unlike the original game, cannot be eaten by the player; it is controlled by another client and its ability to chase the player is driven finding the shortest path from each monster to the player for each movement of the player. To give a full perspective of the map, a client of a watcher is added as well. The input for the agent will be an information of visible grid cell, such as vertically or horizontally reachable cells from current cell not blocked by walls or monsters. Then the agent will determine its best direction to obtain more "gold_ingot" and not to be killed by the monsters.


## Approach:
The Pac-mo is realized by multi-agent. One for the monster which implements the Dijkstra algorithm to chase the player, one for the player to perform reinforcement learning based on the Q_table to get the best reward which means maximum gold without dying, and the other one is for the watcher which is placed above the map.

__- Multi-Agent:__
<br> The multi-agent is implemented by using MalmoPython.ClientPool. Also different Xml part is coded for different agent since the placement and game mode is different. The reason why we use Multi agents is that in this case the behavior of the monster is easier to control. Also the perspective of a watcher is given.

__- Dijkstra's Algorithm:__
<br>We are using Dijkstra's shortest path algorithm to calculate the monster's movement. For each step of movement, the algorithm calculates its next location from current cell in its shortest path; the algorithm __moster_action__ returns its turn ratio relative to the monster's current degree (turn). Hence, the monster is always chasing to the player with a half of speed of the player.
   
__- Tabular Q-learning:__
<br>We are using Tabular Q-learing method for the player's (robot) movement. In the current map, there are __52 possible path cells__ (coal_block); each cell has four possible states: __'north','south', 'east', 'west'__. We set epsilon: 0.01, alpha = 0.6, gamma: 1, n: 2.
The following code is the __choose_action__ function in PacMo version 1.6.
```python
def choose_action(curr_coord, grid, last):
   possible_actions = get_possible_action(get_block_index(curr_coord), grid)
   if curr_coord not in q_table:
      q_table[curr_coord] = {}
    
    for direction, coord in possible_actions:
      if direction not in q_table[curr_coord]:
         q_table[curr_coord][direction] = [0, coord]
    
    tol = 0.0001    
    rnd = random.random()    
    if last[1] != "" and last[1] in q_table[curr_coord]:        
      if q_table[last[0]][last[1]][0] >= 0 and q_table[curr_coord][last[1]][0] >= 0:            
         for i in range(len(possible_actions)):                
            if possible_actions[i][0] == last[1]:                    
               return possible_actions[i]
    
    if rnd < epsilon:        
      a = random.randint(0, len(possible_actions) - 1)
    else:        
      m = max([x[0] for x in q_table[curr_coord].values()])        
      l = list()        
      for direction, coord in possible_actions:            
         for value, coordinate in q_table[curr_coord].values():                
            if abs(value-m) <= tol:                    
               l.append((direction, coord))                
               
      return l[random.randint(0, len(l)-1)]
      
    return possible_actions[a]
```
Notice in the middle of the code, there is a statement that makes agent go to the same direction as its last direction from its last location __if and only if__ the last and the current q_value of the last direction for each cell is greater than or equal to zero. This mechanism forces the player to go straight in discovered paths. Otherwise, the player selects next direction based on the maximum value on the q_table. Since, the epsilon is relatively small, theoredically, 99% of the choose_action function instances are based on the above procedures.

## Evaluation:
__- Measurement:__
<br>Current evaluation process is based on the number of steps and the number of missions until the player (Robot) reaches to the solution. The term solution is not the best solution yet; in fact, finding the best solution is not trivial since the game have moving monster that is chasing after the player. __Hence, we decided to compare the number of missions until some solution for each game in the current version (1.6).__ Current version has a range of 2-14 missions to some solution; interestingly, most solutions had 163 turns until the end of the game (solution state).

__- Comparison by version: 1.6 vs. 1.4__
<br>The following graph represents the number of missions until the player reaches some solution:
<br>![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/status_etc/graph.png)
<br> Notice that version 1.4 did not even reach to any solution during the test of more than 200 missions. However, version 1.6 was able to finish acquiring all twenty-seven 'gold_ingot' within 2-14 missions. Hence, the __choose_action__ function revised in 1.6 has better path searching performance than the function in version 1.4

## Remaining Goals and Challenges:
For the challenge, it is mainly about how well the q_table would work. And except that, the remaining goal is to make the map and environment more complicated.

__- Improving Q-learing:__
  
  We are trying to improve cases, where the q-values must be updated. Current version (1.6) Q-values are accumulated based on the success of each movement. For example, if the player succeed moving to the next cell chosen by the choose_action algorithm, the Q-value is updated with reward 1, in which its direction from the previous cell is updated. The player accumulates another 1 reward from picking up the "gold_ingot" in the game. The Q-values are decreased if and only if either the player detects the wall or the player is killed (contacted) to the monster. 

  Since for most cases, the Q-table are implemented in a static enviroment.(eg lava, fixed item). However for our game, the monster follows Dijkstra to the agent which means the pattern of its movement is somehow unpredictable. In this case, q-table doesn’t work perfectly well. If we can find the only one solution to achieve the best reward without dying, the Q_learing would work perfectly well. Our next goal is to find diverse cases of the q-value update instances and improve the accuracy of the Q-table or to modify the algorithm based on current q-learning to help the agent learn.

__- Make more possible paths in the map:__
  
  Current version (1.6) has one square shape map. We are going to add more paths in between maps; test out if the player can finish the game as Q-table is accumulated.For example, we use squared with cross inside instead of a simple square. 
  
__- More monsters inside the map:__

  Current version only has one monster agent in the map, which means the agent is less likely to die. We will try to add 1 more or 2 more monsters to see if the agent still performs good. One drawbacks of more monsters is that it is taking more resources from computer, since 3 agents are already taking almost 8G ram. This memory usage problem is probably not going to be solved.
      
   
