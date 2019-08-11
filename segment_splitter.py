# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 12:17:46 2019

@author: PMAC
"""

import cv2
import numpy as np
import moviepy.editor as mp
import os
import datetime
import sys
import logging
from PIL import * 
from PyQt5.QtWidgets import QLabel, QFrame, QLineEdit, QPushButton, QCheckBox, QApplication, QMainWindow, \
                            QFileDialog, QDialog, QScrollArea, QMessageBox, QWidget, QTextEdit
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPixmap, QIntValidator, QPalette, QColor
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

THIS_FILEPATH = os.path.dirname( __file__ )
THIS_FILENAME = os.path.basename(__file__)

logger = logging.getLogger("")
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

#################
#
#
# GUI 
#
#
#################

class MainWindow(object):
    SCREEN_HEIGHT = 800
    SCREEN_WIDTH = 800
    def __init__(self):
        self.app = QApplication([])
        self.window = QMainWindow()
        self.window.setFixedSize(self.SCREEN_WIDTH,self.SCREEN_HEIGHT)
        self.window.setWindowTitle('Segment Splitter')
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("ico.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.window.setWindowIcon(self.icon)

        ###################
        # INPUT
        ###################
            
        self.title_container = QLabel(self.window)
        self.title_container.setGeometry(QtCore.QRect(0, 0, self.SCREEN_WIDTH, 50))
        # self.title_container = self.set_white(self.title_container)
        
        self.title_label = QLabel("Segment Splitter",self.window)
        self.title_label.setGeometry(QtCore.QRect(0, 0, self.SCREEN_WIDTH, 50))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.title_label_border = QFrame(self.window)
        self.title_label_border.setGeometry(QtCore.QRect(0, 0, self.SCREEN_WIDTH, 50))
        self.title_label_border.setStyleSheet("border:2px solid rgb(0, 0, 0); ")
        
        self.video_label = QLabel("Input video path:",self.window)
        self.video_label.setGeometry(QtCore.QRect(10, 60, 120, 30))
        self.video_label.setToolTip('Choose the video to split into segments based.\nAccepted formats are mp4, flv and mkv.')
        
        self.video_label_input = QLineEdit("",self.window)
        self.video_label_input.setGeometry(QtCore.QRect(140, 60, 550, 30))
        self.video_label_input.setToolTip('Choose the video to split into segments based.\nAccepted formats are mp4, flv and mkv.')
        
        self.video_button = QPushButton("Browse",self.window)
        self.video_button.setGeometry(QtCore.QRect(700, 60, 80, 30))
        self.video_button.clicked.connect(self.video_input_click)
        
        self.start_split_header = QLabel("Start split image:",self.window)
        self.start_split_header.setGeometry(QtCore.QRect(30, 100, 120, 30))
        self.start_split_header.setToolTip('Choose the image that each clip will start on.\nRefer to GitHub instructions for producing best images.')
        
        self.start_split_button = QPushButton("Browse",self.window)
        self.start_split_button.setGeometry(QtCore.QRect(200, 100, 80, 30))
        self.start_split_button.clicked.connect(self.start_split_image_click)
        
        self.start_split_picture = QLabel("",self.window)
        self.start_split_picture.setGeometry(QtCore.QRect(30, 140, 250, 250))
        self.start_split_picture.setAlignment(QtCore.Qt.AlignCenter)
        
        self.start_split_border = QFrame(self.window)
        self.start_split_border.setGeometry(QtCore.QRect(30, 140, 250, 250))
        self.start_split_border.setStyleSheet("border:2px solid rgb(0, 0, 0); ")
        
        self.end_split_header = QLabel("End split image:",self.window)
        self.end_split_header.setGeometry(QtCore.QRect(300, 100, 120, 30))
        self.end_split_header.setToolTip('Choose the image that each clip will end on.\nIf using single split option, leave this blank.\nRefer to GitHub instructions for producing best images.')
        
        self.end_split_button = QPushButton("Browse",self.window)
        self.end_split_button.setGeometry(QtCore.QRect(470, 100, 80, 30))
        self.end_split_button.clicked.connect(self.end_split_image_click)
        
        self.end_split_picture = QLabel("",self.window)
        self.end_split_picture.setGeometry(QtCore.QRect(300, 140, 250, 250))
        self.end_split_picture.setAlignment(QtCore.Qt.AlignCenter)
        
        self.end_split_border = QFrame(self.window)
        self.end_split_border.setGeometry(QtCore.QRect(300, 140, 250, 250))
        self.end_split_border.setStyleSheet("border:2px solid rgb(0, 0, 0); ")
        
        ###################
        # OPTIONS
        ###################
                
        self.start_threshold_label = QLabel("Start split threshold:",self.window)
        self.start_threshold_label.setGeometry(QtCore.QRect(560, 140, 160, 30))
        self.start_threshold_label.setToolTip('This value influences how strict the image matching is. \n2D games should be a tight value around 50, whereas 3D games can go up to ~500.\nIf the program makes too many segments, lower the value.\nIf the program makes too few segments, increase the value.')  
        
        self.start_threshold_input = QLineEdit("50",self.window)
        self.start_threshold_input.setValidator(QIntValidator(self.start_threshold_input))
        self.start_threshold_input.setGeometry(QtCore.QRect(720, 143, 40, 25))
        
        self.end_threshold_label = QLabel("End split threshold:",self.window)
        self.end_threshold_label.setGeometry(QtCore.QRect(560, 170, 160, 30))
        self.end_threshold_label.setToolTip('This value influences how strict the image matching is. \n2D games should be a tight value around 50, whereas 3D games can go up to ~500.\nIf the program makes too many segments, lower the value.\nIf the program makes too few segments, increase the value.')
        
        self.end_threshold_input = QLineEdit("50",self.window)
        self.end_threshold_input.setValidator(QIntValidator(self.end_threshold_input))
        self.end_threshold_input.setGeometry(QtCore.QRect(720, 173, 40, 25))
        
        self.frame_buffer_label = QLabel("Split wait buffer:",self.window)
        self.frame_buffer_label.setGeometry(QtCore.QRect(560, 200, 160, 30))
        self.frame_buffer_label.setToolTip('This value influences how long after each split \nto wait before checking for the next split.')
        
        self.frame_buffer_input = QLineEdit("60",self.window)
        self.frame_buffer_input.setValidator(QIntValidator(self.frame_buffer_input))
        self.frame_buffer_input.setGeometry(QtCore.QRect(720, 203, 40, 25))
        
        self.start_pre_roll_label = QLabel("Start pre-roll:",self.window)
        self.start_pre_roll_label.setGeometry(QtCore.QRect(560, 230, 160, 30))
        self.start_pre_roll_label.setToolTip('This value will dictate how many frames before the desired split to crop.\nAs an example, if a segment is 60 frames, setting this pre-roll\nto 30 frames will create a 90 frame clip, where the \nbeginning of the split starts 30 frames in.')
        
        self.start_pre_roll_label_input = QLineEdit("0",self.window)
        self.start_pre_roll_label_input.setValidator(QIntValidator(self.frame_buffer_input))
        self.start_pre_roll_label_input.setGeometry(QtCore.QRect(720, 233, 40, 25))
        
        self.end_post_roll_label = QLabel("End post-roll:",self.window)
        self.end_post_roll_label.setGeometry(QtCore.QRect(560, 260, 160, 30))
        self.end_post_roll_label.setToolTip('This value will dictate how many frames after the desired split to crop.\nAs an example, if a segment is 100 frames, setting this post-roll\nto 30 frames will create a 130 frame clip, where the \nsplit starts immediately and has 30 frames extra of video \nafter the split ends.')
        
        self.end_post_roll_label_input = QLineEdit("0",self.window)
        self.end_post_roll_label_input.setValidator(QIntValidator(self.frame_buffer_input))
        self.end_post_roll_label_input.setGeometry(QtCore.QRect(720, 263, 40, 25))
        
        self.create_video_checkbox = QCheckBox("Create video clips",self.window)
        self.create_video_checkbox.setGeometry(QtCore.QRect(560, 320, 150, 30))
        self.create_video_checkbox.setToolTip('Creates video clips of split segments when checked.\nIf only a log of frame windows per segment is desired (without splitting video), then uncheck.\nUnchecking will result in faster processing time.')
        self.create_video_checkbox.setChecked(True)

        self.single_split_checkbox = QCheckBox("Split on start image only",self.window)
        self.single_split_checkbox.setGeometry(QtCore.QRect(560, 350, 200, 30))
        self.single_split_checkbox.setToolTip('Use this setting if the start and end of each segment should only rely upon one image. \nThe starting image will be used.')


        
        
        ###################
        # OUTPUT  
        ###################
        
        self.output_dir_label = QLabel("Output path:",self.window)
        self.output_dir_label.setToolTip('Output path for videos & output log. If left blank, a new directory will be created.')
        self.output_dir_label.setGeometry(QtCore.QRect(10, 400, 120, 30))
        
        self.output_dir_label_input = QLineEdit("",self.window)
        self.output_dir_label_input.setGeometry(QtCore.QRect(140, 400, 550, 30))
        self.output_dir_label_input.setToolTip('Output path for videos & output log. If left blank, a new directory will be created.')
        
        self.output_dir_button = QPushButton("Browse",self.window)
        self.output_dir_button.setGeometry(QtCore.QRect(700, 400, 80, 30))
        self.output_dir_button.clicked.connect(self.output_dir_click)
        
        ###################
        # PROCESSING & LOG
        ###################
        
        self.process_video = QPushButton("PUSH TO BEGIN PROCESSING",self.window)
        self.process_video.setGeometry(QtCore.QRect(50, 450, 700, 30))
        self.process_video.clicked.connect(self.process_video_click)
        self.process_video.setToolTip('Begins processing based on parameters. Options and file paths will be valided before running.')
        
        self.log_header_label = QLabel("Console log:",self.window)
        self.log_header_label.setGeometry(QtCore.QRect(10, 480, 120, 30))

        self.log_output = QTextEdit(self.window)
        self.log_output.setGeometry(QtCore.QRect(30, 510, 740, 250))
        # self.log_output = self.set_white(self.log_output)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().minimum())
        
        self.log_output_thread = LogThread(self.window)
        self.log_output_thread.log.connect(self.update_log_text)
        # self.log_output_thread.started.connect(lambda: self.update_log('start'))
        
        
        self.log_clear_button = QPushButton("Clear Log",self.window)
        self.log_clear_button.setGeometry(QtCore.QRect(30, 765, 80, 30))
        self.log_clear_button.clicked.connect(self.clear_log)        
        
        self.processing_reset_button = QPushButton("Reset Processing",self.window)
        self.processing_reset_button.setGeometry(QtCore.QRect(120, 765, 130, 30))
        self.processing_reset_button.clicked.connect(self.reset_processing)
        self.processing_reset_button.setToolTip('If the Push to Begin Processing bar is inactive, use this to reset.')
#        
#        self.log_label_border = QFrame(self.window)
#        self.log_label_border.setGeometry(QtCore.QRect(30, 510, 740, 250))
#        self.log_label_border.setStyleSheet("border:2px solid rgb(0, 0, 0); ")
                
        self.github_label = QLabel("https://github.com/cleartonic/segment_splitter",self.window)
        urlLink="<a href=\'https://github.com/cleartonic/segment_splitter'>https://github.com/cleartonic/segment_splitter</a>" 
        self.github_label.setText(urlLink)
        self.github_label.setGeometry(QtCore.QRect(470, 770, 400, 50))
        self.github_label.setAlignment(QtCore.Qt.AlignBottom)
        self.github_label.setAlignment(QtCore.Qt.AlignLeft)
        self.github_label.setOpenExternalLinks(True)
        
        # Final settings
        self.app.setStyle('Fusion')
        self.app.setFont(QtGui.QFont("Segoe UI", 12))
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(120, 120, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.app.setPalette(palette)
        
        
    ###############################
    # FUNCTIONS
    ###############################
#    def update_log(self, message):
#        # self.log_output.append(str(message))
        
    def update_log(self, text):
        self.log_output_thread.setText(text)
        self.log_output_thread.start()
        
    def update_log_text(self, val):
        self.log_output.append(str(val))
        
    def clear_log(self, message):
        self.log_output.setText("")
        
    def reset_processing(self, message):
        self.process_video.setEnabled(True)
        
    def set_white(self,obj):
        obj.setAutoFillBackground(True)
        p = obj.palette()
        p.setColor(obj.backgroundRole(),QColor(255, 255, 255))
        obj.setPalette(p)
        return obj
    
    def video_input_click(self):
        dialog = QFileDialog()
        new_file = dialog.getOpenFileName(None,"Select video","",filter="mp4 (*.mp4);;flv (*.flv);;mkv (*.mkv)")
        self.video_label_input.setText(new_file[0])
        
    def output_dir_click(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec_() == QDialog.Accepted:
            self.output_dir_label_input.setText(dialog.selectedFiles()[0])

    def start_split_image_click(self):
        dialog = QFileDialog()
        new_file = dialog.getOpenFileName(None,"Select split image","",filter="png (*.png);;jpeg (*.jpeg);;jpg (*.jpg)")
        if QDialog.Accepted:
            self.start_split_image_loc = new_file[0]
            self.start_split_pixmap = QPixmap(new_file[0])
            self.start_split_picture.setPixmap(self.start_split_pixmap.scaled(250, 250, QtCore.Qt.KeepAspectRatio))

    def end_split_image_click(self):
        dialog = QFileDialog()
        new_file = dialog.getOpenFileName(None,"Select split image","",filter="png (*.png);;jpeg (*.jpeg);;jpg (*.jpg)")
        if QDialog.Accepted:
            self.end_split_image_loc = new_file[0]
            self.end_split_pixmap = QPixmap(new_file[0])
            self.end_split_picture.setPixmap(self.end_split_pixmap.scaled(250, 250, QtCore.Qt.KeepAspectRatio))
            
    def process_video_click(self):
        validate_flag = self.validate_input()
        if type(validate_flag) == bool and validate_flag:
            self.update_log("Success on inputs, beginning generation.")
            self.process_video.setEnabled(False)
            QTimer.singleShot(1, lambda: self.begin_video_processing())
        else:
            self.update_log(validate_flag)

            
    def begin_video_processing(self):
            self.video_processor = VideoProcessor(self, self.processing_start_split_image, self.processing_end_split_image, \
                                             self.processing_video_cv2_cap, self.processing_video_moviepy_cap, \
                                             self.processing_output_dir_label_input, \
                                             self.processing_single_split_checkbox, \
                                             self.processing_create_video_checkbox, \
                                             self.processing_start_threshold, \
                                             self.processing_end_threshold, \
                                             100, \
                                             self.processing_frame_buffer, \
                                             -self.processing_start_pre_roll, \
                                             self.processing_end_post_roll) # Scan size (100) hardcoded for now
            self.video_processor_thread = VideoProcessorThread(self.video_processor)
            self.video_processor_thread.start()
            
    def validate_input(self):
        ############
        # Validate the inputs for running the process
        ############
        pass_flag = True
           
        # THRESHOLDS
        try:
            self.processing_start_threshold = int(main_window.start_threshold_input.text())
            if self.processing_start_threshold <= 0 or self.processing_start_threshold > 1000:
                return "Start threshold needs to be between 1 - 1000."
            self.processing_end_threshold = int(main_window.end_threshold_input.text())
            if self.processing_end_threshold <= 0 or self.processing_end_threshold > 1000:
                return "End threshold needs to be between 1 - 1000."            
            self.processing_frame_buffer = int(main_window.frame_buffer_input.text())
            if self.processing_frame_buffer <= 0 or self.processing_frame_buffer  > 1000:
                return "Frame buffer needs to be between 1 - 1000."
            self.processing_start_pre_roll = int(main_window.start_pre_roll_label_input.text())
            if self.processing_start_pre_roll < 0 or self.processing_start_pre_roll > 1000:
                return "Start pre-roll needs to be between 0 - 1000."
            self.processing_end_post_roll = int(main_window.end_post_roll_label_input.text())
            if self.processing_end_post_roll < 0 or self.processing_end_post_roll> 1000:
                return "End pre-roll needs to be between 0 - 1000."
        except Exception as e:
            print("Error on thresholds, check thresholds and resubmit: "+str(e))
            return "Error on thresholds, check thresholds and resubmit"
            
        # CHECKMARKS
        try:
            if self.single_split_checkbox.checkState() == 0:
                self.processing_single_split_checkbox = False
            else:
                self.processing_single_split_checkbox = True
            if self.create_video_checkbox.checkState() == 0:
                self.processing_create_video_checkbox = False
            else:
                self.processing_create_video_checkbox = True
        except:
            pass
        # START IMAGE
        try:
            self.processing_start_split_image = cv2.imread(self.start_split_image_loc)
            if type(self.processing_start_split_image) != np.ndarray:
                return "Failure to validate start split as image."
        except Exception as e:
            print("Failure to validate start split as image: "+str(e))
            return "Failure to validate start split as image"
            
        # END IMAGE
        try:
            if not self.processing_single_split_checkbox:
                self.processing_end_split_image = cv2.imread(self.end_split_image_loc)
                if type(self.processing_end_split_image) != np.ndarray:
                    return "Failure to validate end split as image."
            else:
                self.processing_end_split_image = None
        except Exception as e:
            print("Failure to validate end split as image: "+str(e))
            return "Failure to validate end split as image"
        
        # INPUT PATH
        try:
            print("Video path: "+self.video_label_input.text())
            self.processing_video_cv2_cap = cv2.VideoCapture(self.video_label_input.text())
            self.processing_video_moviepy_cap = mp.VideoFileClip(self.video_label_input.text())
        except Exception as e:
            print("Failure to load : "+str(e))
            return "Failure to load video file"

        # OUTPUT PATH
        try:
            if self.output_dir_label_input.text() == '':
                timestamp = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
                if not os.path.exists(os.path.join(THIS_FILEPATH,'output')):
                    os.mkdir(os.path.join(THIS_FILEPATH,'output'))
                new_dir = os.path.abspath(os.path.join(THIS_FILEPATH,'output',timestamp))
                self.update_log("Creating new directory for current load: "+new_dir)
                os.mkdir(new_dir)
                self.processing_output_dir_label_input = new_dir
            else:
                if not os.path.exists(self.output_dir_label_input.text()):
                    return "Failure on output directory, provide a valid directory path"
                else:
                    self.processing_output_dir_label_input = os.path.abspath(self.output_dir_label_input.text())
                    return "Setting output dir to: "+str(self.output_dir_label_input.text())

        except Exception as e:
            print("Failure on output directory, provide a valid directory path: "+str(e))
            return "Failure on output directory, provide a valid directory path"

        return pass_flag
        


###############################
# THREAD
###############################        
        
class LogThread(QThread):
    log = pyqtSignal(str)

    def __init__(self, parent=None):
        super(LogThread, self).__init__(parent)
        self._text = ''

    def setText(self, text):
            self._text = text

    def run(self):
        self.log.emit(str(self._text))

        

class VideoProcessorThread(QThread):
    def __init__(self,video_processor):
        QThread.__init__(self)
        self.video_processor = video_processor
    def __del__(self):
        self.wait()
    def run(self):
        self.video_processor.run_all()
        self.sleep(2)
































#################
#
#
# CORE
#
#
#################

OUTPUT_DEBUG = False
#FLAG_VALUE = 100 # mse to flag on 
#SIZE_CHECK = 100 # how many items after the first match to check for
#FRAME_BUFFER = 60 # how many frames to skip after a split 
#start_clip_buffer = -60 # how many frames to add to the video before starting
#end_clip_buffer = 120 # how many frames to add to the video after finishing


class VideoProcessor(object):
    def __init__(self,window_object,processing_start_split_image,processing_end_split_image,processing_video_cv2_cap,processing_video_moviepy_cap,processing_output_dir_label_input,processing_single_split_checkbox,processing_create_video_checkbox,processing_start_threshold,processing_end_threshold,scan_size,processing_frame_buffer,processing_start_clip_buffer,processing_end_clip_buffer):
        
        print("Save videos: "+str(processing_single_split_checkbox))
        print("Start split threshold: "+str(processing_start_threshold))
        print("End split threshold: "+str(processing_end_threshold))
        print("Size of matching images to minimize on: "+str(scan_size))
        print("Frames to skip after split: "+str(processing_frame_buffer))
        print("Frames to buffer video before start split: "+str(processing_start_clip_buffer))
        print("Frames to buffer video after end split: "+str(processing_end_clip_buffer))
        self.window_object = window_object
        self.start_split_image = processing_start_split_image
        self.end_split_image = processing_end_split_image
        self.video_cv2_cap = processing_video_cv2_cap
        self.video_moviepy_cap = processing_video_moviepy_cap
        self.output_dir = processing_output_dir_label_input 
        self.single_split_checkbox = processing_single_split_checkbox
        self.create_video_checkbox = processing_create_video_checkbox
        self.start_threshold = processing_start_threshold
        self.end_threshold = processing_end_threshold
        self.scan_size = scan_size # This is hardcoded and not parameterized for now, set to 100. May be unimportant for user to input this value
        self.frame_buffer = processing_frame_buffer
        self.start_clip_buffer = processing_start_clip_buffer
        self.end_clip_buffer = processing_end_clip_buffer

        
    def run_all(self):
        
        print("Loading video...")
        self.window_object.update_log("Loading video...")
        cap = self.video_cv2_cap
        video = self.video_moviepy_cap
        # video = video.resize(height=240)
      
        
        # NEEDS TO BE ADDRESSED 
        # self.processing_single_split_checkbox = processing_single_split_checkbox

        # Set up proper pathing for new subdir to save to - needs to be passed in init 
        
        
        start_split = self.start_split_image
        start_split = cv2.resize(start_split,(426,240))
        start_split = cv2.cvtColor(start_split, cv2.COLOR_BGR2GRAY)
        
        if not self.single_split_checkbox:
            end_split = self.end_split_image
            end_split = cv2.resize(end_split,(426,240))
            end_split = cv2.cvtColor(end_split, cv2.COLOR_BGR2GRAY)
        
        #cv2.imshow("TEST",start_split)
        #cv2.waitKey()
        
        print("Creating frame by frame of video")
        self.window_object.update_log("Creating frame by frame of video")
        video_frames = {}
        count = 0
        ret = True
        while(ret):
            try:
                ret, frame = cap.read()
                frame = cv2.resize(frame,(426,240))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                count = count + 1
                video_frames[str(count)] = frame
            except:
                pass
        cap.release()
        cv2.destroyAllWindows()
        
        def mse(imageA, imageB):
            # the 'Mean Squared Error' between the two images is the
            # sum of the squared difference between the two images;
            # NOTE: the two images must have the same dimension
            err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
            err /= float(imageA.shape[0] * imageA.shape[1])
            return err
        
        def check_a_frame(source,compare):
            error_level = mse(source,compare)
            return int(round(error_level))
        
        print("Starting video mse process")
        self.window_object.update_log("Starting video mse process")

        if not self.single_split_checkbox:        
            start_array = np.empty((0,len(video_frames)))
            end_array = np.empty((0,len(video_frames)))
            start_array = []
            end_array = []
            for title, image_to_compare in video_frames.items():
                start_i = check_a_frame(start_split,image_to_compare)
                end_i = check_a_frame(end_split,image_to_compare)
                start_array.append(start_i)
                end_array.append(end_i)
                
        else:
            start_array = np.empty((0,len(video_frames)))
            start_array = []
            for title, image_to_compare in video_frames.items():
                start_i = check_a_frame(start_split,image_to_compare)
                start_array.append(start_i)
        
        print("Starting timestamp process")
        self.window_object.update_log("Starting timestamp process")
        timestamps = [] # stamps will be lists of [start_timestamp,end_timestamp]
        current_frame = 0
        
        
        framerate = 60    
        def _seconds(value):
            if isinstance(value, str):  # value seems to be a timestamp
                _zip_ft = zip((3600, 60, 1, 1/framerate), value.split(':'))
                return sum(f * float(t) for f,t in _zip_ft)
            elif isinstance(value, (int, float)):  # frames
                return value / framerate
            else:
                return 0
            
        if not self.single_split_checkbox:
            print("Processing for start & end split images")
            self.window_object.update_log("Processing for start & end split images")
            while current_frame < len(video_frames):
                start_split_time = False
                end_split_time = False
                
                while end_split_time is False:
                    if start_split_time is False: # first searching for start_split
                        if current_frame >= len(video_frames):
                            break
                        if OUTPUT_DEBUG:
                            print("START Current second: "+str(round(_seconds(current_frame)))+" "+str(start_array[current_frame])+" "+str(start_split_time))
                        if start_array[current_frame] < self.start_threshold:
                            # now we're checking around this area in the array to find a min value 
                            new_array = start_array[current_frame:current_frame+self.scan_size]
                            min_pos = new_array.index(min(new_array))
                            current_frame = current_frame + min_pos
                            start_split_time = current_frame
                            print("Start split identified at pos: "+str(current_frame))
                            # self.window_object.update_log("Start split identified at pos: "+str(current_frame))
                            current_frame = current_frame + self.frame_buffer
                        else: # didnt match an image based on mse, continue
                            current_frame = current_frame + 1
                    elif end_split_time is False:
                        if current_frame >= len(video_frames):
                            break
                        if OUTPUT_DEBUG:
                            print("END Current second: "+str(round(_seconds(current_frame)))+" "+str(end_array[current_frame])+" "+str(end_split_time))
                        if end_array[current_frame] < self.end_threshold:
                            # now we're checking around this area in the array to find a min value 
                            new_array = start_array[current_frame:current_frame+self.scan_size]
                            min_pos = new_array.index(min(new_array))
                            current_frame = current_frame + min_pos
                            end_split_time = current_frame
                            print("End split identified at pos: "+str(current_frame))
                            # self.window_object.update_log("End split identified at pos: "+str(current_frame))
                            current_frame = current_frame + self.frame_buffer
                            
                            # then now add to timestamps
                            timestamps.append([start_split_time+self.start_clip_buffer,end_split_time+self.end_clip_buffer])
                            # after this, it'll roll over to the top of the loop and reset start/end
                            
                        else: # didnt match an image based on mse, continue
                            current_frame = current_frame + 1
                            if current_frame >= len(video_frames):
                                break
        else:
            print("Processing for start split image only")
            self.window_object.update_log("Processing for start split image only")
            while current_frame < len(video_frames):
                start_split_time = False                
                while start_split_time is False:
                    if current_frame >= len(video_frames):
                        break
                    if OUTPUT_DEBUG:
                        print("START Current second: "+str(round(_seconds(current_frame)))+" "+str(start_array[current_frame])+" "+str(start_split_time))
                    if start_array[current_frame] < self.start_threshold:
                        # now we're checking around this area in the array to find a min value 
                        new_array = start_array[current_frame:current_frame+self.scan_size]
                        min_pos = new_array.index(min(new_array))
                        current_frame = current_frame + min_pos
                        start_split_time = current_frame
                        print("Start split identified at pos: "+str(current_frame))
                        # self.window_object.update_log("Start split identified at pos: "+str(current_frame))
                        current_frame = current_frame + self.frame_buffer
                        timestamps.append(start_split_time)
                    else: # didnt match an image based on mse, continue
                        current_frame = current_frame + 1

        if len(timestamps) > 0:
            list_of_deltas = []
            
            if self.create_video_checkbox:
                print("Saving subclips of timestamps...")
                self.window_object.update_log("Saving subclips of timestamps...")
                
            # What's happening here is that the timestamps are created no matter what, if the save_video checkbox
            # is marked or not. Then only videos are saved if the option was selected
            
            if not self.single_split_checkbox:
                for index, timestamp in enumerate(timestamps):
                    delta = timestamp[1] - timestamp[0]
                    if self.create_video_checkbox:
                        try:
                            video_filepath = os.path.join(self.output_dir,'clip_'+str(index+1)+'_'+str(delta)+'_frames.mp4')
                            self.window_object.update_log("Saving file: "+video_filepath)
                            video.subclip(_seconds(timestamp[0]),_seconds(timestamp[1])).write_videofile(video_filepath)
                        except:
                            try:
                                video_filepath = os.path.join(self.output_dir,'clip_'+str(index+1)+'_'+str(delta)+'_frames.mp4')
                                self.window_object.update_log("Saving file: "+video_filepath)
                                # try again but remove the buffers for start/end 
                                video.subclip(_seconds(timestamp[0]-self.start_clip_buffer),_seconds(timestamp[1]-self.end_clip_buffer )).write_videofile(video_filepath)
                            except Exception as e:
                                print("Error on clip: "+video_filepath+" "+str(e))
                    list_of_deltas.append(delta)
            else: # self.single_split_checkbox == True
                for index in range(0,len(timestamps)-1): # -1 at the end here is so that it doesnt go one too far at the end when doing [index+1]
                    try:
                        delta = timestamps[index+1] - timestamps[index] # this is a little different than before, you're taking each individual timestamp (rather than start/end) and using each as a start/end
                        if self.create_video_checkbox:
                            try:
                                video_filepath = os.path.join(self.output_dir,'clip_'+str(index+1)+'_'+str(delta)+'_frames.mp4')
                                self.window_object.update_log("Saving file: "+video_filepath)
                                video.subclip(_seconds(timestamps[index]),_seconds(timestamps[index+1])).write_videofile(video_filepath)
                            except:
                                try:
                                    video_filepath = os.path.join(self.output_dir,'clip_'+str(index+1)+'_'+str(delta)+'_frames.mp4')
                                    self.window_object.update_log("Saving file: "+video_filepath)
                                    # try again but remove the buffers for start/end 
                                    video.subclip(_seconds(timestamps[index]-self.start_clip_buffer),_seconds(timestamps[index+1]-self.end_clip_buffer )).write_videofile(video_filepath)
                                except Exception as e:
                                    print("Error on clip: "+video_filepath+" "+str(e))
                    except Exception as e:
                        print("Error: "+str(e))
                    list_of_deltas.append(delta)

            
            
            min_delta_time = min(list_of_deltas)
            average_delta = int(np.mean(list_of_deltas))
            
            self.window_object.update_log("\n")
            output_str = ''
            output_str = output_str + "Timestamp log:\n"
            output_str = output_str + "Number of subclips: "+str(len(list_of_deltas))+"\n"
            output_str = output_str + "Average frames: "+str(average_delta)+"\n"

            
            for index, delta in enumerate(list_of_deltas):
                percentage_of_min = round((delta/min_delta_time)*100)
                text = "Clip #"+str(index+1)+": "+str(delta)+" frames ("+str(percentage_of_min)+"%)"
                output_str = output_str + text + "\n"
            with open(os.path.join(self.output_dir,'log.txt'),'w') as file:
                file.write(output_str)
            print(output_str)
            self.window_object.update_log(output_str)

        else:
            print("No matched splits on image, ending process.")
            self.window_object.update_log("No matched splits on image, ending process.")
        cap.release()
        cv2.destroyAllWindows()
        self.window_object.video_button.setEnabled(True)

if __name__ == '__main__':
    main_window = MainWindow()
    main_window.window.show()
    # main_window.app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())
    main_window.app.exec_()
    # del main_window