"""
CS 175 Group 17 Project Pac-mo Version 1.1
Pacmo is trying to get the most diamonds from the moster pool
Code structures based on the two assignments and multi_agent_test.py

Instructions:
  1. Launch 3 clients through launchClient in Minecraft folder.
  2. Enjoy watching

Author:
  Ding, Qimu (qdingqim)
  Shinn, Jong Duk (jdshinn)
  Yang, Xiaocheng (xiaochy2)

Version 1.1:
   - now there exists a basic 14x14 map
   - added terminal states

Todo:
    Q-learning for the player
        functions:
          - get_direction
          - keep in track of turns

    Dijkstra for the Monster
        - return only the next "turn" based on the next node from the shortest path
  
"""

import MalmoPython
import json
import logging
import math
import os
import random
import sys
import time
import re
import uuid
import math
from collections import namedtuple
from operator import add

EntityInfo = namedtuple('EntityInfo', 'x, y, z, yaw, pitch, name, colour, variation, quantity')
EntityInfo.__new__.__defaults__ = (0, 0, 0, 0, 0, "", "", "", 1)

# Create one agent host for parsing:
agent_hosts = [MalmoPython.AgentHost()]

# Parse the command-line options:
agent_hosts[0].addOptionalFlag( "debug,d", "Display debug information.")
agent_hosts[0].addOptionalIntArgument("agents,n", "Number of agents to use, including observer.", 3)

try:
    agent_hosts[0].parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:',e
    print agent_hosts[0].getUsage()
    exit(1)
if agent_hosts[0].receivedArgument("help"):
    print agent_hosts[0].getUsage()
    exit(0)

DEBUG = agent_hosts[0].receivedArgument("debug")
INTEGRATION_TEST_MODE = agent_hosts[0].receivedArgument("test")
agents_requested = agent_hosts[0].getIntArgument("agents")
NUM_AGENTS = max(1, agents_requested - 1) # Will be NUM_AGENTS robots running around, plus one static observer.

# Create the rest of the agent hosts - one for each robot, plus one to give a bird's-eye view:
agent_hosts += [MalmoPython.AgentHost() for x in xrange(1, NUM_AGENTS + 1) ]

# Set up debug output:
for ah in agent_hosts:
    ah.setDebugOutput(DEBUG)    # Turn client-pool connection messages on/off.

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately


########################################################################
#### Functions for the Map

def startMission(agent_host, my_mission, my_client_pool, my_mission_record, role, expId):
    max_retries = 3
    for retry in range(max_retries):
        try:
            # Attempt to start the mission:
            agent_host.startMission( my_mission, my_client_pool, my_mission_record, role, expId )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print "Error starting mission",e
                print "Is the game running?"
                exit(1)
            else:
                # In a multi-agent mission, startMission will fail if the integrated server
                # hasn't yet started - so if none of our clients were available, that may be the
                # reason. To catch this specifically we could check the results for "MALMONOSERVERYET",
                # but it should be sufficient to simply wait a bit and try again.
                time.sleep(5)

def end_mission(agent_hosts):
    for i in xrange(NUM_AGENTS):
        agent_hosts[i].sendCommand("quit")

    return True

# def calcTurnValue(us, them, current_yaw):
    # ''' Calc turn speed required to steer "us" towards "them".'''
    # dx = them[0] - us[0]
    # dz = them[1] - us[1]
    # yaw = -180 * math.atan2(dx, dz) / math.pi
    # difference = yaw - current_yaw
    # while difference < -180:
        # difference += 360;
    # while difference > 180:
        # difference -= 360;
    # difference /= 180.0;
    # return difference

def drawItems():
    xml = ""
    for i in [-7,-5,-3,-1,1,3,5,7]:
        xml += '<DrawItem x="' + str(i) + '" y="210" z="' + str(7) + '" type="gold_ingot"/>'

    for i in [-7, -5,-3,-1,1,3,5]:
        xml += '<DrawItem x="' + str(i) + '" y="210" z="' + str(-7) + '" type="gold_ingot"/>'

    for i in [-5,-3,-1,1,3,5]:
        for j in [-7, 7]:
            xml += '<DrawItem x="' + str(j) + '" y="210" z="' + str(i) + '" type="gold_ingot"/>'

    return xml

