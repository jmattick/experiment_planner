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

    def days_passed(self): ##TODO fix this
        """Returns total days passed in previous chain of steps"""
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
        self.days = 1
        self.days_from_start = days
        self.details = None
        self.gap = gap
        
    def type(self):
        """Returns type of step (TDS)"""
        return "TDS"


class Protocol:
    """
    Class to represent a protocol as linked steps
    """
    def __init__(self):
        self.head = Step()

    def add_step(self, step=Step()):
        if step.data == None:
            return None
        new_step = step
        curr = self.head
        while curr.next != None:
            curr = curr.next
        curr.next = new_step
        new_step.prev = curr
        
    def total_days(self):
        curr_step = self.head
        while curr_step.next != None:
            curr_step = curr_step.next
        return curr_step.days_passed()

    def length(self):
        curr = self.head
        total = 0
        while curr.next!=None:
            total += 1
            curr = curr.next
        return total

    def display(self):
        items = []
        curr_step = self.head
        while curr_step.next != None:
            curr_step = curr_step.next
            items.append(curr_step.data)
        print(items)

    def get(self, index):
        if index >= self.length():
            print('Error: out of range')
            return None
        curr_id = 0
        curr_step = self.head
        while True:
            curr_step = curr_step.next
            if curr_id == index: return curr_step
            curr_id +=1


class Experiment(Protocol):

    def __init__(self, date):
        self.date = date

# initialize demo protocol
demo1 = Protocol()

# add steps to demo protocol
demo1.add_step(Step('start'))

for i in range(13):
    demo1.add_step(SDStep('daily media change'))
    
demo1.add_step(TDStep('passage cells on day 13-15'))

for i in range(5):
    demo1.add_step(SDStep('media change every 2-3 days',2))

demo1.add_step(TDStep('passage cells on day 25-30'))

# print protocol info
print("\nDemo protocol:")
for i in range(demo1.length()):
    print(str(demo1.get(i).type()) + ': ' + str(demo1.get(i).data) + ', ' + str(demo1.get(i).days_passed()))

print("\nDemo protocol # of steps: " + str(demo1.length()))
print("Demo protocol # of days: " + str(demo1.total_days()))

# initialize demo protocol 2
demo2 = Protocol()

# add steps to demo protocol
for i in range(13):
    demo2.add_step(SDStep('day ' + str(i) + ' media change',1))
demo2.add_step(TDStep('passage cells on day 13-15',13,2))
demo2.add_step(RSDStep('media change every 2-3 days',2,3))
demo2.add_step(TDStep('passage cells on day 25-30',25,5))


# print protocol info
print("\nDemo protocol:")
for i in range(demo2.length()):
    print(str(demo2.get(i).type()) + ': ' + str(demo2.get(i).data) + ', ' + str(demo2.get(i).days_passed()))

print("\nDemo protocol # of steps: " + str(demo2.length()))
print("Demo protocol # of days: " + str(demo2.total_days()))

# demo experiment
demo_exp = Experiment('today')
