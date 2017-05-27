---
layout: default
title: Status
---

## Project Summary: 
Since things may have changed since proposal (even if they haven’t), write a shortparagraph summarizing the goals of the project (updated/improved version from the proposal).

## Approach:
1. Dijkstra's Algorithm
   We are using <br>Dijkstra's hortest path<br> algorithm to calculate the monster's movement. For each step of movement, the algorithm      calculates its next location from current cell in its shortest path; the algorithm moster_action returns its turn ratio relative to      the monster's current degree (turn). Hence, the monster is always chasing to the player with a half of speed that the player walk.
   
2. Tabular Q-learning
   We are using <br>Tabular Q-learing<br> method for the player's (robot) movement.

## Evaluation:
An important aspect of your project, as we mentioned in the beginning, is evaluating yourproject. Be clear and precise about describing the evaluation setup, for both quantitative and qualitativeresults. Present the results to convince the reader that you have a working implementation. Use plots, charts,tables, screenshots, figures, etc. as needed. I expect you will need at least a few paragraphs to describe eachtype of evaluation that you perform.

## Remaining Goals and Challenges:
In a few paragraphs, describe your goals for the next 2-3 weeks, whenthe final report is due. At the very least, describe how you consider your prototype to be limited, and whatyou want to add to make it a complete contribution. Note that if you think your algorithm is quite good,but have not performed sufficient evaluation, doing them can also be a reasonable goal. Similarly, you maypropose some baselines (such as a hand-coded policy) that you did not get a chance to implement, butwant to compare against for the final submission. Finally, given your experience so far, describe some of thechallenges you anticipate facing by the time your final report is due, how crippling you think it might be,and what you might do to solve them.
