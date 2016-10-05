#!/usr/bin/env python3
"""Use the iching to dictate the behavior of a series of sine waves."""

import os
import random
import wave
import math

import numpy

from blur import iching
from blur import rand

from examples.waves import oscillator
from examples.waves import amplitude
from examples.waves import config


###############################################################################
#                                                        Initialize oscillators
###############################################################################

# A mapping of pitch classes to frequencies above concert A
frequency_map = {
    9: 440,      # A
    10: 466.16,  # A# / Bb
    11: 493.88,  # B
    0: 523.25,   # C
    1: 554.37,   # C# / Db
    2: 587.33,   # D
    3: 622.25,   # D# / Eb
    4: 659.26,   # E
    5: 698.46,   # F
    6: 739.99,   # F# / Gb
    7: 783.99,   # G
    8: 830.61    # G# / Ab
}

# Primary pitches to be used in the oscillators
# Multiple / divide frequencies by powers of 2 to change octaves
primary_osc_pitches = [
    frequency_map[10] / 8,
    frequency_map[5] / 4,
    frequency_map[7] / 2,
    frequency_map[3],
    frequency_map[10] / 4,
    frequency_map[10] / 4,
    frequency_map[10] * 2,
    frequency_map[9] * 4,
]

# initialize oscillators
osc_list = []
for frequency in primary_osc_pitches:
    osc_list.append(
        oscillator.Oscillator(
            frequency,
            amplitude.AmplitudeHandler(
                init_value=0,
                drift_target_weights=[
                    (-1, 1), (0.02, 6), (0.2, 5), (0.3, 1), (0.4, 0)
                    ]
            )
        )
    )


# add some random pitches ####################################################
rand_pitch_weights = [(120, 0), (220, 250), (440, 500), (1000, 1), (5000, 0)]
pitches = [rand.weighted_rand(rand_pitch_weights) for i in range(4)]

for pitch in pitches:
    osc_list.append(
        oscillator.Oscillator(
            pitch,
            amplitude.AmplitudeHandler(
                init_value=0,
                drift_target_weights=[
                    (-2, 30), (0.02, 8), (0.05, 2), (0.1, 0.1), (0.3, 0)
                ],
                change_rate_weights=[
                    (0.00001, 12000),
                    (0.0001, 100),
                    (0.001, 10)
                ],
            )
        )
    )

###############################################################################
#                                                        Setup output wave file
###############################################################################

out_dir = os.path.join(os.path.dirname(__file__),
                       config.OUTPUT_LOCATION)
# Ensure out dir exists
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)
out_path = os.path.join(out_dir, config.OUTPUT_BASE_FILENAME + '.wav')
# If conflicting files exist, add/increment suffix until an available
# filename is found
suffix = 0
while os.path.isfile(out_path):
    suffix += 1
    out_path = os.path.join(out_dir,
                            '{}_{}.wav'.format(
                                config.OUTPUT_BASE_FILENAME, suffix))
out_file = wave.open(out_path, 'wb')
out_file.setparams((
    config.NUM_CHANNELS,
    config.BYTES_PER_SAMPLE,
    config.SAMPLE_RATE,
    0,
    'NONE',
    'not compressed'))

###############################################################################
#                                           Function to handle random processes
###############################################################################


def step_random_processes(oscillators):
    """
    Args:
        oscillators (list): A list of oscillator.Oscillator objects
            to operate on

    Returns: None
    """
    if not rand.prob_bool(0.01):
        return
    amp_bias_weights = [(0.001, 1), (0.1, 100), (0.15, 40), (1, 0)]
    # Find out how many oscillators should move
    num_moves = iching.get_hexagram('NAIVE') % len(oscillators)
    for i in range(num_moves):
        pair = [gram % len(oscillators)
                for gram in iching.get_hexagram('THREE COIN')]
        amplitudes = [(gram / 64) * rand.weighted_rand(amp_bias_weights)
                      for gram in iching.get_hexagram('THREE COIN')]
        oscillators[pair[0]].amplitude.drift_target = amplitudes[0]
        oscillators[pair[1]].amplitude.drift_target = amplitudes[1]


###############################################################################
#                                                Function to build audio chunks
###############################################################################


def build_chunk(oscillators):
    """
    Args:
        oscillators (list): A list of oscillator.Oscillator objects
            to build chunks from

    Returns:
        str:
    """
    step_random_processes(oscillators)
    subchunks = []
    for osc in oscillators:
        osc.amplitude.step_amp()
        osc_chunk = osc.get_samples(config.CHUNK_SIZE)
        if osc_chunk is not None:
            subchunks.append(osc_chunk)
    new_chunk = sum(subchunks)
    if isinstance(new_chunk, int):
        new_chunk = numpy.zeros(config.CHUNK_SIZE)
    chunk_amplitude = amplitude.find_amplitude(new_chunk)
    if chunk_amplitude > config.MAX_AMPLITUDE:
        new_chunk = amplitude.normalize_amplitude(new_chunk,
                                                  config.MAX_AMPLITUDE)
        # Find the average amp of every oscillator
        avg_amp = (sum(osc.amplitude.value for osc in oscillators) /
                   len(oscillators))
        for osc in oscillators:
            if (osc.amplitude.value > avg_amp and rand.prob_bool(0.1) or
                    rand.prob_bool(0.01)):
                osc.amplitude.drift_target = random.uniform(-5, 0)
                osc.amplitude.change_rate = rand.weighted_rand(
                    osc.amplitude.change_rate_weights)
    return new_chunk.astype(numpy.int16).tostring()

###############################################################################
#                                                                      Liftoff!
###############################################################################

print('Generating sine waves in {}'.format(out_path))
chunks_needed = int((config.OUTPUT_DUR_IN_SEC *
                     (config.SAMPLE_RATE / config.CHUNK_SIZE)))
for i in range(chunks_needed):
    out_file.writeframes(build_chunk(osc_list))
    if i % int(chunks_needed / 5) == 0:
        # Print progress
        print('{}%...'.format(math.ceil((i / chunks_needed) * 100)))

# Clean up and exit

print('File written to {}'.format(out_path))
out_file.close()
