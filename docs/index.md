---
layout: default
title:  Home
---

Pacmo! ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/timg.gif) 
=========

Summary
---------

Project Pac-Mo is an AI agent that plays a modified version of the Pac-Man by Bandai Namco Games. The AI of Pac-Mo will be developed based on Minecraft Malmo. The goal of this game is to get the highest score from each stage, while the agent should avoid a monster in the closed map(17 by 17 for now) that kills the player at once if contacted. The dots, which gives a score in the original game, will be replaced by "the gold_ingot" in Minecraft.

The monster in Pac-Mo, unlike the original game, cannot be eaten by the player; it is controlled by another client and its ability to chase the player is to find the shortest path from each monster to the player for each movement of the player. To give a full perspective of the map, a client of a watcher is added as well. The input for the agent will be an information of visible grid cell, such as vertically or horizontally reachable cells from current cell not blocked by walls or monsters. Then the agent will determine its best direction to obtain more "gold_ingot" and not to be killed by the monsters.

<div style="text-align:center"><img src ="https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/intro.png" /></div>

Algorithm adapted
---------
- Dijkrstra for the monster's action
- Q-Learning for agent's reinforcement learning

![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)                                                          | The monster    | |The player| |The watcher|    
| :-------: |--- | :------:   |--- |  :--------:    |    
| Dijkstra        || Q-table |     |       |     
|![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/monster.png)          |![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg) ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg) |    ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/player.png)          | ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/blank.jpg)  |      ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/watcher.png)         | 



___Check out the original game! :___ [click](https://www.google.com/search?q=pac+man&rlz=1C1CHZL_zh-CNUS736US736&oq=pac+man&aqs=chrome..69i57j0l5.2287j0j9&sourceid=chrome&ie=UTF-8#clb=clb)

___See our game here!:___

__Introduction:__
<br>[![Watch the video](https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/introv.png)](https://youtu.be/5p-iBizMFhM)
<br><br>__Current progress:__
<br>[![Watch the video](https://github.com/qdingqim/Pac-mo/raw/master/docs/status_etc/pv.png)](https://youtu.be/xJiR9AwN5yE)
<br><br>[Latest Source_Code:checkout!](https://github.com/qdingqim/Pac-mo/blob/master/pacmo1_6.py)
[Old version Source_Code:checkout!](https://github.com/qdingqim/Pac-mo)
