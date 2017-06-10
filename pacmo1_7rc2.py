"""
CS 175 Group 17 Project Pac-mo Version 1.5
Pacmo is trying to get the most gold bars from the moster pool
Code structures based on the two assignments and multi_agent_test.py

Instructions:
  1. Launch 3 clients through launchClient in Minecraft folder.
  2. You should have priority_dict.py
  3. Enjoy watching

Author:
  Ding, Qimu (qdingqim)
  Shinn, Jong Duk (jdshinn)
  Yang, Xiaocheng (xiaochy2)

Version 1.1:
   - now there exists a basic 14x14 map
   - added terminal states

Version 1.2:
   - now the monster moves based on Dijkstra's Algorithm

Version 1.3:
   - now the player moves based on Q-table
       - alpha decreases over the time
   - switched move and turn for movement accuracy
   - added time.sleep(0.08) between turn and move
   - fixed get_dist_pm freeze during the timeout
   - added timer

Version 1.3.1:
   - the monster is not moving for Q-learning test purpose

Version 1.4:
   - now it has visual Q-table
   - MsPerTick decreased to 25 (originally 50)

Version 1.5:
   - now it has smarter choose_action function
       - it took 4-10 loops to reach the max reward
   - MsPerTick restored to 50 for test purpose
   - the monster is moving again
   - fixed calcTurnValue that sometimes return wrong turn (caused pause of the player)

Version 1.5.5:
    - added decoration in the map

Version 1.6:
   - added video recording feature (observer view)
   - fixed bug on choose_action function
   - now game ends after finding all gold_ingots
   - changed the reward of death to -1 (originally -100)

Version 1.7 #####

Todo:
    Q-learning for the player
        - need to validate if the function works properly
  
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
import time
from priority_dict import priorityDictionary as PQ
from collections import namedtuple, defaultdict
from operator import add
import Tkinter as tk
expID = 'Pac_mo_1_6'

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

def startMission(agent_host, my_mission, my_client_pool, my_mission_record, role, expId, mission_no):
    max_retries = 3
    # Create mission xml - use forcereset if this is the first mission.
    if role == 2:
        my_mission_record = MalmoPython.MissionRecordSpec( "./%s-mission%d.tgz" % (expID, mission_no) )
        my_mission_record.recordCommands()
        my_mission_record.recordMP4(16, 134217728)
        my_mission_record.recordRewards()
        my_mission_record.recordObservations()
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
                time.sleep(8)

def end_mission(agent_hosts, death, last):
    if death:
        update_q_table(last[0], last[1], -1)

    for i in xrange(NUM_AGENTS):
        agent_hosts[i].sendCommand("quit")

    return True

def drawItems():
    xml = ""
    for i in [-7,-5,-3,-1,1,3,5,7]:
        xml += '<DrawItem x="' + str(i) + '" y="210" z="' + str(7) + '" type="gold_ingot"/>'

    for i in [-7, -5,-3,-1,1,3,5]:
        xml += '<DrawItem x="' + str(i) + '" y="210" z="' + str(-7) + '" type="gold_ingot"/>'

    for i in [-5,-3,-1,1,3,5]:
        for j in [-7, 7]:
            xml += '<DrawItem x="' + str(j) + '" y="210" z="' + str(i) + '" type="gold_ingot"/>'
    #new map
    for i in [-5,-3,-1,1,3,5]:
        xml += '<DrawItem x="' + str(i) + '" y="210" z="' + str(0) + '" type="gold_ingot"/>'
    for i in [-5,-2,2]:
        xml += '<DrawItem x="' + str(0) + '" y="210" z="' + str(i) + '" type="gold_ingot"/>'
    #new map2
    '''for i in [2,5]:
        for j in [-2, 2]:
            xml += '<DrawItem x="' + str(j) + '" y="210" z="' + str(i) + '" type="gold_ingot"/>'
    #new map3
    for i in [-3,-5]:
        for j in [4, 2]:
            xml += '<DrawItem x="' + str(j) + '" y="210" z="' + str(i) + '" type="gold_ingot"/>'
    xml += '<DrawItem x="' + str(4) + '" y="210" z="' + str(2) + '" type="gold_ingot"/>'
    xml += '<DrawItem x="' + str(-4) + '" y="210" z="' + str(5) + '" type="gold_ingot"/>'
    xml += '<DrawItem x="' + str(-4) + '" y="210" z="' + str(2) + '" type="gold_ingot"/>'
    '''

    return xml

def drawWalls():
    xml = ""
    x = [ x for x in range(-8, 9)]
    z = [ z for z in range(-8, 9)]
    for n in [-8, 8]:
       for i in xrange(1, 5):
           for j in x:
               xml += '<DrawBlock x="' + str(j) + '" y="' + str(200+i) + '" z="' + str(n) + '" type="lapis_block"/>'

    for n in [-8, 8]:
       for i in xrange(1, 5):
           for j in z:
               xml += '<DrawBlock x="' + str(n) + '" y="' + str(200+i) + '" z="' + str(j) + '" type="lapis_block"/>'

    for n in range(-6, 7):
       for i in xrange(1, 3):
           for j in range(-6, 7):
               xml += '<DrawBlock x="' + str(n) + '" y="' + str(200+i) + '" z="' + str(j) + '" type="lapis_block"/>'

    for n in [-7, 7]:
           for j in range(-7, 8):
               xml += '<DrawBlock x="' + str(j) + '" y="' + str(201) + '" z="' + str(n) + '" type="coal_block"/>'

    for n in [-7, 7]:
           for j in range(-7, 8):
               xml += '<DrawBlock x="' + str(n) + '" y="' + str(201) + '" z="' + str(j) + '" type="coal_block"/>'


    return xml

def pacmo_decorator():
    xml = ""
    #P
    xml+= '<DrawCuboid x1="5" y1="202" z1="5" x2="5" y2="202" z2="1" type="sponge"/>'
    xml+= '<DrawCuboid x1="4" y1="202" z1="5" x2="3" y2="202" z2="5" type="sponge"/>'
    xml+= '<DrawCuboid x1="4" y1="202" z1="3" x2="3" y2="202" z2="3" type="sponge"/>'
    xml+= '<DrawCuboid x1="3" y1="202" z1="4" x2="3" y2="202" z2="4" type="sponge"/>'
    #A
    xml+= '<DrawCuboid x1="1" y1="202" z1="5" x2="1" y2="202" z2="1" type="sponge"/>'
    xml+= '<DrawCuboid x1="-1" y1="202" z1="5" x2="-1" y2="202" z2="1" type="sponge"/>'
    xml+= '<DrawCuboid x1="0" y1="202" z1="5" x2="0" y2="202" z2="5" type="sponge"/>'
    xml+= '<DrawCuboid x1="0" y1="202" z1="3" x2="0" y2="202" z2="3" type="sponge"/>'
    #C
    xml+= '<DrawCuboid x1="-3" y1="202" z1="5" x2="-3" y2="202" z2="1" type="sponge"/>'
    xml+= '<DrawCuboid x1="-5" y1="202" z1="5" x2="-4" y2="202" z2="5" type="sponge"/>'
    xml+= '<DrawCuboid x1="-5" y1="202" z1="1" x2="-4" y2="202" z2="1" type="sponge"/>'
    #M
    xml+= '<DrawCuboid x1="5" y1="202" z1="-5" x2="5" y2="202" z2="-1" type="sponge"/>'
    xml+= '<DrawCuboid x1="3" y1="202" z1="-5" x2="3" y2="202" z2="-1" type="sponge"/>'
    xml+= '<DrawCuboid x1="1" y1="202" z1="-5" x2="1" y2="202" z2="-1" type="sponge"/>'
    xml+= '<DrawCuboid x1="1" y1="202" z1="-1" x2="5" y2="202" z2="-1" type="sponge"/>'
    #O
    xml+= '<DrawCuboid x1="-1" y1="202" z1="-5" x2="-1" y2="202" z2="-1" type="sponge"/>'
    xml+= '<DrawCuboid x1="-5" y1="202" z1="-5" x2="-5" y2="202" z2="-1" type="sponge"/>'
    xml+= '<DrawCuboid x1="-1" y1="202" z1="-1" x2="-5" y2="202" z2="-1" type="sponge"/>'
    xml+= '<DrawCuboid x1="-1" y1="202" z1="-5" x2="-5" y2="202" z2="-5" type="sponge"/>'
    #new map
    xml+='<DrawCuboid x1="-6" y1="202" z1="0" x2="6" y2="202" z2="0" type="air"/>'
    xml+='<DrawCuboid x1="0" y1="202" z1="-6" x2="0" y2="202" z2="3" type="air"/>'
    xml+='<DrawCuboid x1="-6" y1="201" z1="0" x2="6" y2="201" z2="0" type="coal_block"/>'
    xml+='<DrawCuboid x1="0" y1="201" z1="-6" x2="0" y2="201" z2="3" type="coal_block"/>'
    
    
    
    '''
    #new map2
    xml+='<DrawCuboid x1="2" y1="202" z1="1" x2="2" y2="202" z2="6" type="air"/>'
    xml+='<DrawCuboid x1="-2" y1="202" z1="1" x2="-2" y2="202" z2="6" type="air"/>'
    xml+='<DrawCuboid x1="2" y1="201" z1="1" x2="2" y2="201" z2="6" type="coal_block"/>'
    xml+='<DrawCuboid x1="-2" y1="201" z1="1" x2="-2" y2="201" z2="6" type="coal_block"/>'
    #new map3
    xml+='<DrawCuboid x1="4" y1="202" z1="2" x2="3" y2="202" z2="2" type="air"/>'
    xml+='<DrawCuboid x1="4" y1="202" z1="1" x2="4" y2="202" z2="1" type="air"/>'
    xml+='<DrawCuboid x1="-4" y1="202" z1="2" x2="-4" y2="202" z2="5" type="air"/>'
    xml+='<DrawCuboid x1="-5" y1="202" z1="5" x2="-6" y2="202" z2="5" type="air"/>'
    xml+='<DrawCuboid x1="-5" y1="202" z1="2" x2="-6" y2="202" z2="2" type="air"/>'
    xml+='<DrawCuboid x1="4" y1="202" z1="-2" x2="4" y2="202" z2="-6" type="air"/>'
    xml+='<DrawCuboid x1="2" y1="202" z1="-2" x2="2" y2="202" z2="-6" type="air"/>'
    xml+='<DrawCuboid x1="4" y1="201" z1="2" x2="3" y2="201" z2="2" type="coal_block"/>'
    xml+='<DrawCuboid x1="4" y1="201" z1="1" x2="4" y2="201" z2="1" type="coal_block"/>'
    xml+='<DrawCuboid x1="-4" y1="201" z1="2" x2="-4" y2="201" z2="5" type="coal_block"/>'
    xml+='<DrawCuboid x1="-5" y1="201" z1="5" x2="-6" y2="201" z2="5" type="coal_block"/>'
    xml+='<DrawCuboid x1="-5" y1="201" z1="2" x2="-6" y2="201" z2="2" type="coal_block"/>'
    xml+='<DrawCuboid x1="4" y1="201" z1="-2" x2="4" y2="201" z2="-6" type="coal_block"/>'
    xml+='<DrawCuboid x1="2" y1="201" z1="-2" x2="2" y2="201" z2="-6" type="coal_block"/>'
    '''
    return xml

def inventory_condition(index):
    xml = ""
    if index == 0:
        xml += '<InventoryObject type="wooden_pickaxe" slot="0" quantity="1"/>'
    else:
        for i in range(0,39):
            xml += '<InventoryObject type="diamond_sword" slot="' + str(i) + '" quantity="1"/>'

    return xml

def player_grid(index):
    xml = ""
    if index ==0:
        xml+='<ObservationFromGrid><Grid name="floor3x3"><min x="-1" y="0" z="-1"/><max x="1" y="0" z="1"/></Grid></ObservationFromGrid>'
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
            <DrawCuboid x1="-9" y1="200" z1="-9" x2="9" y2="220" z2="9" type="stained_glass" colour="WHITE"/>
            <DrawCuboid x1="-8" y1="202" z1="-8" x2="8" y2="250" z2="8" type="air"/>
            <DrawBlock x="0" y="213" z="0" type="barrier"/>''' + drawWalls() + drawItems() + pacmo_decorator() + '''
          </DrawingDecorator>
          <ServerQuitFromTimeUp description="" timeLimitMs="120000"/>
        </ServerHandlers>
      </ServerSection>
    '''

    # Add an agent section for each robot. Robots run in survival mode.
    # Give each one a wooden pickaxe for protection...

    for i in xrange(NUM_AGENTS):
      x_loc, z_loc = spawn_loc(i)
      xml += '''<AgentSection mode="Survival">
        <Name>''' + agentName(i) + '''</Name>
        <AgentStart>
          <Placement x="''' + str(x_loc) + '''" y="202" z="''' + str(z_loc) + '''"/>
          <Inventory>''' + inventory_condition(i) + '''</Inventory>
        </AgentStart>
        <AgentHandlers>
          <ContinuousMovementCommands turnSpeedDegs="720"/>
          <ChatCommands/>
          <MissionQuitCommands/>
          <RewardForCollectingItem>
            <Item type="gold_ingot" reward="1"/>
          </RewardForCollectingItem>
          <ObservationFromNearbyEntities>
            <Range name="entities" xrange="50" yrange="2" zrange="50"/>
          </ObservationFromNearbyEntities>'''+player_grid(i)+'''
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
            <Range name="entities" xrange="50" yrange="50" zrange="50"/>
          </ObservationFromNearbyEntities>
          <ObservationFromGrid>
            <Grid name="floor201">
              <min x="-8" y="-13" z="-8"/>
              <max x="8" y="-13" z="8"/>
            </Grid>
          </ObservationFromGrid>
          <VideoProducer>
            <Width>800</Width>
            <Height>600</Height>
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
        cnt, loc, json_ob = get_obj_locations(observer, 'gold_ingot')
        return cnt, json_ob

def load_grid(ob):
    grid = ob.get(u'floor201', 0)
    return grid

def is_solution(reward):
    return reward == MAX_REWARD


def get_obj_locations(agent_host, obj_name):
    """Queries for the object's location in the world.
       This returns the counter for the object and its locations.
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

            return len(locations), locations, ob

