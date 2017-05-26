---
layout: default
title:  Home
---

# Pac-mo in Minecraft 
:gem::gem:__Summery__:gem::gem:

Project Pac-Mo is an AI agent that plays a modified version of the Pac-Man by Bandai Namco Games.The AI of Pac-Mo will be developed based on Minecraft Malmo. The goal of this game is to get the highest score from each stage, while the agent should avoid four monsters in the closed map that kills the player at once if contacted. The dots, which gives a score in the original game, will be replaced by "the sword" in Minecraft. 

The monsters in Pac-Mo, unlike the original game, cannot be eaten by the player; its ability to chase the player are varied by "the Level" of the game, such as finding the shortest path from each monster to the player for each movement of the player. The input for the agent will be an information of visible grid cell, such as vertically or horizontally reachable cells from current cell not blocked by walls or monsters. Then the agent will determine its best direction to obtain more swords or not to be killed by the monsters.

:gem::gem:__Algorithm adapted__:gem::gem:
- Dijkrstra for the monster's action
- Q-Learning for agent's reinforcement learning

[Source_Code](../../pacmo1.5.py)


