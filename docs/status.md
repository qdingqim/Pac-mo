---
layout: default
title: Status
---

## Project Summary: 
Since things may have changed since proposal (even if they haven’t), write a shortparagraph summarizing the goals of the project (updated/improved version from the proposal).

## Approach:
1. Dijkstra's Algorithm
   We are using Dijkstra's shortest path algorithm to calculate the monster's movement. For each step of movement, the algorithm              calculates its next location from current cell in its shortest path; the algorithm moster_action returns its turn ratio relative to      the monster's current degree (turn). Hence, the monster is always chasing to the player with a half of speed that the player walk.
   
2. Tabular Q-learning
   We are using <br>Tabular Q-learing<br> method for the player's (robot) movement.

## Evaluation:
An important aspect of your project, as we mentioned in the beginning, is evaluating yourproject. Be clear and precise about describing the evaluation setup, for both quantitative and qualitativeresults. Present the results to convince the reader that you have a working implementation. Use plots, charts,tables, screenshots, figures, etc. as needed. I expect you will need at least a few paragraphs to describe eachtype of evaluation that you perform.

## Remaining Goals and Challenges:
1. Improving Q-learing:
   We are trying to improve cases, where the q-values must be updated. Current version (1.6) Q-values are accumulated based on the success    of each movement. For example, if the player success moving to the next cell chosen by the choose_action algorithm, the Q-value is      updated with reward 1, in which its direction from the previous cell is updated. The player accumulates another 1 reward from picking    up the "gold_ingot" in the game. The Q-values are decreased if and only if either the player detects the wall or the player is killed    (contacted) to the monster. Our next goal is to find diverse cases of the q-value update instances and improve the accuracy of the        Q-table.
