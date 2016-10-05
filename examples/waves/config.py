"""Config values for easy changing."""

import numpy

OUTPUT_DUR_IN_SEC = 250  # Duration of output file, in seconds

OUTPUT_LOCATION = 'output/'
OUTPUT_BASE_FILENAME = 'waves'

MAX_AMPLITUDE = 0.6

NUM_CHANNELS = 1  # More channels not supported
SAMPLE_RATE = 44100
CHUNK_SIZE = 1024
SAMPLE_DATA_TYPE = numpy.int16  # Only int data types supported
BYTES_PER_SAMPLE = numpy.dtype(SAMPLE_DATA_TYPE).itemsize
SAMPLE_RANGE = (numpy.iinfo(SAMPLE_DATA_TYPE).max -
                numpy.iinfo(SAMPLE_DATA_TYPE).min)
