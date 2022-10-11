import copy
import random
import numpy as np
import matplotlib.pyplot as plt


# We opened class for "message" object that contains who sent it, who it is for, and what the content of the message is.
class message:
    Iteration = None
    id_agent_from = None
    id_agent_to = None
    content = 0

    def __init__(self, Iteration, id_agent_from, id_agent_to, content):
        self.id_agent_from = id_agent_from
        self.content = content
        self.id_agent_to = id_agent_to
        self.Iteration = Iteration


# agent object that contains the agent domain, constrains, current variable,Inbox with all his messages
# price for each iteration (dict) and for MGM only - Rj and Inbox Rj
class agent:
    def __init__(self, id):
        self.id = id
        self.Domain = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.Constraints = dict()
        self.Inbox = []
        self.variable = 0
        self.price_of_Iteration = dict()
        self.min_variable_mgm = None
        self.Rj_mgm = 0
        self.Inbox_Rj = []
        self.min_price = None
        self.all_variable_price = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}

    def random_variable(self):  # choose random variable in the first Iteration
        self.variable = random.choice(self.Domain)
        return self.variable

    def det_Constraints(self, Constraint_1,
                        id_agent):  # method that help us to set the constraint for the current agent
        self.Constraints[id_agent] = copy.copy(Constraint_1)

    # the method that helped us to choose variable in the DSA algorithm
    def choose_variable_dsa(self, p, Iteration):
        self.price_of_Iteration[Iteration] = 0
        all_variable_price = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0,
                              10: 0}  # we save here the total price that I will have to pay for each variable that I would choose
        for i in self.Inbox:  # we read all our messages from our and add to the prices dict
            price_table = self.Constraints[i.id_agent_from]
            for key in all_variable_price:
                all_variable_price[key] += price_table[i.content - 1, key - 1]
        min_price = None
        min_variable = None
        for d in all_variable_price:  # we find the min price - the best variable for us in the current state
            if min_price == None:
                min_price = all_variable_price[d]
                min_variable = d
            else:
                if min_price > all_variable_price[d]:
                    min_price = all_variable_price[d]
                    min_variable = d
        x = random.random()
        if x < p:  # we will choose the variable in Chance p
            self.variable = min_variable
            self.price_of_Iteration[Iteration] = min_price
        else:  # if we don't choose to change the variable - we set the price with our last variable
            price = 0
            for i in self.Inbox:
                price_table = self.Constraints[i.id_agent_from]
                price += price_table[i.content - 1, self.variable - 1]
            self.price_of_Iteration[Iteration] = price

    def calcul_first_price(self, Iteration):  # function that help us to calculate the price for each iteration
        self.price_of_Iteration[Iteration] = 0
        all_variable_price = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        for i in self.Inbox:  # we are looking on all other neighbors variable and sum the constraints prices
            price_table = self.Constraints[i.id_agent_from]
            for key in all_variable_price:
                all_variable_price[key] += price_table[i.content - 1, key - 1]
        self.price_of_Iteration[Iteration] = all_variable_price[self.variable]

    def choose_variable_MGM(self, Iteration):  # the function that choose variable for MGM algoritm
        self.all_variable_price = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        for i in self.Inbox:  # read all the messeges from the inbox and set the variable prices
            price_table = self.Constraints[i.id_agent_from]
            for key in self.all_variable_price:
                self.all_variable_price[key] += price_table[i.content - 1, key - 1]
        if Iteration == 1:  # if we are on the first iteration - we want to set the price to the random variable that we choose
            self.price_of_Iteration[Iteration] = self.all_variable_price[self.variable]
        min_price = None
        min_variable = None
        for d in self.all_variable_price:  # we find the variable with the min price
            if min_price == None:
                min_price = self.all_variable_price[d]
                min_variable = d
            else:
                if min_price > self.all_variable_price[d]:
                    min_price = self.all_variable_price[d]
                    min_variable = d
        self.min_variable_mgm = min_variable
        if Iteration != 1:  # we set the rj to be the last price minus the current price
            self.Rj_mgm = self.price_of_Iteration[Iteration - 1] - min_price
        else:
            self.Rj_mgm = self.price_of_Iteration[Iteration] - min_price
        self.min_price = min_price

    def best_Rj(self, Iteration):  # function that help us to choose the best Rj per iteration
        flag = True  # we set the flag to be true - if I find better Rj than mine I set the flag to be false
        for i in self.Inbox_Rj:
            if self.Rj_mgm < i.content:
                flag = False
        if flag == True:  # if my Rj is the best Rj im changing my variable
            self.variable = self.min_variable_mgm
            self.price_of_Iteration[Iteration] = self.min_price
            if Iteration != 100:
                self.price_of_Iteration[Iteration + 1] = self.min_price
        else:  # else - I just set the price for this iteration
            self.price_of_Iteration[Iteration] = self.all_variable_price[self.variable]
            if Iteration != 100:
                self.price_of_Iteration[Iteration + 1] = self.all_variable_price[self.variable]


