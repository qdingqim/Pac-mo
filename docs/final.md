---
layout: default
title: Final Report
---

# Final Report ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/timg.gif)


## Video!

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg)](https://www.youtube.com/watch?v=YOUTUBE_VIDEO_ID_HERE)


## Project Summary:

Project Pac-Mo is an AI agent that plays a modified version of the Pac-Man by Bandai Namco Games. The AI of Pac-Mo will be developed based on Minecraft Malmo. The player is named after 'Robot'. The goal of this game is to get the highest score from each stage, while the agent should avoid a monster in the closed map (two versions: easy map and hard map) that kills the player at once if contacted. The dots, which gives a score in the original game, will be replaced by the 'gold_ingot' in Minecraft.

The monster in Pac-Mo, unlike the original game, cannot be eaten by the player; it is controlled by another client and its ability to chase the player is driven finding the shortest path from each monster to the player for each movement of the player. To give a full perspective of the map, a client of a watcher is added as well. The input for the agent will be an information of visible grid cell, such as vertically or horizontally reachable cells from current cell not blocked by walls or monsters. Then the agent will determine its best direction to obtain more "gold_ingot" and not to be killed by the monsters.

The biggest challenge for surviving the pac-man using q_learning is the time dependency. Since the agent might visit the same cell several times in one episode, and once the q_value for the cell is updated(for example ,the agent encounter the monster), this cell would never be visited. However, if the q_value of one cell is updated several times in one episode, the q_table would not be accurate enough for the following episodes. Meanwhile, the monster is always following the shortest path to the player, which makes the monster smarter compared to normal zombie. Therefore some modification on Q_learning should be made(e.g. consistency check).

![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)   ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/easy_map.png)                                                 ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/hard_map.png)  


## Approaches:
The Pac-mo uses multi-agent Minecrafts. One for the monster, which implements the Dijkstra algorithm to chase the player, one for the player to perform reinforcement learning based on the Q_table to get the best reward which means maximum gold_ingot without death, and one for the observer which is placed above the map.

Compared to status report, There are a hard mode map and an easy mode map. Also as mentioned in the challenges part in status report, since the monster is using dijkstra algorithm which means its behaviour hard to predict, the Q_learning does not work perfectly well. To improve the Q_learning algorithm, the consistency check is implemented to help the q_learning update better. One more thing we improved is that we change the continuous movement to discrete movement for the player so that the movement is more accurate to fit the hard mode map. 

### Muti-Agent
The multi-agent is implemented by using MalmoPython.ClientPool. Also different Xml part is coded for different agent since the placement and game mode is different. The reason why we use Multi agents is that in this case the behavior of the monster is easier to implement Dijkstra's algorithm, which also makes monster more smarter and more difficult for AI to win the pac-man game! The perspective of a watcher is given by another client, which makes it easier to observe. However, too man clients indeed takes too much RAM and resources, which sometimes makes the turning of the agent delay.

![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)                                                          | The monster    | |The player| |The watcher|    
| :-------: |--- | :------:   |--- |  :--------:    |    
| Dijkstra        || Q-table |     |       |     
|![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/monster.png)          |![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg) ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg) |    ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/player.png)          | ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)  |      ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/watcher.png)         | 

### Dijkstra's Algorithm
<br>We are using Dijkstra's shortest path algorithm to calculate the monster's movement. For each step of movement, the algorithm calculates its next location from current cell in its shortest path; the algorithm __monster_action__ returns its turn ratio relative to the monster's current degree (turn). Hence, the monster is always chasing to the player with a half of speed of the player.

<div style="text-align:center"><img src ="https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/dij.png" /></div>

### Tabular Q-learning
<br>We are using Tabular Q-learning method for the player's (robot) movement. In the current map, there are __52 possible path cells__ (coal_block); each cell has four possible actions: __'north','south', 'east', 'west'__. Normally there are 2 possible paths in most time in this map which is shown below. The walls' q_value is set to -9999 to be excluded from possible actions. We set epsilon: 0.01, alpha = 0.6, gamma: 1, n: 2.

The following pictures depict the reward of the wall for each situation:
<br>![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/status_etc/status1.png)                                              ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/status_etc/status2.png)

Notice that the reward of the wall is -9,999; that score forces the player not to walk through the wall.

