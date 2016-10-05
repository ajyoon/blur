"""Config values for easy changing."""

NUM_CHANNELS = 1
SAMPLE_RATE = 44100
CHUNK_SIZE = 1024
BYTES_PER_SAMPLE = 2  # Int16
SAMPLE_RANGE = 2 ** (BYTES_PER_SAMPLE * 8)

OUTPUT_DUR_IN_SEC = 250  # Duration of output file, in seconds

OUTPUT_LOCATION = 'output/'
OUTPUT_BASE_FILENAME = 'waves'

MAX_AMPLITUDE = 0.6