def get_dist_pm(ob):
    """ Returns the distance between the player
        and the monster.
        Application: if dist < 0.5, player dies
    """
    robot = ()
    monster = ()
    for ent in ob['entities']:
        if ent['name'] == "Robot":
            robot = (ent['yaw'], ent['x'], ent['z'])
        if ent['name'] == "Monster":
            monster = (ent['yaw'], ent['x'], ent['z'])

    pl_y, pl_x, pl_z = robot
    m_y, m_x, m_z = monster
    dist = math.sqrt((pl_x - m_x)**2 + (pl_z - m_z)**2)
    return dist

def to_block_coordinate(current_pos):
    pl_x, pl_z = current_pos[0]
    m_x, x_z = current_pos[1]
    coordinates = [pl_x, pl_z, m_x, x_z]
    for i in range(4):
        coordinates[i] = math.floor(coordinates[i])

    return coordinates  

########################################################################
#### Functions for Q-Learning

# Create one Q-table for the plyaer
q_table = {}
epsilon = 0.01
alpha = 0.6
gamma = 1
n = 2
fs_appeared_at = -1 # first solution appeared at which state?
fs_appeared = False

class q_draw:
    def __init__(self, canvas=None, root=None):
        self.canvas = canvas
        self.root = root

    def drawQ( self, curr_x=None, curr_y=None ):
        if self.canvas is None or self.root is None:
            return
        self.canvas.delete("all")
        action_inset = 0.1
        action_radius = 0.1
        curr_radius = 0.2
        action_positions = [ ( 0.5, 1-action_inset ), ( 0.5, action_inset ), ( 1-action_inset, 0.5 ), ( action_inset, 0.5 ) ]
        # (NSWE to match action order)
        min_value = -20
        max_value = 20
        for x in range(world_x):
            for y in range(world_y):
                s = (x-8,y-8)
                self.canvas.create_rectangle( (world_x-1-x)*scale, (world_y-1-y)*scale, (world_x-1-x+1)*scale, (world_y-1-y+1)*scale, outline="#fff", fill="#000")
                for direction, action in [('south',0), ('north',1), ('east',2), ('west',3)]:
                    if not s in q_table:
                        continue
                    if not direction in q_table[s]:
                        q_table[s][direction] = [-9999, (0,0)]
                    value = q_table[s][direction][0]
                    color = 255 * ( value - min_value ) / ( max_value - min_value ) # map value to 0-255
                    color = max( min( color, 255 ), 0 ) # ensure within [0,255]
                    color_string = '#%02x%02x%02x' % (255-color, color, 0)
                    self.canvas.create_oval( (world_x - 1 - x + action_positions[action][0] - action_radius ) *scale,
                                             (world_y - 1 - y + action_positions[action][1] - action_radius ) *scale,
                                             (world_x - 1 - x + action_positions[action][0] + action_radius ) *scale,
                                             (world_y - 1 - y + action_positions[action][1] + action_radius ) *scale, 
                                             outline=color_string, fill=color_string )
        if curr_x is not None and curr_y is not None:
            self.canvas.create_oval( (world_x - 1 - curr_x + 0.5 - curr_radius ) * scale, 
                                     (world_y - 1 - curr_y + 0.5 - curr_radius ) * scale, 
                                     (world_x - 1 - curr_x + 0.5 + curr_radius ) * scale, 
                                     (world_y - 1 - curr_y + 0.5 + curr_radius ) * scale, 
                                     outline="#fff", fill="#fff" )
        self.root.update()

