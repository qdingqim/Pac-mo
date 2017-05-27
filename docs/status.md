---
layout: default
title: Status
---

## Project Summary: 
<br>Project Pac-Mo is an AI agent that plays a modified version of the Pac-Man by Bandai Namco Games. The AI of Pac-Mo will be developed based on Minecraft Malmo. The goal of this game is to get the highest score from each stage, while the agent should avoid a monster in the closed map(14 by 14 for now) that kills the player at once if contacted. The dots, which gives a score in the original game, will be replaced by "the gold_ingot" in Minecraft. 
<br>The monster in Pac-Mo, unlike the original game, cannot be eaten by the player; it is controlled by another client and its ability to chase the player is to find the shortest path from each monster to the player for each movement of the player. To give a full perspective of the map, a client of a watcher is added as well. The input for the agent will be an information of visible grid cell, such as vertically or horizontally reachable cells from current cell not blocked by walls or monsters. Then the agent will determine its best direction to obtain more "gold_ingot" and not to be killed by the monsters.


## Approach:
1. Dijkstra's Algorithm:
<br>We are using Dijkstra's shortest path algorithm to calculate the monster's movement. For each step of movement, the algorithm calculates its next location from current cell in its shortest path; the algorithm moster_action returns its turn ratio relative to the monster's current degree (turn). Hence, the monster is always chasing to the player with a half of speed that the player walk.
   
2. Tabular Q-learning:
<br>We are using Tabular Q-learing method for the player's (robot) movement.

## Evaluation:
<br>An important aspect of your project, as we mentioned in the beginning, is evaluating your project. Be clear and precise about describing the evaluation setup, for both quantitative and qualitative results. Present the results to convince the reader that you have a working implementation. Use plots, charts,tables, screenshots, figures, etc. as needed. I expect you will need at least a few paragraphs to describe eachtype of evaluation that you perform.

## Remaining Goals and Challenges:
1. Improving Q-learing:
<br>We are trying to improve cases, where the q-values must be updated. Current version (1.6) Q-values are accumulated based on the success of each movement. For example, if the player succeed moving to the next cell chosen by the choose_action algorithm, the Q-value is updated with reward 1, in which its direction from the previous cell is updated. The player accumulates another 1 reward from picking up the "gold_ingot" in the game. The Q-values are decreased if and only if either the player detects the wall or the player is killed (contacted) to the monster. 
<br>Since for most cases, the Q-table are implemented in a static enviroment.(eg lava, fixed item). However for our game, the monster follows Dijkstra to the agent which means the pattern of its movement is somehow unpredictable. In this case, q-table doesn't work perfectly well. Our next goal is to find diverse cases of the q-value update instances and improve the accuracy of the Q-table or to find a better algorithm to help the agent learn.
	
2. Make more possible paths in the map:		
<br>Current version (1.6) has one square shape map. We are going to add more paths in between maps; test out if the player can finish the game as Q-table is accumulated.
