import ctypes
import time
from ctypes import wintypes

# Load Windows multimedia library
winmm = ctypes.WinDLL('winmm')

# Set up argument and return types
winmm.timeBeginPeriod.argtypes = [wintypes.UINT]
winmm.timeBeginPeriod.restype = wintypes.UINT
winmm.timeEndPeriod.argtypes = [wintypes.UINT]
winmm.timeEndPeriod.restype = wintypes.UINT

class precise_timer:

    def __init__(self, resolution_ms=1):

        """Initialize with desired timer resolution (default 1ms)"""

        self.resolution = resolution_ms
        self._set_resolution()
    

    def _set_resolution(self):

        """Set system timer resolution"""
        winmm.timeBeginPeriod(self.resolution)
    

    def _reset_resolution(self):

        """Reset system timer resolution"""
        winmm.timeEndPeriod(self.resolution)
    

    def sleep(self, ms):

        """High resolution sleep in ms"""

        start = time.perf_counter()
        while (time.perf_counter() - start) * 1000 < ms:
            if ms - (time.perf_counter() - start) * 1000 > 2:  # 2ms threshold
                time.sleep(0.001)  # yield to OS
    

    def __enter__(self):
        return self
    

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._reset_resolution()