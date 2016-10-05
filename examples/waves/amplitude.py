import numpy

from blur import rand

from examples.waves import config


def find_amplitude(chunk):
    """
    Calculate the 0-1 amplitude of an ndarray chunk of audio samples.

    Samples in the ndarray chunk are signed int16 values oscillating
    anywhere between -32768 and 32767. Find the amplitude between 0 and 1
    by summing the absolute values of the minimum and maximum, and dividing
    by 32767.

    Args:
        chunk (numpy.ndarray): An array of int16 audio samples

    Returns:
        float: The amplitude of the sample between 0 and 1.
            Note that this is not a decibel representation of
            the amplitude.
    """
    return (abs(int(chunk.max() - chunk.min())) / config.SAMPLE_RANGE)


def normalize_amplitude(chunk, amplitude):
    """
    Normalize a chunk of audio samples to a given amplitude

    Args:
        chunk (numpy.ndarray): An array of int16 audio samples
        amplitude (float): The amplitude to normalize to.
            Should be between 0 and 1.

    Returns:
        (numpy.ndarray): An array of int16 audio samples whose amplitude
        is normalized to `amplitude`
    """
    chunk_amplitude = find_amplitude(chunk)
    return chunk * (amplitude / chunk_amplitude)


class AmplitudeHandler:
    """
    A handler for audio amplitude values.
    """
    def __init__(self,
                 init_value,
                 drift_target_weights=None,
                 change_rate_weights=None):
        """
        Args:
            init_value (float): The initial amplitude level
            drift_target_weights (list): a list of 2-tuple weights
            change_rate_weights (list): a list of 2-tuple weights
        """
        # Set up amplitude
        self._raw_value = None
        self.value = init_value
        if drift_target_weights is None:
            self.drift_target_weights = [
                (-1, 1), (0.02, 6), (0.2, 1), (0.3, 0)]
        else:
            self.drift_target_weights = drift_target_weights
        self.drift_target = rand.weighted_rand(self.drift_target_weights)
        if change_rate_weights is None:
            self.change_rate_weights = [(0.00001, 100), (0.001, 5), (0.01, 1)]
        else:
            self.change_rate_weights = change_rate_weights
        self.change_rate = rand.weighted_rand(self.change_rate_weights)

    @property
    def value(self):
        """
        float: Adjusted amplitude. Sub-zero values return 0
        """
        if self._raw_value < 0:
            return 0
        else:
            return self._raw_value

    @value.setter
    def value(self, new_value):
        self._raw_value = new_value

    def step_amp(self):
        """
        Change the amplitude according to the change rate and drift target.

        Returns: None
        """
        difference = self.drift_target - self._raw_value
        if abs(difference) < self.change_rate:
            self.value = self.drift_target
        else:
            delta = self.change_rate * numpy.sign(difference)
            self.value = self._raw_value + delta
