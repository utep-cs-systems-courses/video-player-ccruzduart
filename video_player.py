#! /usr/bin/env python3
#
# video_player.py
#
# Made by: Cristian Cruz

from threading import Semaphore
import cv2, os
from threading import Thread

# Class that uses semaphores to lock the resources to cordinate the threads
# adding frames as items into the queues
#
class ProductConsumer:

    # Initializes an empty queue, and two semaphores
    # 0 indicating that isEmpty and isFull are respectevly empty and full
    #
    def __init__(self):
        self.queue = []
        self.isEmpty = Semaphore(0)
        self.isFull = Semaphore(0)
    
    # add item to the queue
    # 
    def produce(self, item):
        if len(self.queue) == 10:
            self.isFull.acquire()
        self.queue.append(item)
        self.isEmpty.release()
    
    # consumes item from the queue
    #
    def consume(self):
        self.isEmpty.acquire()
        item = self.queue.pop(0)
        self.isFull.release()
        return item

# extracts frames from the mp4 file
# adding each extract frame to queue
# return a last item to the queue as None
#
def extract_frames(color_frames):
    clipFileName = 'clip.mp4'
    count = 0
    vidcap = cv2.VideoCapture(clipFileName)
    success,frame = vidcap.read()
    while success and count < 50:
        color_frames.produce(frame)
        success,frame = vidcap.read()
        print(f'Reading frame {count}')
        count += 1
    print('Extraction completed.....')
    color_frames.produce(None)

# Converts extracted frames to gray scale
# consumes color frames and then adds the gray scale frames to a queue
# returns a last item to the queue as None
#
def convert_frames_to_grayscale(gray_frames, color_frames):
    count = 0
    inputFrame = color_frames.consume()
    while inputFrame is not None:
        print(f'Converting frame {count}')
        grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
        gray_frames.produce(grayscaleFrame)
        count += 1
        inputFrame = color_frames.consume()
    print('Convertion Completed.....')
    gray_frames.produce(None)

# Displays the gray scale frames
# it displays by consuming frames from the queue
#
def display_frames(gray_frames):
    count = 0
    frame = gray_frames.consume()
    while frame is not None:
        print(f'Displaying frame {count}')
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break    
        count += 1
        frame = gray_frames.consume()
    print('Finish displaying.....')    
    cv2.destroyAllWindows()
    

# Main method that creates 3 threads
# one thread to extract the frames from the mp4
# one thread to covert extracted frames to gray scale
# one to display gray scale frames
#
def main():
    color_frames = ProductConsumer()
    gray_frames = ProductConsumer()
    
    extract_thread = Thread(target=extract_frames, args=(color_frames,))
    convert_thread = Thread(target=convert_frames_to_grayscale, args=(gray_frames, color_frames))
    display_thread = Thread(target=display_frames, args=(gray_frames,))
    
    extract_thread.start()
    convert_thread.start()
    display_thread.start()

    extract_thread.join()
    convert_thread.join()
    display_thread.join()
    
if __name__ == "__main__":
    main()