scale = 40
world_x = 17
world_y = 17
root = tk.Tk()
root.wm_title("Q-table")
canvas = tk.Canvas(root, width=world_x*scale, height=world_y*scale, borderwidth=0, highlightthickness=0, bg="black")
canvas.grid()
root.update()
dq = q_draw(canvas, root)

def get_possible_action(curr_idx, grid):
    msg = world_state.observations[-1].text
    observations = json.loads(msg)
    grid = observations.get(u'floor3x3', 0)
    action = []
    if grid[7] == u'air':
        action.append(["north",get_block_coordinate(curr_idx+17)])
    if grid[1] == u'air':
        action.append(["south",get_block_coordinate(curr_idx-17)])
    if grid[3] == u'air':
        action.append(["east",get_block_coordinate(curr_idx-1)])
    if grid[5] == u'air':
        action.append(["west",get_block_coordinate(curr_idx+1)])
    return action

def choose_action(curr_coord, m_coord, grid, last):
    possible_actions = get_possible_action(get_block_index(curr_coord), grid)
    print "original:", possible_actions
    if curr_coord not in q_table:
        q_table[curr_coord] = {}

    for direction, coord in possible_actions:
        if direction not in q_table[curr_coord]:
            q_table[curr_coord][direction] = [0, coord]

    many_pos_path = False # True : >2, False : 0-2
    neighs = get_neighbor(get_block_index(curr_coord),grid)
    impossible_action = ""
    return_action = list()
    if monster_is_neighbor(curr_coord, m_coord, grid):
        if curr_coord[0] < m_coord[0]: # x coordinate,
            impossible_action = "west"
        elif curr_coord[0] > m_coord[0]: # x coordinate,
            impossible_action = "east"
        elif curr_coord[1] > m_coord[1]: # z coordinate,
            impossible_action = "south"
        elif curr_coord[1] < m_coord[1]: # z coordinate,
            impossible_action = "north"

    if impossible_action != "":
        for x in possible_actions:
            if x[0] == impossible_action:
                possible_actions.remove(x)
                break

    if len(neighs) == 2:
        if last[1] != "" and last[1] in q_table[curr_coord]:
            if q_table[last[0]][last[1]][0] >= 0 and q_table[curr_coord][last[1]][0] >= 0:
                for i in range(len(possible_actions)):
                    if possible_actions[i][0] == last[1]:
                        return_action.append(possible_actions[i])

    tol = 0.0001
    rnd = random.random()   
    if len(return_action) == 0:
        if rnd < epsilon:
            a = random.randint(0, len(possible_actions) - 1)
            return_action.append(possible_actions[a])

        else:
            m = max([x[0] for x in q_table[curr_coord].values()])
            l = list()
            for direction, coord in possible_actions:
                for value, coordinate in q_table[curr_coord].values():
                    if abs(value-m) <= tol:
                        l.append((direction, coord))
        
            return_action.append(l[random.randint(0, len(l)-1)])
    print "actual:", return_action[0]
    print "m_coord:", m_coord
    print "imp_act:", impossible_action
    return return_action[0]

