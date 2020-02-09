from datetime import datetime


class Step:
    """
    Class to represent steps in a protocol.

    Attributes:
        prev: previous step in protocol or None
        next: next step in protocol or None
        data: information about step
        days: days since previous step, default 1
        details: extra information about protocol
        gap: how many days step can be delayed
    """

    def __init__(self, data=None, minutes=5, days=1, gap=0):
        """Initializes prev, next, data, days, details"""
        self.prev = None
        self.next = None
        self.data = data
        self.minutes = minutes
        self.days = days
        self.details = None
        self.gap = gap

    def add_details(self, details=None):
        """Updates step details"""
        self.details = details

    def show_details(self):
        """Returns step details"""
        return self.details

    def type(self):
        """Returns step type default"""
        return "default"

    def days_passed(self):  ##TODO fix this
        """Returns max total days passed in previous chain of steps"""
        passed = -1
        curr_step = self
        while curr_step.prev != None:
            passed += curr_step.days
            curr_step = curr_step.prev
        return passed


class SDStep(Step):
    """
    Class to represent step dependent steps in a protocol.
    Used for steps that depend on the days passed since the
    previous step.

    Attributes:
        prev: previous step in protocol or None
        next: next step in protocol or None
        data: information about step
        days: days since previous step, default 1
        details: extra information about protocol
        gap: how many days step can be delayed
    """

    def type(self):
        """Returns type of step (SDS)"""
        return "SDS"


class RSDStep(SDStep):
    """
    Class to represent repetitive step dependent steps in a protocol.
    Used for steps that depend on the days passed since the
    previous step and continue until the next step.

    Attributes:
        prev: previous step in protocol or None
        next: next step in protocol or None
        data: information about step
        days: days since previous step, default 1
        details: extra information about protocol
        gap: how many days step can be delayed
    """

    def type(self):
        """Returns type of step (RSDS)"""
        return "RSDS"


class TDStep(Step):
    """
    Class to represent time dependent steps in a protocol.
    Used for steps that depend on the days passed since the
    start of the protocol.

    Attributes:
        prev: previous step in protocol or None
        next: next step in protocol or None
        data: information about step
        days: days since start, default 1
        details: extra information about protocol
        gap: how many days step can be delayed
    """

    def __init__(self, data=None, minutes=5, days=1, gap=0):
        """Initializes prev, next, data, days, details"""
        self.prev = None
        self.next = None
        self.data = data
        self.minutes = minutes
        self.days = self.prev.days if self.prev != None else 1
        self.days_from_start = days
        self.details = None
        self.gap = gap

    def type(self):
        """Returns type of step (TDS)"""
        return "TDS"

    def days_passed(self):
        """Returns max total days passed"""
        return self.days_from_start + self.gap


