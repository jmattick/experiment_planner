from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .Protocol import ProtocolLinkedList, RSDStep, SDStep, TDStep
from .models import Event, Step
from heapq import heappush, heappop
from timeit import default_timer


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day)
        d = ''
        t = 0
        for event in events_per_day:
            t += int(event.minutes)
            d += f'<li class="calendar_list"> {event.get_html_url} </li>'
        trans = t / 480
        if trans > 1:
            trans = 1

        if day != 0:
            if self.month == datetime.today().month and day == datetime.today().day:
                return f"<td class='cal-cell' style='background-color:rgba(223,76,115,{trans})'><span id = 'today' class='date'>{day}</span><ul> {d} </ul></td>"
            return f"<td class='cal-cell' style='background-color:rgba(223,76,115,{trans})'><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal


class ScheduleObject:
    def __init__(self, date=None, score=0):
        self.date = date
        self.score = score


def build_schedule(start, days, events):
    schedule_objs = []
    # get total time of all events for each day
    curr = start
    for i in range(days):
        events_per_day = events.filter(start_time__date=curr)
        t = 0
        for e in events_per_day:
            t += int(e.minutes)
        schedule_objs.append(ScheduleObject(curr, t))
        curr = curr + timedelta(days=1)
    return schedule_objs


def format_dag_json(dag, nodes):
    """Function to format the dag, nodes output from build_DAG() into json for D3"""
    json_nodes = [] # { "id": 1, "name": node}, ...
    json_links = [] # {"source": 1, "target": 2}, ...
    for i in range(len(nodes)):
        node = nodes[i]
        json_n = {}
        json_n["id"] = i
        json_n["name"] = node[1].data
        json_nodes.append(json_n)
        for v in dag[node]:
            if v not in nodes:
                nodes.append(v)
                j = nodes.index(v)
                n = {}
                n["id"] = j
                n["name"] = "End"
                json_nodes.append(n)

            j = nodes.index(v)
            json_l = {}
            json_l["source"] = i
            json_l["target"] = j
            json_links.append(json_l)
    json_dag = {}
    json_dag["nodes"] = json_nodes
    json_dag["links"] = json_links
    print(json_dag)
    return json_dag


def protocol_to_protocol_ll(protocol):
    """Function to convert django protocol model into a ProtocolLinkedLIst"""
    steps = Step.objects.filter(protocol=protocol)  # get all step associated with protocol
    protocol_ll = ProtocolLinkedList()  # initialize protocol linked list
    for s in steps:  # loop through all steps to add to protocol linked list
        step_text = s.step_text
        time_min = s.time_min,
        days_between = s.days_between
        gap_days = s.gap_days
        if s.type == "TDS":
            step = TDStep(step_text, time_min, days_between, gap_days)
            step.id = s.pk
            protocol_ll.add_step(step)
        elif s.type == "RSDS":
            step = RSDStep(step_text, time_min, days_between, gap_days)
            step.id = s.pk
            protocol_ll.add_step(step)
        else:
            step = SDStep(step_text, time_min, days_between, gap_days)
            step.id = s.pk
            protocol_ll.add_step(step)
    dag, nodes = protocol_ll.build_DAG()  # store the dag and nodes in variables to be passed

    protocol.protocol_ll = protocol_ll

    protocol.nodes = nodes
    protocol.dag = []
    for node in nodes:
        u = node
        if hasattr(node[1], 'data'):
            u = (node[0], node[1].data)
        if node not in dag:
            continue
        v = list(dag[node])
        v.sort()
        w = []
        for i in v:
            if hasattr(i[1], 'data'):
                w.append((i[0], i[1].data))
            else:
                w.append((i[0], i[1]))
        protocol.dag.append(str(u) + ': ' + str(w))
    return protocol_ll


def score_dijkstra(dag, nodes, schedule, penalty=(1, 1, 1, 1, 1, 100, 100)):
    """Function using a dijkstra's shortest path algorithm"""
    distances = {node: float('inf') for node in nodes}  # initialize distances to inf
    parents = {node: None for node in nodes}  # initialize parent dictionary
    distances[nodes[0]] = 0  # set first node dist to 0
    pq = [(0, nodes[0])]  # initialize priority queue

    while len(pq) > 0:
        curr_d, curr_u = heappop(pq)  # get node with lowest distance
        if curr_d > distances[curr_u]:  # if distance is greater than lowerst distance
            continue  # continue
        if curr_u not in dag:
            continue
        for v in dag[curr_u]:  # for adjacent v in graph
            if v[1] is None:  # if terminal node
                if v not in nodes:
                    nodes.append(v)
                    distances[v] = float('inf')
                weight = 0
            else:
                pen = int(penalty[schedule[v[0]].date.weekday()])
                sch = int(schedule[v[0]].score)
                time = int(v[1].minutes[0])
                weight = pen * (sch + time)
            dist = curr_d + weight

            # is dist shorter than current shortest dist?
            if dist < distances[v]:
                distances[v] = dist  # update distance
                parents[v] = curr_u  # update parents
                heappush(pq, (dist, v))  # add node to priority queue
    return distances[nodes[-1]], parents, nodes[-1]  # return distance of terminal node


