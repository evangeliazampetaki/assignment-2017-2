import argparse
import copy
import itertools

# I am using a global function because I use it prior to its valorization
global total_connections


class Team:
    """
    This class represents a team. It has two attributes:
    members: A list which contains the team members
    neighbors: A list of team neighbors
    a: The a factor
    """
    def __init__(self):
        self.members = []
        self.neighbors = list()
        self.a = float()
        
    def add_member(self, member, neighbors):
        """
        Adding a member to a team. A add this member to the self.member attribute, and I also append its neighbors.
        In the end I calculate factor a (it's changed, since the number of neighbors are changed
        :param member: a string variable (e.g. '1')
        :param neighbors: a list variable (e.g. ['2', '3', '10')
        :return:
        """
        self.members.append(member)
        
        # self.neighbors[member] = neighbors
        for n in neighbors:
            self.neighbors.append(n)
        self.calculate_a()
    
    def merge_team(self, team):
        """
        I merge two teams! I add the attributes of the second to the first. This is why I return "self".
        Returning self, I return the object.
        
        :param team:
        :return:
        """
        for m in team.members:
            self.members.append(m)
        for n in team.neighbors:
            self.neighbors.append(n)
        self.calculate_a()
        return self

    def calculate_a(self):
        """
        I calculate a factor!
        :return:
        """
        self.a = float(len(self.neighbors)) / total_connections
                
    def __repr__(self):
        """
        I used this for debugging purposes. To check the creation of teams step-by-step.
        :return:
        """
        return '<Members: %r>' % (self.members)
 
    
def calculate_modularity_difference(team_i, team_j):
    """
    This function implements the math type for DQ as shown in assignment description.
    :param team_i: team_i object
    :param team_j: team_j object
    :return:
    """
    # I am calling a dedicated function (i.e. calculate_e_ij)
    e_ij = calculate_e_ij(team_i, team_j)
    # I am returning dq
    return 2 * (e_ij - team_i.a * team_j.a)


def calculate_e_ij(team_i, team_j):
    """
    This dedicated function is used to calculate e_ij, whenever is needed.
    :param team_i:
    :param team_j:
    :return:
    """
    e_ij = float()
    for i_member in team_i.members:
        for j_neighbor in team_j.neighbors:
            if i_member == j_neighbor:
                e_ij += 1
    e_ij = e_ij / total_connections
    return e_ij


def find_neighbors(member, connections):
    """
    Find all neighbors for a given member
    :param member:
    :return: a list of all neighbors
    """
    neighbors = list()
    for connection in connections:
        if member in connection:
            temp = copy.deepcopy(connection)
            temp.remove(member)
            neighbors.append(temp[0])
    
    return neighbors

# The following lines are used to create "-n" , and file arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n',
                    dest='groups',
                    const=2,
                    default=2,
                    action='store',
                    nargs='?',
                    type=int)

parser.add_argument("filename")
args = parser.parse_args()
groups = args.groups
filename = args.filename

total_connections = 0
# A list of Team objects
teams = list()

connections = list()
unique_nodes = list()
with open(filename, 'r') as graph:
    for line in graph:
        pair = line.split()
        connections.append(pair)
        unique_nodes.append(pair[0])
        unique_nodes.append(pair[1])
        total_connections += 2
        
unique_nodes = list(set(unique_nodes))

for node in unique_nodes:
    temp = Team()
    temp.add_member(node, find_neighbors(node, connections))
    teams.append(temp)


def calculate_initial_q(init_team):
    """
    This function is used to calculate the Q of the initial teams arrangement.
    That means we have as many teams as the UNIQUE given nodes.
    This function implements the Q math type (the one with the sum!)
    :param init_team:
    :return:
    """
    q = float()
    for t in init_team:
        q += calculate_e_ij(t, t) - t.a ** 2
    return q
# I am storing the initial Q value
q = calculate_initial_q(teams)

# I am repeating the process while we end up to the required group number
# I am updating teams (i.e. list) elements, merging and creating teams
while len(teams) > groups:
    # I used this function to create all unique combinations between teams
    iterations = itertools.combinations(teams, 2)
    
    # I am checking the dq of the first pair of teams (manually)
    # This is done to end up with an initial DQmax value, in order to compare future dq's.
    # I need this so to finally find out which pair results in the max DQ value.
    # A pair of teams with the max DQ will be merged
    fpair = next(iterations)
    # Initial dqmax value
    dqmax = calculate_modularity_difference(fpair[0], fpair[1])
    # Initial pair with resulting dqmax value (as a tuple)
    pairmax = fpair[0], fpair[1]
    # Iterating through unique pair combinations
    # Remember I iterated MANUALLY through the first pair
    for pair in iterations:
        # Calculate pair's dq
        dq = calculate_modularity_difference(pair[0], pair[1])
        # Compare it with dqmax. If dq > dqmax we found a new pair which results in dqmax!!
        if dq > dqmax:
            dqmax = dq
            pairmax = pair[0], pair[1]
    # At that point we ended up to the dqmax and to the corresponding pair of teams
    # We remove each these teams from the teams (python list)
    teams.remove(pairmax[0])
    teams.remove(pairmax[1])
    # We merge them into one and append it to the teams (python list)
    new_team = pairmax[0].merge_team(pairmax[1])
    # So we removed two teams, and inserted one!
    teams.append(new_team)
    # according to the math type Q = Q + dqmax
    q += dqmax

output = list()
for team in teams:
    # map(int, team.members) applies int function to each team.members elements. (ie. I convert str to int)
    # I did this to use "sorted" function. To sort team members.
    output.append(sorted(map(int, team.members)))
output = sorted(output)

for team in output:
    print(team)
print("Q = %.4f" % q)
