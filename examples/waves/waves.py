#!/usr/bin/env python
"""An example using the I Ching to control a series of oscillators.

This script can be executed directly from the command line: ::

    cd blur/examples/waves
    python waves.py

We construct a series of oscillators using a combination of
deterministic and indeterminate processes operating on their
various parameters, including frequency and amplitude biases.

We then generate a ``.wav`` file, storing it in an output folder.
The contents of the file are populated by generating and mixing
samples from the various oscillators as chance processes manipulate
the amplitudes of each independent oscillator.

To see where ``blur`` is used most in this example, have a look at
the code below. Of particular interest may be the oscillator
initialization below, the function ``step_random_processes()``,
and the function ``build_chunk()``.
"""

from __future__ import division
import math
import os
import wave

import oscillator
import amplitude
import config

import numpy

from blur import iching
from blur import rand


###############################################################################
#                                                        Initialize oscillators
###############################################################################

# A mapping of pitch classes to frequencies above concert A
frequency_map = {
    9:  440,      # A
    10: 466.16,   # A# / Bb
    11: 493.88,   # B
    0:  523.25,   # C
    1:  554.37,   # C# / Db
    2:  587.33,   # D
    3:  622.25,   # D# / Eb
    4:  659.26,   # E
    5:  698.46,   # F
    6:  739.99,   # F# / Gb
    7:  783.99,   # G
    8:  830.61    # G# / Ab
}

# Primary pitches to be used in the oscillators
# Multiple / divide frequencies by powers of 2 to change octaves
primary_osc_pitches = [
    frequency_map[10] / 8,  # Bb1
    frequency_map[5]  / 4,  # F3
    frequency_map[10] / 4,  # Bb2
    frequency_map[7]  / 2,  # G4
    frequency_map[3]     ,  # Eb5
    frequency_map[10] * 2,  # Bb6
    frequency_map[9]  * 4,  # A6
]

# Initialize primary pitch oscillators
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

# Initialize softer oscillators slightly out of tune with consonant pitches
detune_weights = rand.normal_distribution(0, 20)
detune_base_pitches_weights = [(frequency_map[10], 50),
                               (frequency_map[0], 1),
                               (frequency_map[2], 30),
                               (frequency_map[3], 40),
                               (frequency_map[5], 80),
                               (frequency_map[7], 30),
                               (frequency_map[9], 20)]
octave_choice_weights = [(1/8, 20),
                         (1/4, 15),
                         (1/2, 10),
                         (1, 5),
                         (2, 5),
                         (4, 5)]
# Find detuned pitches
pitches = [((rand.weighted_choice(detune_base_pitches_weights) +  # Base pitch
             rand.weighted_rand(detune_weights)) *                # Detune
            rand.weighted_choice(octave_choice_weights))          # Set Octave
           for i in range(50)]
amp_multiplier_weights = [(0.05, 10), (0.2, 2), (0.7, 1)]

for pitch in pitches:
    osc_list.append(
        oscillator.Oscillator(
            pitch,
            amplitude.AmplitudeHandler(
                init_value=0,
                drift_target_weights=[
                    (-2, 30), (0.02, 8), (0.05, 2), (0.1, 0.1), (0.3, 0)],
                change_rate_weights=[
                    (0.00001, 12000),
                    (0.0001, 100),
                    (0.001, 10)],
            ),
            amplitugde_multiplier=rand.weighted_rand(amp_multiplier_weights)
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
    0,                        # Initial frame count
    'NONE',                   # Set compression (not supported in stdlib)
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
    Build an audio chunk and progress the oscillator states.

    Args:
        oscillators (list): A list of oscillator.Oscillator objects
            to build chunks from

    Returns:
        str: a string of audio sample bytes ready to be written to a wave file
    """
    step_random_processes(oscillators)
    subchunks = []
    for osc in oscillators:
        osc.amplitude.step_amp()
        osc_chunk = osc.get_samples(config.CHUNK_SIZE)
        if osc_chunk is not None:
            subchunks.append(osc_chunk)
    if len(subchunks):
        new_chunk = sum(subchunks)
    else:
        new_chunk = numpy.zeros(config.CHUNK_SIZE)
    # If we exceed the maximum amplitude, handle it gracefully
    chunk_amplitude = amplitude.find_amplitude(new_chunk)
    if chunk_amplitude > config.MAX_AMPLITUDE:
        # Normalize the amplitude chunk to mitigate immediate clipping
        new_chunk = amplitude.normalize_amplitude(new_chunk,
                                                  config.MAX_AMPLITUDE)
        # Pick some of the offending oscillators (and some random others)
        # and lower their drift targets
        avg_amp = (sum(osc.amplitude.value for osc in oscillators) /
                   len(oscillators))
        for osc in oscillators:
            if (osc.amplitude.value > avg_amp and rand.prob_bool(0.1) or
                    rand.prob_bool(0.01)):
                osc.amplitude.drift_target = rand.weighted_rand(
                    [(-5, 1), (0, 10)])
                osc.amplitude.change_rate = rand.weighted_rand(
                    osc.amplitude.change_rate_weights)
    return new_chunk.astype(config.SAMPLE_DATA_TYPE).tostring()

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
        print('{}%...'.format(int(math.ceil((i / chunks_needed) * 100))))

# Clean up and exit
print('File written to {}'.format(out_path))
out_file.close()