The following code is the __choose_action__ function in PacMo version 1.6.
```python
###  pseudocode for choosing action

```
Notice in the middle of the code, there is a statement that makes agent go to the same direction as its last direction from its last location __if and only if__ the last and the current q_value of the last direction for each cell is greater than or equal to zero. This mechanism forces the player to go straight in discovered paths. Otherwise, the player selects next direction based on the maximum value on the q_table. Since, the epsilon is relatively small, theoredically, 99% of the choose_action function instances are based on the above procedures. Similarly the turn ratio relative to the player's current degree (turn) is returned.

The following code is a part of updating q table function:
```python
#### q_table function
   G = gamma * value
   G += gamma ** n * q_table[curr_coord][direction][0]
   old_q = q_table[curr_coord][direction][0]
   q_table[curr_coord][direction][0] = old_q + alpha * (G - old_q)
```
<br>Notice that from __choose_action__ function and the function above, the q_table has both value ([0] th value) and its adjacent coordinates towards its current cell's relative direction. The coordinates are used to calculate the turn ratio of the player.

The reward of actions is set as if __wall__, __-9999__; if __monster__, __-1__; __if successful movement__ (from cell to cell), __+1__; if __gold__, __+1 (extra on top of the successful movement)__. The q_value is updated once the next cell chosen by the choose_action algorithm is performed. As more times q_value is updated, finally it leads to the best solution.

q_table example:
<br>![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)    ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/q_capture.PNG)                                                 ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/q_capture2.png) 

### Consistency Check
__- Force Going:__
The reason why we are using consistency check is to ensure the agent is not trapped by negative rewards so that the q value can be updated. Since if the agent meets a monster somewhere, there would be a negative q_value in that cell, which makes an obstacle for agent. However, there might be an another moment where monster is actually far away from this cell, while the agent is still afraid to cross the cell due to the negative q_value, which makes the agent kind of "stupid". We call it time dependency here.

Therefore we are detecting the distance between the monster and the player every movement. If the distance between the monster and the player is not the safe distance, then the agent turns around to avoid the monster; meanwhile the q_value got updated. However sometimes this q_value is not reliable because of time dependency. Therefore we are detecting the distance between players and monsters all the time: if agent is facing the monster, he turns around and q_value get updated; if the cell in front of the agent has negative value, while there actually is no monster in front of him, the agent still goes forward so that the q_value of the following cell's could be updated.

|![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/meet.png)|   ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/non_meet.png) |   ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/forcego.png)|

__- Avoiding the monster:__

At the same time, by detecting the distance between player and monster, the player tries to turn around before it was caught by the monster. This is because we do not want the mission start again and again. Because after the agent get the gold in the cell, there is no more reward when the second time agent get there. If the player dies, then the gold would be reset, which makes the q_value for the cell accumulate extreme high and makes q_table not accurate. Therefore avoiding players die can actually improve Q_learning in some extent.

<div style="text-align:center"><img src ="https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/avoid.png" /></div>

```python
#### pseudocode for consistency check

```
## Evaluation:

### Quantitative 


### Qualitative
__- Measurement:__
<br>Current evaluation process is based on the number of steps and the number of missions until the player (Robot) reaches to the solution. The term solution is not the best solution yet; in fact, finding the best solution is not trivial since the game have moving monster that is chasing after the player. __Hence, we decided to compare the number of missions until some solution for each game in the different versions.__ Current version(1.8) has a range of 1-5 missions to some solution; interestingly, most solutions had 163 turns (in easy mode map) until the end of the game (solution state).

__- Comparison between different versions__
<br>The following graph represents the number of missions until the player reaches the first solution (1.4 version: unrevised choosing function without going straight feature; 1.6: without consistency check)

![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/graph_final.png)

Notice that version 1.4 did not even reach to any solution during the test of more than 200 missions. However, version 1.6 was able to finish acquiring all twenty-seven 'gold_ingot' within 2-14 missions. After adding the consistency check as version 1.8, the performance is even better. It achieves the best solution within 1-5 missions. Hence, the __choose_action__ function revised in 1.6 and the __consistency check__ in 1.8 has better learning performance than the original version.

## References:
- __The original Pac-man game__:  <https://www.google.com/search?q=pacman&rlz=1C1CHZL_zh-CNUS736US736&oq=pacman&aqs=chrome..69i57j0j69i59l2j0l2.3004j0j8&sourceid=chrome&ie=UTF-8#clb=clb>
- __Q_learning Algorithm in Discussion__:  <https://github.com/MosheLichman/CS175-Discussions>
- __Malmo Minecraft setup__:  <https://github.com/Microsoft/malmo>
- __Multi Agent__:  <https://github.com/Microsoft/malmo/blob/master/Malmo/samples/Python_examples/multi_agent_test.py>