def update_q_table(curr_coord, direction, value):
    if fs_appeared == False:
        G = gamma * value
        G += gamma ** n * q_table[curr_coord][direction][0]

        old_q = q_table[curr_coord][direction][0]
        q_table[curr_coord][direction][0] = old_q + alpha * (G - old_q)
        dq.drawQ(curr_coord[0]+8, curr_coord[1]+8)

########################################################################
#### Functions for Dijkstra's algorithm

def find_start_end(block_coord):
    x_coord = { -8: 0, -7: 1, -6: 2, -5: 3,
                -4: 4, -3: 5, -2: 6, -1: 7,
                 0: 8,  1: 9, 2: 10, 3: 11,
                 4: 12, 5: 13, 6: 14, 7: 15,
                 8: 16 }
    z_coord = { -8: 0, -7: 17, -6: 34, -5: 51,
                -4: 68, -3: 85, -2: 102, -1: 119,
                 0: 136,  1: 153, 2: 170, 3: 187,
                 4: 204, 5: 221, 6: 238, 7: 255,
                 8: 272 }

    pl_x = block_coord[0]
    pl_z = block_coord[1]
    m_x = block_coord[2]
    m_z = block_coord[3]
    start = x_coord[pl_x] + z_coord[pl_z]
    end = x_coord[m_x] + z_coord[m_z]

    return (start, end)

