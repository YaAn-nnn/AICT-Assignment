import heapq
import math
import itertools
from graph import coordinates


class Node:
    """
    state  = station name
    parent = previous Node
    action = (from_station, to_station, base_minutes, line_code)
    g      = path cost from start in minutes (used by A*)
    line   = line used to reach this node (for transfer detection during cost-based search)
    """
    def __init__(self, state, parent=None, action=None, g=0.0, line=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.line = line


class StackFrontier:
    def __init__(self):
        self.frontier = []

    def add(self, item):
        self.frontier.append(item)

    def empty(self):
        return len(self.frontier) == 0

    def contains_state(self, state):
        # item may be Node or (Node, depth)
        for x in self.frontier:
            node = x[0] if isinstance(x, tuple) else x
            if node.state == state:
                return True
        return False

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        return self.frontier.pop()


class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        return self.frontier.pop(0)


class SearchAlgorithms:
    def __init__(self, graph):
        self.graph = graph

        # minutes added when line changes between consecutive edges
        self.transfer_penalty = 5

        self.crowding_multiplier = {
            "peak": 1.3,
            "off_peak": 1.0,
            "disrupted": 1.5
        }

        # convert coordinate distance units into minutes for heuristic
        self.heuristic_min_per_unit = 3.0

        # tie-breaker counter for heapq
        self._counter = itertools.count()

    def heuristic_minutes(self, a, b):
        x1, y1 = coordinates[a]
        x2, y2 = coordinates[b]
        dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return dist * self.heuristic_min_per_unit

    def edge_cost_minutes(self, base_minutes, time_of_day="off_peak", transfer=False):
        mult = self.crowding_multiplier.get(time_of_day, 1.0)
        cost = base_minutes * mult
        if transfer:
            cost += self.transfer_penalty
        return cost

    def reconstruct_path(self, node):
        stations = []
        actions = []
        while node is not None:
            stations.append(node.state)
            if node.action is not None:
                actions.append(node.action)
            node = node.parent
        stations.reverse()
        actions.reverse()
        return stations, actions

    def calculate_path_cost(self, path, time_of_day="off_peak"):
        """
        Post-evaluate cost for any algorithm output.
        Transfer penalty triggers only when line changes.
        """
        if not path or len(path) == 1:
            return 0.0

        total = 0.0
        prev_line = None

        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]

            found = False
            for nbr, base_minutes, line in self.graph[u]:
                if nbr == v:
                    transfer = (prev_line is not None and prev_line != line)
                    total += self.edge_cost_minutes(base_minutes, time_of_day, transfer)
                    prev_line = line
                    found = True
                    break

            if not found:
                return float("inf")

        return total

    # DFS
    def dfs(self, start, goal, max_depth=None, time_of_day="off_peak"):
        max_depth = len(self.graph)

        start_node = Node(state=start)
        frontier = StackFrontier()
        frontier.add((start_node, 0))  # (node, depth)

        nodes_expanded = 0

        while not frontier.empty():
            node, depth = frontier.remove() #LIFO
            nodes_expanded += 1

            if node.state == goal:
                path, _ = self.reconstruct_path(node)
                return path, self.calculate_path_cost(path, time_of_day), nodes_expanded

            if depth >= max_depth:
                continue

            path_stations, _ = self.reconstruct_path(node)
            in_path = set(path_stations)

            for neighbor, base_minutes, line in self.graph[node.state]:
                if neighbor in in_path:
                    continue
                child = Node(
                    state=neighbor,
                    parent=node,
                    action=(node.state, neighbor, base_minutes, line)
                )
                frontier.add((child, depth + 1))

        return None, float("inf"), nodes_expanded

    # BFS
    def bfs(self, start, goal, time_of_day="off_peak"):
        start_node = Node(state=start)
        frontier = QueueFrontier()
        frontier.add(start_node)

        explored = set()
        nodes_expanded = 0

        while not frontier.empty():
            node = frontier.remove() #FIFO
            nodes_expanded += 1

            if node.state == goal:
                path, _ = self.reconstruct_path(node)
                return path, self.calculate_path_cost(path, time_of_day), nodes_expanded

            explored.add(node.state)

            for neighbor, base_minutes, line in self.graph[node.state]:
                if neighbor in explored or frontier.contains_state(neighbor):
                    continue
                child = Node(
                    state=neighbor,
                    parent=node,
                    action=(node.state, neighbor, base_minutes, line)
                )
                frontier.add(child)

        return None, float("inf"), nodes_expanded

    # GBFS
    def gbfs(self, start, goal, time_of_day="off_peak"):
        pq = []
        start_node = Node(state=start)
        heapq.heappush(pq, (self.heuristic_minutes(start, goal), next(self._counter), start_node))

        explored = set()
        nodes_expanded = 0

        while pq:
            _, _, node = heapq.heappop(pq) #underscore: ignores heuristic and counter
            nodes_expanded += 1

            if node.state == goal:
                path, _ = self.reconstruct_path(node)
                return path, self.calculate_path_cost(path, time_of_day), nodes_expanded

            if node.state in explored:
                continue
            explored.add(node.state)

            for neighbor, base_minutes, line in self.graph[node.state]:
                if neighbor in explored:
                    continue
                child = Node(
                    state=neighbor,
                    parent=node,
                    action=(node.state, neighbor, base_minutes, line)
                )
                heapq.heappush(pq, (self.heuristic_minutes(neighbor, goal), next(self._counter), child))

        return None, float("inf"), nodes_expanded

    # A*
    def a_star(self, start, goal, time_of_day="off_peak"):
        start_node = Node(state=start, g=0.0, line=None)

        pq = []
        heapq.heappush(pq, (self.heuristic_minutes(start, goal), next(self._counter), start_node))

        # best known g for (station, line_context)
        best_g = {}
        nodes_expanded = 0

        while pq:
            _, _, node = heapq.heappop(pq)
            nodes_expanded += 1

            if node.state == goal:
                path, _ = self.reconstruct_path(node)
                return path, node.g, nodes_expanded

            state_key = (node.state, node.line)
            if state_key in best_g and best_g[state_key] <= node.g:
                continue
            best_g[state_key] = node.g

            for neighbor, base_minutes, line in self.graph[node.state]:
                transfer = (node.line is not None and node.line != line)
                step = self.edge_cost_minutes(base_minutes, time_of_day, transfer)
                new_g = node.g + step
                new_f = new_g + self.heuristic_minutes(neighbor, goal)

                child = Node(
                    state=neighbor,
                    parent=node,
                    action=(node.state, neighbor, base_minutes, line),
                    g=new_g,
                    line=line
                )
                heapq.heappush(pq, (new_f, next(self._counter), child))

        return None, float("inf"), nodes_expanded