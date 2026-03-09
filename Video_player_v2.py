# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 16:55:17 2023

@author: apraa
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 17:10:27 2023

@author: StefaniaParigi
"""

# https://coderslegacy.com/python/pyqt5-video-player-with-qmediaplayer/

import cv2
import os
import sys
sys.setrecursionlimit(5000)
# This will increase the recursion limit for Python, which should resolve the pathlib conflict.

from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
# from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QApplication,
#                              QLabel, QFileDialog, QStyle, QVBoxLayout)
from PyQt5.QtWidgets import (QMainWindow,QApplication, QFileDialog, QHBoxLayout, QLabel, 
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar,QLineEdit)
 
import numpy as np
# import os 
# from skimage.metrics import structural_similarity as compare_ssim
# import argparse
# import imutils

import matplotlib.pyplot as plt
import time

from matplotlib.widgets import Slider

from my_functions import   write_number_to_timefile, overwrite_timefile#,compare_frames

# import compare_frames

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Video Player") 
        
        #I should create some options button such as frame rate
        
        
        
 ## enable the video player
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()
 
    #play and pause button
        self.playButton = QPushButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
 
    #Select video button
        self.openButton = QPushButton("Select Video")   
        self.openButton.clicked.connect(self.openFile)
 
    # Create a button to save all frames in a folder 
        self.extractButton = QPushButton("Extract Frames", self)
        self.extractButton.clicked.connect(self.extract_frames)
        self.extractButton.setEnabled(False)
        
    # Create a button to enable analysis: face_detection + compareframes
        # self.faceButton = QPushButton("Face recon +compare frames function", self)
        # self.faceButton.clicked.connect(self.face_detection)
        # self.faceButton.setEnabled(False)    
        
     # Create a button to enable analysis:compare frames analyzing binary images
        self.binaryButton = QPushButton("Analyze binary images", self)
        self.binaryButton.clicked.connect(self.binary_analysis)
        self.binaryButton.setEnabled(False)
        
    
        
    # Create a button to decompose video into shots
        self.decomposeButton = QPushButton("Decompose into shots", self)
        self.decomposeButton.clicked.connect(self.split_video)
        self.decomposeButton.setEnabled(False)
        
        self.plotscoreButton = QPushButton("Plot scorevstime", self)
        self.plotscoreButton.clicked.connect(self.plot_scorevstime)
        self.plotscoreButton.setEnabled(False)
        

        
    #TO DO Create a button to set frame rate 
            # self.decomposeButton = QPushButton("Frame rate", self)
            # self.decomposeButton.clicked.connect(self.frame_rate)

    
        
    #Create text window showing the currentframe

        self.framebox = QLineEdit(self)
        # self.textbox.move(20, 20)
    #Create text window showing the output of compare function
        self.messagebox = QLineEdit(self)
    
    
    
    
    
    ###Additional text to help user
        self.frameLabel = QLabel(self)
        self.frameLabel.setText('frame')
    
        self.messageLabel = QLabel(self)
        self.messageLabel.setText('framecomparison')
    
    
    #layout widgets, to be understood well 
        widget = QWidget(self)
        self.setCentralWidget(widget)
 
    

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addWidget(self.openButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.extractButton)
        # layout.addWidget(self.faceButton)
        layout.addWidget(self.binaryButton)

        layout.addWidget(self.frameLabel)
        layout.addWidget(self.framebox)
        layout.addWidget(self.messageLabel)
        layout.addWidget(self.messagebox)
        layout.addWidget(self.decomposeButton)
        layout.addWidget(self.plotscoreButton)

 
 
        widget.setLayout(layout)
        self.mediaPlayer.setVideoOutput(videoWidget)
 
    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())
 
        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
        self.extractButton.setEnabled(True)
        # self.faceButton.setEnabled(True)
        self.binaryButton.setEnabled(True)
        self.video_path = fileName
        print("Open video in "+self.video_path)
 
    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
            
    def extract_frames(self):
    # Open the video file
        video = cv2.VideoCapture(self.video_path)
    
        # Get the number of frames in the video
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
        # Set the starting frame
        start_frame = 0
    
        # Set the ending frame
        end_frame = total_frames
    
        # Iterate through the frames
        for i in range(start_frame, end_frame):
            # Read the current frame
            ret, frame = video.read()
    
            # If the current frame could not be read, break the loop
            if not ret:
                break
    
            # Perform object detection
            # ...
    
            # Save the current frame as an image file in newfolder
            current_directory = os.getcwd()
            final_directory = os.path.join(current_directory, r'frames')
            if not os.path.exists(final_directory):
                    os.makedirs(final_directory)
            cv2.imwrite(final_directory+"/frame_{}.jpg".format(i), frame)
    
        # Release the video capture object
        video.release()
        cv2.destroyAllWindows()
    
    
    def binary_analysis(self):
        
        self.decomposeButton.setEnabled(False)
        self.plotscoreButton.setEnabled(False)
        current_directory = os.getcwd()
        video=cv2.VideoCapture(self.video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        # Read the first frame
        _, previous_frame = video.read()
        previous_frame = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
    
        # Initialize the time and change arrays
        times = []
        changes = []
        binary_list=[]
    
        # Initialize the list of change of shot times
        change_of_shot_times = []
        dissolve_times = []
        fast_movement_times = []
    
        # Initialize the time of the last change of shot
        last_change_of_shot_time = 0
    
        # Loop through the rest of the frames
        frame_index = 0
        while True:
            # Read the current frame
            _, frame = video.read()
            
            if frame is None:
                break
            self.framebox.setText(str(frame_index))
            # Convert the current frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply binary thresholding to the grayscale image
            _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
            
            # Compare the binary image to the previous binary image
            difference = cv2.absdiff(binary, previous_frame)
            change = np.mean(difference)
    
            
            # Check if the mean difference is greater than a threshold
            if change > 6:
                current_time = frame_index /fps
                if current_time - last_change_of_shot_time > 0.5:
                    # Check if the difference is due to a dissolve or a fast camera movement
                    if np.mean(binary) > 50:
                        dissolve_times.append(current_time)
                        print("Dissolvence at time", frame_index / video.get(cv2.CAP_PROP_FPS), "seconds")
                        self.messagebox.setText('Dissolvence at time'+str( frame_index /fps)+'s')
                        last_change_of_shot_time = current_time
                    # else:
                    #     fast_movement_times.append(current_time)
                    #     print("Camera quickly moves at time ", frame_index / video.get(cv2.CAP_PROP_FPS), "seconds") 
                    #     last_change_of_shot_time = current_time
                        
                    else:
                        change_of_shot_times.append(current_time)
                        last_change_of_shot_time = current_time
                        if len(change_of_shot_times)==1:
                            overwrite_timefile(current_directory+'\\times.txt')
                        print("Change of shot detected at time", frame_index /fps, "seconds")
                        self.messagebox.setText('COS at time'+str( frame_index /fps)+'s')
                        write_number_to_timefile(frame_index/fps)

            
            # Add the time and change to the arrays
            times.append(frame_index /fps)
            changes.append(change)
            binary_list.append(np.mean(binary))
            
            # Show the original and binary images
            cv2.imshow("Original", frame)
            cv2.imshow("Binary", binary)
            
            # Set the current binary image as the previous image for the next iteration
            previous_frame = binary
            
            # Break the loop if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            frame_index += 1
            
            
        # print("Change of shot times:", change_of_shot_times)
        # # Plot the change value as a function of time
        # plt.plot(times, changes)
        # plt.plot(times, binary_list)
        # plt.xlabel("Time (seconds)")
        # plt.ylabel("Change Value")
        # plt.show()
        
        self.messagebox.setText("Number of shots="+str(len(change_of_shot_times)))
        # avoid looping on video
        video.release()
        cv2.destroyAllWindows()
        #COPIED from face_detection
        
        #saveframe where I change shot in a list
        change_of_shot_times.append(frame_index/fps)
        # save_crit_frame.append(frame_index)
        #write last frame time in txt file
        write_number_to_timefile(frame_index/fps)
        #enable other buttons after analysis
        self.decomposeButton.setEnabled(True)
        self.plotscoreButton.setEnabled(True)
        #define stuff to use in other functions as for example list to plot
        self.score_list=changes
        # self.score_list=binary_list
        self.time_list=times
    
    
    
#     def face_detection(self):
#         #disable buttons, required if I analyse two movies in a row
#         self.decomposeButton.setEnabled(False)
#         self.plotscoreButton.setEnabled(False)
        
        
#         cascPath=os.path.dirname(cv2.__file__)+"/data/haarcascade_frontalface_default.xml"
#         faceCascade = cv2.CascadeClassifier(cascPath)
        
#         initframe = 0
#         currentframe=0

#         #parameter_updated when change shot
#         #to define avg_shot_length
#         #define function that converts from frames numbers into time
#         CHANGESHOT=1
#         score_list=[]
#         time_list=[]
        
        
        
#         save_crit_frame=[]
#         save_crit_time=[]
#         face_coordinates=[]
#         video_capture = cv2.VideoCapture(self.video_path)
#         fps = video_capture.get(cv2.CAP_PROP_FPS)
# # execute analysis and frame comparison
#         while True:

#             # Capture frame-by-frame
#             ret, frame = video_capture.read()
#             if not ret:
#                 break
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             # profile=0
#             face=0
#             # eye=0
#             # body=0
#             # lowerbody=0
#             # upperbody=0
            
#             ##########
#             faces = faceCascade.detectMultiScale(
#                 gray,
#                 scaleFactor=1.1,
#                 minNeighbors=5,
#                 minSize=(20, 20),
#                 flags=cv2.CASCADE_SCALE_IMAGE
#             )
#             for (x, y, w, h) in faces:
#                      face=1
#                      cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#                      roi_gray=gray[y:y+h,x:x+w]
#                      # message=compare_frames(img1,img2)
#                      ###depending on face size we can determine kind of shooting ()
#                      roi_color=frame[y:y+h,x:x+w]
#                      #
#                      # message=compare_frames(img1,img2)
#             current_directory = os.getcwd()
#             final_directory = os.path.join(current_directory, r'frames')
#             name = final_directory+"/frame_" + str(currentframe) + '.jpg'
#             # print (str(currentframe)) 
#             self.framebox.setText(str(currentframe))
       
#             # writing the extracted images 

#             if currentframe!=initframe:
#                     img2 = cv2.imread(name,cv2.IMREAD_GRAYSCALE)
#                     message,score=compare_frames(img1,img2)
#                     # self.messagebox.setText(message)
#                     score_list.append(score)
#                     time_list.append(currentframe/fps)
#                     if message=='CHANGE_SHOT':

#                         #both redundant??
#                         save_crit_frame.append(currentframe)
#                         ##saving twice the same information, redundant but ok for now
#                         save_crit_time.append(currentframe/fps)
                        
#                         if CHANGESHOT==1:
#                             overwrite_timefile(current_directory+'\\times.txt')
#                             save_crit_time.append(0)
#                             save_crit_frame.append(0)
#                         CHANGESHOT+=1
#                         write_number_to_timefile(currentframe/fps)
#                         self.messagebox.setText('COS at time'+str(currentframe/fps)+'s')
                        
#                     img1=img2

#            #skip comparison for first frame, perhaps better to start  directly at second
#             else:
#                 img1 = cv2.imread(name,cv2.IMREAD_GRAYSCALE)
#                 CURRENTSHOT=CHANGESHOT
#            #  #2 approaches to determine character, fix image recognition, determine zoom in-out, avoid fake characters 
#            #  #save coordinate of all images where either a face of a profile has been detected: 
#            #  #1compare images and sizes of face rectangles
#            #  #2 feed and train recognition alghoritm live 
#            #  #approach 1 is easier and probably less efficient, for the moment I just save face positions and rectangle dimensions, it would be useful to decompose movie into shot before
#            #  #try to average these info over many frames 
#             # if face or profile or facestree:
#             #     if face:
#             #         face_coordinates.append([faces,currentframe])
#             #     elif profile:
#             #             face_coordinates.append([profiles,currentframe])
#             #     elif facestree:
#             #             face_coordinates.append([facestree,currentframe])
                       
#             # Display the resulting frame
        
#             currentframe += 1
#             #add marker for each character
        
#             # # Display the resulting frame
#             cv2.imshow('Video', frame)
#             #break with q-->close video
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break    
#             #break with CTRL+C--> break python
#             k = cv2.waitKey(30) & 0xff
#             if k == 27:
#                 break
#         self.messagebox.setText("Number of shots="+str(CHANGESHOT))
#  # avoid looping on video
#         video_capture.release()
#         cv2.destroyAllWindows()
        
#         #saveframe where I change shot in a list
#         save_crit_time.append(currentframe/fps)
#         save_crit_frame.append(currentframe)
#         #write critical times in txt file
#         write_number_to_timefile(currentframe/fps)
#         #enable other buttons after analysis
#         self.decomposeButton.setEnabled(True)
#         self.plotscoreButton.setEnabled(True)
#         #define stuff to use in other functions as for example list to plot
#         self.score_list=score_list
#         self.time_list=time_list
    
   
    # def split_video(self):
    #     # from moviepy.editor import VideoFileClip##CONFLICT with pillow, find other solution
   
    #     # Load the video file
    #     clip = VideoFileClip(self.video_path)
    #     with open("times.txt") as f:
    #           times = f.readlines()
    #           times = [x.strip() for x in times] 
    #           current_directory = os.getcwd()
    #     final_directory = os.path.join(current_directory, r'clips')
    #     if not os.path.exists(final_directory):
    #             os.makedirs(final_directory)
    #     # cv2.imwrite(final_directory+"/frame_{}.jpg".format(i), frame)
    #     for i in range (1,len(times)):
    #     # Split the video into two clips
    #         cut_clip = clip.subclip(times[i-1], times[i]) # clip from 0 to x seconds
    #         filename=final_directory+"/clip"+str(i)
    #         cut_clip.write_videofile(filename+".mp4")
            
            
    def split_video(self):
    # Open the video file
        cap = cv2.VideoCapture(self.video_path)
    
        # Read the times from the text file
        with open("times.txt") as f:
            times = f.readlines()
            times = [float(x.strip()) for x in times]
    
        # Create the output folder if it doesn't exist
        if not os.path.exists(r'clips'):
            os.makedirs(r'clips')
    
        # Initialize variables
        scene_counter = 1
        start_frame = 0
        out=None
    
        # Loop through video frames
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if scene_counter <= len(times) and cap.get(cv2.CAP_PROP_POS_MSEC) >= times[scene_counter - 1] * 1000:
                # Release the previous writer
                if out is not None:
                    out.release()
                # Write the scene to a new video file
                out = cv2.VideoWriter(os.path.join(r'clips', f"scene_{scene_counter}.mp4"), cv2.VideoWriter_fourcc(*'mp4v'), cap.get(cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
                scene_counter += 1
                start_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    
            # Write frame to the current scene
            if out is not None and scene_counter <= len(times) and cap.get(cv2.CAP_PROP_POS_FRAMES) >= start_frame:
                out.write(frame)
    
        # Release video capture
        cap.release()
        
        # Release the last writer
        if out is not None:
            out.release()
    
    
    
    def plot_scorevstime(self):
        
        plt.rcParams['font.size'] = '22'
        
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'plots')
        if not os.path.exists(final_directory):
                    os.makedirs(final_directory)
        
        fig, ax = plt.subplots()
        # plt.plot(T,nb)
        # plt.plot(self.time_list,self.score_list)


        plt.xlabel('t (s)')#,fontsize=18)
        plt.ylabel('score')

        
        l, = plt.plot(self.time_list,self.score_list,lw=2)
        plt.savefig(final_directory+'/score_nointerpolation.png')
        # Define slider
        axcolor = 'lightgoldenrodyellow'
        ax_win = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
        win = Slider(ax_win, 'Window', 0.1, 10.0, valinit=1)

        # Update plot
        def update(val):
            window = win.val
            y_avg = np.convolve(self.score_list, np.ones((int(window),))/int(window), mode='same')
            l.set_ydata(y_avg)
            fig.canvas.draw_idle()
        win.on_changed(update)

        # Show plot
        plt.show()
        

        
        
        
        
        
        
        
        
        
#show output of analysis on GUI
 
app = QApplication(sys.argv)
videoplayer = VideoPlayer()
videoplayer.resize(640, 480)
videoplayer.show()
sys.exit(app.exec_())




####time settings
#convert frame in time




# PLOTTING
# t vs scorelist
#t vs brightness list



