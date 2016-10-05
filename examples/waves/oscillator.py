import numpy

from examples.waves.amplitude import AmplitudeHandler
import config


class Oscillator:
    """
    A sine wave oscillator.
    """

    sample_rate = config.SAMPLE_RATE

    def __init__(self, frequency,
                 amplitude=None,
                 start_mode='ON'):
        """
        Args:
            frequency (float): Frequency in herz of the oscillator
            amplitude (AmplitudeHandler): Amplitude handler for the oscillator
            start_mode (str): legal values: ON, OFF
        """
        if frequency <= 0:
            raise ValueError("Oscillator.frequency cannot be <= 0")
        self.frequency = frequency
        self.last_played_sample = 0
        self.play_mode = start_mode  # legal values: ON, OFF, STOPPING

        # Build self.wave chunk, a numpy array of a full period of the wave
        self.cache_length = round(self.sample_rate / self.frequency)
        factor = self.frequency * ((numpy.pi * 2) / self.sample_rate)
        self.wave_cache = numpy.arange(self.cache_length)
        self.wave_cache = numpy.sin(self.wave_cache * factor) * 65535

        if amplitude:
            self.amplitude = amplitude
        else:
            change_rate_weights = [
                (0.000001, 1000),
                (0.00001, 100),
                (0.0001, 10),
                (0.001, 0.1)]
            self.amplitude = AmplitudeHandler(
                0, change_rate_weights=change_rate_weights)

    def get_samples(self, sample_count):
        """
        Fetch a number of samples from self.wave_cache

        Args:
            sample_count (int): Number of samples to fetch

        Returns: ndarray
        """
        if self.play_mode == 'OFF' or self.amplitude.value <= 0:
            return None

        rolled_array = numpy.roll(self.wave_cache,
                                  -1 * self.last_played_sample)
        full_count, remainder = divmod(sample_count, self.cache_length)
        final_subarray = rolled_array[:remainder]
        return_array = numpy.concatenate((numpy.tile(rolled_array, full_count),
                                          final_subarray))

        self.last_played_sample = ((self.last_played_sample + remainder) %
                                   self.cache_length)
        return return_array * self.amplitude.value