def get_block_index(coord):
    x_coord = { -8: 0, -7: 1, -6: 2, -5: 3,
                -4: 4, -3: 5, -2: 6, -1: 7,
                 0: 8,  1: 9, 2: 10, 3: 11,
                 4: 12, 5: 13, 6: 14, 7: 15,
                 8: 16 }
    z_coord = { -8: 0, -7: 17, -6: 34, -5: 51,
                -4: 68, -3: 85, -2: 102, -1: 119,
                 0: 136,  1: 153, 2: 170, 3: 187,
                 4: 204, 5: 221, 6: 238, 7: 255,
                 8: 272 }

    x = coord[0]
    z = coord[1]
    idx = x_coord[x] + z_coord[z]

    return idx

def get_block_coordinate(idx):
    coord = { 0: -8, 1: -7, 2: -6, 3: -5,
              4: -4, 5: -3, 6: -2, 7: -1,
              8: 0, 9: 1, 10: 2, 11: 3,
              12: 4, 13: 5, 14: 6, 15: 7,
              16: 8 }

    col, row = divmod(idx, 17)
    return coord[row], coord[col]

def get_neighbor(u, grid):
    R_list = [i*17 for i in range(1, 16)]
    L_list = [i*17 - 1 for i in range(2, 17)]
    candidate = []
    ret = []
    if u == 0:
        candidate = [1, 17]
    elif u == 16:
        candidate = [15, 33]
    elif u == 272:
        candidate = [273, 255]
    elif u == 288:
        candidate = [271, 287]
    elif u in R_list:
        candidate = [u-17, u+1, u+17]
    elif u in L_list:
        candidate = [u-17, u-1, u+17]
    elif u in range(1, 16):
        candidate = [u-1, u+1, u+17]
    elif u in range(273, 288):
        candidate = [u-17, u-1, u+1]
    else:
        candidate = [u-17, u-1, u+1, u+17]

    for x in candidate:
        if grid[x] == u'coal_block':
            ret.append(x)

    return ret

