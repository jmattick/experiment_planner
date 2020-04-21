from Protocol import ProtocolLinkedList, RSDStep, SDStep, TDStep
from datetime import datetime, timedelta
from random import randint
from heapq import heappush, heappop
from timeit import default_timer
print("running runtime tests")


class ScheduleObject:
    def __init__(self, date=None, score=0):
        self.date = date
        self.score = score


def build_schedule(start, days):
    """Modified function for testing purpose. Original in utils.py"""
    schedule_objs = []
    # get total time of all events for each day
    curr = start
    for i in range(days):
        t = randint(0,500) # random time on schedule
        schedule_objs.append(ScheduleObject(curr, t))
        curr = curr + timedelta(days=1)
    return schedule_objs


def setup_RSDS_tests(n, days_between, gap):
    demo = ProtocolLinkedList()
    # add SDSteps to demo protocol
    demo.add_step(RSDStep('step', 5, days_between, gap))
    # add TDStep to protocool
    demo.add_step(TDStep('step', 5, n))
    return demo


def setup_SDS_tests(n, days_between, gap):
    demo = ProtocolLinkedList()
    # add SDSteps to demo protocol
    for i in range(n):
        demo.add_step(SDStep('step', 5, days_between, gap))
    print('total within')
    tot = demo.total_days()
    print(tot)
    return demo


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
                time = int(node[1].minutes)
                node_scores[node] = pen * (sch + time)
            for v in dag[node]:
                if v[1] is None:
                    node_scores[v] = float('inf')
                    final_node = v
                if not hasattr(v[1], 'minutes'):
                    new_score = node_scores[node]
                else:
                    print('schedule')
                    print(schedule[v[0] + i].date.weekday())
                    print(v[0] + i)
                    pen = int(penalty[schedule[v[0] + i].date.weekday()])
                    sch = int(schedule[v[0] + i].score)
                    time = int(v[1].minutes)
                    new_score = node_scores[node] + (pen * (sch + time))
                if new_score < node_scores[v]:  # if better path
                    node_scores[v] = new_score
        return node_scores[final_node]  # return final score

    def score_dijkstra(i):
        """Function using a dijkstra's shortest path algorithm"""
        dag, nodes = protocol_ll.build_DAG()
        distances = {node: float('inf') for node in nodes}  # initialize distances to inf
        distances[nodes[0]] = 0  # set first node dist to 0
        pq = [(0, nodes[0])] #initialize priority queue

        while len(pq) > 0:
            curr_d, curr_u = heappop(pq) # get node with lowest distance
            if curr_d > distances[curr_u]:  # if distance is greater than lowerst distance
                continue  # continue
            if curr_u not in dag:
                continue
            for v in dag[curr_u]:  # for adjacent v in graph
                if v[1] is None: #if terminal node
                    if v not in nodes:
                        nodes.append(v)
                        distances[v] = float('inf')
                    weight = 0
                else:
                    pen = int(penalty[schedule[v[0] + i].date.weekday()])
                    sch = int(schedule[v[0] + i].score)
                    time = int(v[1].minutes)
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

    for i in range(start_range):
        start = default_timer()
        all_scores.append((schedule[i].date, score(i)))
        mid = default_timer()
        #all_scores_dijkstra.append((schedule[i].date, score_dijkstra(i)))
        end = default_timer()
        times.append(mid - start)
        times_dijkstra.append(end-mid)
        if (end-mid) < (mid - start):
            dijkstra_faster.append(True)
        else:
            dijkstra_faster.append(False)
    # print('topological:')
    # for item in all_scores:
    #     print(item)
    # print(times)
    # print('dijkstra:')
    # for item in all_scores_dijkstra:
    #     print(item)
    # print(times_dijkstra)
    # print(dijkstra_faster)
    return all_scores


# Setup for runtime analysis
demo_ll = setup_RSDS_tests(3, 2, 1)
prot_days = demo_ll.total_days()
print('prot_days')
print(prot_days)
num_days = 14
total = (num_days + prot_days) * 2
print(total)
sched = build_schedule(datetime.now(), total)
print('sche len:')
print(len(sched))
print(score_alignments(demo_ll, sched, total, penalty=(1, 1, 1, 1, 1, 100, 100)))
