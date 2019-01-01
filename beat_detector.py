import alsaaudio, aubio, audioop
import pydub
import matplotlib.pyplot as plt
import numpy as np
from numpy_ringbuffer import RingBuffer
import scipy.io.wavfile
from scipy.fftpack import rfft, irfft
from scipy.signal import butter, lfilter, freqz
import struct

from helpers import get_mic_listener


class BeatDetector(object):

    def __init__(self, sample_rate, big_batch_size, instant_batch_size, color_screen):
        """
        Beat Detector constructor
        
        Arguments:
            sample_rate {int} -- sample rate of the input sound
            big_batch_size {int} -- sample size for average energy computing
            instant_batch_size {int} -- sample size for instant energy computing
            color_screen {ColorScreen} -- color displayer
        """

        self.color_screen = color_screen
        self.sample_rate = sample_rate
        self.big_batch_size = big_batch_size
        self.instant_batch_size = instant_batch_size

    def listen(self, time_in_sec):
        """
        Sound listener from microphone
        time_in_sec {int} -- time (in seconds) to make the listening last
        """

        total_samples = time_in_sec * self.sample_rate

        inp = get_mic_listener(self.instant_batch_size, self.sample_rate)
        wav = np.array([])
        buffer = RingBuffer(capacity=int(self.big_batch_size / self.instant_batch_size), dtype=np.float32)

        for _ in range(int(total_samples / self.instant_batch_size)):

            _, data = inp.read()
            data = np.array(list(struct.iter_unpack("<f", data)), dtype=np.float32)[:,0]
            #import ipdb; ipdb.set_trace()
            wav = np.concatenate((wav, data))
            instant_energy = self.get_local_energy(data)
            buffer.append(instant_energy)

            if len(wav) >= self.big_batch_size:
                instant_beat = self.get_instant_beat(instant_energy, np.average(np.array(buffer)))
                print(instant_energy, instant_beat)
                if instant_energy < 0.0001 and instant_beat > 2:
                    continue
                self.color_screen.animate(instant_beat)
            
        scipy.io.wavfile.write("oe.wav", self.sample_rate, wav)

    def get_local_energy(self, sample):
        """
        Local energy computer
        
        Arguments:
            sample {int-list} -- signal
        """

        return sum(map(lambda x: x**2, sample))

    def get_instant_beat(self, instant_energy, average_energy):
        """
        Computes an instant beat level compared to average history
        
        Arguments:
            instant_energy {int} -- energy over the last self.instant_batch_size samples
            average_energy {int} -- energy over the last self.big_batch_size samples
        """

        return instant_energy / average_energy

                



            


