from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main import VideoStream

class BaseGetterVideoStream:
    def __init__(self, vs:'VideoStream'):
        self.VideoStream = vs

    @property
    def original_frame(self):
        return self.VideoStream.original_frame
    
    @property
    def cam_fps(self):
        return self.VideoStream.fps
    
    @property
    def frame_height(self):
        return self.VideoStream.height
    
    @property
    def frame_width(self):
        return self.VideoStream.width
    
    @property
    def frame(self):
        if self.VideoStream.current_frame is None:
            return None
        frame = self.VideoStream.current_frame.copy()
        self.VideoStream.current_frame = None
        return frame
    
    @property
    def stream_fps(self):
        if self.VideoStream.lock_fps == -1 or self.VideoStream.fps < self.VideoStream.lock_fps:
            return self.VideoStream.fps
        elif self.VideoStream.fps >= self.VideoStream.lock_fps:
            return self.VideoStream.lock_fps 
    @property
    def time_gap(self):
        return 1/self.cam_fps
    
    @property
    def is_running(self):
        return self.VideoStream.is_running
    
    @property
    def frame_not_none(self):
        if self.VideoStream.current_frame_not_none is None:
            raise ValueError
        return self.VideoStream.current_frame_not_none