def monster_is_neighbor(p_coord, m_coord, grid):
    p_idx = get_block_index(p_coord)
    m_idx = get_block_index(m_coord)
    neigh = get_neighbor(p_idx, grid)
    if m_idx in neigh:
        return True

    return False

def dijkstra_shortest_path(grid_obs, source, dest):
    ## helper functions
    def extract_min(queue):
        if len(queue) == 0:
            return None

        val = queue.smallest()
        del queue[val]

        return val

    ## Dijkstra's Algorithm
    dist = []
    prev = []
    pq = PQ()

    for i in range(len(grid_obs)):
        if i == source: dist.append(0)
        else: dist.append(float('inf'))
        prev.append(-1)
        pq[i] = dist[i]

    while len(pq) > 0:
        u = extract_min(pq)
        for v in get_neighbor(u,grid_obs):
            alt = dist[u] + 1
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                pq[v] = alt
    
    return prev[dest] if len(prev) > 0 else -1

def calcTurnValue(us, them, current_yaw):
    ''' Calc turn speed required to steer "us" towards "them".'''
    dx = them[0] + 0.3 - us[0] if them[0] >= 0 else them[0] - 0.3 - us[0]
    dz = them[1] + 0.3 - us[1] if them[1] >= 0 else them[1] - 0.3 - us[1]
    yaw = -180 * math.atan2(dx, dz) / math.pi
    difference = yaw - current_yaw
    while difference < -180:
        difference += 360;
    while difference > 180:
        difference -= 360;
    difference /= 180.0;

    return difference