def MGM(list_agent):
    messege_from_all = dict()  # we have one mailbox for variable messages and one for Rj messages
    my_messege_Rj_for_all = dict()
    for i in range(1, 31):  # starting the mail boxes
        messege_from_all[i] = []
        my_messege_Rj_for_all[i] = []
    for agent in list_agent:  # each agent choose random variable
        varible = agent.random_variable()
        for agent_neighbor in agent.Constraints.keys():  # each agent send his variable to all his neighbors in the big mailbox
            my_messege = message(1, agent.id, agent_neighbor, varible)
            messege_from_all[agent_neighbor].append(my_messege)  # we give each agent his messages to his private mailbox
    i = 2
    while i < 101:
        messege_from_all_2 = dict()  # after all the agent send and read - we're restarting the mailboxes
        for key in range(1, 31):
            messege_from_all_2[key] = []
            my_messege_Rj_for_all[key] = []
        for agent in list_agent:
            agent.Inbox = copy.copy(messege_from_all[agent.id])  # every agent read all the messages from his neighbors
            agent.choose_variable_MGM(i - 1)  # function that choose variable in Mgm
            for agent_neighbor in agent.Constraints.keys():
                my_messege_Rj = message(i, agent.id, agent_neighbor, agent.Rj_mgm)  # send message to all your neighbors
                my_messege_Rj_for_all[agent_neighbor].append(my_messege_Rj)
        for agent in list_agent:
            agent.Inbox_Rj = copy.copy(my_messege_Rj_for_all[agent.id])
            agent.best_Rj(i)
            for agent_neighbor in agent.Constraints.keys():
                my_messege = message(1, agent.id, agent_neighbor, agent.variable)
                messege_from_all_2[agent_neighbor].append(my_messege)
        i += 2  # every Iteration its like two - because we're sending getting two messages
        messege_from_all = copy.copy(messege_from_all_2)
    sum_for_Iteration = dict()
    for i in list_agent:  # calcul the price of every Iteration
        for j in i.price_of_Iteration.keys():
            if j not in sum_for_Iteration.keys():
                sum_for_Iteration[j] = i.price_of_Iteration[j]
            else:
                sum_for_Iteration[j] += i.price_of_Iteration[j]
    for key in sum_for_Iteration.keys():
        sum_for_Iteration[key] = sum_for_Iteration[key] / 2
    return sum_for_Iteration


def DSA(p, list_agent):
    messege_from_all = dict()  # we have one mailbox for all variable messages
    for i in range(1, 31):
        messege_from_all[i] = []
    for agent in list_agent:  # each agent choose random variable
        varible = agent.random_variable()
        agent.calcul_first_price(1)
        for agent_neighbor in agent.Constraints.keys():   # each agent send his variable to all his neighbors in the big mailbox
            my_messege = message(1, agent.id, agent_neighbor, varible)
            messege_from_all[agent_neighbor].append(my_messege)   # we give each agent his messages to his private mailbox
    for i in range(2, 101):
        messege_from_all_2 = dict()  # after every agent send and get all the messages - we're restarting the mailbox
        for key in range(1, 31):
            messege_from_all_2[key] = []
        for agent in list_agent:
            agent.Inbox = copy.copy(messege_from_all[agent.id])  # read all the messages
            agent.choose_variable_dsa(p, i)  # choose variable and chane it in chance p
            for agent_neighbor in agent.Constraints.keys():
                my_messege = message(i, agent.id, agent_neighbor, agent.variable)  # send message to all your neighbors
                messege_from_all_2[agent_neighbor].append(my_messege)
        messege_from_all = copy.copy(messege_from_all_2)
    sum_for_Iteration = dict()
    for i in list_agent: # calcul the iteration total price
        for j in i.price_of_Iteration.keys():
            if j not in sum_for_Iteration.keys():
                sum_for_Iteration[j] = i.price_of_Iteration[j]
            else:
                sum_for_Iteration[j] += i.price_of_Iteration[j]
    for key in sum_for_Iteration.keys():
        sum_for_Iteration[key] = sum_for_Iteration[key] / 2
    return sum_for_Iteration


