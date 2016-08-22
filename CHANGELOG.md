# Change Log
---
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
