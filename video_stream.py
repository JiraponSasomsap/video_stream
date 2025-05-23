import cv2
import threading
import time
from .utils import version

def video_streaming(insts:'VideoStream'):
    if insts.cap is None:
        insts.cap = insts.cam_connect()
    prev_time = time.perf_counter()
    while insts.is_running:
        ret, frame = insts.cap.read()
        if ret:
            insts.original_frame = frame.copy()
            
            if insts.callback is not None:
                frame = insts.callback(frame)

            if insts.is_resize:
                dsize = (insts.width, insts.height)  # Only (width, height) is needed
                frame = cv2.resize(frame, dsize)

            if insts.lock_fps == -1 or insts.fps < insts.lock_fps:
                insts.current_frame = frame.copy()
                insts.current_frame_not_none = frame.copy()
            elif insts.fps >= insts.lock_fps:
                if insts.frame_count % (insts.fps//insts.lock_fps) == 0:
                    insts.current_frame = frame.copy()
                    insts.current_frame_not_none = frame.copy()
                    insts.frame_count = 0 # reset frame count
            insts.frame_count += 1   
        else:
            insts.cap.release()
            print(f'Lost connection to source: {insts.source}.')
            if insts.reconnect:
                print('Reconnecting...')
                insts.cap = insts.cam_connect()
            else:
                insts.is_running = False
        next_time = prev_time + (1 / insts.fps)
        sleep_time = max(0, next_time - time.perf_counter())
        time.sleep(sleep_time)
        prev_time = next_time
    insts.cap.release()

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
        self.callback = None

        self._thread = None
        self._cam_connect = False 

    def cam_connect(self):
        self.frame_count = 0
        # self.cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
        self.cap = cv2.VideoCapture(self.source)
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
            return _GetVideoStream(self)
        else:
            raise ConnectionError('Camera Connection Error!')
    
    def wait(self):
        while self.current_frame is None:
            time.sleep(0.1)

    def start(self, callback=None):
        self.is_running = True
        self.callback = callback
        self._thread = threading.Thread(target=video_streaming, args=(self,), daemon=True)
        self._thread.start()
        self.wait()
        return _GetVideoStream(self)
    
    def stop(self):
        self.is_running = False

    def set_callback(self, callback):
        self.callback = callback
    
class _GetVideoStream:
    def __init__(self, instance:VideoStream):
        self._videoStream = instance

    @property
    def original_frame(self):
        return self._videoStream.original_frame
    
    @property
    def cam_fps(self):
        return self._videoStream.fps
    
    @property
    def frame_height(self):
        return self._videoStream.height
    
    @property
    def frame_width(self):
        return self._videoStream.width
    
    @property
    def frame(self):
        if self._videoStream.current_frame is None:
            return None
        frame = self._videoStream.current_frame.copy()
        self._videoStream.current_frame = None
        return frame
    
    @property
    def stream_fps(self):
        if self._videoStream.lock_fps == -1 or self._videoStream.fps < self._videoStream.lock_fps:
            return self._videoStream.fps
        elif self._videoStream.fps >= self._videoStream.lock_fps:
            return self._videoStream.lock_fps 
    @property
    def time_gap(self):
        return 1/self.cam_fps
    
    @property
    def is_running(self):
        return self._videoStream.is_running
    
    @property
    def frame_not_none(self):
        if self._videoStream.current_frame_not_none is None:
            raise ValueError
        return self._videoStream.current_frame_not_none
        
if __name__ == '__main__':
    import numpy as np
    video_source = r"C:\Users\JiraponSasomsap\ArticulusProjects\projects\EGAT\EGAT_Demo\videos\EGAT_test.mp4"
    stream = VideoStream(video_source, 1)
    streaming = stream.start()
    frame_tmp = None
    while stream.is_running:
        frame = streaming.frame
        if frame is not None:
            frame_tmp = frame
            frame_tmp = cv2.resize(frame_tmp, np.array([frame_tmp.shape[1]*0.5, frame_tmp.shape[0]*0.5], dtype=np.int32))
        
        if frame_tmp is not None:
            cv2.imshow('hello', frame_tmp)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stream.stop()
    cv2.destroyAllWindows()