def score_alignments(protocol_ll, schedule, start_range, penalty=(1, 1, 1, 1, 1, 100, 100)):
    def score(i):
        """Function using a topological shortest path algorithm"""
        dag, nodes = protocol_ll.build_DAG()
        # initialize score of nodes to infinity
        node_scores = {}
        for node in nodes:
            node_scores[node] = float('inf')
        final_node = [0]
        # loop through nodes in topological order
        changed = False
        for node in nodes:
            if node_scores[node] == float('inf') and not changed:
                changed = True
                pen = int(penalty[schedule[node[0] + i].date.weekday()])
                sch = int(schedule[node[0] + i].score)
                time = int(node[1].minutes[0])
                node_scores[node] = pen * (sch + time)
            for v in dag[node]:
                if v[1] is None:
                    node_scores[v] = float('inf')
                    final_node = v
                if not hasattr(v[1], 'minutes'):
                    new_score = node_scores[node]
                else:
                    pen = int(penalty[schedule[v[0] + i].date.weekday()])
                    sch = int(schedule[v[0] + i].score)
                    time = int(v[1].minutes[0])
                    new_score = node_scores[node] + (pen * (sch + time))
                if new_score < node_scores[v]:  # if better path
                    node_scores[v] = new_score
        return node_scores[final_node]  # return final score


    def score_dijkstra(i):
        """Function using a dijkstra's shortest path algorithm"""
        dag, nodes = protocol_ll.build_DAG()
        distances = {node: float('inf') for node in nodes}  # initialize distances to inf
        distances[nodes[0]] = 0  # set first node dist to 0
        pq = [(0, nodes[0])]  # initialize priority queue

        while len(pq) > 0:
            curr_d, curr_u = heappop(pq) # get node with lowest distance
            if curr_d > distances[curr_u]:  # if distance is greater than lowerst distance
                continue  # continue
            if curr_u not in dag:
                continue
            for v in dag[curr_u]:  # for adjacent v in graph
                if v[1] is None:  # if terminal node
                    if v not in nodes:
                        nodes.append(v)
                        distances[v] = float('inf')
                    weight = 0
                else:
                    pen = int(penalty[schedule[v[0] + i].date.weekday()])
                    sch = int(schedule[v[0] + i].score)
                    time = int(v[1].minutes[0])
                    weight = pen * (sch + time)
                dist = curr_d + weight

                # is dist shorter than current shortest dist?
                if dist < distances[v]:
                    distances[v] = dist  # update distance
                    heappush(pq, (dist, v))  # add node to priority queue
        return distances[nodes[-1]]  # return distance of terminal node

    all_scores = []
    times = []
    all_scores_dijkstra = []
    times_dijkstra = []
    dijkstra_faster = []
    # z = open("runtime_tests.txt", "a")
    # z.write(str(datetime.now()) + '\n')
    # z.write(str(protocol_ll.build_DAG)+ '\n')
    # z.write("date\ttopological_score\ttopological_time\tdijkstra_score\tdijkstra_time\tdijkstra_faster\n")
    for i in range(start_range):
        start = default_timer()
        all_scores.append((schedule[i].date, score(i)))
        mid = default_timer()
        all_scores_dijkstra.append((schedule[i].date, score_dijkstra(i)))
        end = default_timer()
        times.append(mid - start)
        times_dijkstra.append(end-mid)
        if (end-mid) < (mid -start):
            dijkstra_faster.append(True)
        else:
            dijkstra_faster.append(False)
        # z.write(str(schedule[i].date.strftime('%y-%m-%d')) + '\t' + str(all_scores[-1][1]) + '\t' + str(times[-1]) + '\t' + str(all_scores_dijkstra[-1][1]) + '\t' + str(times_dijkstra[-1]) + '\t' + str(dijkstra_faster[-1]) + '\n')
    print(dijkstra_faster)
    return all_scores_dijkstra


def add_experiment_to_calendar(experiment, dag, nodes, schedule):
    _, parents, final = score_dijkstra(dag, nodes, schedule)

    curr = parents[final]
    while curr is not None:
        step = Step.objects.get(pk=curr[1].id)
        date = experiment.date + timedelta(days=curr[0])
        Event.objects.create(step=step, experiment_id=experiment.pk, title=experiment.name, start_time=date, minutes=step.time_min)
        curr = parents[curr]

