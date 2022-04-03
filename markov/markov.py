from collections import defaultdict
import random
from typing import Any, Callable, DefaultDict, Dict, List, Tuple

import attr
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import tqdm

Second = int
StateVar = str
ActionId = str
NodeId = str

EPSILON = 1e-6  # Some small number


class MarkovError(Exception):
    pass


class State(object):
    def __init__(self):
        self._state = dict()

    def __setitem__(self, name: str, value: Any) -> None:
        self._state[name] = value

    def __getitem__(self, name: str) -> Any:
        return self._state[name]

    def __contains__(self, name: str) -> bool:
        return name in self._state

    def __str__(self) -> str:
        return str(self._state)

    def __repr__(self) -> str:
        return str(self)


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
            if r <= 0:
                return k
        else:
            raise MarkovError("Histogram sample didn't converge")


Action = Callable[[State], "Node"]


class Node(object):
    def __init__(self, id: NodeId, states: List[StateVar], actions: List[ActionId]):
        self.id = id
        self.states = states
        self.state_values: Dict[StateVar, List] = dict()
        self.num_values: int = 0
        self.actions = actions
        self.histogram = Histogram()
        self.model = None

    def _row_from_state(self, state: State) -> np.ndarray:
        assert self.num_values > 0
        result = np.zeros(self.num_values)
        i = 0
        for s in self.states:
            for v in self.state_values[s]:
                if state[s] == v:
                    result[i] = 1
                i += 1
        return result

    # TODO: Profile and improve
    def train(self, data: List["Datum"]) -> None:
        # Start with assertions
        for datum in data:
            assert datum.node_id == self.id
            assert datum.action_id in self.actions
        for s in self.states:
            assert s in datum.state

        # Prepare state_values
        state_values = defaultdict(set)
        for datum in data:
            for s in self.states:
                state_values[s].add(datum.state[s])
        self.state_values = {k: list(v) for k, v in state_values.items()}
        for v in state_values.values():
            self.num_values += len(v)

        X = np.stack((self._row_from_state(datum.state) for datum in data))
        y = [datum.action_id for datum in data]

        self.model = LogisticRegression().fit(X, y)

        # Also do the histogram
        for datum in data:
            self.histogram.push(datum.duration)

    def simulate(self, state: State) -> Tuple[Second, ActionId]:
        assert self.model is not None
        X = [self._row_from_state(state)]
        pred = self.model.predict_proba(X)[0]
        r = random.random()
        for action, prob in zip(self.model.classes_, pred):
            r -= prob
            if r <= EPSILON:
                return self.histogram.sample(), action
        else:
            raise MarkovError("No action selected.")


@attr.s(frozen=True)
class Datum(object):
    duration: Second = attr.ib()
    node_id: NodeId = attr.ib()
    state: State = attr.ib()
    action_id: ActionId = attr.ib()


class SimLogger(object):
    def __init__(self):
        pass

    def append(self, s: str) -> None:
        pass

    def dump(self) -> str:
        pass


class Graph(object):
    def __init__(self):
        self.nodes = dict()
        self.actions = dict()

    def add_node(
        self, id: NodeId, states: List[StateVar], actions: List[ActionId]
    ) -> None:
        assert id not in self.nodes
        self.nodes[id] = Node(id, states, actions)

    def add_action(self, id: ActionId, action: Action) -> None:
        assert id not in self.actions
        self.actions[id] = action

    def train(self, data: List[Datum]) -> None:
        # TODO: This fails in multistate, because it sends all data to all nodes.
        for node in self.nodes.values():
            node.train(data)

    # TODO: Import School type
    def simulate(
        self, teams: List[str], logger: SimLogger = SimLogger()
    ) -> Dict[str, int]:
        # state is simulation-specific
        state = State()

        # Special states
        state["_teams"] = teams
        state["_scores"] = {t: 0 for t in teams}

        logger.append("clock;action;state;node")

        # Two halfs
        for _ in range(2):
            log_entry = list()

            # TODO: Use constants instead of literals
            clock = 60 * 20
            node_id = self.actions["tip-off"](state)
            # TODO: Refactor to avoid repeated code.
            log_entry.append(str(clock))
            log_entry.append("tip-off")
            log_entry.append(str(state))
            log_entry.append(node_id)
            logger.append(";".join(log_entry))
            log_entry = list()

            while True:
                duration, action_id = self.nodes[node_id].simulate(state)
                clock -= duration
                if clock < 0:
                    break
                node_id = self.actions[action_id](state)
                log_entry.append(str(clock))
                log_entry.append(action_id)
                log_entry.append(str(state))
                log_entry.append(node_id)
                logger.append(";".join(log_entry))
                log_entry = list()

        return state["_scores"]


def sims(graph: Graph, teams: List[str], num_sims: int = 1000) -> Dict[str, float]:
    """We may have ties."""
    assert len(teams) == 2

    win_prob = {t: 0.0 for t in teams}
    for _ in tqdm.tqdm(range(num_sims)):
        final_score = graph.simulate(teams)
        if final_score[teams[0]] > final_score[teams[1]]:
            win_prob[teams[0]] += 1.0 / num_sims
        if final_score[teams[0]] < final_score[teams[1]]:
            win_prob[teams[1]] += 1.0 / num_sims
    return win_prob