def drawWalls():
    xml = ""
    x = [ x for x in range(-8, 9)]
    z = [ z for z in range(-8, 9)]
    for n in [-8, 8]:
       for i in xrange(1, 4):
           for j in x:
               xml += '<DrawBlock x="' + str(j) + '" y="' + str(201+i) + '" z="' + str(n) + '" type="lapis_block"/>'

    for n in [-8, 8]:
       for i in xrange(1, 4):
           for j in z:
               xml += '<DrawBlock x="' + str(n) + '" y="' + str(201+i) + '" z="' + str(j) + '" type="lapis_block"/>'

    for n in range(-6, 7):
       for i in xrange(1, 2):
           for j in range(-6, 7):
               xml += '<DrawBlock x="' + str(n) + '" y="' + str(201+i) + '" z="' + str(j) + '" type="lapis_block"/>'

    for n in [-7, 7]:
           for j in range(-7, 8):
               xml += '<DrawBlock x="' + str(j) + '" y="' + str(201) + '" z="' + str(n) + '" type="coal_block"/>'

    for n in [-7, 7]:
           for j in range(-7, 8):
               xml += '<DrawBlock x="' + str(n) + '" y="' + str(201) + '" z="' + str(j) + '" type="coal_block"/>'


    return xml

def inventory_condition(index):
    xml = ""
    if index == 0:
        xml += '<InventoryObject type="wooden_pickaxe" slot="0" quantity="1"/>'
    else:
        for i in range(0,39):
            xml += '<InventoryObject type="diamond_sword" slot="' + str(i) + '" quantity="1"/>'

    return xml

