This is a library that makes a markov chain out of games for the sake of simulating.

## Components

### State
This is just a dict.  It is scoped to the graph.  The dict is wrapped with a class with set and get methods, so that we can provide transformation logic if we wish.

### Action
Actions are units of logic, represented by a function.  They may read and alter the state.  After doing this it must return a node to move to; this node may depend on state.  Actions do not get trained.

A special action called "tip-off" starts each half.  It's upto the use case to define this function.  Any initial state can be set in that action.

### Nodes
Nodes must specify at construction time, state variables used (by key) and possible actions taken (by name).  At train time, the model will train for each node a multi-value categorical logistic regression with outputs being actions and inputs being the state variables specified.

Nodes also have a time histogram.  This specifies how many discrete seconds the graph spends in this node before taking a step.  (May be zero.)  Actions are not allowed to take any time; so all 40 min of a game must be accounted for in nodes.  This histogram gets trained.  The histogram may not depend on state.  If this is necessary, then each second spent in a state can be made into its own state.

### Graph
An object that contains a dict of nodes keyed by name, and a dict of actions keyed by name.  It also contains a state variable.

Note: There's no good way to validate a graph today.  That is we can't check that actions return existing nodes, that passed states exist, or that states passed to nodes exist.  We accept this for now.

### Datum

(Starting time, node name, state dict, action name)

## Example
As a V1 model, we'll do turn-over and score as the only actions.  With score-one (for fouls), score-two, and score-three as specific types of scores, with the assumption that the turn-over follows.  Notice that an offensive recovery after a missed one-and-one violates this assumption.  We build robustly enough that this is okay.  That is assumptions may be violated in training, but not in simulations.

This Graph would have a node, Play, with actions: turn-over, score-one, score-two, score-three.  The state considered for this node in the most simple model will be offense-only.

Note the convention established here that nodes are Pascal case and actions are hypenated.

## Save and load

For now we will save the graph directly using the dill package.  This is brittle because it breaks when we update code.  However, a more robust solution early on risks over-engineering.

## Code
The happy path looks like:

```
graph = Graph()
graph.add_node("Play", ["offense"], ["turn-over", "score-one", "score-two", "score-three"])
graph.add_action("turn-over", turn_over)  # functions turn_over, etc. defined elsewhere
graph.add_action("score-one", score_one)
graph.add_action("score-two", score_two)
graph.add_action("score-three", score_three)

raw_playbyplay = read_html(...)
data: List[Datum] = extract_data(raw_playbyplay)
graph.train(data)
# team_1 and team_2 must make an appearance in the train set.
print(graph.simulate(teams=["team_1", "team_2"]))  # Returns dict, e.g. {"team_1": 0.81, "team_2": 0.19}
```
