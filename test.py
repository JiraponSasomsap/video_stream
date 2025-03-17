from video_stream import VideoStream
import cv2
from dotenv import load_dotenv
import os
load_dotenv()

cam_source = os.getenv('RTSP-STREAMING')

cam = VideoStream(cam_source, lock_fps=-1)
cap = cam.cam_connect()
result = cam.start()

if __name__ == '__main__':
    orig_frame = None
    while cam.is_running:
        frame = result.get_frame()
        if frame is None:
            continue
        else: orig_frame = frame
        cv2.imshow('test', orig_frame)
        if cv2.waitKey(1) & 0xFF ==  ord('q'):
            break
    cv2.destroyAllWindows()

# if __name__ == '__main__':
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if ret:
#             cv2.imshow('test',frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#     cv2.destroyAllWindows()