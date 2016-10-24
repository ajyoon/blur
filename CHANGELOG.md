# Change Log
---
### 0.4 (dev)

* The lowest workable Python 3 version has been correctly identified
  as `3.3`. This is not an API change, as it didn't work in earlier
  versions either.
* `markov.nodes` is now named `markov.node`
* `markov.node.Node.name` has been renamed to `markov.node.Node.value`
* `markov.graph.Graph.find_node_by_name()` has been renamed
  to `markov.graph.Graph.find_node_by_value()`
* `markov.graph.Graph.remove_node_by_name()` has been renamed
  to `markov.graph.Graph.remove_node_by_value()`
* `markov.graph.Graph.has_node_with_name()` has been renamed
  to `markov.graph.Graph.has_node_with_value()`
* In `markov.node.Node.merge_links_from()`, the keyword argument
  `merge_same_name_targets` has been renamed `merge_same_value_targets`
* `markov.graph.Graph.merge_nodes()` now preserves graph links pointing to
  `kill_node`, merging them into links pointing to `keep_node`
* `SoftColor.__init__()` now raises a `TypeError` if invalid arguments
  are passed to it for `red`, `green`, or `blue`.
* When called with neither `minimum` nor `maximum`,
  `rand.bound_weights()` now returns the input `weights` unmodified
  instead of raising a `TypeError`
* `rand._linear_interp()` now raises a `ProbabilityUndefinedError`
  instead of a `ValueError` when the tested x value lies outside of the
  given curve.
* SoftObject is now a new-style class
* The following names have been changed from attributes to properties
  with type-enforcing setters. Their API's have not changed except
  where noed:
  * `SoftOptions.options`
  * `SoftBool.prob_true`
  * `SoftFloat.weights`
  * `SoftInt.weights`
  * `SoftColor.red`, `SoftColor.blue`, `SoftColor.green` now store a copy
    of arguments assigned to them rather than the original. This will only
    affect existing code if `SoftInt` values are created manually before being
    passed to `SoftColor`'s, then and the `SoftInt` are manipulated outside of
    the context of the `SoftColor` with the expectation that the `SoftColor`'s
    attributes would be changed as well.

### 0.3

* The `Graph.from_string()` and `from_file()` methods now support
  punctuation marks inside words This allows words to be grouped
  correctly when they contain internal punctuation marks such
  as `we're` - cases like this will now be grouped into single nodes.
* The `Graph.from_string()` and `from_file()` additionally now support
  non-ascii characters.

### 0.2

* `rand.weighted_shuffle()` was broken in 0.1 and
  has been reimplemented as `rand.weighted_order()`
* `markov.graph.Graph.from_file()` and `.from_string()` now use `<<` and `>>`
  as the default word group markers and allow custom markers to be passed
  as optional arguments
* rand.weighted_choice() now has the option to return a 2-tuple of
  `(index, value)` in addition to the existing option of returning
  just the chosen value
* `rand` now has a `ProbabilityUndefinedError` for when invalid probability
  distributions are passed.
* stochastic tests in `rand` are now more reliable and should not raise false
  alarms as often.
* A folder of examples has been started with an implementation of
  Conway's Game of Life where cells are represented by soft objects which
  sometimes decide not to follow the rules. A file has also been started
  for a future list of external examples which use *blur*.
