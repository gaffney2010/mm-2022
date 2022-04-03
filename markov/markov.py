from collections import defaultdict
import random
from typing import Any, Callable, DefaultDict, Dict, List

import attr
import pandas as pd
from sklearn.linear_model import LogisticRegression

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

    def __contains__(self, __name: str) -> bool:
        return __name in self._state


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
    # TODO: Consider making these sets.
    def __init__(self, id: NodeId, states: List[StateVar], actions: List[ActionId]):
        self.id = id
        self.states = states
        self.actions = actions
        self.histogram = Histogram()
        self.model = None

    # TODO: Profile and improve
    def train(self, data: List['Datum']) -> None:
        rows = list()
        for datum in data:
            assert datum.node_id == self.id
            assert datum.action_id in self.actions
            row = dict()
            for s in self.states:
                assert s in datum.state
                row[s] = datum.state[s]
            row["target"] = datum.action_id
            rows.append(row)

            self.histogram.push(datum.duration)
        df = pd.DataFrame(rows)

        dummy_dfs = list()
        for s in self.states:
            dummy_dfs.append(pd.get_dummies(df[s]))
        X = pd.concat(dummy_dfs, axis=1)
        y = df["target"]

        self.model = LogisticRegression().fit(X, y)


@attr.s(frozen=True)
class Datum(object):
    duration: Second = attr.ib()
    node_id: NodeId = attr.ib()
    state: State = attr.ib()
    action_id: ActionId = attr.ib()


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

    def train(self, data: List[Datum]) -> None:
        pass

    # TODO: Import School type
    def simulate(self, teams: List[str]) -> Dict[str, float]:
        pass
