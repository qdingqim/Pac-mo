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

The biggest chanllenge for surviving the pac-man using q_learning is the time dependency. Since the agent might visit the same cell several times in one episode, and once the q_value for the cell is updated(for example ,the agent encounter the monster), this cell would never be visited. However, if the q_value of one cell is updated several times in one episode, the q_table would not be accurate enough for the following episodes. Meanwhile, the monster is always following the shortest path to the player, which makes the monster smarter compared to normal zombie. Therefore some modification on Q_learning should be made(e.g. consistency check).

![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)   ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/easy_map.png)                                                 ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/final_deco/hard_map.png)  


## Approaches:

### Muti-Agent
<br> The multi-agent is implemented by using MalmoPython.ClientPool. Also different Xml part is coded for different agent since the placement and game mode is different. The reason why we use Multi agents is that in this case the behavior of the monster is easier to implement Dijkstra's algorithm, which also makes monster more smarter and more difficult for AI to win the pac-man game! The perspective of a watcher is given by another client, which makes it easier to observe. However, too man clients indeed takes too much RAM and resources, which sometimes makes the turning of the agent delay.

![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)                                                          | The monster    | |The player| |The watcher|    
| :-------: |--- | :------:   |--- |  :--------:    |    
| Dijkstra        || Q-table |     |       |     
|![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/monster.png)          |![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg) ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg) |    ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/player.png)          | ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)  |      ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/watcher.png)         | 

### Dijkstra's Algorithm
<br>We are using Dijkstra's shortest path algorithm to calculate the monster's movement. For each step of movement, the algorithm calculates its next location from current cell in its shortest path; the algorithm __monster_action__ returns its turn ratio relative to the monster's current degree (turn). Hence, the monster is always chasing to the player with a half of speed of the player.

### Tabular Q-learning

### Consistency Check


## Evaluation:


## References:
- __The original Pac-man game__:  <https://www.google.com/search?q=pacman&rlz=1C1CHZL_zh-CNUS736US736&oq=pacman&aqs=chrome..69i57j0j69i59l2j0l2.3004j0j8&sourceid=chrome&ie=UTF-8#clb=clb>
- __Q_learning Algorithm in Discussion__:  <https://github.com/MosheLichman/CS175-Discussions>
- __Malmo Minecraft setup__:  <https://github.com/Microsoft/malmo>
- __Multi Agent__:  <https://github.com/Microsoft/malmo/blob/master/Malmo/samples/Python_examples/multi_agent_test.py>