def random_Constraints(p, list_agent):
    for agent in list_agent: # choose how constraint with how
        for n in range(agent.id + 1, 31):
            x = random.random()
            if x < p:
                Constraints_1 = np.array(
                    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
                for i in range(0, 10): # choose random price to each constraint
                    for j in range(0, 10):
                        Constraints_1[i][j] = random.randint(1, 10)
                agent.det_Constraints(Constraints_1, n)
                list_agent[n - 1].det_Constraints(Constraints_1.T, agent.id)


def avg_price(sum_Iteration):  # get the average for the 10 times that the algorithm run
    sum_all_Iteration = dict()
    for i in sum_Iteration:
        for j in i.keys():
            if j not in sum_all_Iteration.keys():
                sum_all_Iteration[j] = i[j]
            else:
                sum_all_Iteration[j] += i[j]
    for key in sum_all_Iteration.keys():
        sum_all_Iteration[key] = sum_all_Iteration[key] / 10
    return sum_all_Iteration


def print_flot(avg_price_07, avg_price_04, avg_price_MGM_1): # print the plots
    lisMGM = sorted(avg_price_MGM_1.items())
    xMGM, yMGM = zip(*lisMGM)
    lis07 = sorted(avg_price_07.items())
    x07, y07 = zip(*lis07)
    lis04 = sorted(avg_price_04.items())
    x04, y04 = zip(*lis04)
    # plt.ylim(bottom=0, top=1200)
    plt.plot(x07, y07, label='line for p=0.7')
    plt.plot(x04, y04, label='line for p=0.4')
    plt.plot(xMGM, yMGM, label='line for MGM')
    plt.legend()
    plt.show()


def main():
    list_agent_1 = []
    list_agent_2 = []
    list_sum_Iteration_07 = []
    list_sum_Iteration_04 = []
    list_sum_Iteration_MGM = []
    for id in range(1, 31):  # set different ID for each agent
        agent_1 = agent(id)
        agent_2 = agent(id)
        list_agent_1.append(agent_1)
        list_agent_2.append(agent_2)
    random_Constraints(0.2, list_agent_1)
    random_Constraints(0.5, list_agent_2)
    for i in range(0, 10):  # problem 1
        sum_Iteration_07 = DSA(0.7, list_agent_1)
        sum_Iteration_04 = DSA(0.4, list_agent_1)
        sum_Iteration_MGM = MGM(list_agent_1)
        list_sum_Iteration_07.append(sum_Iteration_07)
        list_sum_Iteration_04.append(sum_Iteration_04)
        list_sum_Iteration_MGM.append(sum_Iteration_MGM)
    avg_price_07_1 = avg_price(list_sum_Iteration_07)
    avg_price_04_1 = avg_price(list_sum_Iteration_04)
    avg_price_MGM_1 = avg_price(list_sum_Iteration_MGM)
    print_flot(avg_price_07_1, avg_price_04_1, avg_price_MGM_1)
    list_sum_Iteration_07_2 = []
    list_sum_Iteration_04_2 = []
    list_sum_Iteration_MGM_2 = []
    for i in range(0, 10): # problem 2
        sum_Iteration_07 = DSA(0.7, list_agent_2)
        sum_Iteration_04 = DSA(0.4, list_agent_2)
        sum_Iteration_MGM = MGM(list_agent_2)
        list_sum_Iteration_07_2.append(sum_Iteration_07)
        list_sum_Iteration_04_2.append(sum_Iteration_04)
        list_sum_Iteration_MGM_2.append(sum_Iteration_MGM)
    avg_price_07_1_2 = avg_price(list_sum_Iteration_07_2)
    avg_price_04_1_2 = avg_price(list_sum_Iteration_04_2)
    avg_price_MGM_1_2 = avg_price(list_sum_Iteration_MGM_2)
    print_flot(avg_price_07_1_2, avg_price_04_1_2, avg_price_MGM_1_2)


main()
