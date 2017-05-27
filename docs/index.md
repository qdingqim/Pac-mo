---
layout: default
title:  Home
---

Pacmo! ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/timg.gif) 
=========

Summary
---------

Project Pac-Mo is an AI agent that plays a modified version of the Pac-Man by Bandai Namco Games.The AI of Pac-Mo will be developed based on Minecraft Malmo. The goal of this game is to get the highest score from each stage, while the agent should avoid four monsters in the closed map that kills the player at once if contacted. The dots, which gives a score in the original game, will be replaced by "gold_ingot" in Minecraft. 

The monsters in Pac-Mo, unlike the original game, cannot be eaten by the player; its ability to chase the player are varied by "the Level" of the game, such as finding the shortest path from each monster to the player for each movement of the player. The input for the agent will be an information of visible grid cell, such as vertically or horizontally reachable cells from current cell not blocked by walls or monsters. Then the agent will determine its best direction to obtain more swords or not to be killed by the monsters.

<img src ="https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/intro.png" /><img src ="https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/q_table.png" />  

Algorithm adapted
---------
- Dijkrstra for the monster's action
- Q-Learning for agent's reinforcement learning

| The monster     |       |  The player      |       |   The watcher|    
| :--------------:| ------|:---------------: |-----  |  :----------------:    |    
| Dijkstra        |       |   Q-table        |       |                   |     
|![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/monster.png)    |  |    ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs/decos/player.png)   |  |   ![Alt Text](https://github.com/qdingqim/Pac-mo/raw/master/docs//decos/watcher.png)    | 

_Check out the original game! :_ [click](https://www.google.com/search?q=pac+man&rlz=1C1CHZL_zh-CNUS736US736&oq=pac+man&aqs=chrome..69i57j0l5.2287j0j9&sourceid=chrome&ie=UTF-8#clb=clb)

_See our game here!:_


[Latest Source_Code:checkout!](https://github.com/qdingqim/Pac-mo/blob/master/pacmo1_6.py)

[Old version Source_Code:checkout!](https://github.com/qdingqim/Pac-mo)
