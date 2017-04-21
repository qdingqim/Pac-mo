---
layout: default
title: Proposal
---
## Project Pac-Mo

### Summary of the Project


Project Pac-Mo is an AI agent that plays a modified version of the Pac-Man by Bandai
Namco Games. The AI of Pac-Mo will be developed based on Minecraft Malmo. The goal of this game is to get the highest score from each stage, while the agent should avoid four monsters in the closed map that kills the player at once if contacted. The dots, which gives a score in the original game, will be replaced by "the sword" in Minecraft. The monsters in Pac-Mo, unlike the original game, cannot be eaten by the player; its ability to chase the player are varied by "the Level" of the game, such as find the shortest path from each monster to the player for each movement of the player. The input for the agent will be an information of visible grid cell and it will determine where to go to get more swords or not to be killed by the monsters. The outcome of the input will be the direction of the movement of the agent.

### AI/ML Algorithms
We are planning to use reinforcement learning with neural function approximator for the solving agent, and Dijkstra's algorithm for the monsters in the game.

### Evaluation Plan
The metrics of the project is the scores which are calculated by the dots( the sword in the game). At the start of the game, the agent follows a fixed path list to go randomly. As the agent dies and learns, it will gradually know some certain point and path it cannot go. There is a time limit for the game. The final score is calculated once the agent is killed or the time runs out. 

With experiments, the agent will find a optimum route to get all the swords without being killed by monsters. The best route is made by building the path list in the algorithm. The sanity case will be that the agent gets all the sword which means the highest score within the least time without dying.

### Appointment with the Instructor
(reserved) May 1st, 2017 at 2:30pm