class Protocol:
    """
    Class to represent a protocol as linked steps
    """

    def __init__(self):
        """Initializes head"""
        self.head = Step()

    def add_step(self, step=Step()):
        """Adds step to protocol"""
        if step.data == None:
            return None
        new_step = step
        curr = self.head
        while curr.next != None:
            curr = curr.next
        curr.next = new_step
        new_step.prev = curr

    def total_days(self):
        """Counts the total days of the protocol"""
        curr_step = self.head
        while curr_step.next != None:
            curr_step = curr_step.next
        return curr_step.days_passed()

    def length(self):
        """Returns the number of steps in the protocol"""
        curr = self.head
        total = 0
        while curr.next != None:
            total += 1
            curr = curr.next
        return total

    def display(self):
        """Prints out items in the protocol"""
        items = []
        curr_step = self.head
        while curr_step.next != None:
            curr_step = curr_step.next
            items.append(curr_step.data)
        print(items)

    def get(self, index):
        """Gets step at index"""
        if index >= self.length():
            print('Error: out of range')
            return None
        curr_id = 0
        curr_step = self.head
        while True:
            curr_step = curr_step.next
            if curr_id == index: return curr_step
            curr_id += 1

    def build_DAG(self):
        """Function to build a directed acyclical graph from a protocol"""
        G = {}
        nodes = set()
        curr = self.head.next
        end_node = (self.total_days() + 1, None)

        def add_node(G, d, step):
            """Function to recursively add a node to the graph"""
            if step.next == None:  # base case if no more nodes to add in path
                return
            d2 = d + step.days  # next day in protocol
            if step.type() == "TDS":  # if step is a time dependent step
                d2 = d + step.next.days  # next day depends on next step
            if step.type() == "RSDS":  # if step is repeating
                latest_day_next_step = step.next.days_from_start + step.next.gap  # last day in protocol that step can be added
                for i in range(step.gap + 1):  # loop through gap values
                    if d2 + i <= latest_day_next_step:  # if the base day + gap is less than the last day to add
                        if latest_day_next_step - (
                                d2 + i) >= step.days:  # if the gap between the last day is larger than the days between the repeating step
                            # setup tuples with day and step for edge to repeating step
                            u = (d, step.data)
                            v = (d2 + i, step.data)
                            # add edge to graph
                            if u in G:
                                G[u].add(v)
                            else:
                                nodes.add(u)
                                G[u] = set()
                                G[u].add(v)
                            add_node(G, d2 + i, step)  # call function on step with next day
                        if d2 + i >= step.next.days_from_start:  # if next day is greater than first day to start next step
                            # setup tuples with day and step for edge to next step
                            u = (d, step.data)
                            v = (d2 + i, step.next.data)
                            # add edge to graph
                            if u in G:
                                G[u].add(v)
                            else:
                                nodes.add(u)
                                G[u] = set()
                                G[u].add(v)
                            add_node(G, d2 + i, step.next)  # call function on next step
            else:  # for all other steps
                for i in range(step.gap + 1):  # loop through gap values
                    # setup tuples with day and step for edge
                    u = (d, step.data)
                    v = (d2 + i, step.next.data)
                    # add edge to graph
                    if u in G:
                        G[u].add(v)
                    else:
                        nodes.add(u)
                        G[u] = set()
                        G[u].add(v)
                    add_node(G, d2 + i, step.next)  # call funtion on next step

        add_node(G, 0, curr)  # call function on first node in protocol
        # sort nodes into a list
        nodes = list(nodes)
        nodes.sort()
        # add terminal node to any leaf nodes
        added = []
        for node in nodes:
            for item in G[node]:
                if item not in G:
                    G[item] = set()
                    G[item].add(end_node)
                    added.append(item)
        # add added items to nodes list
        for item in added:
            nodes.append(item)
        nodes.sort()

        return G, nodes  # return DAG and ordered list of nodes


class Schedule():

    def __init__(self, startdate=datetime.now().date()):
        self.default_scores = [100, 1, 1, 1, 1, 1, 100]
        self.startdate = startdate
        self.date_list = []
        self.score_list = []

    def display_today_score(self):
        print('today is ' + str(self.startdate.isoweekday()))
        print(self.default_scores[self.startdate.isoweekday()])


class Experiment(Protocol):

    def __init__(self, protocol, date=datetime.now().date()):
        self.protocol = protocol
        self.date = date


# example protocol
example_protocol = Protocol()
example_protocol.add_step(Step('A', 30))
example_protocol.add_step(SDStep('B', 20))
example_protocol.add_step(RSDStep('C', 5, 1, 1))
example_protocol.add_step(TDStep('D', 60, 7))

print('\nExample protocol:')
for i in range(example_protocol.length()):
    print(str(example_protocol.get(i).type()) + ': ' + str(example_protocol.get(i).data) + ', ' + str(
        example_protocol.get(i).minutes) + ', ' + str(example_protocol.get(i).days_passed()))

# build DAG

print('\n DAG')
dag, nodes = example_protocol.build_DAG()
for node in nodes:
    print(str(node) + ': ' + str(dag[node]))

### initialize schedule
##sd = Schedule()
##sd.display_today_score()
### initialize demo protocol
demo1 = Protocol()

# add steps to demo protocol
demo1.add_step(Step('start'))

demo1.add_step(RSDStep('daily', 5, 1, 0))

demo1.add_step(TDStep('p1 13-15', 60, 13, 2))

demo1.add_step(RSDStep('every 2-3d', 5, 2, 1))

demo1.add_step(TDStep('p2 25-30', 60, 25, 5))

# print protocol info
print("\nDemo protocol:")
for i in range(demo1.length()):
    print(str(demo1.get(i).type()) + ': ' + str(demo1.get(i).data) + ', ' + str(demo1.get(i).days_passed()))

print("\nDemo protocol # of steps: " + str(demo1.length()))
print("Demo protocol # of days: " + str(demo1.total_days()))

print('\ndemo1 DAG')
dag, nodes = demo1.build_DAG()
for node in nodes:
    print(str(node) + ': ' + str(dag[node]))

###demo experiment
##exp1 = Experiment(demo1)
##print(str(exp1.date))
##print(exp1.date.isoweekday())
