import cv2
import threading
import time
from .getter import BaseGetterVideoStream
from ..utils.version import version

class VideoStream:
    __version__ = version()
    def __init__(self, 
                 source, 
                 lock_fps=-1, 
                 reconnect=True,
                 height=None, 
                 width=None):
        self.source = source
        self.is_running = False
        self.lock_fps = lock_fps
        self.original_frame = None
        self.current_frame = None
        self.current_frame_not_none = None
        self.fps = None
        self.is_resize = True if height is not None and width is not None else False
        self.height = height
        self.width = width
        self.frame_count = None
        self.cap = None
        self.reconnect = reconnect

        self.end_run_loop_task = threading.Event()

        self._thread = None
        self._cam_connect = False 

        self.getter = BaseGetterVideoStream

    def cam_connect(self):
        self.frame_count = 0
        # self.cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            self.end_run_loop_task.set()
            raise RuntimeError(f"Unable to open video source: {self.source}")
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        if self.height is None or self.width is None:
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        if self.cap.isOpened():
            print(f'Connected to source : {self.source}')
            self._cam_connect = True
        else:
            print(f'Failed to connect to source : {self.source}')
            self._cam_connect = False
        return self.cap

    @property
    def get(self):
        if not self._cam_connect:
            self.cam_connect()
        if self._cam_connect:
            return self.getter(self)
        else:
            raise ConnectionError('Camera Connection Error!')
    
    def wait(self):
        while self.current_frame is None:
            time.sleep(0.1)
            if self.end_run_loop_task.is_set():
                break

    def start(self):
        self.is_running = True
        self._thread = threading.Thread(target=self.run_video_loop, daemon=True)
        self._thread.start()
        self.wait()
        return self.getter(self)
    
    def run_video_loop(self):
        if self.cap is None:
            self.cap = self.cam_connect()
        prev_time = time.perf_counter()
        while self.is_running:
            if self.end_run_loop_task.is_set():
                break
            ret, frame = self.cap.read()
            if ret:
                self.original_frame = frame.copy()
                if self.is_resize:
                    dsize = (self.width, self.height)  # Only (width, height) is needed
                    frame = cv2.resize(frame, dsize)

                if self.lock_fps == -1 or self.fps < self.lock_fps:
                    self.current_frame = frame.copy()
                    self.current_frame_not_none = frame.copy()
                elif self.fps >= self.lock_fps:
                    if self.frame_count % (self.fps//self.lock_fps) == 0:
                        self.current_frame = frame.copy()
                        self.current_frame_not_none = frame.copy()
                        self.frame_count = 0 # reset frame count
                self.frame_count += 1   
            else:
                self.cap.release()
                print(f'Lost connection to source: {self.source}.')
                if self.reconnect:
                    print('Reconnecting...')
                    self.cap = self.cam_connect()
                else:
                    self.is_running = False
            next_time = prev_time + (1 / self.fps)
            sleep_time = max(0, next_time - time.perf_counter())
            time.sleep(sleep_time)
            prev_time = next_time
        self.cap.release()
    
    def stop(self):
        self.is_running = False