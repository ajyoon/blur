from pprint import pprint

from rand import *

# Test merge_markov_weights_dicts()
main_dict = {-10: 100, 10: 0}
pprint(main_dict)

noisy_dict = markov_weights_dict(-5, 7)
pprint(noisy_dict)

merged_dict = merge_markov_weights_dicts(main_dict, noisy_dict, 0.8)
pprint(merged_dict)
