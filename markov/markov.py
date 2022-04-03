from collections import defaultdict
import random
from typing import Any, Callable, DefaultDict, List

Second = int
StateVar = str
ActionId = str
NodeId = str


class MarkovError(Exception):
    pass


class State(object):
    def __init__(self):
        self._state = dict()

    def __setattr__(self, __name: str, __value: Any) -> None:
        self._state[__name] = __value

    def __getattribute__(self, __name: str) -> Any:
        return self._state[__name]


class Histogram(object):
    def __init__(self):
        self._histogram: DefaultDict[Second, int] = defaultdict(int)
        self._denom: int = 0

    def push(self, second: Second) -> None:
        self._histogram[second] += 1
        self._denom += 1

    def sample(self) -> Second:
        r = random.randint(1, self._denom)
        for k, v in self._histogram.items():
            r -= v
            if r >= 0:
                return k
        else:
            raise MarkovError("Histogram sample didn't converge")


Action = Callable[[State], 'Node']


# TODO: Run black
class Node(object):
    def __init__(self, id: NodeId, states: List[StateVar], actions: List[ActionId]):
        self.id = id
        self.states = states
        self.actions = actions
        self.histogram = Histogram()


class Graph(object):
    def __init__(self):
        self.nodes = dict()
        self.actions = dict()
        self.state = State()

    def add_node(self, id: NodeId, states: List[StateVar], actions: List[ActionId]) -> None:
        assert id not in self.nodes
        self.nodes[id] = Node(id, states, actions)

    def add_action(self, id: ActionId, action: Action) -> None:
        assert id not in self.actions
        self.actions[id] = action
