from __future__ import division

import numpy

import config
from amplitude import AmplitudeHandler


class Oscillator(object):
    """
    A sine wave oscillator.
    """

    sample_rate = config.SAMPLE_RATE

    def __init__(self,
                 frequency,
                 amplitude=None,
                 amplitude_multiplier=1):
        """
        Args:
            frequency (float): Frequency in herz of the oscillator
            amplitude (AmplitudeHandler): Amplitude handler for the oscillator
            amplitude_multiplier (float): A factor to multiply amplitudes by
                during sample generation in addition to transformations
                occuring within ``self.amplitude``.
        """
        if frequency <= 0:
            raise ValueError("Oscillator.frequency cannot be <= 0")
        self.frequency = frequency
        self.last_played_sample = 0
        if amplitude:
            self.amplitude = amplitude
        else:
            self.amplitude = AmplitudeHandler(0)
        self.amplitude_multiplier = amplitude_multiplier
        # Build a cache of a full period of the wave
        # and store it in self.wave_cache
        self.cache_length = round(self.sample_rate / self.frequency)
        factor = self.frequency * ((numpy.pi * 2) / self.sample_rate)
        self.wave_cache = numpy.arange(self.cache_length)
        self.wave_cache = (numpy.sin(self.wave_cache * factor) *
                           config.SAMPLE_RANGE)

    def get_samples(self, sample_count):
        """
        Fetch a number of samples from self.wave_cache

        Args:
            sample_count (int): Number of samples to fetch

        Returns: ndarray
        """
        if self.amplitude.value <= 0:
            return None
        # Build samples by rolling the period cache through the buffer
        rolled_array = numpy.roll(self.wave_cache,
                                  -1 * self.last_played_sample)
        # Append remaining partial period
        full_count, remainder = divmod(sample_count, self.cache_length)
        final_subarray = rolled_array[:int(remainder)]
        return_array = numpy.concatenate((numpy.tile(rolled_array, full_count),
                                          final_subarray))
        # Keep track of where we left off to prevent popping between chunks
        self.last_played_sample = int(((self.last_played_sample + remainder) %
                                       self.cache_length))
        # Multiply output by amplitude
        return return_array * (self.amplitude.value *
                               self.amplitude_multiplier)
