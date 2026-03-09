#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 19:16:13 2023

@author: StefaniaParigi
"""
import cv2
import os
# from skimage.metrics import structural_similarity as compare_ssim
# import numpy as np
import os 
# import argparse
# import imutils
# import time
####comparing function, is the crucial one to go from image to video analysis



filepath='/Users/StefaniaParigi/Desktop/video_analysis/videoplayback.mp4'
folderpath='/Users/StefaniaParigi/Desktop/video_analysis'

# from skimage.metrics import structural_similarity as compare_ssim
# def compare_frames(img1,img2):
#     # threshold=0.35#good enough for clockwork orange
#     threshold=0.35
#     # threshold2=0.985
#     threshold2=0.98
#     (score, diff) = compare_ssim(img1, img2, full=True)
#     diff = (diff * 255).astype("uint8")
#     # print("SSIM: {}".format(score))
#     if score<=threshold:
#         message='CHANGE_SHOT'
#         # CHANGESHOT+=1
#     elif score>threshold and score<=threshold2:
#         message='CAMERA_IS_MOVING'
#     #Discriminate if camera is zooming in or characters are moving
#     #edge evaluation function might help for this
#     #missing to detect moving camera...left-right-zoom in zoom out
#     else:
#         message='CAMERA_IS_NOT_MOVING'
#     return message,score



def write_number_to_timefile(number):
    current_directory = os.getcwd()
    # final_directory = os.path.join(current_directory, r'timesfolder')
    with open(current_directory+'\\times.txt', 'a+') as file_object:
        file_object.write(str(number)+'\n')

def overwrite_timefile(filename):
    with open(filename, 'w') as file:
        file.write(str(0)+'\n')
        