def getXML(reset):
    # Set up the Mission XML:
    xml = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <About>
        <Summary/>
      </About>
      <ModSettings>
        <MsPerTick>50</MsPerTick>
      </ModSettings>
      <ServerSection>
        <ServerInitialConditions>
          <Time>
            <StartTime>1000</StartTime>
          </Time>
        </ServerInitialConditions>
        <ServerHandlers>
          <FlatWorldGenerator forceReset="'''+reset+'''" generatorString="3;2*4,225*22;1;" seed=""/>
          <DrawingDecorator>
            <DrawCuboid x1="-9" y1="200" z1="-9" x2="9" y2="227" z2="9" type="stained_glass" colour="WHITE"/>
            <DrawCuboid x1="-8" y1="201" z1="-8" x2="8" y2="247" z2="8" type="air"/>
            <DrawBlock x="0" y="213" z="0" type="barrier"/>''' + drawWalls() + drawItems() + '''
          </DrawingDecorator>
          <ServerQuitFromTimeUp description="" timeLimitMs="50000"/>
        </ServerHandlers>
      </ServerSection>
    '''

    # Add an agent section for each robot. Robots run in survival mode.
    # Give each one a wooden pickaxe for protection...

    for i in xrange(NUM_AGENTS):
      x_loc, y_loc = spawn_loc(i)
      xml += '''<AgentSection mode="Survival">
        <Name>''' + agentName(i) + '''</Name>
        <AgentStart>
          <Placement x="''' + str(x_loc) + '''" y="204" z="''' + str(y_loc) + '''"/>
          <Inventory>''' + inventory_condition(i) + '''</Inventory>
        </AgentStart>
        <AgentHandlers>
          <ContinuousMovementCommands turnSpeedDegs="360"/>
          <ChatCommands/>
          <MissionQuitCommands/>
          <RewardForCollectingItem>
            <Item type="gold_ingot" reward="1"/>
          </RewardForCollectingItem>
          <ObservationFromNearbyEntities>
            <Range name="entities" xrange="1000" yrange="2" zrange="1000"/>
          </ObservationFromNearbyEntities>
          <ObservationFromRay/>
          <ObservationFromFullStats/>
        </AgentHandlers>
      </AgentSection>'''


    # Add a section for the observer. Observer runs in creative mode.

    xml += '''<AgentSection mode="Creative">
        <Name>TheWatcher</Name>
        <AgentStart>
          <Placement x="0.5" y="214" z="0.5" pitch="90"/>
        </AgentStart>
        <AgentHandlers>
          <ContinuousMovementCommands turnSpeedDegs="360"/>
          <MissionQuitCommands/>
          <ObservationFromNearbyEntities>
            <Range name="entities" xrange="400" yrange="300" zrange="400"/>
          </ObservationFromNearbyEntities>
          <VideoProducer>
            <Width>1600</Width>
            <Height>1600</Height>
          </VideoProducer>
        </AgentHandlers>
      </AgentSection>'''

    xml += '</Mission>'
    return xml


########################################################################
#### Functions for the game play

def get_max_reward(observer):
    world_state = observer.getWorldState()
    if not world_state.is_mission_running:
        print "Mission already ended."
        return 0
    else:
        cnt, loc = get_obj_locations(observer, 'gold_ingot')
        return cnt

def is_solution(reward):
    return reward == MAX_REWARD


def get_obj_locations(agent_host, obj_name):
    """Queries for the object's location in the world.
       This returns the counter for the object and its locations
    """
    locations = []
    while True:
        world_state = agent_host.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            for ent in ob['entities']:
                if ent['name'] == obj_name:
                    locations.append([ent['yaw'], ent['x'], ent['z']])

            return len(locations), locations

def get_dist_pm():
    """ Returns the distance between the player
        and the monster.
        Application: if dist < 0.5, player dies
    """
    pl_y, pl_x, pl_z = get_obj_locations(agent_hosts[-1], "Robot")[1][0]
    m_y, m_x, m_z = get_obj_locations(agent_hosts[-1], "Monster")[1][0]
    dist = math.sqrt((pl_x - m_x)**2 + (pl_z - m_z)**2)
    return dist

########################################################################
#### Functions for the player/Monster

def agentName(i):
    if i == 0:
        return "Robot"

    return "Monster"

def spawn_loc(index):
    x, y = 0, 0
    if index == 0:
        x, y = 6.98, -6.5
    else:
        x, y = -6.5, 6.5

    return x, y

def player_action(agent_host):
    walk_speed = 1
    turn = [0,90,180,-90]
    # implement as Q-learning
    return walk_speed, turn[random.randint(0, 3)]

def monster_action(world_state, agent_host):
    walk_speed = 0.4
    turn = [0,90,180,-90]
    ## use Dijkstras algorithm to find the next turn.
    # 1. use Dijkstras algorithm to find the shortest path.
    # 2. only return the next turn
    return walk_speed, turn[random.randint(0, 3)]

########################################################################
#### Main

# Set up a client pool.
# IMPORTANT: If ANY of the clients will be on a different machine, then you MUST
# make sure that any client which can be the server has an IP address that is
# reachable from other machines - ie DO NOT SIMPLY USE 127.0.0.1!!!!
# The IP address used in the client pool will be broadcast to other agents who
# are attempting to find the server - so this will fail for any agents on a
# different machine.
client_pool = MalmoPython.ClientPool()
for x in xrange(10000, 10000 + NUM_AGENTS + 1):
    client_pool.add( MalmoPython.ClientInfo('127.0.0.1', x) )

# Keep score of how our robot is doing:
robot_scores = 0 # number of diamonds acquired

num_missions = 5 if INTEGRATION_TEST_MODE else 30000
for mission_no in xrange(1, num_missions+1):
    print "Running mission #" + str(mission_no)
    # Create mission xml - use forcereset if this is the first mission.
    my_mission = MalmoPython.MissionSpec(getXML("true" if mission_no == 1 else "false"), True)

    # Generate an experiment ID for this mission.
    # This is used to make sure the right clients join the right servers -
    # if the experiment IDs don't match, the startMission request will be rejected.
    # In practice, if the client pool is only being used by one researcher, there
    # should be little danger of clients joining the wrong experiments, so a static
    # ID would probably suffice, though changing the ID on each mission also catches
    # potential problems with clients and servers getting out of step.

    # Note that, in this sample, the same process is responsible for all calls to startMission,
    # so passing the experiment ID like this is a simple matter. If the agentHosts are distributed
    # across different threads, processes, or machines, a different approach will be required.
    # (Eg generate the IDs procedurally, in a way that is guaranteed to produce the same results
    # for each agentHost independently.)
    experimentID = str(uuid.uuid4())

    for i in range(len(agent_hosts)):
        startMission(agent_hosts[i], my_mission, client_pool, MalmoPython.MissionRecordSpec(), i, experimentID)

    # Wait for mission to start - complicated by having multiple agent hosts, and the potential
    # for multiple errors to occur in the start-up process.
    print "Waiting for the mission to start ",
    hasBegun = False
    hadErrors = False
    while not hasBegun and not hadErrors:
        sys.stdout.write(".")
        time.sleep(0.1)
        for ah in agent_hosts:
            world_state = ah.getWorldState()
            if world_state.has_mission_begun:
                hasBegun = True
            if len(world_state.errors):
                hadErrors = True
                print "Errors from agent " + agentName(agent_hosts.index(ah))
                for error in world_state.errors:
                    print "Error:",error.text

    if hadErrors:
        print "ABORTING"
        exit(1)

    time.sleep(1)
    
    print "Mission Start!"
    MAX_REWARD = get_max_reward(agent_hosts[-1])
    print "MAX_REWARD:", MAX_REWARD
    running = True
    current_yaw = [0 for x in range(NUM_AGENTS)]
    current_pos = [(0,0) for x in range(NUM_AGENTS)]
    current_reward = 0
    turn_count = 0

    # When an agent is killed, it stops getting observations etc. Track this, so we know when to bail.
    unresponsive_count = [10 for x in range(NUM_AGENTS)]
    num_responsive_agents = lambda: sum([urc > 0 for urc in unresponsive_count])

    timed_out = False
    found_all_diamonds = False
    player_dead = False
 
    while num_responsive_agents() > 0 and not timed_out and not found_all_diamonds and not player_dead:
        ## 0: player, 1: Monster
        for i in xrange(NUM_AGENTS):
            ah = agent_hosts[i]
            if is_solution(current_reward) == True:
                print "found"
                found_all_diamonds = end_mission(agent_hosts)
                break
                
            world_state = ah.getWorldState()
            if world_state.is_mission_running == False:
                timed_out = True
            if world_state.is_mission_running and world_state.number_of_observations_since_last_state > 0:
                unresponsive_count[i] = 10
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                if "Yaw" in ob:
                    current_yaw[i] = ob[u'Yaw']

                #### not required since no one attacks###########
                # if "Life" in ob:
                    # life = ob[u'Life']
                    # if life != 20:
                        # print "life"
                        # player_dead = end_mission(agent_hosts)
                        # break
                #################################################

                if get_dist_pm() <= 0.5:
                    print "dead"
                    player_dead = end_mission(agent_hosts)
                    break

                if "XPos" in ob and "ZPos" in ob:
                    current_pos[i] = (ob[u'XPos'], ob[u'ZPos'])

                if "entities" in ob:
                    if i == 0: # player
                        speed, turn = player_action(ah)
                        ah.sendCommand("move " + str(speed))
                        ah.sendCommand("turn " + str(turn))
                        turn_count += 1
                    else: # Monster
                        speed, turn = monster_action(world_state, ah)
                        ah.sendCommand("move " + str(speed))
                        ah.sendCommand("turn " + str(turn))

            elif world_state.number_of_observations_since_last_state == 0:
                unresponsive_count[i] -= 1
            if world_state.number_of_rewards_since_last_state > 0 and i == 0:
                for rew in world_state.rewards:
                    current_reward += rew.getValue()

        time.sleep(0.05)

    if not timed_out:
        # All agents except the watcher have died.
        # We could wait for the mission to time out, but it's quicker
        # to make the watcher quit manually:
        agent_hosts[-1].sendCommand("quit")

    print "Waiting for mission to end ",
    # Mission should have ended already, but we want to wait until all the various agent hosts
    # have had a chance to respond to their mission ended message.
    hasEnded = False
    while not hasEnded:
        hasEnded = True # assume all good
        sys.stdout.write(".")
        time.sleep(0.1)
        for ah in agent_hosts:
            world_state = ah.getWorldState()
            if world_state.is_mission_running:
                hasEnded = False # all not good


    print
    print "Mission Statistics"
    print "========================================="
    print "Player survived for ", " second(s)"
    print "Player score: ", current_reward, "gold bar(s)"
    print "Number of turns: ", turn_count
    print "========================================="
    print

    time.sleep(2)