########################################################################
#### Functions for the player/Monster
player_spawn = (7.0, -6.5)
monster_spawn = (-6.5, 7.0)

def agentName(i):
    if i == 0:
        return "Robot"

    return "Monster"

def spawn_loc(index):
    x, z = 0, 0
    if index == 0:
        x, z = player_spawn
    else:
        x, z = monster_spawn

    return x, z

def player_action(last, block_coord, turn_count, yaw, grid):
    walk_speed = 1
    # implement as Q-learning
    block = (block_coord[0], block_coord[1])
    m_block = (block_coord[2], block_coord[3])
    direction, to_where = choose_action(block, m_block, grid, last)
    new_last = (block, direction)
    if new_last[0] != block:
        update_q_table(block, direction, 1)

    turn = calcTurnValue(block, to_where, yaw)
    return walk_speed, turn, new_last

def monster_action(block_coord, grid, yaw):
    walk_speed = 0
    turn = 0
    ## use Dijkstras algorithm to find the next turn.
    # start: player, end: monster
    #   we just need the first prev node for the next turn

    start, end = find_start_end(block_coord)
    next = dijkstra_shortest_path(grid, start, end)
    if next > -1:
        monster = [block_coord[2], block_coord[3]]
        block = get_block_coordinate(next)
        walk_speed = 0.2
        turn = calcTurnValue(monster, block, yaw)

    return walk_speed, turn

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
    if fs_appeared:
        break

    print "Running mission #" + str(mission_no)

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
        startMission(agent_hosts[i], my_mission, client_pool, MalmoPython.MissionRecordSpec(), i, experimentID, mission_no)

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
    MAX_REWARD, json_ob = get_max_reward(agent_hosts[-1])
    print "MAX_REWARD:", MAX_REWARD
    grid = load_grid(json_ob)
    running = True
    current_yaw = [0 for x in range(NUM_AGENTS)]
    current_pos = [(0,0) for x in range(NUM_AGENTS)]
    current_turn = [0 for x in range(NUM_AGENTS)]
    block_coord = [0 for x in range(4)]
    current_reward = 0
    turn_count = 0
    last = [player_spawn, ""]
    reason_for_term = ""
    if alpha > 0 and mission_no > 1: alpha -= 0.000001

    # When an agent is killed, it stops getting observations etc. Track this, so we know when to bail.
    unresponsive_count = [10 for x in range(NUM_AGENTS)]
    num_responsive_agents = lambda: sum([urc > 0 for urc in unresponsive_count])

    timed_out = False
    player_dead = False
 
    start_t = time.time()
    while num_responsive_agents() > 0 and not timed_out and not player_dead and not fs_appeared:
        ## 0: player, 1: Monster
        for i in xrange(NUM_AGENTS):
            ah = agent_hosts[i]
            world_state = ah.getWorldState()
            if world_state.is_mission_running == False:
                timed_out = True
            if world_state.is_mission_running and world_state.number_of_observations_since_last_state > 0:
                unresponsive_count[i] = 10
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                if "Yaw" in ob:
                    current_yaw[i] = ob[u'Yaw']

                if "XPos" in ob and "ZPos" in ob:
                    current_pos[i] = (ob[u'XPos'], ob[u'ZPos'])

                if get_dist_pm(ob) <= 0.1:
                    reason_for_term = "death"
                    player_dead = end_mission(agent_hosts, True, last)
                    break

                if "entities" in ob:
                    if i == 0: # player
                        block_coord = to_block_coordinate(current_pos)
                        speed, turn, last = player_action(last, block_coord, turn_count, current_yaw[i], grid)  
                        ah.sendCommand("turn " + str(turn))
                        time.sleep(0.05)
                        ah.sendCommand("move " + str(speed))
                        turn_count += 1
                    else: # Monster
                        block_coord = to_block_coordinate(current_pos)
                        speed, turn = monster_action(block_coord, grid, current_yaw[i])
                        ah.sendCommand("turn " + str(turn))
                        time.sleep(0.05)
                        ah.sendCommand("move " + str(speed))

            elif world_state.number_of_observations_since_last_state == 0:
                unresponsive_count[i] -= 1
            if not fs_appeared and world_state.number_of_rewards_since_last_state > 0 and i == 0:
                for rew in world_state.rewards:
                    update_q_table(last[0], last[1], rew.getValue())
                    current_reward += rew.getValue()

            if is_solution(current_reward) == True:
                reason_for_term = "found"
                if fs_appeared == False:
                    fs_appeared_at = mission_no
                    fs_appeared = end_mission(agent_hosts, False, last)

                break

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

    end_t = time.time()

    print
    print "Mission Statistics"
    print "========================================="
    if fs_appeared == True:
        print "Solution appeared at mission", fs_appeared_at
    print "Game finished due to", reason_for_term if not timed_out else "timeout"
    print "Player survived for",end_t-start_t, "second(s)"
    print "Player score:", current_reward, "gold bar(s)"
    print "Number of turns:", turn_count
    print "========================================="
    print

    time.sleep(2)
