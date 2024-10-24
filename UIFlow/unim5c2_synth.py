#####################################################################################################
# Standard MIDI file player, MIDI-IN player and Sequencer for M5Stack CORE2 with Unit-MIDI.
#   Hardware:
#     M5Stack CORE2
#     Unit-MIDI synthesizer M5Stack (SAM2695)
#     8encoder unit for M5Stack (U153)
#     Micro SD card
#     MIDI-IN instruments
#
#   Program: micropython for UIFlow2.0 (V2.1.4)
#            UnitMIDI_SMF_MIDIin.py
#              1.0.0: 09/24/2024
#              1.1.0: 09/25/2024
#                       Improved data structor for effector parameters to reduce code.
#              1.1.1: 09/26/2024
#                       Remove functions not used.
#                       Add documents.
#            UnitMIDI_SYNTH_SEQ.py
#              1.0.0: 10/01/2024
#              1.0.1: 10/02/2024
#                       Velocity editor in Sequencer screen.
#                       Start and end time setting to play with sequencer.
#              1.0.2: 10/03/2024
#                       Insert/Delete time.
#                       Clear all note (a MIDI channel or all channels)
#                       Note in a bar/Time resolution
#                       Play temp for sequencer
#              1.1.0: 10/04/2024
#                       PAUSE/STOP for sequencer play.
#                       Sequencer GM program settings.
#                       Save/Load all sequencer settings.
#              1.1.1: 10/07/2024
#                       Tempo parameter conforms to the music score regulation.
#                       MIDI-IN works in duaring sequencer play.
#              1.1.2: 10/08/2024
#                       Repeat signs on score. (LOOP/SKIP/REPEAT)
#              1.1.3: 10/10/2024
#                       Volume ration for each sequencer MIDI channel.
#                       Change sequencer parameter value by decade or 1.
#            unim5c2_synth.py
#              1.0.0: 10/23/2024
#                       Source code improvement.  Use classes to ensure independency between modules.
#
# Copyright (C) Shunsuke Ohira, 2024
#####################################################################################################
# Functions as a music instrument
#====================================================================================================
# Standard MIDI File PLAYER (Screen Mode: PLAYER, 8encoder slide switch ON)
#   Play a standard MIDI file in the SD-card.
#   MIDI channel settings for MIDI-IN PLAYER are changed by SMF in playing,
#   however the setting are restored when the play stops.
#
# MIDI-IN PLAYER (Screen Mode: PLAYER, 8encoder slide switch OFF)
#   Recieve MIDI data at MIDI-IN connector on Unit-MIDI,
#   and send the received raw data to Unit-MIDI synthesizer.
#
# SEQUENCER (Screen Mode: SEQUENCER)
#   Step sequencer to compose music.
#   Play it with both Unit-MIDI synthesizer and instruments via MIDI-OUT.
#====================================================================================================
# Operation
#====================================================================================================
# Standard MIDI File PLAYER (PLAYER Screen, 8encoder slide switch ON)
#   8encoder.CH1
#     VALUE : Select a MIDI file. (never works in playing a MIDI file.)
#     BUTTON: PLAY/STOP the MIDI file selected.z
#
#   8encoder.CH2
#     VALUE : SMF player key transpose.  (All notes off in advance of the transpose.)
#     BUTTON: PAUSE/RESTART the MIDI file playing.
#
#   8encoder.CH3
#     VALUE : SMF player volume.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH4
#     VALUE : Change SMF player tempo to play.
#     BUTTON: n/a
#
#   8encoder.CH5
#     VALUE : Change the effector parameter to edit. (SMF player reverb, chorus and vibrate)
#     BUTTON: n/a
#
#   8encoder.CH6
#     VALUE : Change the effector parameter designated by CH6.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH7
#     VALUE : n/a
#     BUTTON: n/a
#
#   8encoder.CH8
#     VALUE : Master volume.
#     BUTTON: All notes off.
#
# MIDI-IN PLAYER (PLAYER Screen, 8encoder slide switch OFF)
#   8encoder.CH1
#     VALUE : Select a MIDI setting file.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH2
#     VALUE : Control the setting file. (LOAD/SAVE)
#     BUTTON: Execute the control selected without any confirmation.
#
#   8encoder.CH3
#     VALUE : Change MIDI channel of MIDI-IN play.
#     BUTTON: All notes off in the MIDI channel for MIDI-IN play.
#
#   8encoder.CH4
#     VALUE : Select a program.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH5
#     VALUE : Change the effector parameter to edit. (MIDI-IN player reverb, chorus and vibrate)
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH6
#     VALUE : Change the effector parameter value designated by CH5.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH7
#     VALUE : Change the screen to SEQUENCER.
#     BUTTON: n/a
#
#   8encoder.CH8
#     VALUE : Master volume.
#     BUTTON: All notes off.
#
# SEQUENCER (SEQUENCER Screen)
#   Slide Switch:
#     ON : Edit track1 (upper track)
#     OFF: Edit track2 (lower track)
#
#   8encoder.CH1
#     VALUE : Select a sequencer data file.
#     BUTTON: Play or Stop sequencer score. (toggle)
#
#   8encoder.CH2
#     VALUE : Control the sequencer file. (LOAD/SAVE)
#     BUTTON: Execute the control selected without any confirmation.
#
#   8encoder.CH3
#     VALUE : Move sequencer cursor.
#             A note is selected if the cursor is on it.
#     BUTTON: Switch the function to move the time cursor or the key cursor. (toggle)
#
#   8encoder.CH4
#     VALUE : Add or delete a note.
#     BUTTON: Add new note at the cursor when no note is selected.
#             Delete the note selected.
#
#   8encoder.CH5
#     VALUE : Change the sequencer parameter to edit.
#     BUTTON: n/a
#
#   8encoder.CH6
#     VALUE : Change the sequencer parameter value designated by CH5.
#     BUTTON: n/a
#
#   8encoder.CH7
#     VALUE : Change the screen to PLAYER.
#     BUTTON: n/a
#
#   8encoder.CH8
#     VALUE : Master volume.
#     BUTTON: All notes off.
#
#####################################################################################################
# SD card files and formats
#====================================================================================================
# Directory: /SYNTH/MIDIFILE/
# Files:
#   <filename>.MID: Standard MIDI files (format must be 0)
#   LIST.TXT      : MIDI files list.
#                     Music name,MIDI file name,play speed factor (1.0 is normal, larger is farster)
#   GM0.TXT       : GM instrument names list in accending order.
#                     Acostic Grand Piano
#                     Bright Acostic Piano
#                     Electric Grand Piano
#                        :
#                     Gun Shot
#
# Directory: /SYNTH/MIDIUNIT/
# Files:
#   MIDISETxxx.json: MIDI IN parameter settings in JSON format. (xxx is from 000 to 999)
#   Default values are used if a file to load is not available.
#
# Directory: /SYNTH/SEQFILE/
# Files:
#   SEQSCxxx.json: Sequencer music data in JSON format. (xxx is from 000 to 999)
#   Default values are used if a file to load is not available.
#####################################################################################################

import os, sys, io
import json
import M5
from M5 import *
from unit import CardKBUnit
from hardware import *
from unit import MIDIUnit
from unit import Encoder8Unit
import time
from hardware import sdcard
import _thread

######################################
### Application Foundation Classes ###
######################################

##########################
# Message ID definitions
##########################
class message_definitions():
  def __init__(self):
    self.MSGID_NONE = 0
    self.MSGID_APPLICATION_SHOW_MASTER_VOLUME_VALUE = 1
    self.MSGID_APPLICATION_SET_MIDI_IN_CHANNEL = 2
    self.MSGID_APPLICATION_MIDI_FILE_OPERATION = 3
    self.MSGID_APPLICATION_MIDI_FILE_LOAD_SAVE = 4
    self.MSGID_APPLICATION_PLAYER_CONTROL = 5
    self.MSGID_APPLICATION_SWITCH_UPPER_LOWER = 6
    self.MSGID_APPLICATION_SETUP_PLAYER_SCREEN = 7
    self.MSGID_APPLICATION_SCREEN_CHANGE = 8
    self.MSGID_APPLICATION_FLUSH_MIDI_IN_SIGN = 9

    self.MSGID_MIDI_ALL_NOTES_OFF = 101
    self.MSGID_MIDI_GET_PROGRAM_NAME = 102
    self.MSGID_MIDI_SET_INSTRUMENT = 103
    self.MSGID_MIDI_SET_GET_MASTER_VOLUME = 104
    self.MSGID_MIDI_SET_REVERB = 105
    self.MSGID_MIDI_SET_CHORUS = 106
    self.MSGID_MIDI_SET_VIBRATE = 107
    self.MSGID_MIDI_SEND_PITCH_BEND = 108

    self.MSGID_SMF_PLAYER_MAKE_SMF_CATALOG = 201
    self.MSGID_SMF_PLAYER_CONTROL = 202
    self.MSGID_SMF_PLAYER_CHANGE_TRANSPOSE = 203
    self.MSGID_SMF_PLAYER_CHANGE_VOLUME = 204
    self.MSGID_SMF_PLAYER_IS_PLAYING_SMF = 205
    self.MSGID_SMF_PLAYER_SET_GET_PLAY_MODE = 206
    self.MSGID_SMF_PLAYER_SET_GET_SPEED_FACTOR = 207
    self.MSGID_SMF_PLAYER_GET_EFFECTOR_SETTINGS = 208
    self.MSGID_SMF_PLAYER_SET_EFFECTOR_PARAMETER = 209
    self.MSGID_SMF_PLAYER_SET_REVERB = 210
    self.MSGID_SMF_PLAYER_SET_CHORUS = 211
    self.MSGID_SMF_PLAYER_SET_VIBRATE = 212
    self.MSGID_SMF_PLAYER_CHANGE_SMF_FILE_NO = 213

    self.MSGID_MIDI_IN_PLAYER_SET_PROGRAM_DELTA = 301
    self.MSGID_MIDI_IN_PLAYER_SEND_ALL_MIDI_SETTINGS = 302
    self.MSGID_MIDI_IN_PLAYER_SET_REVERB = 303
    self.MSGID_MIDI_IN_PLAYER_SET_CHORUS = 304
    self.MSGID_MIDI_IN_PLAYER_SET_VIBRATE = 305
    self.MSGID_MIDI_IN_PLAYER_SET_GET_SET_NUMBER = 306
    self.MSGID_MIDI_IN_PLAYER_SET_GET_MIDI_IN_CHANNEL = 307
    self.MSGID_MIDI_IN_PLAYER_GET_MIDI_IN_SETTING = 308
    self.MSGID_MIDI_IN_PLAYER_MASTER_VOLUME_DELTA = 309
    self.MSGID_MIDI_IN_PLAYER_SET_SETTING4PARAMS = 310
    self.MSGID_MIDI_IN_PLAYER_SET_CHANNEL_DELTA = 311
    self.MSGID_MIDI_IN_PLAYER_LOAD_SET_FILE = 312
    self.MSGID_MIDI_IN_PLAYER_SAVE_SET_FILE = 313
    self.MSGID_MIDI_IN_PLAYER_SET_DEFAULT = 314

    self.MSGID_SEQUENCER_SETUP = 401
    self.MSGID_SEQUENCER_CHANGE_FILE_OP = 402
    self.MSGID_SEQUENCER_SELECT_FILE = 403
    self.MSGID_SEQUENCER_FILE_LOADED = 404
    self.MSGID_SEQUENCER_MIDI_CHANNEL_CHANGED = 405
    self.MSGID_SEQUENCER_MOVE_TIME_CURSOR = 406
    self.MSGID_SEQUENCER_MOVE_KEY_CURSOR = 407
    self.MSGID_SEQUENCER_FIND_NOTE_ON_CURSOR = 408
    self.MSGID_SEQUENCER_CHANGE_PARAMETER = 409
    self.MSGID_SEQUENCER_GET_REPEAT_FLAG = 410
    self.MSGID_SEQUENCER_IS_NOTE_ON_CURSOR = 411
    self.MSGID_SEQUENCER_CHANGE_NOTE_DURATION = 412
    self.MSGID_SEQUENCER_DELETE_NOTE_ON_CURSOR = 413
    self.MSGID_SEQUENCER_PUT_NOTE_ON_CURSOR = 414
    self.MSGID_SEQUENCER_CHANGE_MIDI_CHANNEL = 415
    self.MSGID_SEQUENCER_CHANGE_TIME_SPAN = 416
    self.MSGID_SEQUENCER_CHANGE_VELOCITY = 417
    self.MSGID_SEQUENCER_CHANGE_PLAY_START = 418
    self.MSGID_SEQUENCER_CHANGE_PLAY_END = 419
    self.MSGID_SEQUENCER_IS_MENU_PARM_CHANNEL = 420
    self.MSGID_SEQUENCER_IS_MENU_PARM_TIMESPAN = 421
    self.MSGID_SEQUENCER_IS_MENU_PARM_VELOCITY = 422
    self.MSGID_SEQUENCER_IS_MENU_PARM_PLAY_START = 423
    self.MSGID_SEQUENCER_IS_MENU_PARM_PLAY_END = 424
    self.MSGID_SEQUENCER_IS_MENU_PARM_STRETCH_ONE = 425
    self.MSGID_SEQUENCER_IS_MENU_PARM_STRETCH_ALL = 426
    self.MSGID_SEQUENCER_IS_MENU_PARM_CLEAR_ONE = 427
    self.MSGID_SEQUENCER_IS_MENU_PARM_CLEAR_ALL = 428
    self.MSGID_SEQUENCER_IS_MENU_PARM_NOTES_BAR = 429
    self.MSGID_SEQUENCER_IS_MENU_PARM_NOTES_BAR = 430
    self.MSGID_SEQUENCER_IS_MENU_PARM_RESOLUTION = 431
    self.MSGID_SEQUENCER_IS_MENU_PARM_TEMPO = 432
    self.MSGID_SEQUENCER_IS_MENU_PARM_MINIMUM_NOTE = 433
    self.MSGID_SEQUENCER_IS_MENU_PARM_PROGRAM = 434
    self.MSGID_SEQUENCER_IS_MENU_PARM_CHANNEL_VOL = 435
    self.MSGID_SEQUENCER_IS_MENU_PARM_REPEAT = 436
    self.MSGID_SEQUENCER_INSERT_TIME = 437
    self.MSGID_SEQUENCER_DELETE_TIME = 438
    self.MSGID_SEQUENCER_ADD_TIME_CURSOR = 439
    self.MSGID_SEQUENCER_SET_NOTE_ON_CURSOR = 440
    self.MSGID_SEQUENCER_CLEAR_TRACK = 441
    self.MSGID_SEQUENCER_CLEAR_SCORE = 442
    self.MSGID_SEQUENCER_CHANGE_TIME_PER_BAR = 443
    self.MSGID_SEQUENCER_RESOLUTION = 444
    self.MSGID_SEQUENCER_CHANGE_TEMPO = 445
    self.MSGID_SEQUENCER_SET_MINIMUM_NOTE = 446
    self.MSGID_SEQUENCER_CHANGE_VOLUME_RATIO = 447
    self.MSGID_SEQUENCER_CHANGE_PROGRAM = 448
    self.MSGID_SEQUENCER_GET_PROGRAM_NAME = 449
    self.MSGID_SEQUENCER_SEND_CHANNEL_SETTINGS = 450
    self.MSGID_SEQUENCER_GET_CURRENT_TRACK_CHANNEL = 451
    self.MSGID_SEQUENCER_SET_INSTRUMENT = 452
    self.MSGID_SEQUENCER_GET_REPEAT_SIGNS = 453
    self.MSGID_SEQUENCER_SET_REPEAT_SIGNS = 454
    self.MSGID_SEQUENCER_GET_SIGNS_CURSOR = 455
    self.MSGID_SEQUENCER_CHANGE_REPEAT_SIGNS = 456
    self.MSGID_SEQUENCER_SET_GET_EDIT_TRACK = 457
    self.VIEW_DISPLAY_CLEAR = 499

    self.VIEW_SMF_PLAYER_SETUP = 2001
    self.VIEW_SMF_PLAYER_SET_TEXT = 2002
    self.VIEW_SMF_PLAYER_SET_VISIBLE = 2003
    self.VIEW_SMF_PLAYER_SET_COLOR = 2004
    self.VIEW_SMF_PLAYER_FNUM_SET_TEXT = 2101
    self.VIEW_SMF_PLAYER_FNAME_SET_TEXT = 2102
    self.VIEW_SMF_PLAYER_TRANSP_SET_TEXT = 2103
    self.VIEW_SMF_PLAYER_VOLUME_SET_TEXT = 2104
    self.VIEW_SMF_PLAYER_TEMPO_SET_TEXT = 2105
    self.VIEW_SMF_PLAYER_PARAMETER_SET_TEXT = 2106
    self.VIEW_SMF_PLAYER_PARM_VALUE_SET_TEXT = 2107
    self.VIEW_SMF_PLAYER_PARM_TITLE_SET_TEXT = 2108
    self.VIEW_SMF_PLAYER_MASTER_VOLUME_SET_TEXT = 2109
    self.VIEW_SMF_PLAYER_SCREEN_VISIBILITY = 2110
    self.VIEW_SMF_PLAYER_ACTIVATED = 2111
    self.VIEW_SMF_PLAYER_INACTIVATED = 2112

    self.VIEW_MIDI_IN_PLAYER_SETUP = 3001
    self.VIEW_MIDI_IN_PLAYER_SET_TEXT = 3002
    self.VIEW_MIDI_IN_PLAYER_SET_VISIBLE = 3003
    self.VIEW_MIDI_IN_PLAYER_SET_COLOR = 3004
    self.VIEW_MIDI_IN_PLAYER_SET_SET_TEXT = 3101
    self.VIEW_MIDI_IN_PLAYER_SET_CTRL_SET_TEXT = 3012
    self.VIEW_MIDI_IN_PLAYER_CHANNEL_SET_TEXT = 3103
    self.VIEW_MIDI_IN_PLAYER_PROGRAM_SET_TEXT = 3104
    self.VIEW_MIDI_IN_PLAYER_PARAMETER_SET_TEXT = 3105
    self.VIEW_MIDI_IN_PLAYER_PARM_VALUE_SET_TEXT = 3106
    self.VIEW_MIDI_IN_PLAYER_PARM_TITLE_SET_TEXT = 3107
    self.VIEW_MIDI_IN_PLAYER_INITIAL_DISPLAY = 3108
    self.VIEW_MIDI_IN_PLAYER_SCREEN_VISIBILITY = 3109
    self.VIEW_MIDI_IN_PLAYER_ACTIVATED = 3110
    self.VIEW_MIDI_IN_PLAYER_INACTIVATED = 3111

    self.VIEW_SEQUENCER_SETUP = 4001
    self.VIEW_SEQUENCER_SET_TEXT = 4002
    self.VIEW_SEQUENCER_SET_VISIBLE = 4003
    self.VIEW_SEQUENCER_SET_COLOR = 4004
    self.VIEW_SEQUENCER_TRACK1_SET_TEXT = 4101
    self.VIEW_SEQUENCER_TRACK2_SET_TEXT = 4102
    self.VIEW_SEQUENCER_KEY1_SET_TEXT = 4103
    self.VIEW_SEQUENCER_KEY2_SET_TEXT = 4104
    self.VIEW_SEQUENCER_FILE_SET_TEXT = 4105
    self.VIEW_SEQUENCER_FILE_OP_SET_TEXT = 4106
    self.VIEW_SEQUENCER_TIME_SET_TEXT = 4107
    self.VIEW_SEQUENCER_MASTER_VOLUME_SET_TEXT = 4108
    self.VIEW_SEQUENCER_PARM_NAME_SET_TEXT = 4109
    self.VIEW_SEQUENCER_SHOW_CURSOR = 4110
    self.VIEW_SEQUENCER_DRAW_TRACK = 4111
    self.VIEW_SEQUENCER_DRAW_PLAYTIME = 4112
    self.VIEW_SEQUENCER_SHOW_PARAMETER_VALUE = 4113
    self.VIEW_SEQUENCER_PROGRAM_SET_TEXT = 4114
    self.VIEW_SEQUENCER_REPEAT_SIGN_SET_TEXT = 4115
    self.VIEW_SEQUENCER_TIMESPAN_SET_TEXT = 4116
    self.VIEW_SEQUENCER_TEMPO_SET_TEXT = 4117
    self.VIEW_SEQUENCER_MINIMUM_NOTE_SET_TEXT = 4118
    self.VIEW_SEQUENCER_PROGRAM_NUMBER_SET_TEXT = 4119
    self.VIEW_SEQUENCER_PROGRAM_NAME_SET_TEXT = 4120
    self.VIEW_SEQUENCER_VOLUME_RATIO_SET_TEXT = 4121
    self.VIEW_SEQUENCER_DRAW_KEYBOARD = 4122
    self.VIEW_SEQUENCER_SCREEN_VISIBILITY = 4123
    self.VIEW_SEQUENCER_ACTIVATED = 4124

    self.MSGID_DEVICE_PHONE_SEQ_TURN_OFF_PLAY_BUTTON = 10001
    self.MSGID_DEVICE_PHONE_SEQ_GET_PAUSE_STOP_BUTTON = 10002
    self.MSGID_DEVICE_PHONE_SEQ_STOP_BUTTON = 10003

################# End of Message ID Definition Class Definition #################

########################
# Message Center Class
#   send_message : CONTRIBUTOR -- message_id, message_data --> MESSAGE CENTER/QUEUE     -- message_id, message_data --> SUBSCRIBERs
#   phone_message: SUBSCRIBER  -- message_id, message_data --> MESSAGE CENTER/IMMEDIATE -- return value             --> SUBSCRIBER
########################
class message_center_class(message_definitions):
  # Constructor
  def __init__(self):
    super().__init__()
    self.message_queue = []       # Message queue to deliver
    self.message_buffer = []      # Temporally buffer of message queue during the message_quere is locked
    self.queue_lock = False       # Message queue is locked or not
    self.contributors = []        # [constributor_class_object1, ...]
    self.subscribers = {}         # {subscriber_class_object1: {message_id1: worker_function1, message_id2: worker_func2, ...}, subscriber_class_object2:...}

  # Lock the message queue
  def lock(self):
    self.queue_lock = True

  # Unlock the message queue
  def unlock(self):
    self.queue_lock = False

  # Wait for the message lock unlocked
  #   lock: True-->Lock just after the lock is unlocked.
  def wait_unlock(self, lock = False):
    while self.queue_lock == True:
      time.sleep(0.01)

    if lock:
      self.lock()

  # Add a contributor object
  #   contributor: Class object whick is permitted to send messages
  def add_contributor(self, contributor):
    self.contributors.append(contributor)

  # Add a dispath information for a subscriber
  #   subscriber: Class object to subscribe the message
  #   message_id: Message ID
  #   worker_func: Called function for this message
  def add_subscriber(self, subscriber, message_id, worker_func):
    if subscriber in self.subscribers:
      self.subscribers[subscriber][message_id] = worker_func
    else:
      self.subscribers[subscriber] = {}
      self.subscribers[subscriber][message_id] = worker_func

  # Send a message immediately without via the message queue, and return its result
  #   subscriber: Class object to subscribe the message
  #   message_id: Message ID
  #   message_data: Message data (allow any data type, 'no_response' in dictionary is used as default value)
  def phone_message(self, subscriber, message_id, message_data = None):
    for subscriber in self.subscribers.keys():
      if message_id in self.subscribers[subscriber]:
#        print('PHONE MESSAGE:', message_id, message_data)
        return self.subscribers[subscriber][message_id](message_data)

    print('message_center_class: Ignore message:', message_id, message_data)
    if message_data is None:
      return None

    if 'no_response' in message_data.keys():
      return message_data['no_response']

    return None

  # Pusu a message in the message queue
  #   contributor: Class object sending this message
  #   message_id: Message ID
  #   message_data: Message data (allow any data type)
  def send_message(self, contributor, message_id, message_data = None):
    if contributor in self.contributors:
      if self.lock:
        self.message_buffer.insert(0, {'message_id': message_id, 'message_data': message_data})
#        print('BUFFERED MESSAGE:', len(self.message_buffer), self.message_buffer)
        return

      self.lock()
      if len(self.message_buffer) > 0:
        self.message_queue = self.message_buffer + self.message_queue
        self.message_buffer = []

      self.message_queue.insert(0, {'message_id': message_id, 'message_data': message_data})
      self.unlock()
#      print('ADD MESSAGE:', len(self.message_queue), self.message_queue)

    else:
      print('MESSAGE CENTER: Message from an unknown contributor:', message_id, message_data)

  # Push messages in the message queue at once
  #   contributor: Class object sending this message
  #   messages: [{'message_id': Message ID, 'message_data': Message Data}, ...]
  def send_messages(self, contributor, messages):
    if not isinstance(messages, list):
      return

    if contributor in self.contributors:
      if self.lock:
        self.message_buffer = messages + self.message_buffer
#        print('BUFFERED MESSAGES:', len(self.message_buffer), self.message_buffer)
        return

      self.lock()
      if len(self.message_buffer) > 0:
        self.message_queue = self.message_buffer + self.message_queue
        self.message_buffer = []

      for mesg_id, mesg_data in messages:
        self.message_queue.insert(0, {'message_id': mesg_id, 'message_data': mesg_data})
      self.unlock()
#      print('ADD MESSAGES:', len(self.message_queue), self.message_queue)

    else:
      print('MESSAGE CENTER: Messages from an unknown contributor:', mesg_id, mesg_data)

  # Get the first message in the queue and send it to all subscribers
  def deliver_message(self):
    mesg_num = len(self.message_queue) + len(self.message_buffer)
    if mesg_num > 0:
      self.wait_unlock(True)

      if len(self.message_buffer) > 0:
        self.message_queue = self.message_buffer + self.message_queue
        self.message_buffer = []

      message = self.message_queue.pop()
      self.unlock()

      dispatched = 0
      for subscriber in self.subscribers.keys():
        message_id = message['message_id']
        message_data = message['message_data']
#        print('POST MESSAGE:', message_id, message_data)
        if message_id in self.subscribers[subscriber]:
#          print('DISPATCH MESSAGE:', message_id, message_data)
          self.subscribers[subscriber][message_id](message_data)
          dispatched = dispatched + 1

      if dispatched == 0:
        print('message_center_class: Lost message:', message_id, message_data)

  # Send all messages to all subscribers
  def flush_messages(self):
    mesg_num = len(self.message_queue) + len(self.message_buffer)
    if mesg_num > 0:
      self.wait_unlock(True)

      if len(self.message_buffer) > 0:
        self.message_queue = self.message_buffer + self.message_queue
        self.message_buffer = []

      while len(self.message_queue) > 0:
        message = self.message_queue.pop()
        dispatched = 0
        for subscriber in self.subscribers.keys():
          message_id = message['message_id']
          message_data = message['message_data']
#          print('FLUSH MESSAGE:', message_id, message_data)
          if message_id in self.subscribers[subscriber]:
#            print('DISPATCH MESSAGE:', message_id, message_data)
            self.subscribers[subscriber][message_id](message_data)
            dispatched = dispatched + 1

        if dispatched == 0:
          print('message_center_class: Lost message:', message_id, message_data)

      self.unlock()

################# End of Message Center Class Definition #################

########################
# Device Manager Class
########################
class device_manager_class():
  # Constructor
  def __init__(self):
    self.devices = []

  # Add a device
  def add_device(self, device):
    self.devices.append(device)

  # Call device controller in each device
  def device_control(self):
    for device in self.devices:
      device.controller()

################# End of Device Controller Class Definition #################

###################################################################################
################# End of Application Foundation Class Definitions #################
###################################################################################

# Class objects
sdcard_obj     = None     # SD Card
midi_obj       = None     # MIDI
smf_player_obj = None     # Standard MIDI File Player
sequencer_obj  = None     # Sequencer
application    = None     # Application


###################
### SD card class
###################
class sdcard_class:
  # Constructor
  def __init__(self):
    self.file_opened = None

  # Initialize SD Card device
  def setup(self):
    print('SD CARD INIT.')
    mf = None
    sdcard.SDCard(slot=2, width=1, sck=18, miso=38, mosi=23, cs=4, freq=1000000)
    print('SD CARD INIT done.')

  # Opened file
  def file_opened(self):
    return self.file_opened

  # File open, needs to close the file
  def file_open(self, path, fname, mode = 'r'):
    try:
      if not self.file_opened is None:
        self.file_opened.close()
        self.file_opened = None

      self.file_opened = open(path + fname, mode)
      return self.file_opened

    except Exception as e:
      self.file_opened = None
      print('sccard_class.file_open Exception:', e, path, fname, mode)

    return None

  # Close the file opened currently
  def file_close(self):
    try:
      if not self.file_opened is None:
        self.file_opened.close()

    except Exception as e:
      print('sccard_class.file_open Exception:', e, path, fname, mode)

    self.file_opened = None

  # Read JSON format file, then retun JSON data
  def json_read(self, path, fname):
    json_data = None
    try:
      with open(path + fname, 'r') as f:
        json_data = json.load(f)

    except Exception as e:
      print('sccard_class.json_read Exception:', e, path, fname)

    return json_data

  # Write JSON format file
  def json_write(self, path, fname, json_data):
    try:
      with open(path + fname, 'w') as f:
        json.dump(json_data, f)

      return True

    except Exception as e:
      print('sccard_class.json_write Exception:', e, path, fname)

    return False

################# End of SD Card Class Definition #################


################
### MIDI class
################
class midi_class:
  # Constructor
  def __init__(self, synthesizer_obj, sdcard_obj):
    self.shynth = synthesizer_obj
    self.midi_uart = self.shynth._uart
    self.sdcard_obj = sdcard_obj
    self.master_volume = 127
    self.key_trans = 0
    self.key_names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    self.USE_GMBANK = 0                              # GM bank number (normally 0, option is 127)
    #self.USE_GMBANK = 127
    self.GM_FILE_PATH = '/sd//SYNTH/MIDIFILE/'       # GM program names list file path

  # Setup
  def setup(self, uart = None):
    if not uart is None:
      self.midi_uart = uart

  # Set/Get GM bank
  def gmbank(self, bank = None):
    if bank is None:
      return self.USE_GMBANK
    
    self.USE_GMBANK = bank

  # Native synthesize object
  def synthesizer_obj(self):
    return self.shynth

  # Native UART object
  def uart_obj(self):
    return self.midi_uart

  # Set/Get GM_FILE_PATH
  def gm_file_path(self, path = None):
    if path is None:
      return self.GM_FILE_PATH

    self.GM_FILE_PATH = path

  # Get GM prgram name
  #   gmbank: GM bank number
  #   program: GM program number
  def get_gm_program_name(self, gmbank, program):
    f = self.sdcard_obj.file_open(self.GM_FILE_PATH, 'GM' + str(gmbank) + '.TXT')
    if not f is None:
      for mf in f:
        mf = mf.strip()
        if len(mf) > 0:
          if program == 0:
            self.sdcard_obj.file_close()
            return mf

        program = program - 1

      self.sdcard_obj.file_close()

    return 'UNKNOWN'

  # Get key name of key number
  #   key_num: MIDI note number
  def key_name(self, key_num):
    octave = int(key_num / 12) - 1
    return self.key_names[key_num % 12] + ('' if octave < 0 else str(octave))

  # MIDI OUT
  def midi_out(self, midi_bytes):
    self.midi_uart.write(midi_bytes)

  # MIDI IN
  def midi_in(self):
    midi_rcv_bytes = self.midi_uart.any()
    if midi_rcv_bytes > 0:
      return self.midi_uart.read()

    return None

  # MIDI IN --> OUT
  # Receive MIDI IN data (UART), then send it to MIDI OUT (UART)
  def midi_in_out(self):
    midi_bytes = self.midi_in()
    if not midi_bytes is None:
      self.midi_out(midi_bytes)
      return True

    return False

  # Set key transopose
  def key_transpose(self, trans = None):
    if not trans is None:
      self.key_trans = trans
  
    return self.key_trans

  # Master volume
  def set_master_volume(self, vol):
    self.master_volume = vol
    self.shynth.set_master_volume(vol)

  # Get master volume
  def get_master_volume(self):
    return self.master_volume

  # Set instrument
  def set_instrument(self, gmbank, channel, prog):
    self.shynth.set_instrument(gmbank, int(channel), int(prog))

  # Note on
  def set_note_on(self, channel, note_key, velosity, transpose = False):
    self.shynth.set_note_on(channel, note_key + (self.key_trans if transpose else 0), velosity)
  
  # Note off
  def set_note_off(self, channel, note_key, transpose = False):
    self.shynth.set_note_off(channel, note_key + (self.key_trans if transpose else 0))

  # Notes off
  def notes_off(self, channel, note_keys, transpose = False):
    for nk in note_keys:
      self.set_note_off(channel, nk, transpose)

  # All notes off
  def set_all_notes_off(self, channel = None):
    if channel is None:
      for ch in range(16):
        self.set_all_notes_off(ch)
    else:
      self.shynth.set_all_notes_off(channel)

  # Reverb
  def set_reverb(self, channel, prog, level, feedback):
    self.shynth.set_reverb(channel, prog, level, feedback)

  # Chorus
  def set_chorus(self, channel, prog, level, feedback, delay):
    self.shynth.set_chorus(channel, prog, level, feedback, delay)

  # Vibrate
  def set_vibrate(self, channel, rate, depth, delay):
    self.shynth.set_vibrate(channel, rate, depth, delay)

################# End of MIDI Class Definition #################


################################
# Message class for MIDI class
################################
class midi_message_class(midi_class):
  # Constructor
  def __init__(self, synthesizer_obj, sdcard_obj, message_center = None):
    super().__init__(synthesizer_obj, sdcard_obj)

    # Message Center
    if not message_center is None:
      self.message_center = message_center
      self.message_center.add_contributor(self)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_ALL_NOTES_OFF, self.func_MIDI_ALL_NOTES_OFF)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_GET_PROGRAM_NAME, self.func_MIDI_GET_PROGRAM_NAME)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_SET_INSTRUMENT, self.func_MIDI_SET_INSTRUMENT)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_SET_GET_MASTER_VOLUME, self.func_MIDI_SET_GET_MASTER_VOLUME)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_SET_REVERB, self.func_MIDI_SET_REVERB)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_SET_CHORUS, self.func_MIDI_SET_CHORUS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_SET_VIBRATE, self.func_MIDI_SET_VIBRATE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_SEND_PITCH_BEND, self.func_MIDI_SEND_PITCH_BEND)

    else:
      self.message_center = message_center_class()

  def func_MIDI_GET_PROGRAM_NAME(self, message_data = None):
    return self.get_gm_program_name(message_data['gm_bank'], message_data['program_number'])

  def func_MIDI_SET_INSTRUMENT(self, message_data = None):
    self.set_instrument(message_data['gm_bank'], message_data['channel'], message_data['program_number'])

  def func_MIDI_ALL_NOTES_OFF(self, message_data = None):
    if message_data is None:
      self.set_all_notes_off()
    elif 'channel' in message_data.keys():
      self.set_all_notes_off(message_data['channel'])
    else:
      self.set_all_notes_off()

  def func_MIDI_SET_GET_MASTER_VOLUME(self, message_data = None):
    if message_data is None:
      return self.get_master_volume()

    if 'value' in message_data.keys():
      self.set_master_volume(message_data['value'])

    return self.get_master_volume()

  def func_MIDI_SET_REVERB(self, message_data = None):
    if not message_data is None:
      if 'channel' in message_data.keys():
        channel = message_data['channel']
      else:
        return
      
      if 'program' in message_data.keys():
        prog = message_data['program']
      else:
        prog = 0
      
      if 'level' in message_data.keys():
        level = message_data['level']
      else:
        level = 0
      
      if 'feedback' in message_data.keys():
        feedback = message_data['feedback']
      else:
        feedback = 0

      self.set_reverb(channel, prog, level, feedback)

  # Chorus
  def func_MIDI_SET_CHORUS(self, message_data = None):
    if not message_data is None:
      if 'channel' in message_data.keys():
        channel = message_data['channel']
      else:
        return
      
      if 'program' in message_data.keys():
        prog = message_data['program']
      else:
        prog = 0
      
      if 'level' in message_data.keys():
        level = message_data['level']
      else:
        level = 0
      
      if 'feedback' in message_data.keys():
        feedback = message_data['feedback']
      else:
        feedback = 0
      
      if 'delay' in message_data.keys():
        delay = message_data['delay']
      else:
        delay = 0

      self.set_chorus(channel, prog, level, feedback, delay)

  # Vibrate
  def func_MIDI_SET_VIBRATE(self, message_data = None):
    if not message_data is None:
      if 'channel' in message_data.keys():
        channel = message_data['channel']
      else:
        return
      
      if 'rate' in message_data.keys():
        rate = message_data['rate']
      else:
        rate = 0
      
      if 'depth' in message_data.keys():
        depth = message_data['depth']
      else:
        depth = 0
      
      if 'delay' in message_data.keys():
        delay = message_data['delay']
      else:
        delay = 0

    self.set_vibrate(channel, rate, depth, delay)

  def func_MIDI_SEND_PITCH_BEND(self, message_data = None):
    if not message_data is None:
      if 'value' in message_data.keys():
        value = message_data['value']
        if value < -8192:
          value = -8192
        elif value > 8191:
          value = 8191
      else:
        return

      if not 'channel' in message_data.keys():
        channel = 0
      else:
        channel = message_data['channel']
        if channel < 0:
          channel = 0
        elif channel > 15:
          channel = 15

    print('PITCH BEND PARM:', channel, hex(0xe0 + channel), value)
    byte_data = [0xe0 + channel]
    byte_data.append(value & 0x7f)
    value = value >> 7
    byte_data.append(value & 0x7f)
    print('PITCH BEND DATA:', byte_data, bytearray(byte_data))
    self.midi_out(bytearray(byte_data))

################# End of Message class for MIDI class #################


###################################
# Standard MIDI FIle Player Class 
###################################
class smf_player_class():
  # Constructor
  def __init__(self, midi_obj, sdcard_obj):
    self.midi_obj = midi_obj
    self.sdcard_obj = sdcard_obj

    self.smf_files = []               # Standar MIDI file names list
    self.smf_file_selected = -1       # SMF index in smf_files to read

    self.smf_transpose = 0            # Transpose keys
    self.smf_volume_delta = 0         # Velosity delta value
    self.smf_settings = {'reverb':[0,0,0], 'chorus': [0,0,0,0], 'vibrate': [0,0,0]}
    self.smf_speed_factor = 1.0       # Speed factor to play SMF
    self.smf_play_mode = 'STOP'       # SMF Player control word
    self.playing_smf = False          # Playing a SMF at the moment or not
    self.SMF_FILE_PATH = '/sd//SYNTH/MIDIFILE/'       # Standard MIDI files path
    self.SMF_LIST_FILE = 'LIST.TXT'                   # SMF files list

  # Make the standard midi files catalog
  def standard_midi_file_catalog(self):
    f = self.sdcard_obj.file_open(self.SMF_FILE_PATH, self.SMF_LIST_FILE)
    if not f is None:
      for mf in f:
        mf = mf.strip()
        if len(mf) > 0:
          cat = mf.split(',')
          if len(cat) == 3:
            self.smf_files.append(cat)

      self.sdcard_obj.file_close()

    if len(self.smf_files) > 0:
      self.smf_file_selected = 0
      for i in range(len(self.smf_files)):
        self.smf_files[i][2] = float(self.smf_files[i][2])

      return True

    return False

  # Set/Get SMF_FILE_PATH
  def smf_file_path(self, path = None):
    if path is None:
      return self.SMF_FILE_PATH

    self.SMF_FILE_PATH = path

  # Set/Get SMF_LIST_FILE
  def smf_file_list(self, fname = None):
    if fname is None:
      return self.SMF_LIST_FILE

    self.SMF_LIST_FILE = fname

  # MIDI: Get a delta time in integer
  def delta_time(self, btime):
  #  print('delta_time=' + str(len(btime)))
    dt = 0
    for b in btime:
      dt = dt << 7
      dt = dt | int(b & 0x7f)

  #  print('btime=' + str(dt))
    return dt

  # MIDI EVENT: Polyphonic key pressure
  #   ch: MIDI channel
  #   rb: Note number
  def midiev_polyphonic_key_pressure(self, ch, rb):
    pass

  # MIDI EVENT: Control change for standard MIDI file
  #   ch: MIDI channel
  #   rb[0]: Control Number
  #   rb[1]: Data
  def midiev_control_change(self, ch, rb):
    # Reverb
    if rb[0] == 0x91:
      self.midi_obj.set_reverb(channel, 0, rb[1], 127)
    # Chorus
    elif rb[0] == 0x93:
      self.midi_obj.set_chorus(channel, 0, rb[1], 127, 127)

  # MIDI EVENT: Program change for standard MIDI file
  #   ch: MIDI channel
  #   rb[0]: Program Number
  def midiev_program_change(self, ch, rb):
    self.midi_obj.set_instrument(self.midi_obj.gmbank(), ch, rb[0])

  # MIDI EVENT: channel pressure for standard MIDI file
  def midiev_channel_pressure(self, ch, rb):
    pass

  # MIDI EVENT: Pitch bend for standard MIDI file
  def midiev_pitch_bend(self, ch, rb):
    pass

  # MIDI EVENT: SysEx F0 for standard MIDI file
  def midiev_sysex_f0(self, rb):
    pass

  # MIDI EVENT: SysEx F7 for standard MIDI file
  def midiev_sysex_f7(self, rb):
    pass

  # MIDI EVENT: SysEx FF (Meta data) for standard MIDI file
  def midiev_meta_data(self, et, rb):
    pass

  # Copy a byte list into an integer list
  #   blist[]: Byte data list (SMF data)
  def to_int_list(self, blist):
    ilist = []
    for b in blist:
      ilist.append(int(b))
    return ilist

  # Set and show new transpose value for SMF player
  # smf_transpose value is added to note-on note number.
  #   dlt: transpose delta value
  def set_smf_transpose(self, dlt):
    self.smf_transpose = self.smf_transpose + dlt
    if self.smf_transpose == -13:
      self.smf_transpose = 0
    elif self.smf_transpose == 13:
      self.smf_transpose = 0

    self.midi_obj.key_transpose(self.smf_transpose)

  # Set and show new volume delta value for SMF player
  # smf_volume_delta value is added to note-on-velocity.
  #   dlt: volume delta value
  def set_smf_volume_delta(self, dlt):
    self.smf_volume_delta = self.smf_volume_delta + dlt

  # Set reverb parameters for SMF player (to all MIDI channel)
  #   prog : Reverb program
  #   level: Reverb level
  #   fback: Reverb feedback
  def set_smf_reverb(self, prog=None, level=None, fback=None):
    disp = None
    if not prog is None:
      self.smf_settings['reverb'][0] = prog
      disp = prog

    if not level is None:
      self.smf_settings['reverb'][1] = level
      disp = level
      
    if not fback is None:
      self.smf_settings['reverb'][2] = fback
      disp = fback

    if not disp is None:
      for ch in range(16):
        self.midi_obj.set_reverb(ch, self.smf_settings['reverb'][0], self.smf_settings['reverb'][1], self.smf_settings['reverb'][2])

    return self.smf_settings

  # Set chorus parameters for SMF player (to all MIDI channel)
  #   prog : Chorus program
  #   level: Chorus level
  #   fback: Chorus feedback
  #   delay: Chorus delay
  def set_smf_chorus(self, prog=None, level=None, fback=None, delay=None):
    send = False
    if not prog is None:
      self.smf_settings['chorus'][0] = prog
      send = True

    if not level is None:
      self.smf_settings['chorus'][1] = level
      send = True
      
    if not fback is None:
      self.smf_settings['chorus'][2] = fback
      send = True
      
    if not delay is None:
      self.smf_settings['chorus'][3] = delay
      send = True

    if send:
      for ch in range(16):
        self.midi_obj.set_chorus(ch, self.smf_settings['chorus'][0], self.smf_settings['chorus'][1], self.smf_settings['chorus'][2], self.smf_settings['chorus'][3])

    return self.smf_settings

  # Set vibrate parameters for SMF player (to all MIDI channel)
  #   level: Vibrate level
  #   depth: Vibrate depth
  #   delay: Vibrate delay
  def set_smf_vibrate(self, rate=None, depth=None, delay=None):
    send = False
    if not rate is None:
      self.smf_settings['vibrate'][0] = rate
      send = True

    if not depth is None:
      self.smf_settings['vibrate'][1] = depth
      send = True
      
    if not delay is None:
      self.smf_settings['vibrate'][2] = delay
      send = True

    if send:
      for ch in range(16):
        self.midi_obj.set_vibrate(ch, self.smf_settings['vibrate'][0], self.smf_settings['vibrate'][1], self.smf_settings['vibrate'][2])

    return self.smf_settings

  # Set settings by key and index
  def set_settings(self, setting_key, prm_index, val):
    self.smf_settings[setting_key][prm_index] = val

  # Get settings
  def get_smf_settings(self):
    return self.smf_settings

  # Set/Get speed factor
  def set_smf_speed_factor(self, factor = None):
    if not factor is None:
      self.smf_speed_factor = factor

    return self.smf_speed_factor

  # Set/Get play mode
  def set_smf_play_mode(self, mode = None):
    if not mode is None:
      self.smf_play_mode = mode

    return self.smf_play_mode

  # Set/Get play
  def set_playing_smf(self, flg = None):
    if not flg is None:
      self.playing_smf = flg

    return self.playing_smf

  # Play a MIDI file function for Unit-MIDI, works in thread process.
  # Read and interpret a standard MIDI file (format-0) and send play data to Unit-MIDI.
  #   fname: Standar MIDI file name to play
  #   callback_changed_status: Callback function to notify change working status of SMF Player
  def play_standard_midi_file(self, fpath, fname, callback_changed_status = None):
    # Read delta-time data in SMF
    def read_delta_time():
      dt = []
      rd = [0x80]
      while rd[0] & 0x80 == 0x80:
        rd = read_track_data(1, 0, 0)
        dt.append(rd[0])

      return dt

    # Read a track-data in SMF
    def read_track_data(read_bytes, del_bytes, add_data):
      nonlocal data_len

      read_bytes = read_bytes - del_bytes
      if read_bytes <= 0:
        rd = []
      else:
        rd = f.read(read_bytes)
        data_len = data_len - read_bytes

      if del_bytes == 1:
        dt = [add_data]
        dt = dt + self.to_int_list(rd)
      else:
        dt = self.to_int_list(rd)
  #    print('RET=' + str(len(dt)))
      return dt

    # MIDI EVENT: Note on
    #   ch: MIDI channel
    #   rb[0]: Note number
    #   rb[1]: Velocity (0 means Note Off)
    def midiev_note_on(ch, rb):
      if rb[1] == 0:
    #    notes_off(ch, [rb[0]])
        self.midi_obj.notes_off(ch, [rb[0]], True)
      else:
        vol = int(rb[1]) + self.smf_volume_delta
        if vol <= 0:
          vol = 1
        elif vol > 127:
          vol = 127
        
        # Note-on with key transpose
        self.midi_obj.set_note_on(ch, int(rb[0]), vol, True)

    def callback_function_ignore(data):
      pass

    ### CODE: play_standard_midi_file() ###

    # Callback function
    if callback_changed_status is None:
      callback_changed_status = callback_function_ignore

    # Now playing
    if self.set_playing_smf() == True:
      print('Now playing...')
      return

    # Start SMF player
    print('MIDI PLAYER:' + fname)
    self.set_playing_smf(True)
    self.set_smf_play_mode('PLAY')
    callback_changed_status('PLAY')

    filename = fpath + fname
    try:
      # Chunk type: 0=void 1=header 2=track
      chunk_type = 0
      data_len = -1
      print(os.stat(filename)[0] == 0x8000)
      f = open(filename, 'rb')
      while True:
        # Read a chunk
        rb = f.read(4)
        if len(rb) < 4:
          break
        
        print('CHUNK:' + str(hex(rb[0])) + ' ' + str(hex(rb[1])) + ' ' + str(hex(rb[2])) + ' ' + str(hex(rb[3])))
        # Header chunk
        if rb[0] == 0x4d and rb[1] == 0x54 and rb[2] == 0x68 and rb[3] == 0x64:
          print('HEADER CHUNK')
          chunk_type = 1
          data_len = -1
          # Data length
          rb = f.read(4)
          if len(rb) < 4:
            break

          data_len = rb[0] * 16777216 + rb[1] * 65536 + rb[2] * 256 + rb[3]
          if data_len != 6:
            print('Data length error in HEADER CHUNK:' + str(data_len))
            break

          # Format
          rb = f.read(2)
          if len(rb) < 2:
            break

          midi_format = rb[0] * 256 + rb[1]
          if midi_format != 0:
            print('MIDI format error in HEADER CHUNK:' + str(midi_format))
            break

          # Track number
          rb = f.read(2)
          if len(rb) < 2:
            break

          track_number = rb[0] * 256 + rb[1]
          if track_number < 1:
            print('Track number error in HEADER CHUNK:' + str(track_number))
            break

          # Time unit
          rb = f.read(2)
          if len(rb) < 2:
            break

          time_unit = rb[0] * 256 + rb[1]
          if time_unit < 1:
            print('Time unit error in HEADER CHUNK:' + str(track_number))
            break

          print('HEADER CHUNK: format=' + str(midi_format) + '/tracks=' + str(track_number) + '/timeunit='+ str(time_unit))
          time_unit = time_unit / 96.0

        # Track chunk
        elif rb[0] == 0x4d and rb[1] == 0x54 and rb[2] == 0x72 and rb[3] == 0x6b:
          chunk_type = 2
          data_len = -1
          print('TRUCK CHUNK')
          # Data length
          rb = f.read(4)
          if len(rb) < 4:
            break

          data_len = rb[0] * 16777216 + rb[1] * 65536 + rb[2] * 256 + rb[3]
          if data_len <= 0:
            print('Data length error in TRUCK CHUNK:' + str(data_len))
            break

          print('READ TRUCK CHUNK: data length=' + str(data_len))

          # Read data in the track chunck
          prev_event = 0
          rsr_bt = 0
          rsr = 0
          ev = 0
          ch = 0
          while True:
            # SMF player thread control: STOP
            if self.set_smf_play_mode() == 'STOP':
              print('--->STOP PLAYER')
              f.close()
              self.set_playing_smf(False)
              callback_changed_status('STOP')
              return

            # SMF player thread control: PAUSE
            if self.set_smf_play_mode() == 'PAUSE':
              print('--->PAUSE MODE')
              master_volume = self.midi_obj.get_master_volume()
              self.midi_obj.set_master_volume(0)
              callback_changed_status('PAUSE')

              while True:
                print('WAITING:' + self.set_smf_play_mode())
                time.sleep(0.5)
                if self.set_smf_play_mode() == 'PLAY':
                  self.midi_obj.set_master_volume(master_volume)
                  callback_changed_status('PLAY')
                  break

                if self.set_smf_play_mode() == 'STOP':
                  f.close()
                  self.set_playing_smf(False)
                  self.midi_obj.set_master_volume(master_volume)
                  callback_changed_status('STOP')
                  return
                  
            # Delta time
  #          print('Get delta time')
            dtbytes = read_delta_time()
  #          print('Delta time bytes=' + str(len(dtbytes)))

            # Get an event or data (if in runing status rule)
            rb = f.read(1)
            data_len = data_len - 1

            # New event
            if rb[0] & 0x80 == 0x80:
              ev = rb[0] & 0xf0
              ch = rb[0] & 0x0f
              rsr = 0
            # Running status rule (inherits the previous event and channel)
            else:
              rsr_bt = rb[0]
              rsr = 1
            
            # Delta time
  #          print('Calc delta time:' + str(len(dtbytes)))
            dtime = self.delta_time(dtbytes)
  #          print('DELTA TIME=' + str(dtime))
            if dtime > 0:
              time.sleep(dtime/200.0/time_unit/self.smf_speed_factor)

  #          print('EVT=' + str(hex(ev)) + '/ CH=' + str(ch) + '/ RSR=' + str(rsr) + '/ DTM =' + str(dtime))

            # Note off
            if ev == 0x80:
              rb = read_track_data(2, rsr, rsr_bt)
              self.midi_obj.notes_off(ch, rb, True)

            # Note on (Note off if volume equals zero)
            elif ev == 0x90:
              rb = read_track_data(2, rsr, rsr_bt)
              midiev_note_on(ch, rb)

            # Polyphonic key pressure
            elif ev == 0xa0:
              rb = read_track_data(2, rsr, rsr_bt)
              self.midiev_polyphonic_key_pressure(ch, rb)

            # Control change
            elif ev == 0xb0:
              rb = read_track_data(2, rsr, rsr_bt)
              self.midiev_control_change(ch, rb)

            # Program change
            elif ev == 0xc0:
              rb = read_track_data(1, rsr, rsr_bt)
              self.midiev_program_change(ch, rb)

            # channel pressure
            elif ev == 0xd0:
              rb = read_track_data(1, rsr, rsr_bt)
              self.midiev_channel_pressure(ch, rb)

            # Pitch bend
            elif ev == 0xe0:
              rb = read_track_data(2, rsr, rsr_bt)
              self.midiev_pitch_bend(ch, rb)

            # SysEx
            elif ev == 0xf0:
              print('Fx EVENT=' + str(ch))
              # F0
              if ch == 0:
                rb = read_track_data(1, rsr, rsr_bt)
                
                # Read data to send
                dlen = int(rb[0])
                rb = read_track_data(dlen, 0, 0)
                self.midiev_sysex_f0(rb)

              # F7
              elif ch == 7:
                rb = read_track_data(1, rsr, rsr_bt)
                
                # Read data to send
                dlen = int(rb[0])
                rb = read_track_data(dlen, 0, 0)
                self.midiev_sysex_f7(rb)

              # FF (Meta data)
              elif ch == 0x0f:
                # Event type
                rb = read_track_data(1, rsr, rsr_bt)
                et = rb[0]

                # Data length
                dtbytes = read_delta_time()
                dlength = self.delta_time(dtbytes)
                print('Data length bytes=' + str(len(dtbytes)) + '/ length=' + str(dlength))
                if dlength > 0:
                  rb = read_track_data(dlength, 0, 0)
                else:
                  rb = []

                print('FF event=' + str(hex(et)) + '/ data=' + str(len(rb)) + '/ data_len=' + str(data_len))
                self.midiev_meta_data(et, rb)
                print('FF')
              # Uknown event
              else:
                print('UNKNOWN EVENT=' + str(hex(et)))

            # Check the end of the track data
            if data_len == 0:
              print('TRUCK DATA END NORMALLY.')
              break
        else:
          print('UNKNOWN CHUNK')
          break

      print('CLOSE FILE.')
      f.close()
    except Exception as e:
      print('FILE ERROR:', e)
    finally:
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_ALL_NOTES_OFF)

    self.set_playing_smf(False)
    self.set_smf_play_mode('STOP')
    callback_changed_status('STOP')

################# End of Standard MIDI File Class Definition #################


######################################
# Message class for SMF PLayer class
######################################
class smf_player_message_class(smf_player_class):
  # Constructor
  def __init__(self, midi_obj, sdcard_obj, message_center = None):
    super().__init__(midi_obj, sdcard_obj)

    # Message Center
    if not message_center is None:
      self.message_center = message_center
      self.message_center.add_contributor(self)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_MAKE_SMF_CATALOG, self.func_SMF_PLAYER_MAKE_SMF_CATALOG)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_CONTROL, self.func_SMF_PLAYER_CONTROL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_CHANGE_SMF_FILE_NO, self.func_SMF_PLAYER_CHANGE_SMF_FILE_NO)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_CHANGE_TRANSPOSE, self.func_SMF_PLAYER_CHANGE_TRANSPOSE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_CHANGE_VOLUME, self.func_SMF_PLAYER_CHANGE_VOLUME)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_IS_PLAYING_SMF, self.func_SMF_PLAYER_IS_PLAYING_SMF)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_SET_GET_PLAY_MODE, self.func_SMF_PLAYER_SET_GET_PLAY_MODE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_SET_GET_SPEED_FACTOR, self.func_SMF_PLAYER_SET_GET_SPEED_FACTOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_GET_EFFECTOR_SETTINGS, self.func_SMF_PLAYER_GET_EFFECTOR_SETTINGS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_SET_EFFECTOR_PARAMETER, self.func_SMF_PLAYER_SET_EFFECTOR_PARAMETER)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_SET_REVERB, self.func_SMF_PLAYER_SET_REVERB)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_SET_CHORUS, self.func_SMF_PLAYER_SET_CHORUS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SMF_PLAYER_SET_VIBRATE, self.func_SMF_PLAYER_SET_VIBRATE)

    else:
      self.message_center = message_center_class()

  def func_SMF_PLAYER_MAKE_SMF_CATALOG(self, message_data = None):
    if self.standard_midi_file_catalog():
      self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_FNAME_SET_TEXT)

  def func_SMF_PLAYER_CONTROL(self, message_data = None):
    # Callback function just after SMF Player status is changed
    #   status: PLAY / PAUSE / STOP
    def on_smf_player_status_changed(status):
      if status == 'PAUSE':
        disp = 'PAUS'
      elif status == 'STOP':
        disp = 'FILE'
      else:
        disp = status

      self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_TEXT, {'label': 'label_smf_file', 'value': disp + ':'})
      if status == 'STOP':
        self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SEND_ALL_MIDI_SETTINGS)

    ### func_SMF_PLAYER_CONTROL ###
    if self.set_playing_smf() == True:
      print('STOP MIDI PLAYER')
      self.set_smf_play_mode('STOP')
    else:
      print('REPLAY MIDI PLAYER')
      if self.smf_file_selected >= 0:
        spf = self.set_smf_speed_factor(self.smf_files[self.smf_file_selected][2])
        self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_TEMPO_SET_TEXT, {'value': spf})
        _thread.start_new_thread(self.play_standard_midi_file, (self.smf_file_path(), self.smf_files[self.smf_file_selected][1], on_smf_player_status_changed,))

  def func_SMF_PLAYER_CHANGE_SMF_FILE_NO(self, message_data = None):
    if self.set_playing_smf() == False:
      if self.smf_file_selected >= 0:
        delta = message_data['delta']
        if delta == -1:
          self.smf_file_selected = self.smf_file_selected - 1
          if self.smf_file_selected == -1:
            self.smf_file_selected = len(self.smf_files) - 1
        elif delta == 1:
          self.smf_file_selected = self.smf_file_selected + 1
          if self.smf_file_selected == len(self.smf_files):
            self.smf_file_selected = 0

        if delta != 0:
          self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_FNUM_SET_TEXT)
          self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_FNAME_SET_TEXT)

  def func_SMF_PLAYER_CHANGE_TRANSPOSE(self, message_data = None):
    delta = message_data['delta']
    self.message_center.phone_message(self, self.message_center.MSGID_MIDI_ALL_NOTES_OFF)
    self.set_smf_transpose(delta)
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_TRANSP_SET_TEXT)

  def func_SMF_PLAYER_CHANGE_VOLUME(self, message_data = None):
    delta = message_data['delta']
    self.set_smf_volume_delta(delta)
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_VOLUME_SET_TEXT)

  def func_SMF_PLAYER_IS_PLAYING_SMF(self, message_data = None):
    return self.set_playing_smf()

  def func_SMF_PLAYER_SET_GET_PLAY_MODE(self, message_data = None):
    if not message_data is None:
      if 'set' in message_data:
        self.set_smf_play_mode(message_data['set'])

    return self.set_smf_play_mode()

  def func_SMF_PLAYER_SET_GET_SPEED_FACTOR(self, message_data = None):
    if not message_data is None:
      if 'set' in message_data.keys():
        self.set_smf_speed_factor(message_data['set'])

    return self.set_smf_speed_factor()

  def func_SMF_PLAYER_GET_EFFECTOR_SETTINGS(self, message_data = None):
    return self.get_smf_settings()

  def func_SMF_PLAYER_SET_EFFECTOR_PARAMETER(self, message_data = None):
    self.set_settings(message_data['effector'], message_data['param_index'], message_data['value'])

  def func_SMF_PLAYER_SET_REVERB(self, message_data = None):
    self.set_smf_reverb(message_data['program'], message_data['level'], message_data['feedback'])

  def func_SMF_PLAYER_SET_CHORUS(self, message_data = None):
    self.set_smf_chorus(message_data['program'], message_data['level'], message_data['feedback'], message_data['delay'])

  def func_SMF_PLAYER_SET_VIBRATE(self, message_data = None):
    self.set_smf_vibrate(message_data['rate'], message_data['depth'], message_data['delay'])


################# End of midi_in_player_message_class Definition #################


###################
# Sequencer Class
###################
class sequencer_class():
  # self.seq_channel: Sequencer channel data
  #   [{'gmbank': <GM bank>, 'program': <GM program>, 'volume': <Volume ratio>}, ..]

  # self.seq_score: Sequencer score data
  #   [
  #     {
  #       'time': <Note on time>,
  #       'max_duration': <Maximum duration in note off times>
  #       'notes': [
  #                  {
  #                   'channel': <MIDI channel>,
  #                   'note': <Note number>, 'velocity': <Velocity>, 'duration': <Note on duration>
  #                  }
  #                ]
  #     }
  #   ] 

  # self.seq_score_sign: Signs on the score
  # [
  #    {
  #       'time': <Signs on time>,
  #       'loop' <True/False>       Repeat play from here
  #       'skip' <True/False>       Bar to skip in repeat play, skip to next to repeat bar
  #       'repeat' <True/False>     Repeat here, go back to loop
  #    }
  # ]

  # Sequencer controls
  #   'tempo': Play a quoter note 'tempo' times per a minutes 
  #   'mini_note': Minimum note length (4,8,16,32,64: data are 2,3,4,5,6 respectively) 
  #   'time_per_bar': Times (number of notes) per bar
  #   'disp_time': Time span to display on sequencer
  #   'disp_key': Key spans to display on sequencer each track
  #   'time_cursor': Time cursor to edit note
  #   'key_cursor': Key cursors to edit note each track
  #   'program': Program number for each MIDI channel

  # self.seq_parm_repeat: Current time cursor position or None

  # Constructor
  def __init__(self, midi_obj, sdcard_obj):
    self.midi_obj = midi_obj
    self.sdcard_obj = sdcard_obj
    self.seq_channel = None
    self.seq_score = None
    self.seq_score_sign = None
    self.seq_parm_repeat = None
    self.seq_control = {'tempo': 120, 'mini_note': 4, 'time_per_bar': 4, 'disp_time': [0,12], 'disp_key': [[57,74],[57,74]], 'time_cursor': 0, 'key_cursor': [60,60], 'program':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], 'gmbank':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}

    # View method delegation
    self.view_delegate_obj = self

    # Sequencer file
    self.SEQ_FILE_LOAD = 0
    self.SEQ_FILE_SAVE = 1
    self.SEQ_FILE_NOP  = 2

    # Sequencer file
    self.seq_file_number = 0                               # Sequencer file number
    self.seq_file_ctrl = self.SEQ_FILE_NOP                 # Currnet MIDI IN setting file operation id
    self.seq_file_ctrl_label = ['L', 'S', '-']             # Load / Save / nop

    # Sequencer parameter
    #   Sequencer parameter strings to show
    self.SEQUENCER_PARM_CHANNEL = 0                        # Change a track MIDI channel
    self.SEQUENCER_PARM_PROGRAM = 1                        # Change program of MIDI channel
    self.SEQUENCER_PARM_CHANNEL_VOL = 2                    # Change volume ratio of MIDI channel
    self.SEQUENCER_PARM_TIMESPAN = 3                       # Change times to display
    self.SEQUENCER_PARM_STRETCH_ONE = 4                    # Insert/Delete a time in the current MIDI channel
    self.SEQUENCER_PARM_STRETCH_ALL = 5                    # Insert/Delete a time in all MIDI channels
    self.SEQUENCER_PARM_VELOCITY = 6                       # Change note velocity
    self.SEQUENCER_PARM_NOTES_BAR = 7                      # Change number of notes in a bar
    self.SEQUENCER_PARM_RESOLUTION = 8                     # Resolution up
    self.SEQUENCER_PARM_CLEAR_ONE = 9                      # Clear all notes in the current MIDI channel
    self.SEQUENCER_PARM_CLEAR_ALL = 10                     # Clear all notes in all MIDI channels
    self.SEQUENCER_PARM_PLAYSTART = 11                     # Start and end time to play with sequencer
    self.SEQUENCER_PARM_PLAYEND = 12                       # End time to play with sequencer
    self.SEQUENCER_PARM_TEMPO = 13                         # Change tempo to play sequencer
    self.SEQUENCER_PARM_MINIMUM_NOTE = 14                  # Change minimum note length
    self.SEQUENCER_PARM_REPEAT = 15                        # Set repeat signs (NONE/LOOP/SKIP/REPEAT)
    self.seq_parm = self.SEQUENCER_PARM_CHANNEL                 # Current sequencer parameter index (= initial)

    # Sequencer parameter
    #   Sequencer parameter strings to show
    self.seq_parameter_names = ['MDCH', 'MDPG', 'CHVL', 'TIME', 'STR1', 'STRA', 'VELO', 'NBAR', 'RESL', 'CLR1', 'CLRA', 'PLYS', 'PLYE', 'TMP', 'MIN', 'REPT']
    self.seq_total_parameters = len(self.seq_parameter_names)   # Number of seq_parm

    # Editor/Player settings
    self.seq_edit_track = 0                  # The track number to edit (0 or 1, 0 is Track1 as display)
    self.seq_track_midi = [0,1]              # MIDI channels for the two tracks on the display
    self.seq_play_time = [0,0]               # Start and end time to play with sequencer
    self.seq_cursor_note = None              # The score and note data on the cursor (to highlite the note)

    # Backup the cursor position
    self.time_cursor_bk = None
    self.key_cursor0_bk = None
    self.key_cursor1_bk = None
    self.seq_disp_time0_bk  = None
    self.seq_disp_time1_bk  = None
    self.master_volume_bk = None

    # Display mode to draw note on sequencer
    self.SEQ_NOTE_DISP_NORMAL = 0
    self.SEQ_NOTE_DISP_HIGHLIGHT = 1
    self.seq_note_color = [[0x00ff88,0x8888ff], [0xff4040,0xffff00]]   # Note colors [frame,fill] for each display mode
    self.seq_draw_area = [[20,40,319,129],[20,150,319,239]]      # Display area for each track

    # Maximum number of sequence files
    self.SEQ_FILE_MAX = 1000

    # Sequencer file path
    self.SEQUENCER_FILE_PATH = '/sd//SYNTH/SEQFILE/'

  # Set delegation class for graphics
  def delegate_graphics(self, view_delegate_obj):
    self.view_delegate_obj = view_delegate_obj

  # Set up the sequencer
  def setup_sequencer(self):
    # Initialize the sequencer channels
    self.seq_channel = []
    for ch in range(16):
      self.seq_channel.append({'gmbank': self.midi_obj.gmbank(), 'program': ch, 'volume': 100})

    # Clear score
    self.seq_score = []
    self.seq_score_sign = []

  # Set/Get sequencer file path
  def set_sequencer_file_path(self, path = None):
    if path is None:
      return self.SEQUENCER_FILE_PATH
    
    self.SEQUENCER_FILE_PATH = path
    return self.SEQUENCER_FILE_PATH

  # Set/Get edit track
  def edit_track(self, trknum = None):
    if not trknum is None:
      self.seq_edit_track = trknum

    return self.seq_edit_track

  # Set MIDI channel of each tracks
  def set_track_midi(self, channel, trknum = None):
    if trknum is None:
      trknum = self.seq_edit_track

    self.seq_track_midi[trknum] = channel
  
  # Get MIDI channel of each tracks
  def get_track_midi(self, trknum = None):
    if trknum is None:
      trknum = self.seq_edit_track

    return self.seq_track_midi[trknum]

  # Set/Get start and end time to play
  def play_time(self, side = None, val = None):
    if side is None:
      return self.seq_play_time

    if val is None:
      return self.seq_play_time[side]

    self.seq_play_time[side] = val
    return val

  # Set the cursor note in sequencer
  def set_cursor_note(self, val):
    self.seq_cursor_note = val

  # Get the cursor note in sequencer
  def get_cursor_note(self, side = None):
    if side is None:
      return self.seq_cursor_note

    return self.seq_cursor_note[side]

  # Clear seq_score
  def clear_seq_score(self):
    self.seq_score = []

  # Get seq_score
  def get_seq_score(self):
    return self.seq_score

  # Set seq_channel
  def set_seq_channel(self, channel, key_str, val):
    self.seq_channel[channel][key_str] = val
    return val

  # Get seq_channel
  def get_seq_channel(self, channel, key_str):
    return self.seq_channel[channel][key_str]

  # Set seq_parm_repeat
  def set_seq_parm_repeat(self, time_cursor):
    self.seq_parm_repeat = time_cursor
    return self.seq_parm_repeat

  # Get seq_parm_repeat
  def get_seq_parm_repeat(self):
    return self.seq_parm_repeat

  # Set time cursor
  def set_seq_time_cursor(self, cursor):
    self.seq_control['time_cursor'] = cursor if cursor >= 0 else 0

  # Get time cursor
  def get_seq_time_cursor(self):
    return self.seq_control['time_cursor']

  # Set key cursor
  def set_seq_key_cursor(self, trknum, cursor):
    if cursor < 0:
      cursor = 0
    elif cursor > 127:
      cursor = 127

    self.seq_control['key_cursor'][trknum] = cursor

  # Get key cursor
  def get_seq_key_cursor(self, trknum = None):
    if trknum is None:
      return self.seq_control['key_cursor']
    else:
      return self.seq_control['key_cursor'][trknum]

  # Set display key
  def set_seq_disp_key(self, trknum, key_from, key_to):
    self.seq_control['disp_key'][trknum][0] = key_from
    self.seq_control['disp_key'][trknum][1] = key_to

  # Get display key
  def get_seq_disp_key(self, trknum, side = None):
    if side is None:
      return self.seq_control['disp_key'][trknum]
    else:
      return self.seq_control['disp_key'][trknum][side]

  # Set display time
  def set_seq_disp_time(self, time_from, time_to):
    self.seq_control['disp_time'][0] = time_from
    self.seq_control['disp_time'][1] = time_to

  # Get display time
  def get_seq_disp_time(self, side = None):
    if side is None:
      return self.seq_control['disp_time']
    else:
      return self.seq_control['disp_time'][side]

  # Set time per bar
  def set_seq_time_per_bar(self, tpb):
    self.seq_control['time_per_bar'] = tpb if tpb > 2 else 2

  # Get time per bar
  def get_seq_time_per_bar(self):
    return self.seq_control['time_per_bar']

  # Set tempo
  def set_seq_tempo(self, tempo):
    if tempo < 6:
      tempo = 6
    elif tempo > 999:
      tempo = 999

    self.seq_control['tempo'] = tempo

  # Get tempo
  def get_seq_tempo(self):
    return self.seq_control['tempo']

  # Set minimum note length
  def set_seq_mini_note(self, length):
    if length < 2:
      length = 2
    elif length > 5:
      length = 5

    self.seq_control['mini_note'] = length

  # Get minimum note length
  def get_seq_mini_note(self):
    return self.seq_control['mini_note']

  # Set GM bank for a channel
  def set_seq_gmbank(self, channel, bank):
    self.seq_control['gmbank'][channel] = bank

  # Get GM bank for a channel
  def get_seq_gmbank(self, channel):
    return self.seq_control['gmbank'][channel]

  # Set program for a channel
  def set_seq_program(self, channel, prog):
    prog = prog % 128
    self.seq_control['program'][channel] = prog

  # Get program for a channel
  def get_seq_program(self, channel):
    return self.seq_control['program'][channel]

  # Save sequencer file
  def sequencer_save_file(self, path, num):
    # Write MIDI IN settings as JSON file
    if self.sdcard_obj.json_write(path, 'SEQSC{:0=3d}.json'.format(num), {'channel': self.seq_channel, 'control': self.seq_control, 'score': self.seq_score, 'sign': self.seq_score_sign}):
      print('SAVED')

  # Load sequencer file
  def sequencer_load_file(self, path, num):
    # Read MIDI IN settings JSON file
    seq_data = self.sdcard_obj.json_read(path, 'SEQSC{:0=3d}.json'.format(num))
    if not seq_data is None:
      if 'score' in seq_data.keys():
        if seq_data['score'] is None:
          self.seq_score = []
        else:
          self.seq_score = seq_data['score']
      else:
        seq_data = []
      
      if 'sign' in seq_data.keys():
        if seq_data['sign'] is None:
          self.seq_score_sign = []
        else:
          self.seq_score_sign = seq_data['sign']
      else:
        self.seq_score_sign = []

      if 'control' in seq_data.keys():
        if seq_data['control'] is None:
          self.seq_control = {'tempo': 120, 'mini_note': 4, 'time_per_bar': 4, 'disp_time': [0,12], 'disp_key': [[57,74],[57,74]], 'time_cursor': 0, 'key_cursor': [60,60], 'program':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], 'gmbank':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
        else:
          for ky in seq_data['control'].keys():
            if ky == 'tempo':
              self.seq_control[ky] = int(seq_data['control'][ky])
            else:
              self.seq_control[ky] = seq_data['control'][ky]
      else:
        self.seq_control = {'tempo': 120, 'mini_note': 4, 'time_per_bar': 4, 'disp_time': [0,12], 'disp_key': [[57,74],[57,74]], 'time_cursor': 0, 'key_cursor': [60,60], 'program':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], 'gmbank':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}

      if 'channel' in seq_data.keys():
        if not seq_data['channel'] is None:
          self.seq_channel = seq_data['channel']
          for ch in range(16):
            if not 'gmbank' in self.seq_channel[ch]:
              self.seq_channel[ch]['gmbank'] = 0
            if not 'program' in self.seq_channel[ch]:
              self.seq_channel[ch]['program'] = 0
            if not 'volume' in self.seq_channel[ch]:
              self.seq_channel[ch]['volume'] = 100

      self.seq_cursor_note = self.sequencer_find_note(self.seq_edit_track, self.seq_control['time_cursor'], self.seq_control['key_cursor'][self.seq_edit_track])
      self.send_all_sequencer_settings()


  # Get key name of key number
  #   key_num: MIDI note number
  def seqencer_key_name(self, key_num):
    return self.midi_obj.key_name(key_num)

  # Find note
  def sequencer_find_note(self, track, seq_time, seq_note):
    channel = self.seq_track_midi[track]
    for score in self.seq_score:
      note_on_tm = score['time']
      note_off_max = note_on_tm + score['max_duration']
      if note_on_tm <= seq_time and seq_time <= note_off_max:
        for note_data in score['notes']:
          if note_data['channel'] == channel and note_data['note'] == seq_note:
            if note_on_tm + note_data['duration'] > seq_time:
              return (score, note_data)

    return None

  # Update maximum duration
  def sequencer_duration_update(self, score):
    max_dur = 0
    for note_data in score['notes']:
      max_dur = max(max_dur, note_data['duration'])

    score['max_duration'] = max_dur

  # Delete a note
  def sequencer_delete_note(self, score, note_data):
    score['notes'].remove(note_data)
    if len(score['notes']) == 0:
      self.seq_score.remove(score)
    else:
      self.sequencer_duration_update(score)

  # Add new note
  def sequencer_new_note(self, channel, note_on_time, note_key, velocity = -1, duration = 1):
    sc = 0
    scores = len(self.seq_score)
    while sc < scores:
      # Add the note to the existing score
      current = self.seq_score[sc]
      if current['time'] == note_on_time:
        # Inset new note at sorted order by key
        nt = 0
        notes_len = len(current['notes'])
        for nt in range(notes_len):
          if current['notes'][nt]['note'] > note_key:
            current['notes'].insert(nt, {'channel': channel, 'note': note_key, 'velocity': max(velocity, current['notes'][nt]['velocity']), 'duration': duration})
            self.seq_cursor_note = current['notes'][nt]
            if duration > self.seq_score[sc]['max_duration']:
              self.seq_score[sc]['max_duration'] = duration

            return (current, self.seq_cursor_note)

        # New note is the highest tone
        current['notes'].append({'channel': channel, 'note': note_key, 'velocity': max(velocity, current['notes'][notes_len-1]['velocity']), 'duration': duration})
        self.seq_cursor_note = current['notes'][len(current['notes']) - 1]
        if duration > self.seq_score[sc]['max_duration']:
          self.seq_score[sc]['max_duration'] = duration

        return (current, self.seq_cursor_note)

      # Insert the note as new score at new note-on time
      elif current['time'] > note_on_time:
        self.seq_score.insert(sc, {'time': note_on_time, 'max_duration': duration, 'notes': [{'channel': channel, 'note': note_key, 'velocity': max(velocity, 127), 'duration': duration}]})
        current = self.seq_score[sc]
        self.seq_cursor_note = current['notes'][0]
        return (current, self.seq_cursor_note)

      # Next note on time
      sc = sc + 1

    # Append the note as new latest note-on time
    self.seq_score.append({'time': note_on_time, 'max_duration': duration, 'notes': [{'channel': channel, 'note': note_key, 'velocity': max(velocity, 127), 'duration': duration}]})
    current = self.seq_score[len(self.seq_score) - 1]
    self.seq_cursor_note = current['notes'][0]
    return (current, self.seq_cursor_note)

  # Change MIDI channel
  def sequencer_change_midi_channel(self, delta):
    channel = (self.seq_track_midi[self.seq_edit_track] + delta) % 16
    self.seq_track_midi[self.seq_edit_track] = channel
    self.sequencer_draw_track(self.seq_edit_track)

  # Change time span to display score
  def sequencer_timespan(self, delta):
    end = self.seq_control['disp_time'][1] + delta
    if end - self.seq_control['disp_time'][0] <= 3:
      return
    
    self.seq_control['disp_time'][1] = end
    self.sequencer_draw_track(0)
    self.sequencer_draw_track(1)

  # Change a note velocity
  def sequencer_velocity(self, delta):
    # No note is selected
    if self.seq_cursor_note is None:
      return False

    # Change velocity of a note selected
    note_data = self.seq_cursor_note[1]
    note_data['velocity'] = note_data['velocity'] + delta
    if note_data['velocity'] < 1:
      note_data['velocity'] = 1
    elif note_data['velocity'] > 127:
      note_data['velocity'] = 127

    return True

  # Insert time at the time cursor on a MIDI channel
  def sequencer_insert_time(self, channel, time_cursor, ins_times):
    affected = False
    for sc_index in list(range(len(self.seq_score)-1,-1,-1)):
      score = self.seq_score[sc_index]

      # Note-on time is equal or larger than the origin time to insert --> move forward
      if score['time'] >= time_cursor:
        note_on_time = score['time'] + ins_times
        to_delete = []
        for note_data in score['notes']:
          if note_data['channel'] == channel:
            # Delete a note
            to_delete.append(note_data)

            # Move the note as new note
            self.sequencer_new_note(channel, note_on_time, note_data['note'], note_data['velocity'], note_data['duration'])
            affected = True

        # Delete notes moved
        for note_data in to_delete:
          self.sequencer_delete_note(score, note_data)

      # Note-on time is less than the origin time to insert
      else:
        # Notes over the origin time to insert --> stretch duration toward forward
        # Not include note-off time
        if score['time'] + score['max_duration'] > time_cursor:
          for note_data in score['notes']:
            if note_data['channel'] == channel:
              if score['time'] + note_data['duration'] > time_cursor:
                note_data['duration'] = note_data['duration'] + ins_times
                affected = True

    return affected

  # Delete time at the time cursor on the all MIDI channels
  def sequencer_delete_time(self, channel, time_cursor, del_times):
    # Can not delete
    if time_cursor <= 0:
      return False
    
    # Adjust times to delete
    times_to_delete = time_cursor - del_times
    if times_to_delete < 0:
      del_times = time_cursor

    affected = False
    notes_moved = []
    to_delete = []
    for score in self.seq_score:
      note_on_time = score['time']

      # Note-on time is equal or larger than the delete time
      if note_on_time >= time_cursor:
        for note_data in score['notes']:
          if note_data['channel'] == channel:
            affected = True

            # Delete a note
            to_delete.append((score, note_data))

            # Move the note as new note
            notes_moved.append((note_on_time - del_times, note_data['note'], note_data['velocity'], note_data['duration']))

      # Note-on time is less than the delete time, and there are some notes acrossing the delete time
      elif note_on_time + score['max_duration'] >= time_cursor:
        for note_data in score['notes']:
          if note_data['channel'] == channel:

            # Accross the time range to delete
            if note_on_time + note_data['duration'] >= time_cursor - del_times:
              affected = True
              note_data['duration'] = note_data['duration'] - del_times

              # Zero length note
              if note_data['duration'] <= 0:
                to_delete.append((score, note_data))

    # Delete notes without duration
    for score, note_data in to_delete:
      self.sequencer_delete_note(score, note_data)

    # Add notes moved
    for note_time, note_key, velosity, duration in notes_moved:
      self.sequencer_new_note(channel, note_time, note_key, velosity, duration)

    return affected

  # Up or Down time resolution
  def sequencer_resolution(self, res_up):
    # Reolution up
    if res_up:
      for score in self.seq_score:
        score['time'] = score['time'] * 2

      for score in self.seq_score_sign:
        score['time'] = score['time'] * 2

    # Resolution down
    else:
      for score in self.seq_score:
        if score['time'] % 2 != 0:
          return

      for score in self.seq_score_sign:
        if score['time'] % 2 != 0:
          return

      for score in self.seq_score:
        score['time'] = int(score['time'] / 2)

      for score in self.seq_score_sign:
        score['time'] = int(score['time'] / 2)

  # Get signs on score at tc(time cursor)
  def sequencer_get_repeat_control(self, tc):
    if not self.seq_score_sign is None:
      for sc_sign in self.seq_score_sign:
        if sc_sign['time'] == tc:
          return sc_sign

    return None

  # Add or change score signs at a time
  def sequencer_edit_signs(self, sign_data):
#    print('REPEAT SIGNS:', sign_data)
    if not sign_data is None:
      tm = sign_data['time']
      sc_sign = self.sequencer_get_repeat_control(tm)

      # Insert new sign data
      if sc_sign is None:
        # Sign status check
        flg = False
        for ky in sign_data.keys():
          if ky != 'time':
            flg = flg or sign_data[ky]
        
        # No sign is True
        if flg == False:
          return

        idx = 0
        for idx in range(len(self.seq_score_sign)):
          if self.seq_score_sign[idx]['time'] > tm:
            self.seq_score_sign.insert(idx, sign_data)
            return
          else:
            idx = idx + 1
        
        self.seq_score_sign.append(sign_data)

      # Change sign parameters
      else:
        for ky in sign_data.keys():
          sc_sign[ky] = sign_data[ky]

        # Sign status check
        flg = False
        for ky in sign_data.keys():
          if ky != 'time':
            flg = flg or sign_data[ky]
        
        # No sign is True
        if flg == False:
          self.seq_score_sign.remove(sign_data)

  # Backup the cursor position
  def pre_play_sequencer(self):
    self.time_cursor_bk = self.seq_control['time_cursor']
    self.key_cursor0_bk = self.seq_control['key_cursor'][0]
    self.key_cursor1_bk = self.seq_control['key_cursor'][1]
    self.seq_disp_time0_bk  = self.seq_control['disp_time'][0]
    self.seq_disp_time1_bk  = self.seq_control['disp_time'][1]

    # Backup master volume
    self.master_volume_bk = self.midi_obj.get_master_volume()

  # Retrieve the backuped cursor position
  def post_play_sequencer(self):
    self.seq_control['time_cursor'] = self.time_cursor_bk
    self.seq_control['key_cursor'][0] = self.key_cursor0_bk
    self.seq_control['key_cursor'][1] = self.key_cursor1_bk
    self.seq_control['disp_time'][0] = self.seq_disp_time0_bk
    self.seq_control['disp_time'][1] = self.seq_disp_time1_bk
    self.sequencer_draw_track(0)
    self.sequencer_draw_track(1)

    # Set master volume (for pause/stop)
    self.midi_obj.set_master_volume(self.master_volume_bk)

  # Play sequencer score
  def play_sequencer(self, func_pause_or_stop = None, func_pause_to_stop = None, func_pre_move_cursor = None, func_post_move_cursor = None):
    print('SEQUENCER STARTS.')
    note_off_events = []

    # Insert a note off event in the notes off list
    def insert_note_off(time, channel, note_num):
      len_evt = len(note_off_events)
      if len_evt == 0:
        note_off_events.append({'time': time, 'notes': [{'channel': channel, 'note': note_num}]})
        return

      for evt_index in range(len_evt):
        evt = note_off_events[evt_index]
        if   evt['time'] == time:
          evt['notes'].append({'channel': channel, 'note': note_num})
          return

        elif evt['time'] > time:
          note_off_events.insert(evt_index,{'time': time, 'notes': [{'channel': channel, 'note': note_num}]})
          return

      note_off_events.append({'time': time, 'notes': [{'channel': channel, 'note': note_num}]})


    # Notes off the first event in the notes off event list
    def sequencer_notes_off():
      for note_data in note_off_events[0]['notes']:
        self.midi_obj.notes_off(note_data['channel'], [note_data['note']])

      note_off_events.pop(0)


    # Move play cursor
    def move_play_cursor(tc):
      if not func_pre_move_cursor is None:
        func_pre_move_cursor()
      tc = tc + 1
      self.seq_control['time_cursor'] = tc

      # Slide score
      if self.seq_control['time_cursor'] < self.seq_control['disp_time'][0] or self.seq_control['time_cursor'] > self.seq_control['disp_time'][1]:
        width = self.seq_control['disp_time'][1] - self.seq_control['disp_time'][0]
        self.seq_control['disp_time'][0] = self.seq_control['time_cursor']
        self.seq_control['disp_time'][1] = self.seq_control['disp_time'][0] + width
        self.sequencer_draw_track(0)
        self.sequencer_draw_track(1)

      if not func_post_move_cursor is None:
        func_post_move_cursor()
      return tc

    ##### CODE: play_sequencer

    # Play parameter
    next_note_on = 0
    next_note_off = 0
    time_cursor = self.seq_play_time[0]
    end_time = self.seq_play_time[1] if self.seq_play_time[0] < self.seq_play_time[1] else -1

    # Repeat controls
    loop_play_time = 0
    loop_play_slot = 0
    repeating_bars = False
    repeat_time = -1
    repeat_slot = -1

    # Sequencer play loop
    self.seq_control['time_cursor'] = time_cursor
    score_len = len(self.seq_score)
    play_slot = 0
    while play_slot < score_len:
      print('SEQ POINT:', time_cursor, play_slot)
      score = self.seq_score[play_slot]

      # Scan stop button (PLAY-->PAUSE-->STOP)
      if not (func_pause_or_stop is None or func_pause_to_stop is None):
        if func_pause_or_stop():
          self.midi_obj.set_master_volume(0)
          count = func_pause_to_stop()
          if count >= 0:    # Stop playing (push the button long)
            self.midi_obj.set_master_volume(self.master_volume_bk)
            if count > 0:
              break

      # Play4,8,16,32,64--1,2,3,4,5--1,2,4,8,16
      skip_continue = False
      repeat_continue = False
      tempo = int((60.0 / self.seq_control['tempo'] / (2**self.seq_control['mini_note']/4)) * 1000000)
      next_notes_on = score['time']
      while next_notes_on > time_cursor:
  #      print('SEQUENCER AT0:', time_cursor)
        time0 = time.ticks_us()
        if len(note_off_events) > 0:
          if note_off_events[0]['time'] == time_cursor:
            sequencer_notes_off()

        # Get MIDI-IN and send data to Unit-MIDI
        self.midi_obj.midi_in_out()
        
        time1 = time.ticks_us()
        timedelta = time.ticks_diff(time1, time0)
        time.sleep_us(tempo - timedelta)
        time_cursor = move_play_cursor(time_cursor)

        # Loop/Skip/Repeat
        repeat_ctrl = self.sequencer_get_repeat_control(time_cursor)
  #      print('REPEAT CTRL0:', time_cursor, repeat_ctrl)
        if not repeat_ctrl is None:
          # Skip bar point
          if repeat_ctrl['skip']:
            # During repeat play, skip to next play slot
            if repeating_bars and repeat_time != -1 and repeat_slot != -1:
              time_cursor = repeat_time
              play_slot = repeat_slot
              repeat_time = -1
              repeat_slot = -1
              repeating_bars = False
              loop_play_time = -1
              loop_play_slot = -1
              skip_continue = True
              break

          # Repeat bar point
          if repeat_ctrl['repeat'] and repeating_bars == False and loop_play_time >= 0:
            repeat_time = repeat_ctrl['time']
            repeat_slot = play_slot
            time_cursor = loop_play_time
            play_slot = loop_play_slot
            loop_play_time = -1
            loop_play_slot = -1
            repeating_bars = True
            repeat_continue = True
            break

          # Loop bar point
          if repeat_ctrl['loop']:
            loop_play_time = repeat_ctrl['time']
            loop_play_slot = play_slot

        if end_time != -1 and time_cursor >= end_time:
          break

      # Note off
  #    print('SEQUENCER AT1:', time_cursor)
      time0 = time.ticks_us()
      if len(note_off_events) > 0:
        if note_off_events[0]['time'] == time_cursor:
          sequencer_notes_off()

      # Skip to next play slot
      if skip_continue:
        skip_continue = False
  #      print('SEQ SKIP TO 0:', time_cursor, play_slot)
        continue

      # Repeat
      if repeat_continue:
        repeat_continue = False
  #      print('SEQ REPEAT TO 0:', time_cursor, play_slot, repeat_time, repeat_slot)
        continue

      # Loop/Skip/Repeat
      repeat_ctrl = self.sequencer_get_repeat_control(time_cursor)
  #    print('REPEAT CTRL1:', time_cursor, repeat_ctrl)
      if not repeat_ctrl is None:
        # Loop bar point
        if repeat_ctrl['loop']:
          loop_play_time = repeat_ctrl['time']
          loop_play_slot = play_slot

        # Skip bar point
        if repeat_ctrl['skip']:
          # During repeat play
          if repeating_bars and repeat_time != -1 and repeat_slot != -1:
            time_cursor = repeat_time
            play_slot = repeat_slot
            repeat_time = -1
            repeat_slot = -1
            repeating_bars = False
  #          print('SEQ SKIP TO 1:', time_cursor, play_slot)
            continue

        # Repeat bar point
        if repeat_ctrl['repeat'] and repeating_bars == False and loop_play_time >= 0:
          repeat_time = repeat_ctrl['time']
          repeat_slot = play_slot
          time_cursor = loop_play_time
          play_slot = loop_play_slot
          loop_play_time = -1
          loop_play_slot = -1
          repeating_bars = True
  #        print('SEQ REPEAT TO 1:', time_cursor, play_slot, repeat_time, repeat_slot)
          continue

      if end_time != -1 and time_cursor >= end_time:
        break

      # Notes on
      for note_data in score['notes']:
        channel = note_data['channel']
  #      print('SEQ NOTE ON:', time_cursor, note_data['note'])
        self.midi_obj.set_note_on(channel, note_data['note'], int(note_data['velocity'] * self.seq_channel[channel]['volume'] / 100))
        note_off_at = time_cursor + note_data['duration']
        insert_note_off(note_off_at, channel, note_data['note'])

      self.midi_obj.midi_in_out()

      time1 = time.ticks_us()
      timedelta = time.ticks_diff(time1, time0)
      time.sleep_us(tempo - timedelta)

      time_cursor = move_play_cursor(time_cursor)

      if end_time != -1 and time_cursor >= end_time:
        break

      # Next time slot
      play_slot = play_slot + 1

    # Notes off (final process)
    print('SEQUENCER: Notes off process =', len(note_off_events))
    while len(note_off_events) > 0:
      score = note_off_events[0]
      timedelta = 0
      while score['time'] > time_cursor:
        time.sleep_us(tempo - timedelta)
        time0 = time.ticks_us()
        time_cursor = move_play_cursor(time_cursor)

        time1 = time.ticks_us()
        timedelta = time.ticks_diff(time1, time0)

      time0 = time.ticks_us()
      sequencer_notes_off()
      self.midi_obj.midi_in_out()

      time1 = time.ticks_us()
      timedelta = time.ticks_diff(time1, time0)
      time.sleep_us(tempo - timedelta)
      time_cursor = move_play_cursor(time_cursor)

    print('SEQUENCER: Finished.')

  # Draw a note on the sequencer
  def sequencer_draw_note(self, trknum, note_num, note_on_time, note_off_time, disp_mode):
    # Delegation
    if not self.view_delegate_obj is self:
      self.view_delegate_obj.sequencer_draw_note(trknum, note_num, note_on_time, note_off_time, disp_mode)
      return

    print('sequencer_draw_note IN SEQUENCER: TO BE IMPLEMENT IN DELEGATE CLASS FUNCTION')
    pass

  # Draw velocity
  def sequencer_draw_velocity(self, trknum, channel, note_on_time, notes):
    # Delegation
    if not self.view_delegate_obj is self:
      self.view_delegate_obj.sequencer_draw_velocity(trknum, channel, note_on_time, notes)
      return

    print('sequencer_draw_velocity IN SEQUENCER: TO BE IMPLEMENT IN DELEGATE CLASS FUNCTION')
    pass

  # Draw start and end time line to play in sequencer
  def sequencer_draw_playtime(self, trknum):
    # Delegation
    if not self.view_delegate_obj is self:
      self.view_delegate_obj.sequencer_draw_playtime(trknum)
      return

    print('sequencer_draw_playtime IN SEQUENCER: TO BE IMPLEMENT IN DELEGATE CLASS FUNCTION')
    pass

  # Draw sequencer track
  #   trknum: The track number to draw (0 or 1)
  def sequencer_draw_track(self, trknum):
    # Delegation
    if not self.view_delegate_obj is self:
      self.view_delegate_obj.sequencer_draw_track(trknum)
      return

    print('sequencer_draw_track IN SEQUENCER: TO BE IMPLEMENT IN DELEGATE CLASS FUNCTION')
    pass

  # Draw keyboard
  def sequencer_draw_keyboard(self, trknum):
    # Delegation
    if not self.view_delegate_obj is self:
      self.view_delegate_obj.sequencer_draw_keyboard(trknum)
      return

    print('sequencer_draw_keyboard IN SEQUENCER: TO BE IMPLEMENT IN DELEGATE CLASS FUNCTION')
    pass

    # Draw a keyboard of the track
    key_s = self.seq_control['disp_key'][trknum][0]
    key_e = self.seq_control['disp_key'][trknum][1]
    area = self.seq_draw_area[trknum]
    xscale = area[0] - 1
    black_scale = int(xscale / 2)
    yscale = int((area[3] - area[1] + 1) / (key_e - key_s  + 1))
    black_key = [1,3,6,8,10]
    for note_num in range(key_s, key_e + 1):
      # Display a key
      y = area[3] - (note_num - key_s + 1) * yscale
      M5.Lcd.drawRect(0, y, xscale, yscale, 0x888888)
      M5.Lcd.fillRect(1, y + 1, xscale - 2, yscale - 2, 0xffffff)

      # Black key on piano
      key_is_black = ((note_num % 12) in black_key) == True
      if key_is_black:
        M5.Lcd.fillRect(1, y + 1, black_scale, yscale - 2, 0x000000)

  # Send all sequencer MIDI settings
  def send_all_sequencer_settings(self):
    for ch in range(16):
      self.midi_obj.set_instrument(self.seq_control['gmbank'][ch], ch, self.seq_control['program'][ch])
      self.midi_obj.set_reverb(ch, 0, 0, 0)
      self.midi_obj.set_chorus(ch, 0, 0, 0, 0)
      self.midi_obj.set_vibrate(ch, 0, 0, 0)


  # Send the current MIDI channel settings to MIDI channel 1
  # Normally, MIDI-IN instruments send MIDI channel1 message.
  def send_sequencer_current_channel_settings(self, ch):
    self.midi_obj.set_instrument(self.seq_control['gmbank'][ch], 0, self.seq_control['program'][ch])
    self.midi_obj.set_reverb(0, 0, 0, 0)
    self.midi_obj.set_chorus(0, 0, 0, 0, 0)
    self.midi_obj.set_vibrate(0, 0, 0, 0)

################# End of Sequencer Class Definition #################


###########################
# Sequencer Message Class
###########################
class sequencer_message_class(sequencer_class):
  # Constructor
  def __init__(self, midi_obj, sdcard_obj, message_center = None):
    super().__init__(midi_obj, sdcard_obj)

    # Message Center
    if not message_center is None:
      self.message_center = message_center
      self.message_center.add_contributor(self)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_SETUP, self.func_SEQUENCER_SETUP)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_FILE_OP, self.func_SEQUENCER_CHANGE_FILE_OP)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_SELECT_FILE, self.func_SEQUENCER_SELECT_FILE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_FILE_LOADED, self.func_SEQUENCER_FILE_LOADED)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_MIDI_CHANNEL_CHANGED, self.func_SEQUENCER_MIDI_CHANNEL_CHANGED)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_MOVE_TIME_CURSOR, self.func_SEQUENCER_MOVE_TIME_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_MOVE_KEY_CURSOR, self.func_SEQUENCER_MOVE_KEY_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_FIND_NOTE_ON_CURSOR, self.func_SEQUENCER_FIND_NOTE_ON_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_PARAMETER, self.func_SEQUENCER_CHANGE_PARAMETER)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_GET_REPEAT_FLAG, self.func_SEQUENCER_GET_REPEAT_FLAG)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_NOTE_ON_CURSOR, self.func_SEQUENCER_IS_NOTE_ON_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_NOTE_DURATION, self.func_SEQUENCER_CHANGE_NOTE_DURATION)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_DELETE_NOTE_ON_CURSOR, self.func_SEQUENCER_DELETE_NOTE_ON_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_PUT_NOTE_ON_CURSOR, self.func_SEQUENCER_PUT_NOTE_ON_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_MIDI_CHANNEL, self.func_SEQUENCER_CHANGE_MIDI_CHANNEL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_TIME_SPAN, self.func_SEQUENCER_CHANGE_TIME_SPAN)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_VELOCITY, self.func_SEQUENCER_CHANGE_VELOCITY)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_PLAY_START, self.func_SEQUENCER_CHANGE_PLAY_START)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_PLAY_END, self.func_SEQUENCER_CHANGE_PLAY_END)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_CHANNEL, self.func_SEQUENCER_IS_MENU_PARM_CHANNEL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_TIMESPAN, self.func_SEQUENCER_IS_MENU_PARM_TIMESPAN)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_VELOCITY, self.func_SEQUENCER_IS_MENU_PARM_VELOCITY)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_PLAY_START, self.func_SEQUENCER_IS_MENU_PARM_PLAY_START)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_PLAY_END, self.func_SEQUENCER_IS_MENU_PARM_PLAY_END)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_STRETCH_ONE, self.func_SEQUENCER_IS_MENU_PARM_STRETCH_ONE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_STRETCH_ALL, self.func_SEQUENCER_IS_MENU_PARM_STRETCH_ALL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_CLEAR_ONE, self.func_SEQUENCER_IS_MENU_PARM_CLEAR_ONE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_CLEAR_ALL, self.func_SEQUENCER_IS_MENU_PARM_CLEAR_ALL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_NOTES_BAR, self.func_SEQUENCER_IS_MENU_PARM_NOTES_BAR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_RESOLUTION, self.func_SEQUENCER_IS_MENU_PARM_RESOLUTION)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_TEMPO, self.func_SEQUENCER_IS_MENU_PARM_TEMPO)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_MINIMUM_NOTE, self.func_SEQUENCER_IS_MENU_PARM_MINIMUM_NOTE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_PROGRAM, self.func_SEQUENCER_IS_MENU_PARM_PROGRAM)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_CHANNEL_VOL, self.func_SEQUENCER_IS_MENU_PARM_CHANNEL_VOL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_REPEAT, self.func_SEQUENCER_IS_MENU_PARM_REPEAT)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_INSERT_TIME, self.func_SEQUENCER_INSERT_TIME)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_DELETE_TIME, self.func_SEQUENCER_DELETE_TIME)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_ADD_TIME_CURSOR, self.func_SEQUENCER_ADD_TIME_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_SET_NOTE_ON_CURSOR, self.func_SEQUENCER_SET_NOTE_ON_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CLEAR_TRACK, self.func_SEQUENCER_CLEAR_TRACK)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CLEAR_SCORE, self.func_SEQUENCER_CLEAR_SCORE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_TIME_PER_BAR, self.func_SEQUENCER_CHANGE_TIME_PER_BAR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_RESOLUTION, self.func_SEQUENCER_RESOLUTION)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_TEMPO, self.func_SEQUENCER_CHANGE_TEMPO)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_SET_MINIMUM_NOTE, self.func_SEQUENCER_SET_MINIMUM_NOTE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_VOLUME_RATIO, self.func_SEQUENCER_CHANGE_VOLUME_RATIO)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_PROGRAM, self.func_SEQUENCER_CHANGE_PROGRAM)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_GET_PROGRAM_NAME, self.func_SEQUENCER_GET_PROGRAM_NAME)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_SEND_CHANNEL_SETTINGS, self.func_SEQUENCER_SEND_CHANNEL_SETTINGS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_GET_CURRENT_TRACK_CHANNEL, self.func_SEQUENCER_GET_CURRENT_TRACK_CHANNEL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_SET_INSTRUMENT, self.func_SEQUENCER_SET_INSTRUMENT)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_GET_REPEAT_SIGNS, self.func_SEQUENCER_GET_REPEAT_SIGNS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_SET_REPEAT_SIGNS, self.func_SEQUENCER_SET_REPEAT_SIGNS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_GET_SIGNS_CURSOR, self.func_SEQUENCER_GET_SIGNS_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_CHANGE_REPEAT_SIGNS, self.func_SEQUENCER_CHANGE_REPEAT_SIGNS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_SEQUENCER_SET_GET_EDIT_TRACK, self.func_SEQUENCER_SET_GET_EDIT_TRACK)

    else:
      self.message_center = message_center_class()

  # To be called just after sequencer_class.sequencer_setup()
  def func_SEQUENCER_SETUP(self, message_data = None):
    # Setup sequencer view
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SETUP, None)

    # SEQUENCER title labels
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'title_seq_track1', 'value': 'CH'})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'title_seq_track2', 'value': 'CH'})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'title_seq_file', 'value': 'NO:'})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'title_seq_time', 'value': 'T/B:'})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'title_seq_master_volume', 'value': 'VOL:'})

    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_track1', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_track2', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_file', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_time', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_master_volume', 'visible': False})

    # SEQUENCER data labels
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_TRACK1_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_TRACK2_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_KEY1_SET_TEXT, None)
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_COLOR, {'label': 'label_seq_key1', 'fore': 0xff4040 if self.seq_edit_track == 0 else 0x00ccff, 'back': 0x222222})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_KEY2_SET_TEXT, None)
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_COLOR, {'label': 'label_seq_key2', 'fore': 0xff4040 if self.seq_edit_track == 1 else 0x00ccff, 'back': 0x222222})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_FILE_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_FILE_OP_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_TIME_SET_TEXT)

    self.message_center.phone_message(self, self.message_center.MSGID_APPLICATION_SHOW_MASTER_VOLUME_VALUE, None)

    ch = self.seq_track_midi[0]
    prg = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_GET_PROGRAM_NAME, {'gm_bank': self.seq_control['gmbank'][ch], 'program_number': self.seq_control['program'][ch]})
    prg = prg[:9]
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_program1', 'value': prg})

    ch = self.seq_track_midi[1]
    prg = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_GET_PROGRAM_NAME, {'gm_bank': self.seq_control['gmbank'][ch], 'program_number': self.seq_control['program'][ch]})
    prg = prg[:9]
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_program2', 'value': prg})
    
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_PARM_NAME_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'value': ''})

    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_track1', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_track2', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_key1', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_key2', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_file', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_file_op', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_time', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_master_volume', 'visible': False})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_parm_name', 'visible': False})

    print('SEQUENCER INITIALIZED.')

  # Message Receiver: Sequencer controls
  def func_SEQUENCER_CHANGE_FILE_OP(self, message_data):
    delta = message_data['delta']
    self.seq_file_ctrl = (self.seq_file_ctrl + delta) % 3
#          self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_file_op', 'value': self.seq_file_ctrl_label[self.seq_file_ctrl]})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_FILE_OP_SET_TEXT)

    enc_button = message_data['do_operation']
    if enc_button:
      if self.seq_file_ctrl == self.SEQ_FILE_LOAD:
        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 0, 'disp_time': False, 'disp_key': False})
        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 1, 'disp_time': False, 'disp_key': False})
        self.sequencer_load_file(self.set_sequencer_file_path(), self.seq_file_number)

        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_KEYBOARD)
        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)
        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_PLAYTIME)

        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 0, 'disp_time': True, 'disp_key': True})
        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 1, 'disp_time': True, 'disp_key': True})
        self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_FILE_LOADED)
        
        self.enc_slide_switch = None
        self.seq_file_ctrl = self.SEQ_FILE_NOP
        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_FILE_OP_SET_TEXT)

      elif self.seq_file_ctrl == self.SEQ_FILE_SAVE:
        self.sequencer_save_file(self.set_sequencer_file_path(), self.seq_file_number)
        self.seq_file_ctrl = self.SEQ_FILE_NOP
        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_FILE_OP_SET_TEXT)

  def func_pause_or_stop(self):
    return self.message_center.phone_message(self, self.message_center.MSGID_DEVICE_PHONE_SEQ_GET_PAUSE_STOP_BUTTON, {'no_response': False})

  def func_pause_to_stop(self):
    return self.message_center.phone_message(self, self.message_center.MSGID_DEVICE_PHONE_SEQ_STOP_BUTTON, {'no_response': 1})

  def func_pre_move_cursor(self):
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': False, 'disp_key': False})

  def func_post_move_cursor(self):
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': True, 'disp_key': False})

  # Message Receiver: Sequencer controls
  def func_SEQUENCER_SELECT_FILE(self, message_data):
    delta = message_data['delta']
    self.seq_file_number = (self.seq_file_number + delta) % self.SEQ_FILE_MAX
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_FILE_SET_TEXT)

    enc_button = message_data['do_operation']
    if enc_button:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': False, 'disp_key': False})
      self.message_center.phone_message(self, self.message_center.MSGID_DEVICE_PHONE_SEQ_TURN_OFF_PLAY_BUTTON, None)
      self.send_all_sequencer_settings()

      self.pre_play_sequencer()
      self.play_sequencer(self.func_pause_or_stop, self.func_pause_to_stop, self.func_pre_move_cursor, self.func_post_move_cursor)

    # Retrieve the cursor position
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': False, 'disp_key': False})
      self.post_play_sequencer()
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': True, 'disp_key': True})

      self.send_sequencer_current_channel_settings(self.get_track_midi())

  def func_SEQUENCER_FILE_LOADED(self, message_data):
    disp = 'NON'
    if not self.seq_parm_repeat is None:
      rept = self.sequencer_get_repeat_control(self.seq_parm_repeat)
      disp = 'NON'
      if not rept is None:
        if rept['loop']:
          disp = 'LOP'
        elif rept['skip']:
          disp = 'SKP'
        elif rept['repeat']:
          disp = 'RPT'
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'value': disp})

    for trk in range(2):
      ch = self.seq_track_midi[trk]
      prg = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_GET_PROGRAM_NAME, {'gm_bank': self.seq_control['gmbank'][ch], 'program_number': self.seq_control['program'][ch]})
      prg = prg[:9]
      if trk == 0:
        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_program1', 'value': prg})
      else:
        self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_program2', 'value': prg})

  def func_SEQUENCER_MIDI_CHANNEL_CHANGED(self, message_data = None):
    channel = self.seq_track_midi[self.seq_edit_track]
    prg = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_GET_PROGRAM_NAME, {'gm_bank': self.seq_control['gmbank'][channel], 'program_number': self.seq_control['program'][channel]})
    prg = prg[:9]

    if   self.seq_edit_track == 0:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_TRACK1_SET_TEXT)
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_program1', 'value': prg})
    elif self.seq_edit_track == 1:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_TRACK2_SET_TEXT)
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_program2', 'value': prg})

  def func_SEQUENCER_MOVE_TIME_CURSOR(self, message_data = None):
    delta = message_data['delta']
    self.set_seq_time_cursor(self.get_seq_time_cursor() + delta)
    if self.get_seq_time_cursor() < 0:
      self.set_seq_time_cursor(0)

    # Move the time for the sign time
    if not self.get_seq_parm_repeat() is None:
      if self.get_seq_time_cursor() != self.get_seq_parm_repeat():
        self.set_seq_parm_repeat(None)

    # Slide score-bar display area (time)
    disp_time = self.get_seq_disp_time()
    if self.get_seq_time_cursor() < disp_time[0]:
      self.set_seq_disp_time(disp_time[0] - self.get_seq_time_per_bar(), disp_time[1] - self.get_seq_time_per_bar())
      self.sequencer_draw_track(0)
      self.sequencer_draw_track(1)

    elif self.get_seq_time_cursor() > disp_time[1]:
      self.set_seq_disp_time(disp_time[0] + self.get_seq_time_per_bar(), disp_time[1] + self.get_seq_time_per_bar())
      self.sequencer_draw_track(0)
      self.sequencer_draw_track(1)

  def func_SEQUENCER_MOVE_KEY_CURSOR(self, message_data = None):
    delta = message_data['delta']
    self.set_seq_key_cursor(self.edit_track(), self.get_seq_key_cursor(self.edit_track()) + delta)

    # Slide score-key display area (key)
    disp_key = self.get_seq_disp_key(self.edit_track())
    if self.get_seq_key_cursor(self.edit_track()) < disp_key[0]:
      self.set_seq_disp_key(self.edit_track(), disp_key[0] - 1, disp_key[1] - 1)
      self.sequencer_draw_keyboard(self.edit_track())
      self.sequencer_draw_track(self.edit_track())

    elif self.get_seq_key_cursor(self.edit_track()) > disp_key[1]:
      self.set_seq_disp_key(self.edit_track(), disp_key[0] + 1, disp_key[1] + 1)
      self.sequencer_draw_keyboard(self.edit_track())
      self.sequencer_draw_track(self.edit_track())

  def func_SEQUENCER_FIND_NOTE_ON_CURSOR(self, message_data = None):
    cursor_note = self.sequencer_find_note(self.edit_track(), self.get_seq_time_cursor(), self.get_seq_key_cursor(self.edit_track()))
    if not cursor_note is None:
      seq_cursor_note = self.get_cursor_note()
      if not seq_cursor_note is None:
        if cursor_note != seq_cursor_note:
          score = seq_cursor_note[0]
          note_data = seq_cursor_note[1]
          if self.seq_parm != self.SEQUENCER_PARM_VELOCITY:
            self.sequencer_draw_note(self.edit_track(), note_data['note'], score['time'], score['time'] + note_data['duration'], self.SEQ_NOTE_DISP_NORMAL)

      self.set_cursor_note(cursor_note)
      score = self.get_cursor_note(0)
      note_data = self.get_cursor_note(1)
      if self.seq_parm != self.SEQUENCER_PARM_VELOCITY:
        self.sequencer_draw_note(self.edit_track(), note_data['note'], score['time'], score['time'] + note_data['duration'], self.SEQ_NOTE_DISP_HIGHLIGHT)
      else:
        self.sequencer_draw_track(self.edit_track())

    # The cursor moves away from the selected note 
    elif not self.get_cursor_note() is None:
      score = self.get_cursor_note(0)
      note_data = self.get_cursor_note(1)
      if self.seq_parm != self.SEQUENCER_PARM_VELOCITY:
        self.sequencer_draw_note(self.edit_track(), note_data['note'], score['time'], score['time'] + note_data['duration'], self.SEQ_NOTE_DISP_NORMAL)
        self.set_cursor_note(None)
      else:
        self.set_cursor_note(None)
        self.sequencer_draw_track(self.edit_track())

  def func_SEQUENCER_CHANGE_PARAMETER(self, message_data = None):
    # Change the target parameter to edit with CTRL1
    delta = message_data['delta']
    self.seq_parm = self.seq_parm + delta
    if self.seq_parm < 0:
      self.seq_parm = self.seq_total_parameters -1
    elif self.seq_parm >= self.seq_total_parameters:
      self.seq_parm = 0

  def func_SEQUENCER_GET_REPEAT_FLAG(self, message_data = None):
    rept = None
    if self.seq_parm == self.SEQUENCER_PARM_REPEAT:
      if self.get_seq_parm_repeat() is None:
        self.set_seq_parm_repeat(self.get_seq_time_cursor())
        rept = self.sequencer_get_repeat_control(self.get_seq_parm_repeat())
        if rept is None:
          rept = {'loop': False, 'skip': False, 'repeat': False}

      elif self.get_seq_parm_repeat() != self.get_seq_time_cursor():
        self.set_seq_parm_repeat(self.get_seq_time_cursor())
        rept = self.sequencer_get_repeat_control(self.get_seq_parm_repeat())

    return rept

  def func_SEQUENCER_GET_SIGNS_CURSOR(self, message_data = None):
    return self.get_seq_parm_repeat()
  
  def func_SEQUENCER_GET_REPEAT_SIGNS(self, message_data = None):
    if message_data is None:
      time_cursor = self.get_seq_parm_repeat()
    else:
      time_cursor = message_data['time']

    rept_signs = self.sequencer_get_repeat_control(time_cursor)
    if rept_signs is None:
      rept_signs = {'time': time_cursor, 'loop': False, 'skip': False, 'repeat': False}

    return rept_signs

  def func_SEQUENCER_SET_REPEAT_SIGNS(self, message_data = None):
    if not message_data is None:
      self.sequencer_edit_signs(message_data['signs'])

  def func_SEQUENCER_CHANGE_REPEAT_SIGNS(self, message_data = None):
    if not message_data is None:
      if 'time' in message_data.keys():
        rept_cursor = message_data['time']
      else:
        rept_cursor = self.get_seq_parm_repeat()

      delta = message_data['delta']
      if delta != 0:
        rept_signs = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_GET_REPEAT_SIGNS, {'time': rept_cursor})

        # none <-- loop --> skip
        if rept_signs['loop']:
          rept_signs['loop'] = False
          if delta == 1:
            rept_signs['skip'] = True

        # loop <-- skip --> repeat
        elif rept_signs['skip']:
          rept_signs['skip'] = False
          if delta == -1:
            rept_signs['loop'] = True
          else:
            rept_signs['repeat'] = True

        # skip <-- repeat --> none
        elif rept_signs['repeat']:
          rept_signs['repeat'] = False
          if delta == -1:
            rept_signs['skip'] = True

        # repeat <-- none --> loop
        else:
          if delta == -1:
            rept_signs['repeat'] = True
          else:
            rept_signs['loop'] = True

        # Set the repeat signs
#        print('SET REPEAT SIGNS:', rept_signs)
        self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SET_REPEAT_SIGNS, {'signs': rept_signs})
        return True
    
    return False

  def func_SEQUENCER_IS_NOTE_ON_CURSOR(self, message_data = None):
    return not self.get_cursor_note() is None

  def func_SEQUENCER_CHANGE_NOTE_DURATION(self, message_data = None):
    delta = message_data['delta']
    score = self.get_cursor_note(0)
    note_data = self.get_cursor_note(1)
    note_dur = note_data['duration'] + delta
    if note_dur >= 1:
      # Check overrap with another note
      overrap_note = self.sequencer_find_note(self.edit_track(), score['time'] + note_dur, self.get_seq_key_cursor(self.edit_track()))
      if not overrap_note is None:
        if overrap_note[1] != note_data and overrap_note[0]['time'] < score['time'] + note_dur:
          note_dur = -1
          print('OVERRAP')

      if note_dur >= 0:
        note_data['duration'] = note_dur
        self.sequencer_duration_update(score)

    return note_dur

  def func_SEQUENCER_DELETE_NOTE_ON_CURSOR(self, message_data = None):
    score = self.get_cursor_note(0)
    note_data = self.get_cursor_note(1)
    self.sequencer_delete_note(score, note_data)
    self.set_cursor_note(None)

  def func_SEQUENCER_PUT_NOTE_ON_CURSOR(self, message_data = None):
    self.set_cursor_note(self.sequencer_new_note(self.get_track_midi(), self.get_seq_time_cursor(), self.get_seq_key_cursor(self.edit_track())))

  def func_SEQUENCER_CHANGE_MIDI_CHANNEL(self, message_data = None):
    delta = message_data['delta']
    self.sequencer_change_midi_channel(delta)

  def func_SEQUENCER_CHANGE_TIME_SPAN(self, message_data = None):
    delta = message_data['delta']
    self.sequencer_timespan(delta)

  def func_SEQUENCER_CHANGE_VELOCITY(self, message_data = None):
    delta = message_data['delta']
    return self.sequencer_velocity(delta)

  def func_SEQUENCER_CHANGE_PLAY_START(self, message_data = None):
    delta = message_data['delta']
    pt = self.play_time(0) + delta
    print('PLAY S:', pt, delta, self.play_time())
    if pt >= 0 and pt <= self.play_time(1):
      self.play_time(0, pt)
      return True

    return False

  def func_SEQUENCER_CHANGE_PLAY_END(self, message_data = None):
    delta = message_data['delta']
    pt = self.play_time(1) + delta
    print('PLAY E:', pt, delta, self.play_time())
    if pt >= self.play_time(0):
      self.play_time(1, pt)
      return True

    return False

  def func_SEQUENCER_INSERT_TIME(self, message_data = None):
    delta = message_data['delta']
    if 'channel' in message_data.keys():
      return self.sequencer_insert_time(message_data['channel'], self.get_seq_time_cursor(), delta)
    else:
      return self.sequencer_insert_time(self.get_track_midi(), self.get_seq_time_cursor(), delta)

  def func_SEQUENCER_DELETE_TIME(self, message_data = None):
    delta = message_data['delta']
    if 'channel' in message_data.keys():
      return self.sequencer_delete_time(message_data['channel'], self.get_seq_time_cursor(), delta)
    else:
      return self.sequencer_delete_time(self.get_track_midi(), self.get_seq_time_cursor(), delta)

  def func_SEQUENCER_ADD_TIME_CURSOR(self, message_data = None):
    delta = message_data['delta']
    self.set_seq_time_cursor(self.get_seq_time_cursor() + delta)
    if self.get_seq_time_cursor() < 0:
      self.set_seq_time_cursor(0)

  def func_SEQUENCER_CLEAR_TRACK(self, message_data = None):
    to_delete = []
    for score in self.get_seq_score():
      for note_data in score['notes']:
        if note_data['channel'] == self.get_track_midi():
          to_delete.append((score, note_data))
      
    for del_note in to_delete:
      self.sequencer_delete_note(*del_note)

    self.set_cursor_note(None)

  def func_SEQUENCER_CLEAR_SCORE(self, message_data = None):
    self.clear_seq_score()
    self.set_cursor_note(None)

  def func_SEQUENCER_CHANGE_TIME_PER_BAR(self, message_data = None):
    delta = message_data['delta']
    self.set_seq_time_per_bar(self.get_seq_time_per_bar() + delta)

  def func_SEQUENCER_RESOLUTION(self, message_data = None):
    resolution_up = message_data['up']
    self.sequencer_resolution(resolution_up)

  def func_SEQUENCER_CHANGE_TEMPO(self, message_data = None):
    delta = message_data['delta']
    self.set_seq_tempo(self.get_seq_tempo() + delta)

  def func_SEQUENCER_SET_MINIMUM_NOTE(self, message_data = None):
    delta = message_data['delta']
    self.set_seq_mini_note(self.get_seq_mini_note() + delta)

  def func_SEQUENCER_SET_NOTE_ON_CURSOR(self, message_data = None):
    self.set_cursor_note(self.sequencer_find_note(self.edit_track(), self.get_seq_time_cursor(), self.get_seq_key_cursor(self.edit_track())))

  def func_SEQUENCER_CHANGE_VOLUME_RATIO(self, message_data = None):
    delta = message_data['delta']
    ch = self.get_track_midi()
    vol = self.get_seq_channel(ch, 'volume') + delta
    if vol < 0:
      vol = 0
    elif vol > 100:
      vol = 100

    self.set_seq_channel(ch, 'volume', vol)
    return vol

  def func_SEQUENCER_CHANGE_PROGRAM(self, message_data = None):
    delta = message_data['delta']
    channel = self.get_track_midi()
    self.set_seq_program(channel, self.get_seq_program(channel) + delta)
    return self.get_seq_program(channel)
  
  def func_SEQUENCER_GET_PROGRAM_NAME(self, message_data = None):
    gm_bank = self.get_seq_gmbank(self.get_track_midi())
    program_number = self.get_seq_program(self.get_track_midi())
    return self.message_center.phone_message(self, self.message_center.MSGID_MIDI_GET_PROGRAM_NAME, {'gm_bank': gm_bank, 'program_number': program_number})

  def func_SEQUENCER_SEND_CHANNEL_SETTINGS(self, message_data = None):
    self.send_sequencer_current_channel_settings(self.get_track_midi())

  def func_SEQUENCER_SET_INSTRUMENT(self, message_data = None):
    channel = self.get_track_midi()
    self.message_center.phone_message(self, self.message_center.MSGID_MIDI_SET_INSTRUMENT, {'gm_bank': self.get_seq_gmbank(channel), 'channel': channel, 'program_number': self.get_seq_program(channel)})

  def func_SEQUENCER_GET_CURRENT_TRACK_CHANNEL(self, message_data = None):
    return self.get_track_midi()

  def func_SEQUENCER_SET_GET_EDIT_TRACK(self, message_data = None):
    if message_data is None:
      return self.edit_track()

    trknum = message_data['track_number']
    self.edit_track(trknum)
    return trknum

  def func_SEQUENCER_IS_MENU_PARM_CHANNEL(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_CHANNEL

  def func_SEQUENCER_IS_MENU_PARM_TIMESPAN(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_TIMESPAN

  def func_SEQUENCER_IS_MENU_PARM_VELOCITY(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_VELOCITY

  def func_SEQUENCER_IS_MENU_PARM_PLAY_START(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_PLAYSTART

  def func_SEQUENCER_IS_MENU_PARM_PLAY_END(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_PLAYEND

  def func_SEQUENCER_IS_MENU_PARM_STRETCH_ONE(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_STRETCH_ONE

  def func_SEQUENCER_IS_MENU_PARM_STRETCH_ALL(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_STRETCH_ALL

  def func_SEQUENCER_IS_MENU_PARM_CLEAR_ONE(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_CLEAR_ONE

  def func_SEQUENCER_IS_MENU_PARM_CLEAR_ALL(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_CLEAR_ALL

  def func_SEQUENCER_IS_MENU_PARM_NOTES_BAR(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_NOTES_BAR

  def func_SEQUENCER_IS_MENU_PARM_RESOLUTION(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_RESOLUTION

  def func_SEQUENCER_IS_MENU_PARM_TEMPO(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_TEMPO

  def func_SEQUENCER_IS_MENU_PARM_MINIMUM_NOTE(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_MINIMUM_NOTE

  def func_SEQUENCER_IS_MENU_PARM_PROGRAM(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_PROGRAM

  def func_SEQUENCER_IS_MENU_PARM_CHANNEL_VOL(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_CHANNEL_VOL

  def func_SEQUENCER_IS_MENU_PARM_REPEAT(self, message_data = None):
    return self.seq_parm == self.SEQUENCER_PARM_REPEAT

################# End of sequencer_message_class Definition #################


########################
# MIDI-IN Player class
########################
class midi_in_player_class():
  def __init__(self, midi_obj, sdcard_obj):
    self.sdcard_obj = sdcard_obj
    self.midi_obj = midi_obj
    self.midi_in_ch = 0                               # MIDI IN channel to edit
    self.midi_in_set_num = 0                          # MIDI IN setting file number to load/save
    self.MIDI_IN_FILE_PATH = '/sd//SYNTH/MIDIUNIT/'   # MIDI IN setting files path
    self.MIDI_SET_FILES_MAX = 1000                    # Maximum MIDI IN setting files

    # MIDI-IN player
    self.midi_in_settings = []                        # MIDI IN settings for each channel, see setup()
                                                      # Each channel has following data structure
                                                      #     {'program':0, 'gmbank':0, 'reverb':[0,0,0], 'chorus':[0,0,0,0], 'vibrate':[0,0,0]}
                                                      #     {'program':PROGRAM, 'gmbank':GM BANK, 'reverb':[PROGRAM,LEVEL,FEEDBACK], 'chorus':[PROGRAM,LEVEL,FEEDBACK,DELAY], 'vibrate':[RATE,DEPTH,DELAY]}

    # SYNTH settings
    for ch in range(16):
      self.midi_in_settings.append({'program':0, 'gmbank':0, 'reverb':[0,0,0], 'chorus':[0,0,0,0], 'vibrate':[0,0,0]})

  # Set midi_in_setting
  def set_midi_in_setting(self, val):
    self.midi_in_settings = val

  def set_midi_in_setting3(self, channel, key_str, val):
    self.midi_in_settings[channel][key_str] = val

  def set_midi_in_setting4(self, channel, key_str, idx, val):
    self.midi_in_settings[channel][key_str][idx] = val

  # Get midi_in_setting
  def get_midi_in_setting(self, channel = None, key_str = None):
    if channel is None:
      return self.midi_in_settings
    
    if key_str is None:
      return self.midi_in_settings[channel]

    return self.midi_in_settings[channel][key_str]

  # Set/Get the current MIDI-IN channel
  def midi_in_channel(self, channel = None):
    if channel is None:
      return self.midi_in_ch
    
    self.midi_in_ch = channel
    return self.midi_in_ch

  # Set/Get midi_in_set_num
  def set_midi_in_set_num(self, num = None):
    if num is None:
      return self.midi_in_set_num
    
    self.midi_in_set_num = num % self.MIDI_SET_FILES_MAX
    return self.midi_in_set_num

  # Set/Get MIDI_IN_FILE_PATH
  def set_midi_in_file_path(self, path = None):
    if path is None:
      return self.MIDI_IN_FILE_PATH
    
    self.MIDI_IN_FILE_PATH = path
    return self.MIDI_IN_FILE_PATH

  # Set/Get MIDI_SET_FILES_MAX
  def set_midi_set_files_max(self, num = None):
    if num is None:
      return self.MIDI_SET_FILES_MAX
    
    self.MIDI_SET_FILES_MAX = num
    return self.MIDI_SET_FILES_MAX

  # Write MIDI IN settings to SD card
  #   num: File number (0..999)
  def write_midi_in_settings(self, num):
    # Write MIDI IN settings as JSON file
    self.sdcard_obj.json_write(self.MIDI_IN_FILE_PATH, 'MIDISET{:0=3d}.json'.format(num), self.midi_in_settings)

  # Read MIDI IN settings from SD card
  #   num: File number (0..999)
  def read_midi_in_settings(self, num):
    # Read MIDI IN settings JSON file
    rdjson = None
    rdjson = self.sdcard_obj.json_read(self.MIDI_IN_FILE_PATH, 'MIDISET{:0=3d}.json'.format(num))
    if not rdjson is None:
      # Default values
      for ch in range(16):
        kys = rdjson[ch]
        if not 'program' in kys:
          rdjson[ch]['program'] = 0
        if not 'gmbank' in kys:
          rdjson[ch]['gmbank'] = 0
        if not 'reverb' in kys:
          rdjson[ch]['reverb'] = [0,0,0]
        if not 'chorus' in kys:
          rdjson[ch]['chorus'] = [0,0,0,0]
        if not 'vibrate' in kys:
          rdjson[ch]['vibrate'] = [0,0,0]
    
    return rdjson

  # Send a MIDI channel settings to Unit-MIDI
  #   ch: MIDI channel
  def send_midi_in_settings(self, ch):
    self.midi_obj.set_instrument(self.midi_in_settings[ch]['gmbank'], ch, self.midi_in_settings[ch]['program'])
    self.midi_obj.set_reverb(ch, self.midi_in_settings[ch]['reverb'][0], self.midi_in_settings[ch]['reverb'][1], self.midi_in_settings[ch]['reverb'][2])
    self.midi_obj.set_chorus(ch, self.midi_in_settings[ch]['chorus'][0], self.midi_in_settings[ch]['chorus'][1], self.midi_in_settings[ch]['chorus'][2], self.midi_in_settings[ch]['chorus'][3])
    self.midi_obj.set_vibrate(ch, self.midi_in_settings[ch]['vibrate'][0], self.midi_in_settings[ch]['vibrate'][1], self.midi_in_settings[ch]['vibrate'][2])

  # Send all MIDI channel settings
  def send_all_midi_in_settings(self):
    for ch in range(16):
      self.send_midi_in_settings(ch)

  # Set and show new MIDI channel for MIDI-IN player
  #   dlt: MIDI channel delta value added to the current MIDI IN channel to edit.
  def set_midi_in_channel(self, dlt):
    self.midi_in_ch = (self.midi_in_ch + dlt) % 16
    self.set_midi_in_program(0)

    midi_in_reverb = self.midi_in_settings[self.midi_in_ch]['reverb']
    self.set_midi_in_reverb(midi_in_reverb[0], midi_in_reverb[1], midi_in_reverb[2])

    midi_in_chorus = self.midi_in_settings[self.midi_in_ch]['chorus']
    self.set_midi_in_chorus(midi_in_chorus[0], midi_in_chorus[1], midi_in_chorus[2], midi_in_chorus[3])

    midi_in_vibrate = self.midi_in_settings[self.midi_in_ch]['vibrate']
    self.set_midi_in_vibrate(midi_in_vibrate[0], midi_in_vibrate[1], midi_in_vibrate[2])

    return self.midi_in_ch

  # Set and show new program to the current MIDI channel for MIDI-IN player
  #   dlt: GM program delta value added to the current MIDI IN channel to edit.
  def set_midi_in_program(self, dlt):
    self.midi_in_settings[self.midi_in_ch]['program'] = (self.midi_in_settings[self.midi_in_ch]['program'] + dlt) % 128
    midi_in_program = self.midi_in_settings[self.midi_in_ch]['program']
    self.midi_obj.set_instrument(self.midi_in_settings[self.midi_in_ch]['gmbank'], self.midi_in_ch, midi_in_program)


  # Set and show new master volume value
  #   dlt: Master volume delta value added to the current value.
  def set_synth_master_volume(self, dlt):
    master_volume = self.midi_obj.get_master_volume() + dlt
    if master_volume < 1:
      master_volume = 0
    elif master_volume > 127:
      master_volume = 127

    self.midi_obj.set_master_volume(master_volume)


  # Set reverb parameters for the current MIDI IN channel
  #   prog : Reverb program
  #   level: Reverb level
  #   fback: Reverb feedback
  def set_midi_in_reverb(self, prog=None, level=None, fback=None):
    disp = None
    if not prog is None:
      self.midi_in_settings[self.midi_in_ch]['reverb'][0] = prog
      disp = prog

    if not level is None:
      self.midi_in_settings[self.midi_in_ch]['reverb'][1] = level
      disp = level
      
    if not fback is None:
      self.midi_in_settings[self.midi_in_ch]['reverb'][2] = fback
      disp = fback

    midi_in_reverb = self.midi_in_settings[self.midi_in_ch]['reverb']
    if not disp is None:
      self.midi_obj.set_reverb(self.midi_in_ch, midi_in_reverb[0], midi_in_reverb[1], midi_in_reverb[2])


  # Set chorus parameters for the current MIDI-IN channel
  #   prog : Chorus program
  #   level: Chorus level
  #   fback: Chorus feedback
  #   delay: Chorus delay
  def set_midi_in_chorus(self, prog=None, level=None, fback=None, delay=None):
    send = False
    if not prog is None:
      self.midi_in_settings[self.midi_in_ch]['chorus'][0] = prog
      send = True

    if not level is None:
      self.midi_in_settings[self.midi_in_ch]['chorus'][1] = level
      send = True
      
    if not fback is None:
      self.midi_in_settings[self.midi_in_ch]['chorus'][2] = fback
      send = True
      
    if not delay is None:
      self.midi_in_settings[self.midi_in_ch]['chorus'][3] = delay
      send = True

    midi_in_chorus = self.midi_in_settings[self.midi_in_ch]['chorus']
    if send:
      self.midi_obj.set_chorus(self.midi_in_ch, midi_in_chorus[0], midi_in_chorus[1], midi_in_chorus[2], midi_in_chorus[3])


  # Set vibrate parameters for the current MIDI-IN channel
  #   level: Vibrate level
  #   depth: Vibrate depth
  #   delay: Vibrate delay
  def set_midi_in_vibrate(self, rate=None, depth=None, delay=None):
    send = False
    if not rate is None:
      self.midi_in_settings[self.midi_in_ch]['vibrate'][0] = rate
      send = True

    if not depth is None:
      self.midi_in_settings[self.midi_in_ch]['vibrate'][1] = depth
      send = True
      
    if not delay is None:
      self.midi_in_settings[self.midi_in_ch]['vibrate'][2] = delay
      send = True

    midi_in_vibrate = self.midi_in_settings[self.midi_in_ch]['vibrate']
    if send:
      self.midi_obj.set_vibrate(self.midi_in_ch, midi_in_vibrate[0], midi_in_vibrate[1], midi_in_vibrate[2])

################# End of MIDI-IN Player Class Definition #################


############################################# 
# Message reciever class for MIDI-IN Player
############################################# 
class midi_in_player_message_class(midi_in_player_class):
  # Constructor
  def __init__(self, midi_obj, sdcard_obj, message_center = None):
    super().__init__(midi_obj, sdcard_obj)

    # Message Center
    if not message_center is None:
      self.message_center = message_center
      self.message_center.add_contributor(self)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_PROGRAM_DELTA, self.func_MIDI_IN_PLAYER_SET_PROGRAM_DELTA)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SEND_ALL_MIDI_SETTINGS, self.func_MIDI_IN_PLAYER_SEND_ALL_MIDI_SETTINGS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_REVERB, self.func_MIDI_IN_PLAYER_SET_REVERB)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_CHORUS, self.func_MIDI_IN_PLAYER_SET_CHORUS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_VIBRATE, self.func_MIDI_IN_PLAYER_SET_VIBRATE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_GET_SET_NUMBER, self.func_MIDI_IN_PLAYER_SET_GET_SET_NUMBER)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_GET_MIDI_IN_CHANNEL, self.func_MIDI_IN_PLAYER_SET_GET_MIDI_IN_CHANNEL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_GET_MIDI_IN_SETTING, self.func_MIDI_IN_PLAYER_GET_MIDI_IN_SETTING)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_MASTER_VOLUME_DELTA, self.func_MIDI_IN_PLAYER_MASTER_VOLUME_DELTA)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_SETTING4PARAMS, self.func_MIDI_IN_PLAYER_SET_SETTING4PARAMS)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_CHANNEL_DELTA, self.func_MIDI_IN_PLAYER_SET_CHANNEL_DELTA)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_LOAD_SET_FILE, self.func_MIDI_IN_PLAYER_LOAD_SET_FILE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SAVE_SET_FILE, self.func_MIDI_IN_PLAYER_SAVE_SET_FILE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_DEFAULT, self.func_MIDI_IN_PLAYER_SET_DEFAULT)

    else:
      self.message_center = message_center_class()

  def func_MIDI_IN_PLAYER_SET_PROGRAM_DELTA(self, message_data = None):
    dlt = message_data['delta']
    self.set_midi_in_program(dlt)
    channel = self.midi_in_channel()
    midi_in_program = self.midi_in_settings[channel]['program']
    prg = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_GET_PROGRAM_NAME, {'gm_bank': self.midi_in_settings[channel]['gmbank'], 'program_number': midi_in_program})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PROGRAM_SET_TEXT, {'value': midi_in_program})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_TEXT, {'label': 'label_program_name', 'value': prg})

  def func_MIDI_IN_PLAYER_SEND_ALL_MIDI_SETTINGS(self, message_data = None):
    self.send_all_midi_in_settings()

  def func_MIDI_IN_PLAYER_SET_REVERB(self, message_data = None):
    if message_data is None:
      self.set_midi_in_reverb()

    else:
      if not 'program' in message_data.keys():
        message_data['program'] = None
      if not 'level' in message_data.keys():
        message_data['level'] = None
      if not 'feedback' in message_data.keys():
        message_data['feedback'] = None

      self.set_midi_in_reverb(message_data['program'], message_data['level'], message_data['feedback'])

  def func_MIDI_IN_PLAYER_SET_CHORUS(self, message_data = None):
    if message_data is None:
      self.set_midi_in_chorus()

    else:
      if not 'program' in message_data.keys():
        message_data['program'] = None
      if not 'level' in message_data.keys():
        message_data['level'] = None
      if not 'feedback' in message_data.keys():
        message_data['feedback'] = None
      if not 'delay' in message_data.keys():
        message_data['delay'] = None

      self.set_midi_in_chorus(message_data['program'], message_data['level'], message_data['feedback'], message_data['delay'])

  def func_MIDI_IN_PLAYER_SET_VIBRATE(self, message_data = None):
    if message_data is None:
      self.set_midi_in_vibrate()

    else:
      if not 'rate' in message_data.keys():
        message_data['rate'] = None
      if not 'depth' in message_data.keys():
        message_data['depth'] = None
      if not 'delay' in message_data.keys():
        message_data['delay'] = None

      self.set_midi_in_vibrate(message_data['rate'], message_data['depth'], message_data['delay'])

  def func_MIDI_IN_PLAYER_SET_GET_SET_NUMBER(self, message_data = None):
    if not message_data is None:
      self.set_midi_in_set_num(message_data['set_number'])

    return self.set_midi_in_set_num()

  def func_MIDI_IN_PLAYER_SET_GET_MIDI_IN_CHANNEL(self, message_data = None):
    if not message_data is None:
      self.midi_in_channel(message_data['channel'])

    return self.midi_in_channel()

  def func_MIDI_IN_PLAYER_GET_MIDI_IN_SETTING(self, message_data = None):
    if message_data is None:
      return self.get_midi_in_setting()

    return self.get_midi_in_setting(message_data['channel'], message_data['key'])

  def func_MIDI_IN_PLAYER_MASTER_VOLUME_DELTA(self, message_data = None):
    self.set_synth_master_volume(message_data['delta'])

  def func_MIDI_IN_PLAYER_SET_SETTING4PARAMS(self, message_data = None):
    self.set_midi_in_setting4(message_data['channel'], message_data['key'], message_data['index'], message_data['value'])

  def func_MIDI_IN_PLAYER_SET_CHANNEL_DELTA(self, message_data):
    return self.set_midi_in_channel(message_data['delta'])

  def func_MIDI_IN_PLAYER_LOAD_SET_FILE(self, message_data = None):
    if message_data is None:
      set_number = self.set_midi_in_set_num()

    elif 'set_number' in message_data.keys():
      set_number = message_data['set_number']

    midi_in_set = self.read_midi_in_settings(set_number)
    if not midi_in_set is None:
      print('LOAD MIDI-IN SET:', midi_in_set)
      self.set_midi_in_setting(midi_in_set)
      self.message_center.phone_message(self, self.message_center.MSGID_APPLICATION_SET_MIDI_IN_CHANNEL, {'delta': 0})
      self.set_midi_in_program(0)
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_PROGRAM_DELTA, {'delta': 0})
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_REVERB)
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_CHORUS)
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_VIBRATE)
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SEND_ALL_MIDI_SETTINGS)
      return True

    else:
      return False

  def func_MIDI_IN_PLAYER_SAVE_SET_FILE(self, message_data = None):
    if message_data is None:
      set_number = self.set_midi_in_set_num()

    elif 'set_number' in message_data.keys():
      set_number = message_data['set_number']
        
    self.write_midi_in_settings(set_number)
    print('SAVE MIDI IN SET:', set_number, self.get_midi_in_setting())

  def func_MIDI_IN_PLAYER_SET_DEFAULT(self, message_data = None):
    midi_in_settings = self.get_midi_in_setting()
    self.message_center.phone_message(self, self.message_center.MSGID_MIDI_SET_INSTRUMENT, {'gm_bank': midi_in_settings[self.midi_in_channel()]['gmbank'], 'channel': self.midi_in_channel(), 'program_number': midi_in_settings[self.midi_in_channel()]['program']})
    for ch in range(16):
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_SET_REVERB, {'channel': ch, 'program': 0, 'level': 0, 'feedback': 0})
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_SET_CHORUS, {'channel': ch, 'program': 0, 'level': 0, 'feedback': 0, 'delay': 0})
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_SET_VIBRATE, {'channel': ch, 'rate': 0, 'depth': 0, 'delay': 0})

################# End of midi_in_player_message_class Definition #################


#####################################
# View base class for M5Stack CORE2
#####################################
class view_m5stack_core2():
  def __init__(self):
    self.label_list = {}      # {Label name: its object, ...}

  # Add label name and its object as a dictionary data.
  # Label object is generated in this function.
  def add_label(self, label_name, x, y, font_size, fore_color, back_color, font):
    self.label_list[label_name] = Widgets.Label(label_name, x, y, font_size, fore_color, back_color, font)

  # Show text on the label
  #   message_data['label' ]: Label name
  #   message_data['format']: Format string (optional)
  #   message_data['value' ]: Value to show.  Data type must be tuple if the value contains two or more data. 
  def label_setText(self, message_data):
    label_name = message_data['label']
    if label_name in self.label_list.keys():
      if 'format' in message_data.keys():
        if isinstance(message_data['value'], tuple):
          self.label_list[label_name].setText(message_data['format'].format(*message_data['value']))
        else:
          self.label_list[label_name].setText(message_data['format'].format(message_data['value']))
      else:
        if isinstance(message_data['value'], tuple):
          self.label_list[label_name].setText(*message_data['value'])
        else:
          self.label_list[label_name].setText(message_data['value'])

      return True
    else:
      return False

  # Set text visible flag
  #   message_data['label'  ]: Label name
  #   message_data['visible']: True or False
  def label_setVisible(self, message_data):
    label_name = message_data['label']
    if label_name in self.label_list.keys():
      self.label_list[label_name].setVisible(message_data['visible'])
      return True
    else:
      return False

  # Set text color
  #   message_data['label']: Label name
  #   message_data['fore' ]: Fore color
  #   message_data['back' ]: Back color
  def label_setColor(self, message_data):
    label_name = message_data['label']
    if label_name in self.label_list.keys():
      self.label_list[label_name].setColor(message_data['fore'], message_data['back'])
      return True
    else:
      return False

  # Clear display
  def display_clear(self, color = 0x000000):
    M5.Lcd.clear(color)

################# End of view_m5stack_core2 Definition #################


############################################################
# View class for Standard MIDI File Player (M5Stack CORE2)
############################################################
class view_smf_player_class(view_m5stack_core2):
  # Constructor
  def __init__(self, smf_player_obj, message_center = None):
    super().__init__()

    # Refer midi_in_player object data to draw GUI
    self.data_obj = smf_player_obj

    if not message_center is None:
      self.message_center = message_center
#      self.message_center.add_contributor(self)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_SETUP, self.func_SMF_PLAYER_SETUP)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_SET_TEXT, self.label_setText)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, self.label_setVisible)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_SET_COLOR, self.label_setColor)

      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_FNUM_SET_TEXT, self.func_SMF_PLAYER_FNUM_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_FNAME_SET_TEXT, self.func_SMF_PLAYER_FNAME_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_TRANSP_SET_TEXT, self.func_SMF_PLAYER_TRANSP_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_VOLUME_SET_TEXT, self.func_SMF_PLAYER_VOLUME_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_TEMPO_SET_TEXT, self.func_SMF_PLAYER_TEMPO_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_PARAMETER_SET_TEXT, self.func_SMF_PLAYER_PARAMETER_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_PARM_VALUE_SET_TEXT, self.func_SMF_PLAYER_PARM_VALUE_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_PARM_TITLE_SET_TEXT, self.func_SMF_PLAYER_PARM_TITLE_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_MASTER_VOLUME_SET_TEXT, self.func_SMF_PLAYER_MASTER_VOLUME_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_ACTIVATED, self.func_SMF_PLAYER_ACTIVATED)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_INACTIVATED, self.func_SMF_PLAYER_INACTIVATED)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SMF_PLAYER_SCREEN_VISIBILITY, self.func_SMF_PLAYER_SCREEN_VISIBILITY)

    else:
      self.message_center = self

  def func_SMF_PLAYER_SETUP(self, message_data):
    # Titles
    self.add_label('title_smf', 0, 0, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('title_smf_params', 0, 20, 1.0, 0xff8080, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('title_general', 0, 200, 1.0, 0xff8080, 0x222222, Widgets.FONTS.DejaVu18)

    # Data labels
    self.add_label('label_master_volume', 0, 220, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_smf_file', 0, 60, 1.0, 0x00ffcc, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_smf_fname', 60, 60, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_smf_fnum', 0, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_smf_transp', 46, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_smf_volume', 94, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_smf_tempo', 150, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_smf_parameter', 201, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_smf_parm_value', 262, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_smf_parm_title', 201, 0, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)

  def func_SMF_PLAYER_ACTIVATED(self, message_data):
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_COLOR, {'label': 'title_smf_params', 'fore': 0xff4040, 'back': 0x555555})

  def func_SMF_PLAYER_INACTIVATED(self, message_data):
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_COLOR, {'label': 'title_smf_params', 'fore': 0xff8080, 'back': 0x222222})

  def func_SMF_PLAYER_FNAME_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'index': self.data_obj.smf_file_selected}

    message_data['label'] = 'label_smf_fname'
    if not 'value' in message_data:
      message_data['value'] = self.data_obj.smf_files[message_data['index']][0]

    return self.label_setText(message_data)

  def func_SMF_PLAYER_FNUM_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.smf_file_selected}

    message_data['label'] = 'label_smf_fnum'
    message_data['format'] = '{:03d}'
    return self.label_setText(message_data)

  def func_SMF_PLAYER_TRANSP_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.smf_transpose}

    message_data['label'] = 'label_smf_transp'
    message_data['format'] = '{:0=+3d}'
    return self.label_setText(message_data)

  def func_SMF_PLAYER_VOLUME_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.smf_volume_delta}

    message_data['label'] = 'label_smf_volume'
    message_data['format'] = '{:0=+3d}'
    return self.label_setText(message_data)

  def func_SMF_PLAYER_TEMPO_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.set_smf_speed_factor()}

    message_data['label'] = 'label_smf_tempo'
    message_data['format'] = 'x{:3.1f}'
    return self.label_setText(message_data)

  def func_SMF_PLAYER_PARAMETER_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': application.enc_parameter_info[application.enc_parm]['params'][0]['label']}

    message_data['label'] = 'label_smf_parameter'
    return self.label_setText(message_data)

  def func_SMF_PLAYER_PARM_VALUE_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': ''}
      return self.label_setText(message_data)

    message_data['label'] = 'label_smf_parm_value'
    message_data['format'] = '{:03d}'
    return self.label_setText(message_data)

  def func_SMF_PLAYER_PARM_TITLE_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': application.enc_parameter_info[application.enc_parm]['title']}

    message_data['label'] = 'label_smf_parm_title'
    return self.label_setText(message_data)

  def func_SMF_PLAYER_MASTER_VOLUME_SET_TEXT(self, message_data):
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_TEXT, {'label': 'label_master_volume', 'format': '{:0>3d}', 'value': self.data_obj.midi_obj.get_master_volume()})

  def func_SMF_PLAYER_SCREEN_VISIBILITY(self, message_data = None):
    visible = message_data['visible']

    # Tile labels
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'title_smf', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'title_smf_params', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'title_general', 'visible': visible})

    # SMF data labels
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_master_volume', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_file', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_fname', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_fnum', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_transp', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_volume', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_tempo', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_parameter', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_parm_value', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_parm_title', 'visible': visible})

################# End of view_smf_player_class Definition #################


#################################################
# View class for MIDI-IN Player (M5Stack CORE2)
#################################################
class view_midi_in_player_class(view_m5stack_core2):
  # Constructor
  def __init__(self, midi_in_player_obj, message_center = None):
    super().__init__()

    # Refer midi_in_player object data to draw GUI
    self.data_obj = midi_in_player_obj

    if not message_center is None:
      self.message_center = message_center
#      self.message_center.add_contributor(self)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_SETUP, self.func_MIDI_IN_PLAYER_SETUP)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_TEXT, self.label_setText)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, self.label_setVisible)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_COLOR, self.label_setColor)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_SET_TEXT, self.func_MIDI_IN_PLAYER_SET_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_CTRL_SET_TEXT, self.func_MIDI_IN_PLAYER_SET_CTRL_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_CHANNEL_SET_TEXT, self.func_MIDI_IN_PLAYER_CHANNEL_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_PROGRAM_SET_TEXT, self.func_MIDI_IN_PLAYER_PROGRAM_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARAMETER_SET_TEXT, self.func_MIDI_IN_PLAYER_PARAMETER_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARM_VALUE_SET_TEXT, self.func_MIDI_IN_PLAYER_PARM_VALUE_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARM_TITLE_SET_TEXT, self.func_MIDI_IN_PLAYER_PARM_TITLE_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_ACTIVATED, self.func_MIDI_IN_PLAYER_ACTIVATED)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_INACTIVATED, self.func_MIDI_IN_PLAYER_INACTIVATED)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_INITIAL_DISPLAY, self.func_MIDI_IN_PLAYER_INITIAL_DISPLAY)
      self.message_center.add_subscriber(self, self.message_center.VIEW_MIDI_IN_PLAYER_SCREEN_VISIBILITY, self.func_MIDI_IN_PLAYER_SCREEN_VISIBILITY)

    else:
      self.message_center = self

  def func_MIDI_IN_PLAYER_SETUP(self, message_data):
    # Titles
    self.add_label('title_midi_in', 0, 100, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('title_midi_in_params', 0, 120, 1.0, 0xff8080, 0x222222, Widgets.FONTS.DejaVu18)

    # Data labels
    self.add_label('label_midi_in_set', 0, 140, 1.0, 0x00ffcc, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_midi_in_set_ctrl', 46, 140, 1.0, 0x00ffcc, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_midi_in', 165, 100, 1.0, 0x00ffcc, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_channel', 108, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_program', 159, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_program_name', 0, 160, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_midi_parameter', 204, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_midi_parm_value', 264, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_midi_parm_title', 204, 100, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)

  def func_MIDI_IN_PLAYER_INITIAL_DISPLAY(self, message_data):
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_TEXT, {'label': 'title_midi_in', 'value': 'MIDI-IN PLAYER'})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_TEXT, {'label': 'title_midi_in_params', 'value': 'NO. FIL  MCH PROG PARM VAL'})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_TEXT, {'label': 'label_midi_in_set_ctrl', 'value': message_data['file_op']})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARM_TITLE_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARAMETER_SET_TEXT)

    midi_in_settings = self.data_obj.get_midi_in_setting()
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_TEXT, {'label': 'label_midi_parm_value', 'format': '{:03d}', 'value': midi_in_settings[self.data_obj.midi_in_channel()]['reverb'][0]})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARM_VALUE_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_COLOR, {'label': 'label_midi_parameter', 'fore': 0x00ffcc, 'back': 0x222222})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_COLOR, {'label': 'label_midi_parm_value', 'fore': 0xffffff, 'back': 0x222222})

    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_TEXT, {'label': 'label_midi_in', 'value': '*'})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_midi_in', 'visible': False})

  def func_MIDI_IN_PLAYER_ACTIVATED(self, message_data):
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_COLOR, {'label': 'title_midi_in_params', 'fore': 0xff4040, 'back': 0x555555})

  def func_MIDI_IN_PLAYER_INACTIVATED(self, message_data):
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_COLOR, {'label': 'title_midi_in_params', 'fore': 0xff8080, 'back': 0x222222})

  def func_MIDI_IN_PLAYER_SET_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.set_midi_in_set_num()}

    message_data['label'] = 'label_midi_in_set'
    message_data['format'] = '{:03d}'
    return self.label_setText(message_data)

  def func_MIDI_IN_PLAYER_SET_CTRL_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': application.enc_midi_set_ctrl_list[application.enc_midi_set_ctrl]}

    message_data['label'] = 'label_midi_in_set_ctrl'
    return self.label_setText(message_data)

  def func_MIDI_IN_PLAYER_CHANNEL_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': 0}

    message_data['label'] = 'label_channel'
    message_data['format'] = '{:0>2d}'
    return self.label_setText(message_data)

  def func_MIDI_IN_PLAYER_PROGRAM_SET_TEXT(self, message_data):
    if message_data is None:
      message_data = {'value': 999}

    message_data['label'] = 'label_program'
    message_data['format'] = '{:0>3d}'
    return self.label_setText(message_data)

  def func_MIDI_IN_PLAYER_PARAMETER_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': application.enc_parameter_info[application.enc_parm]['params'][0]['label']}

    message_data['label'] = 'label_midi_parameter'
    return self.label_setText(message_data)

  def func_MIDI_IN_PLAYER_PARM_VALUE_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.midi_in_settings[self.data_obj.midi_in_ch]['reverb'][0]}

    message_data['label'] = 'label_midi_parm_value'
    message_data['format'] = '{:03d}'
    return self.label_setText(message_data)

  def func_MIDI_IN_PLAYER_PARM_TITLE_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': application.enc_parameter_info[application.enc_parm]['title']}

    message_data['label'] = 'label_midi_parm_title'
    return self.label_setText(message_data)

  def func_MIDI_IN_PLAYER_SCREEN_VISIBILITY(self, message_data = None):
    visible = message_data['visible']

    # Tile labels
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'title_midi_in', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'title_midi_in_params', 'visible': visible})

    # MIDI data labels
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_midi_in_set', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_midi_in_set_ctrl', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_midi_in', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_channel', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_program', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_program_name', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_midi_parameter', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_midi_parm_value', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_VISIBLE, {'label': 'label_midi_parm_title', 'visible': visible})

################# End of view_midi_in_player_class Definition #################


###########################################
# View class for Sequencer (M5Stack CORE2)
###########################################
class view_sequencer_class(view_m5stack_core2):
  # Constructor
  def __init__(self, sequencer_obj, message_center = None):
    super().__init__()

    # Refer sequencer object data to draw GUI
    self.data_obj = sequencer_obj

    if not message_center is None:
      self.message_center = message_center
#      self.message_center.add_contributor(self)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_SETUP, self.func_SEQUENCER_SETUP)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, self.label_setText)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, self.label_setVisible)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_SET_COLOR, self.label_setColor)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_TRACK1_SET_TEXT, self.func_SEQUENCER_TRACK1_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_TRACK2_SET_TEXT, self.func_SEQUENCER_TRACK2_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_KEY1_SET_TEXT, self.func_SEQUENCER_KEY1_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_KEY2_SET_TEXT, self.func_SEQUENCER_KEY2_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_FILE_SET_TEXT, self.func_SEQUENCER_FILE_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_FILE_OP_SET_TEXT, self.func_SEQUENCER_FILE_OP_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_TIME_SET_TEXT, self.func_SEQUENCER_TIME_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_MASTER_VOLUME_SET_TEXT, self.func_SEQUENCER_MASTER_VOLUME_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_PARM_NAME_SET_TEXT, self.func_SEQUENCER_PARM_NAME_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, self.func_SEQUENCER_SHOW_CURSOR)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK, self.func_SEQUENCER_DRAW_TRACK)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_DRAW_PLAYTIME, self.func_SEQUENCER_DRAW_PLAYTIME)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_SHOW_PARAMETER_VALUE, self.func_SEQUENCER_SHOW_PARAMETER_VALUE)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_PROGRAM_SET_TEXT, self.func_SEQUENCER_PROGRAM_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_REPEAT_SIGN_SET_TEXT, self.func_SEQUENCER_REPEAT_SIGN_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_TIMESPAN_SET_TEXT, self.func_SEQUENCER_TIMESPAN_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_TEMPO_SET_TEXT, self.func_SEQUENCER_TEMPO_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_MINIMUM_NOTE_SET_TEXT, self.func_SEQUENCER_MINIMUM_NOTE_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_PROGRAM_NUMBER_SET_TEXT, self.func_SEQUENCER_PROGRAM_NUMBER_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_PROGRAM_NAME_SET_TEXT, self.func_SEQUENCER_PROGRAM_NAME_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_VOLUME_RATIO_SET_TEXT, self.func_SEQUENCER_VOLUME_RATIO_SET_TEXT)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_DRAW_KEYBOARD, self.func_SEQUENCER_DRAW_KEYBOARD)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_ACTIVATED, self.func_SEQUENCER_ACTIVATED)
      self.message_center.add_subscriber(self, self.message_center.VIEW_SEQUENCER_SCREEN_VISIBILITY, self.func_SEQUENCER_SCREEN_VISIBILITY)

      self.message_center.add_subscriber(self, self.message_center.VIEW_DISPLAY_CLEAR, self.func_DISPLAY_CLEAR)

    else:
      self.message_center = self
  
  ###################
  ### DELEGATIONS ###
  ###################

  # Draw a note on the sequencer
  def sequencer_draw_note(self, trknum, note_num, note_on_time, note_off_time, disp_mode):
    # Key range to draw
    key_s = self.data_obj.seq_control['disp_key'][trknum][0]
    key_e = self.data_obj.seq_control['disp_key'][trknum][1]
    if note_num < key_s or note_num > key_e:
      return

    # Note rectangle to draw
    time_s = self.data_obj.seq_control['disp_time'][0]
    time_e = self.data_obj.seq_control['disp_time'][1]
    if note_on_time < time_s:
      note_on_time = time_s
    elif note_on_time > time_e:
      return

    if note_off_time > time_e:
      note_off_time = time_e
    elif note_off_time < time_s:
      return

    # Display coordinates
    area = self.data_obj.seq_draw_area[trknum]
    xscale = int((area[2] - area[0] + 1) / (time_e - time_s))
    yscale = int((area[3] - area[1] + 1) / (key_e  - key_s  + 1))
    x = (note_on_time  - time_s) * xscale + area[0]
    w = (note_off_time - note_on_time) * xscale
    y = area[3] - (note_num - key_s + 1) * yscale
    h = yscale
    M5.Lcd.fillRect(x, y, w, h, self.data_obj.seq_note_color[disp_mode][1])
    M5.Lcd.drawRect(x, y, w, h, self.data_obj.seq_note_color[disp_mode][0])

  # Draw velocity
  def sequencer_draw_velocity(self, trknum, channel, note_on_time, notes):
    # Key range to draw
    key_s = self.data_obj.seq_control['disp_key'][trknum][0]
    key_e = self.data_obj.seq_control['disp_key'][trknum][1]

    # Time range to draw
    time_s = self.data_obj.seq_control['disp_time'][0]
    time_e = self.data_obj.seq_control['disp_time'][1]

    # Display coordinates
    area = self.data_obj.seq_draw_area[trknum]
    xscale = int((area[2] - area[0] + 1) / (time_e - time_s))
    yscale = int((area[3] - area[1] + 1) / (key_e  - key_s  + 1))

    # Draw velocity bar graph
    draws = 0
    for note_data in notes:
      if note_data['channel'] == channel:
        # Out of draw area
        note_num = note_data['note']
        if note_num < key_s or note_num > key_e:
          continue

        # Graph color
        if self.data_obj.seq_cursor_note is None:
          color = 0x888888
        else:
          if note_data == self.data_obj.seq_cursor_note[1]:
            color = 0xff4040
          else:
            color = 0x888888

        # Draw a bar graph
        x = area[0] + (note_on_time - time_s) * xscale + draws * 5 + 2
        y = int((area[3] - area[1] - 2) * note_data['velocity'] / 127)
        M5.Lcd.fillRect(x, area[3] - y - 1, 3, y, color)
        draws = draws + 1

  # Draw start and end time line to play in sequencer
  def sequencer_draw_playtime(self, trknum):
    # Draw track frame
    area = self.data_obj.seq_draw_area[trknum]
    x = area[0]
    y = area[1]
    xscale = int((area[2] - area[0] + 1) / (self.data_obj.seq_control['disp_time'][1] - self.data_obj.seq_control['disp_time'][0]))

    # Draw time line
    M5.Lcd.drawLine(x, y, area[2], y, 0x00ff40)
    if self.data_obj.seq_play_time[0] < self.data_obj.seq_play_time[1]:
      # Play time is on screen
      if self.data_obj.seq_play_time[0] < self.data_obj.seq_control['disp_time'][1] and self.data_obj.seq_play_time[1] > self.data_obj.seq_control['disp_time'][0]:
        ts = self.data_obj.seq_play_time[0] if self.data_obj.seq_play_time[0] > self.data_obj.seq_control['disp_time'][0] else self.data_obj.seq_control['disp_time'][0]
        te = self.data_obj.seq_play_time[1] if self.data_obj.seq_play_time[1] < self.data_obj.seq_control['disp_time'][1] else self.data_obj.seq_control['disp_time'][1]
        xs = x + (ts - self.data_obj.seq_control['disp_time'][0]) * xscale
        xe = x + (te - self.data_obj.seq_control['disp_time'][0]) * xscale
        M5.Lcd.drawLine(xs, y, xe, y, 0xff40ff)
    # Play all
    else:
      M5.Lcd.drawLine(x, y, area[2], y, 0xff40ff)

  # DELEGATION FUNCTION to sequencer_class.sequencer_draw_track
  # Draw sequencer track
  #   trknum: The track number to draw (0 or 1)
  def sequencer_draw_track(self, trknum):
#    print('DRAW TRACK IN SEQUENCER VIEW')
    # Draw with velocity
    with_velocity = (self.data_obj.seq_parm == self.data_obj.SEQUENCER_PARM_VELOCITY)

    # Draw track frame
    area = self.data_obj.seq_draw_area[trknum]
    x = area[0]
    w = area[2] - area[0] + 1
    y = area[1]
    h = area[3] - area[1] + 1
    xscale = int((area[2] - area[0] + 1) / (self.data_obj.seq_control['disp_time'][1] - self.data_obj.seq_control['disp_time'][0]))
    M5.Lcd.fillRect(x, y, w, h, 0x222222)
    for t in range(self.data_obj.seq_control['disp_time'][0] + 1, self.data_obj.seq_control['disp_time'][1]):
      # Draw vertical line as a time grid
      color = 0xffffff if t % self.data_obj.seq_control['time_per_bar'] == 0 else 0x60a060
      x0 = x + (t - self.data_obj.seq_control['disp_time'][0]) * xscale
      M5.Lcd.drawLine(x0, y, x0, area[3], color)

      # Signs on score
      if t != 0:
        sc_sign = self.data_obj.sequencer_get_repeat_control(t)
        if not sc_sign is None:
          if sc_sign['loop']:
            color = 0xffff00
            x0 = x0 + 2
          elif sc_sign['skip']:
            color = 0x40a0ff
            x0 = x0 + 2
          elif sc_sign['repeat']:
            color = 0xff4040
            x0 = x0 - 2

          M5.Lcd.drawLine(x0, y, x0, area[3], color)

    # Draw frame
    M5.Lcd.drawRect(x, y, w, h, 0x00ff40)

    # Draw start and end time to play
    self.data_obj.sequencer_draw_playtime(trknum)

    # Draw time span
    time_s = self.data_obj.seq_control['disp_time'][0]
    time_e = self.data_obj.seq_control['disp_time'][1]

    # Draw notes of the track MIDI channel
    channel = self.data_obj.seq_track_midi[trknum]
    time_e = max(time_e+1, len(self.data_obj.seq_score))
    draw_time = time_s
    for score in self.data_obj.seq_score:
      # Note on/off(max) time
      note_on_time  = score['time']
      note_off_time = score['time'] + score['max_duration']

      # All notes in this score are out of time range
      if note_off_time <= time_s or note_on_time >= time_e:
        continue

      # Note on time is the time to draw
      if note_on_time == draw_time:
        # Skip blank times
        while note_on_time > draw_time:
          # DRAW SOMETHING HERE
          draw_time = draw_time + 1

        # Note on time is the draw time
        for notes_data in score['notes']:
          if notes_data['channel'] == channel:
            if self.data_obj.seq_cursor_note is None:
              color = self.data_obj.SEQ_NOTE_DISP_NORMAL
            else:
              color = self.data_obj.SEQ_NOTE_DISP_HIGHLIGHT if score == self.data_obj.seq_cursor_note[0] and notes_data == self.data_obj.seq_cursor_note[1] else self.data_obj.SEQ_NOTE_DISP_NORMAL

            self.data_obj.sequencer_draw_note(trknum, notes_data['note'], note_on_time, note_on_time + notes_data['duration'], color)

        if with_velocity:
          self.data_obj.sequencer_draw_velocity(trknum, channel, note_on_time, score['notes'])

      # Note on time is less than draw time but note is in display area
      else:
        for notes_data in score['notes']:
          if notes_data['channel'] == channel:
            if self.data_obj.seq_cursor_note is None:
              color = self.data_obj.SEQ_NOTE_DISP_NORMAL
            else:
              color = self.data_obj.SEQ_NOTE_DISP_HIGHLIGHT if score == self.data_obj.seq_cursor_note[0] and notes_data == self.data_obj.seq_cursor_note[1] else self.data_obj.SEQ_NOTE_DISP_NORMAL

            self.data_obj.sequencer_draw_note(trknum, notes_data['note'], note_on_time, note_on_time + notes_data['duration'], color)

        if with_velocity:
          self.data_obj.sequencer_draw_velocity(trknum, channel, note_on_time, score['notes'])

      # Next the time to draw
      draw_time = draw_time + 1

  # Draw keyboard
  def sequencer_draw_keyboard(self, trknum):
    # Draw a keyboard of the track
    key_s = self.data_obj.seq_control['disp_key'][trknum][0]
    key_e = self.data_obj.seq_control['disp_key'][trknum][1]
    area = self.data_obj.seq_draw_area[trknum]
    xscale = area[0] - 1
    black_scale = int(xscale / 2)
    yscale = int((area[3] - area[1] + 1) / (key_e - key_s  + 1))
    black_key = [1,3,6,8,10]
    for note_num in range(key_s, key_e + 1):
      # Display a key
      y = area[3] - (note_num - key_s + 1) * yscale
      M5.Lcd.drawRect(0, y, xscale, yscale, 0x888888)
      M5.Lcd.fillRect(1, y + 1, xscale - 2, yscale - 2, 0xffffff)

      # Black key on piano
      key_is_black = ((note_num % 12) in black_key) == True
      if key_is_black:
        M5.Lcd.fillRect(1, y + 1, black_scale, yscale - 2, 0x000000)

  ##########################
  ### END OF DELEGATIONS ###
  ##########################

  def func_SEQUENCER_SETUP(self, message_data):
    # Titles
    self.add_label('title_seq_track1', 0, 20, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('title_seq_track2', 0, 131, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('title_seq_file', 0, 0, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('title_seq_time', 100, 0, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('title_seq_master_volume', 230, 0, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)

    # Data labels
    self.add_label('label_seq_track1', 30, 20, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_track2', 30, 131, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_key1', 57, 20, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_key2', 57, 131, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_file', 40, 0, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_file_op', 80, 0, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_time', 140, 0, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_master_volume', 280, 0, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_parm_name', 215, 20, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_parm_value', 280, 20, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_program1', 100, 20, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
    self.add_label('label_seq_program2', 100, 131, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  def func_SEQUENCER_ACTIVATED(self, message_data):
    self.data_obj.set_cursor_note(self.data_obj.sequencer_find_note(self.data_obj.edit_track(), self.data_obj.get_seq_time_cursor(), self.data_obj.get_seq_key_cursor(self.data_obj.edit_track())))
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_COLOR, {'label': 'label_seq_key1', 'fore': 0xff4040 if self.data_obj.edit_track() == 0 else 0x00ccff, 'back': 0x222222})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_COLOR, {'label': 'label_seq_key2', 'fore': 0xff4040 if self.data_obj.edit_track() == 1 else 0x00ccff, 'back': 0x222222})

    self.data_obj.send_all_sequencer_settings()

    # Set MIDI channel 1 program as the current MIDI channel program
    self.data_obj.send_sequencer_current_channel_settings(self.data_obj.get_track_midi())

  def func_SEQUENCER_TRACK1_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.seq_track_midi[0]+1}

    message_data['label'] = 'label_seq_track1'
    message_data['format'] = '{:02d}'
    return self.label_setText(message_data)

  def func_SEQUENCER_TRACK2_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.seq_track_midi[1]+1}

    message_data['label'] = 'label_seq_track2'
    message_data['format'] = '{:02d}'
    return self.label_setText(message_data)

  def func_SEQUENCER_KEY1_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.seqencer_key_name(self.data_obj.seq_control['key_cursor'][0])}

    message_data['label'] = 'label_seq_key1'
    return self.label_setText(message_data)

  def func_SEQUENCER_KEY2_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.seqencer_key_name(self.data_obj.seq_control['key_cursor'][1])}

    message_data['label'] = 'label_seq_key2'
    return self.label_setText(message_data)

  def func_SEQUENCER_FILE_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.seq_file_number}

    message_data['label'] = 'label_seq_file'
    message_data['format'] = '{:03d}'
    return self.label_setText(message_data)

  def func_SEQUENCER_FILE_OP_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.seq_file_ctrl_label[self.data_obj.seq_file_ctrl]}

    message_data['label'] = 'label_seq_file_op'
    return self.label_setText(message_data)

  def func_SEQUENCER_TIME_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': (self.data_obj.seq_control['time_cursor'], int(self.data_obj.seq_control['time_cursor']/self.data_obj.seq_control['time_per_bar']) + 1)}

    message_data['label'] = 'label_seq_time'
    message_data['format'] = '{:03d}/{:03d}'
    return self.label_setText(message_data)

  def func_SEQUENCER_MASTER_VOLUME_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.midi_obj.get_master_volume()}

    message_data['label'] = 'label_seq_master_volume'
    message_data['format'] = '{:0>3d}'
    return self.label_setText(message_data)

  def func_SEQUENCER_PARM_NAME_SET_TEXT(self, message_data = None):
    if message_data is None:
      message_data = {'value': self.data_obj.seq_parameter_names[self.data_obj.seq_parm]}

    message_data['label'] = 'label_seq_parm_name'
    return self.label_setText(message_data)

  def func_SEQUENCER_PROGRAM_SET_TEXT(self, message_data = None):
    prg = message_data['value']
    current_ch = self.data_obj.get_track_midi()
    if self.data_obj.get_track_midi(0) == current_ch:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_program1', 'value': prg})
    elif self.data_obj.get_track_midi(1) == current_ch:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_program2', 'value': prg})

  def func_SEQUENCER_REPEAT_SIGN_SET_TEXT(self, message_data = None):
    if not message_data is None:
      if 'time' in message_data.keys():
        rept_cursor = message_data['time']
      else:
        rept_cursor = self.data_obj.get_seq_parm_repeat()
    else:
      rept_cursor = self.data_obj.get_seq_parm_repeat()

    # Show the current repeat sign
    disp = 'NON'
    if rept_cursor > 0:
      rept_signs = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_GET_REPEAT_SIGNS, {'time': rept_cursor})
      if not rept_signs is None:
        if rept_signs['loop']:
          disp = 'LOP'
        elif rept_signs['skip']:
          disp = 'SKP'
        elif rept_signs['repeat']:
          disp = 'RPT'

    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'value': disp})

  def func_SEQUENCER_TIMESPAN_SET_TEXT(self, message_data = None):
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:03d}', 'value': self.data_obj.get_seq_disp_time(1) - self.data_obj.get_seq_disp_time(0)})

  def func_SEQUENCER_TEMPO_SET_TEXT(self, message_data = None):
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:03d}', 'value': self.data_obj.get_seq_tempo()})

  def func_SEQUENCER_MINIMUM_NOTE_SET_TEXT(self, message_data = None):
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:=2d}', 'value': 2**self.data_obj.get_seq_mini_note()})

  def func_SEQUENCER_PROGRAM_NUMBER_SET_TEXT(self, message_data = None):
    channel = self.data_obj.get_track_midi()
    prg_num = self.data_obj.get_seq_program(channel)
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:03d}', 'value': prg_num})

  def func_SEQUENCER_PROGRAM_NAME_SET_TEXT(self, message_data = None):
    prg = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_GET_PROGRAM_NAME)
    prg = prg[:9]
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_PROGRAM_SET_TEXT, {'value': prg})

  def func_SEQUENCER_VOLUME_RATIO_SET_TEXT(self, message_data = None):
    channel = self.data_obj.get_track_midi()
    vol = self.data_obj.get_seq_channel(channel, 'volume')
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:03d}', 'value': vol})

  # Show / erase sequencer cursor
  def func_SEQUENCER_SHOW_CURSOR(self, message_data = None):
    edit_track = self.data_obj.edit_track() if message_data['edit_track'] is None else message_data['edit_track']
    disp_time  = message_data['disp_time']
    disp_key   = message_data['disp_key']

    # Draw time cursor
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_TIME_SET_TEXT)
    if self.data_obj.seq_control['disp_time'][0] <= self.data_obj.seq_control['time_cursor'] and self.data_obj.seq_control['time_cursor'] <= self.data_obj.seq_control['disp_time'][1]:
      for trknum in range(2):
        area = self.data_obj.seq_draw_area[trknum]
        x = area[0]
        w = area[2] - area[0] + 1
        y = area[1]
        h = area[3] - area[1] + 1
        xscale = int((area[2] - area[0] + 1) / (self.data_obj.seq_control['disp_time'][1] - self.data_obj.seq_control['disp_time'][0]))

        color = 0xffff40 if disp_time else 0x222222
        M5.Lcd.fillRect(x + (self.data_obj.seq_control['time_cursor'] - self.data_obj.seq_control['disp_time'][0]) * xscale - 3, y - 3, 6, 3, color)

    # Draw key cursor
    area = self.data_obj.seq_draw_area[edit_track]

    # Draw a keyboard of the track
    key_s = self.data_obj.seq_control['disp_key'][edit_track][0]
    key_e = self.data_obj.seq_control['disp_key'][edit_track][1]
    note_num = self.data_obj.seq_control['key_cursor'][edit_track]
    if key_s <= note_num and note_num <= key_e:
      area = self.data_obj.seq_draw_area[edit_track]
      x = area[0] - 6
      yscale = int((area[3] - area[1] + 1) / (key_e - key_s  + 1))

      # Display a key cursor
      y = area[3] - (note_num - key_s + 1) * yscale
      color = 0xff4040 if disp_key else 0xffffff
  #    print('KEY CURS:', note_num, x, y + 1, yscale - 2, color)
      M5.Lcd.fillRect(x, y + 1, 5, yscale - 2, color)

    # Show key name
    if edit_track == 0:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_KEY1_SET_TEXT, None)
    else:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_KEY2_SET_TEXT, None)

  def func_SEQUENCER_DRAW_TRACK(self, message_data = None):
    if message_data is None:
      self.data_obj.sequencer_draw_track(0)
      self.data_obj.sequencer_draw_track(1)
    else:
      if 'track' in message_data.keys():
        self.data_obj.sequencer_draw_track(message_data['track'])
      elif 'editing_track' in message_data.keys():
        self.data_obj.sequencer_draw_track(self.data_obj.edit_track())

  def func_SEQUENCER_DRAW_KEYBOARD(self, message_data = None):
    if message_data is None:
      self.data_obj.sequencer_draw_keyboard(0)
      self.data_obj.sequencer_draw_keyboard(1)
    else:
      if 'track' in message_data.keys():
        self.data_obj.sequencer_draw_keyboard(message_data['track'])
      elif 'editing_track' in message_data.keys():
        self.data_obj.sequencer_draw_keyboard(self.data_obj.edit_track())

  def func_SEQUENCER_DRAW_PLAYTIME(self, message_data = None):
    if message_data is None:
      self.data_obj.sequencer_draw_playtime(0)
      self.data_obj.sequencer_draw_playtime(1)
    else:
      if 'track' in message_data.keys():
        self.data_obj.sequencer_draw_playtime(message_data['track'])
      elif 'editing_track' in message_data.keys():
        self.data_obj.sequencer_draw_playtime(self.data_obj.edit_track())

  def func_SEQUENCER_SHOW_PARAMETER_VALUE(self, message_data = None):
    if   self.data_obj.seq_parm == self.data_obj.SEQUENCER_PARM_TIMESPAN:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:03d}', 'value': self.data_obj.get_seq_disp_time(1) - self.data_obj.get_seq_disp_time(0)})
    elif self.data_obj.seq_parm == self.data_obj.SEQUENCER_PARM_TEMPO:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:03d}', 'value': self.data_obj.get_seq_tempo()})
    elif self.data_obj.seq_parm == self.data_obj.SEQUENCER_PARM_MINIMUM_NOTE:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:=2d}', 'value': 2**self.data_obj.get_seq_mini_note()})
    elif self.data_obj.seq_parm == self.data_obj.SEQUENCER_PARM_PROGRAM:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:03d}', 'value': self.data_obj.get_seq_program(self.data_obj.get_track_midi())})
    elif self.data_obj.seq_parm == self.data_obj.SEQUENCER_PARM_CHANNEL_VOL:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'format': '{:03d}', 'value': self.data_obj.get_seq_channel(self.data_obj.get_track_midi(), 'volume')})
    else:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'value': ''})

  def func_SEQUENCER_SCREEN_VISIBILITY(self, message_data = None):
    visible = message_data['visible']

    # SEQUENCER title labels
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_track1', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_track2', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_file', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_time', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'title_seq_master_volume', 'visible': visible})

    # SEQUENCER data labels
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_track1', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_track2', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_key1', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_key2', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_file', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_file_op', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_time', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_master_volume', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_parm_name', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_parm_value', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_program1', 'visible': visible})
    self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_VISIBLE, {'label': 'label_seq_program2', 'visible': visible})

    # Draw sequencer tracks
    if visible:
      self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SET_NOTE_ON_CURSOR)
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_KEYBOARD)
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 0, 'disp_time': True, 'disp_key': True})
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 1, 'disp_time': True, 'disp_key': True})
  
  def func_DISPLAY_CLEAR(self, message_data = None):
    color = None
    if not message_data is None:
      if 'color' in message_data.keys():
        color = message_data['color']

    self.display_clear(color)

################# End of view_sequencer_class Definition #################


###############################################
# Unit-MIDI / M5Stack CORE2 application class
###############################################
class unit5c2_synth_application_class(message_center_class):
  # Constructor
  def __init__(self, message_center = None):
    # Screen mode
    self.SCREEN_MODE_PLAYER = 0
    self.SCREEN_MODE_SEQUENCER = 1
    self.app_screen_mode = self.SCREEN_MODE_PLAYER

    # MIDI setting file controls list
    self.enc_midi_set_ctrl_list = ['LOD', 'SAV', '---']     # MIDI IN setting file operation sign (load, save, nop)
    self.MIDI_SET_FILE_LOAD = 0                             # Read a MIDI IN setting file menu id
    self.MIDI_SET_FILE_SAVE = 1                             # Save a MIDI IN setting file menu id
    self.MIDI_SET_FILE_NOP  = 2                             # Nop  a MIDI IN setting file menu id
    self.enc_midi_set_ctrl  = self.MIDI_SET_FILE_NOP        # Currnet MIDI IN setting file operation id

    # Effector control parameters
    self.enc_parameter_info = None                          # Information to change program task for the effector controle menu
                                                            # Data definition is in setup(), see setup(). 
    self.enc_total_parameters = 0                           # Sum of enc_parameter_info[*]['params'] array size, see setup()
    self.EFFECTOR_PARM_INIT   = 0                           # Initial parameter index
    self.enc_parm = self.EFFECTOR_PARM_INIT                      # Current parameter index

    if not message_center is None:
      self.message_center = message_center
      self.message_center.add_contributor(self)
      self.message_center.add_subscriber(self, self.message_center.MSGID_APPLICATION_SHOW_MASTER_VOLUME_VALUE, self.func_APPLICATION_SHOW_MASTER_VOLUME_VALUE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_APPLICATION_SET_MIDI_IN_CHANNEL, self.func_APPLICATION_SET_MIDI_IN_CHANNEL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_APPLICATION_MIDI_FILE_OPERATION, self.func_APPLICATION_MIDI_FILE_OPERATION)
      self.message_center.add_subscriber(self, self.message_center.MSGID_APPLICATION_MIDI_FILE_LOAD_SAVE, self.func_APPLICATION_MIDI_FILE_LOAD_SAVE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_APPLICATION_SWITCH_UPPER_LOWER, self.func_APPLICATION_SWITCH_UPPER_LOWER)
      self.message_center.add_subscriber(self, self.message_center.MSGID_APPLICATION_SETUP_PLAYER_SCREEN, self.func_APPLICATION_SETUP_PLAYER_SCREEN)
      self.message_center.add_subscriber(self, self.message_center.MSGID_APPLICATION_SCREEN_CHANGE, self.func_APPLICATION_SCREEN_CHANGE)
      self.message_center.add_subscriber(self, self.message_center.MSGID_APPLICATION_PLAYER_CONTROL, self.func_APPLICATION_PLAYER_CONTROL)
      self.message_center.add_subscriber(self, self.message_center.MSGID_APPLICATION_FLUSH_MIDI_IN_SIGN, self.func_APPLICATION_FLUSH_MIDI_IN_SIGN)

    else:
      self.message_center = self

  def is_player_screen(self):
    return self.app_screen_mode == self.SCREEN_MODE_PLAYER

  def is_sequencer_screen(self):
    return self.app_screen_mode == self.SCREEN_MODE_SEQUENCER

  # Get a parameter info array and parameter('params') index in the info.
  def get_enc_param_index(self, idx):
    pfrom = 0
    pto = -1
    for effector in self.enc_parameter_info:
      pnum = len(effector['params'])
      pfrom = pto + 1
      pto = pfrom + pnum - 1
      if pfrom <= idx and idx <= pto:
        return (effector, idx - pfrom)

    return (None, -1)

  def func_APPLICATION_SHOW_MASTER_VOLUME_VALUE(self, message_data):
    if self.app_screen_mode == self.SCREEN_MODE_PLAYER:
      self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_MASTER_VOLUME_SET_TEXT)
  
    elif self.app_screen_mode == self.SCREEN_MODE_SEQUENCER:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_MASTER_VOLUME_SET_TEXT)

  def func_APPLICATION_SET_MIDI_IN_CHANNEL(self, message_data):
    channel = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_CHANNEL_DELTA, {'delta': message_data['delta']})
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_CHANNEL_SET_TEXT, {'value': channel + 1})

    # Reset the parameter to edit
    self.enc_parm = self.EFFECTOR_PARM_INIT
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARM_TITLE_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARAMETER_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARM_VALUE_SET_TEXT)

  def func_APPLICATION_MIDI_FILE_OPERATION(self, message_data):
    delta = message_data['delta']
    if delta != 0:
      self.enc_midi_set_ctrl = (self.enc_midi_set_ctrl + delta) % 3
      self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_CTRL_SET_TEXT, None)

  def func_APPLICATION_MIDI_FILE_LOAD_SAVE(self, message_data):
    # Load a MIDI settings file
    if self.enc_midi_set_ctrl == self.MIDI_SET_FILE_LOAD:
      if self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_LOAD_SET_FILE) == False:
        print('MIDI IN SET: NO FILE')

      self.enc_midi_set_ctrl = self.MIDI_SET_FILE_NOP
      self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_CTRL_SET_TEXT, None)

    # Save MIDI settings file
    elif self.enc_midi_set_ctrl == self.MIDI_SET_FILE_SAVE:
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SAVE_SET_FILE)
      self.enc_midi_set_ctrl = self.MIDI_SET_FILE_NOP
      self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_CTRL_SET_TEXT, None)

  def func_APPLICATION_SWITCH_UPPER_LOWER(self, message_data):
    # Player screen
    if self.app_screen_mode == self.SCREEN_MODE_PLAYER:
      # SMF Player side
      if message_data['slide_switch_value']:
        self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_INACTIVATED)
        self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_ACTIVATED)

      # MIDI-IN Player side
      else:
        self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_INACTIVATED)
        self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_ACTIVATED)
        self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SEND_ALL_MIDI_SETTINGS)        

    # Sequencer screen
    self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SET_GET_EDIT_TRACK, {'track_number': 0 if message_data['slide_switch_value'] else 1})
    if self.app_screen_mode == self.SCREEN_MODE_SEQUENCER:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_ACTIVATED)

  # Set up the program
  def func_APPLICATION_SETUP_PLAYER_SCREEN(self, message_data):

    def set_smf_reverb(prog=None, level=None, fback=None):
      self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_SET_REVERB, {'program': prog, 'level': level, 'feedback': fback})

    def set_smf_chorus(prog=None, level=None, fback=None, delay=None):
      self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_SET_CHORUS, {'program': prog, 'level': level, 'feedback': fback, 'delay': delay})

    def set_smf_vibrate(rate=None, depth=None, delay=None):
      self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_SET_VIBRATE, {'rate': rate, 'depth': depth, 'delay': delay})

    def set_midi_in_reverb(prog=None, level=None, fback=None):
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_REVERB, {'program': prog, 'level': level, 'feedback': fback})

    def set_midi_in_chorus(prog=None, level=None, fback=None, delay=None):
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_CHORUS, {'program': prog, 'level': level, 'feedback': fback, 'delay': delay})

    def set_midi_in_vibrate(rate=None, depth=None, delay=None):
      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_VIBRATE, {'rate': rate, 'depth': depth, 'delay': delay})

    # GUI for Standard MIDI File Player setup
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SETUP, None)

    # GUI for MIDI-IN Player setup
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SETUP, None)

    # Parameter items settings
    #   'key': effector dict key in smf_settings and midi_in_settings.
    #   'params': effector parameters definition.
    #             'label'.  : label to show as PARM name.
    #             'value'.  : tupple (MAX,DECADE), MAX: parameter maximum value, DECADE: value change in decade mode or not. 
    #             'set_smf' : effector setting function for SMF player
    #             'set_midi': effector setting function for MIDI IN player
    self.enc_parameter_info = [
        {'title': 'REVERB',  'key': 'reverb',  'params': [{'label': 'PROG', 'value': (  7,False)}, {'label': 'LEVL', 'value': (127,True)}, {'label': 'FDBK', 'value': (255,True)}],                                         'set_smf': set_smf_reverb,  'set_midi': set_midi_in_reverb },
        {'title': 'CHORUS',  'key': 'chorus',  'params': [{'label': 'PROG', 'value': (  7,False)}, {'label': 'LEVL', 'value': (127,True)}, {'label': 'FDBK', 'value': (255,True)}, {'label': 'DELY', 'value': (255,True)}], 'set_smf': set_smf_chorus,  'set_midi': set_midi_in_chorus },
        {'title': 'VIBRATE', 'key': 'vibrate', 'params': [{'label': 'RATE', 'value': (127,True )}, {'label': 'DEPT', 'value': (127,True)}, {'label': 'DELY', 'value': (127,True)}],                                         'set_smf': set_smf_vibrate, 'set_midi': set_midi_in_vibrate}
      ]

    # Number of effector parameters
    for effector in self.enc_parameter_info:
      self.enc_total_parameters = self.enc_total_parameters + len(effector['params'])

    # Set synthesizer default
    self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_DEFAULT)

    # Initialize GUI display
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_TEXT, {'label': 'title_smf', 'value': 'SMF PLAYER'})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_TEXT, {'label': 'title_smf_params', 'value': 'NO. TRN VOL TEMP PARM VAL'})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_TEXT, {'label': 'title_general', 'value': 'VOL'})

    self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_MASTER_VOLUME_DELTA, {'delta': 0})
    self.message_center.phone_message(self, self.message_center.MSGID_APPLICATION_SHOW_MASTER_VOLUME_VALUE, None)

    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_TEXT, {'label': 'label_smf_file', 'value': 'FILE:'})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_file', 'visible': True})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_FNAME_SET_TEXT, {'value': 'none'})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_VISIBLE, {'label': 'label_smf_fname', 'visible': True})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_FNUM_SET_TEXT, {'value': 0})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_COLOR, {'label': 'label_smf_fnum', 'fore': 0x00ffcc, 'back': 0x222222})

    self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_CHANGE_TRANSPOSE, {'delta': 0})    
    self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_CHANGE_VOLUME, {'delta': 0})    
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_TEMPO_SET_TEXT)

    self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_CHANNEL_DELTA, {'delta': 0})
    self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_PROGRAM_DELTA, {'delta': 0})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_PARM_TITLE_SET_TEXT)
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_PARAMETER_SET_TEXT)

    smf_settings = self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_GET_EFFECTOR_SETTINGS)
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_PARM_VALUE_SET_TEXT, {'value': smf_settings['reverb'][0]})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_COLOR, {'label': 'label_smf_parameter', 'fore': 0x00ffcc, 'back': 0x222222})
    self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SET_COLOR, {'label': 'label_smf_parm_value', 'fore': 0xffffff, 'back': 0x222222})

    # Prepare SYNTH data and all notes off
    self.message_center.phone_message(self, self.message_center.MSGID_MIDI_ALL_NOTES_OFF)

    # Load default MIDI IN settings
    if self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_LOAD_SET_FILE) == False:
      print('DEFAULT MIDI-IN SET: NO FILE')

    # All notes off
    self.message_center.phone_message(self, self.message_center.MSGID_MIDI_ALL_NOTES_OFF)

    # GUI for MIDI-IN Player draw
    self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_INITIAL_DISPLAY, {'file_op': self.enc_midi_set_ctrl_list[self.enc_midi_set_ctrl]})

  # Screen change
  def func_APPLICATION_SCREEN_CHANGE(self, message_data):
    self.message_center.phone_message(self, self.message_center.VIEW_DISPLAY_CLEAR, {'color': 0x222222})

    self.app_screen_mode = (self.app_screen_mode + message_data['delta']) % 2

    if   self.app_screen_mode == self.SCREEN_MODE_PLAYER:
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SCREEN_VISIBILITY, {'visible': False})
      self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SCREEN_VISIBILITY, {'visible': True})
      self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SCREEN_VISIBILITY, {'visible': True})
      self.message_center.send_message(self, self.message_center.MSGID_APPLICATION_SHOW_MASTER_VOLUME_VALUE, None)

      self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SEND_ALL_MIDI_SETTINGS)

    elif self.app_screen_mode == self.SCREEN_MODE_SEQUENCER:
      self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_SCREEN_VISIBILITY, {'visible': False})
      self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SCREEN_VISIBILITY, {'visible': False})
      self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SCREEN_VISIBILITY, {'visible': True})
      self.message_center.send_message(self, self.message_center.MSGID_APPLICATION_SHOW_MASTER_VOLUME_VALUE, None)

  def func_APPLICATION_FLUSH_MIDI_IN_SIGN(self, message_data = None):
    if self.app_screen_mode == self.SCREEN_MODE_PLAYER:
      self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_TEXT, {'label': 'label_midi_in', 'value': '*' if message_data['midi_in'] else ''})

  def func_APPLICATION_PLAYER_CONTROL(self, message_data = None):
    self.message_center.send_message(self, self.message_center.MSGID_SMF_PLAYER_CONTROL)

################# End of unit5c2_synth_application_class Definition #################


#########################
# 8Encoder Device Class
#########################
class device_8encoder_class(message_center_class):
  # Constructor
  def __init__(self, device_manager, message_center = None):
    # Encoder number in slide switch on
    #   11: CH1 .. 18: CH8
    #   Change number, you can change function assignment channel.
    self.ENC_SMF_FILE       = 11     # Select SMF file
    self.ENC_SMF_TRANSPORSE = 12     # Set transpose for SMF player
    self.ENC_SMF_VOLUME     = 13     # Set volume for SMF player
    self.ENC_SMF_TEMPO      = 14     # Set tempo for SMF player
    self.ENC_SMF_PARAMETER  = 15     # Select parameter to edit
    self.ENC_SMF_CTRL       = 16     # Set effector parameter values
    self.ENC_SMF_SCREEN     = 17     # not available
    self.ENC_SMF_MASTER_VOL = 18     # Change master volume

    # Encoder number in slide switch off
    #   1: CH1 .. 8: CH8
    #   Change number, you can change function assignment channel.
    self.ENC_MIDI_SET        = 1     # Select MIDI setting file
    self.ENC_MIDI_FILE       = 2     # File operation (load, save)
    self.ENC_MIDI_CHANNEL    = 3     # Select MIDI channel to edit
    self.ENC_MIDI_PROGRAM    = 4     # Select program for MIDI channel
    self.ENC_MIDI_PARAMETER  = 5     # Select parameter to edit
    self.ENC_MIDI_CTRL       = 6     # Set effector parameter values
    self.ENC_MIDI_SCREEN     = 7     # not available
    self.ENC_MIDI_MASTER_VOL = 8     # Change master volume

    # Sequencer mode: Encoder number in slide switch off
    #   1: CH1 .. 8: CH8
    #   Change number, you can change function assignment channel.
    #     TRACK1
    self.ENC_SEQ_SET1        = 111   # Select MIDI setting file
    self.ENC_SEQ_FILE1       = 112   # File operation (load, save)
    self.ENC_SEQ_CURSOR1     = 113   # Move sequencer cursor
    self.ENC_SEQ_NOTE_LEN1   = 114   # Set sequencer note length
    self.ENC_SEQ_PARAMETER1  = 115   # Select parameter to edit
    self.ENC_SEQ_CTRL1       = 116   # Set effector parameter values
    self.ENC_SEQ_SCREEN1     = 117   # not available
    self.ENC_SEQ_MASTER_VOL1 = 118   # Change master volume
    #     TRACK2
    self.ENC_SEQ_SET2        = 101   # Select MIDI setting file
    self.ENC_SEQ_FILE2       = 102   # File operation (load, save)
    self.ENC_SEQ_CURSOR2     = 103   # Move sequencer cursor
    self.ENC_SEQ_NOTE_LEN2   = 104   # Set sequencer note length
    self.ENC_SEQ_PARAMETER2  = 105   # Select parameter to edit
    self.ENC_SEQ_CTRL2       = 106   # Set effector parameter values
    self.ENC_SEQ_SCREEN2     = 107   # not available
    self.ENC_SEQ_MASTER_VOL2 = 108   # Change master volume

    # Change parameter value by decade or 1 (decade: True, 1: False)
    self.enc_parm_decade = False                     # Change effector parameter values
    self.enc_volume_decade = False                   # Change SMF volume
    self.enc_mastervol_decade = False                # Change master volume
    self.enc_midi_set_decade = False                 # Select MIDI IN setting file
    self.enc_midi_prg_decade = False                 # Select program for MIDI IN channel

    # Sequencer internal parameters
    self.seq_cursor_time_or_key = True             # True: Move time cursor / False: Move key cursor

    # I2C
    i2c0 = I2C(0, scl=Pin(33), sda=Pin(32), freq=100000)
    i2c_list = i2c0.scan()
    print('I2C:', i2c_list)
    self.encoder8_0 = Encoder8Unit(i2c0, 0x41)      # 8 Encoder object
    for enc_ch in range(1, 9):
      self.encoder8_0.set_counter_value(enc_ch, 0)

    self.slide_switch_change = False
    self.slide_switch_value = None      # None: inii / Treu: Upper side / False: Lower side
    self.enc_button_ch = [False] * 8    # 8Encoder buttons are pushed or released 

    self.enc_slide_switch = None     # 8encoder slide switch status (on:True, off:False)

    device_manager.add_device(self)
    if not message_center is None:
      self.message_center = message_center
      self.message_center.add_contributor(self)
      self.message_center.add_subscriber(self, self.message_center.MSGID_DEVICE_PHONE_SEQ_TURN_OFF_PLAY_BUTTON, self.func_DEVICE_PHONE_SEQ_TURN_OFF_PLAY_BUTTON)
      self.message_center.add_subscriber(self, self.message_center.MSGID_DEVICE_PHONE_SEQ_GET_PAUSE_STOP_BUTTON, self.func_DEVICE_PHONE_SEQ_GET_PAUSE_STOP_BUTTON)
      self.message_center.add_subscriber(self, self.message_center.MSGID_DEVICE_PHONE_SEQ_STOP_BUTTON, self.func_DEVICE_PHONE_SEQ_STOP_BUTTON)
    else:
      self.message_center = self

  def func_DEVICE_PHONE_SEQ_TURN_OFF_PLAY_BUTTON(self, message_data):
    scan_enc_channel = self.ENC_SEQ_SET1 % 10
    while self.encoder8_0.get_button_status(scan_enc_channel) == False:
      time.sleep(0.1)

    return True

  def func_DEVICE_PHONE_SEQ_GET_PAUSE_STOP_BUTTON(self, message_data):
    scan_enc_channel = self.ENC_SEQ_SET1 % 10
    return not self.encoder8_0.get_button_status(scan_enc_channel)

  def func_DEVICE_PHONE_SEQ_STOP_BUTTON(self, message_data):
    scan_enc_channel = self.ENC_SEQ_SET1 % 10
    count = -1
    if self.encoder8_0.get_button_status(scan_enc_channel) == False:
      # Stop sound
      self.encoder8_0.set_led_rgb(scan_enc_channel, 0x40ff40)

      # Wait for releasing the button
      count = 0
      while self.encoder8_0.get_button_status(scan_enc_channel) == False:
        time.sleep(0.1)
        count = count + 1
        if count >= 10:
          self.encoder8_0.set_led_rgb(scan_enc_channel, 0xff4040)

      # Stop
      if count >= 10:
        self.encoder8_0.set_led_rgb(scan_enc_channel, 0x000000)
        return count

      # Pause
      self.encoder8_0.set_led_rgb(scan_enc_channel, 0xffff00)
      while self.encoder8_0.get_button_status(scan_enc_channel) == True:
        time.sleep(0.1)

      count = 0
      while self.encoder8_0.get_button_status(scan_enc_channel) == False:
        time.sleep(0.1)
        count = count + 1
        if count >= 10:
          self.encoder8_0.set_led_rgb(scan_enc_channel, 0xff4040)

      # Stop
      self.encoder8_0.set_led_rgb(scan_enc_channel, 0x000000)
      if count >= 10:
        return count

    return 0 if count > 0 else -1

  # Device controller
  #   Read input informatiom
  def controller(self):
    # Slide switch
    self.slide_switch_change = False
    slide_switch_change = False                     ### TO BE DELETED
    slide_switch = self.encoder8_0.get_switch_status()
    if self.slide_switch_value is None:
      self.slide_switch_value = slide_switch
      self.enc_slide_switch = slide_switch               ### TO BE DELETED
      self.slide_switch_change = True
      slide_switch_change = True                    ### TO BE DELETED

    elif slide_switch != self.slide_switch_value:
      self.slide_switch_value = slide_switch
      self.enc_slide_switch = slide_switch               ### TO BE DELETED
      self.slide_switch_change = True
      slide_switch_change = True                    ### TO BE DELETED

    # The slide switch status is changed
    if self.slide_switch_change:
      self.message_center.send_message(self, self.message_center.MSGID_APPLICATION_SWITCH_UPPER_LOWER, {'slide_switch_value': self.slide_switch_value})

    # Scan encoders
    for enc_ch in range(1,9):
      enc_menu = enc_ch + (10 if self.slide_switch_value else 0) + (100 if application.is_sequencer_screen() else 0)
      enc_count = self.encoder8_0.get_counter_value(enc_ch)
      enc_button = not self.encoder8_0.get_button_status(enc_ch)

      # Get an edge trigger of the encoder button
      if enc_button == True:
        if self.enc_button_ch[enc_ch-1] == True:
          enc_button = False
        else:
          self.enc_button_ch[enc_ch-1] = True
          self.encoder8_0.set_led_rgb(enc_ch, 0x40ff40)
      else:
        if self.enc_button_ch[enc_ch-1] == True:
          self.encoder8_0.set_led_rgb(enc_ch, 0x000000)
          self.enc_button_ch[enc_ch-1] = False

      # Encoder rotations
      if enc_count >= 2:
        delta = 1
      elif  enc_count <= -2:
        delta = -1
      else:
        delta = 0

      # Reset the encoder counter
      if delta != 0:
        self.encoder8_0.set_counter_value(enc_ch, 0)

######====== IMPLEMET NOT YET ======######
      ## PRE-PROCESS: Parameter encoder
      if enc_menu == self.ENC_SMF_PARAMETER or enc_menu == self.ENC_MIDI_PARAMETER:
        if delta != 0 or slide_switch_change:
          # Change the target parameter to edit with CTRL1
          application.enc_parm = application.enc_parm + delta
          if application.enc_parm < 0:
            application.enc_parm = application.enc_total_parameters -1
          elif application.enc_parm >= application.enc_total_parameters:
            application.enc_parm = 0

      ## PRE-PROCESS: Parameter control encoder
      if enc_menu == self.ENC_SMF_CTRL or enc_menu == self.ENC_MIDI_CTRL:
        # Decade value button (toggle)
        if enc_button and self.enc_button_ch[enc_ch-1]:
          self.enc_parm_decade = not self.enc_parm_decade

        if self.enc_parm_decade:
          self.encoder8_0.set_led_rgb(enc_ch, 0xffa000)

      ## PRE-PROCESS: Sequencer parameter encoder
      if enc_menu == self.ENC_SEQ_PARAMETER1 or enc_menu == self.ENC_SEQ_PARAMETER2:
        if delta != 0 or slide_switch_change:
          # Change the target parameter to edit with CTRL1
          self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_PARAMETER, {'delta': delta})

      ## PRE-PROCESS: Parameter control encoder
      if enc_menu == self.ENC_SEQ_CTRL1 or enc_menu == self.ENC_SEQ_CTRL2:
        # Decade value button (toggle)
        if enc_button and self.enc_button_ch[enc_ch-1]:
          self.enc_parm_decade = not self.enc_parm_decade

        if self.enc_parm_decade:
          self.encoder8_0.set_led_rgb(enc_ch, 0xffa000)

        # Show repeat sign parameter just after changing the current time
        rept = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_GET_REPEAT_FLAG)
        if not rept is None:
          if rept['loop']:
            disp = 'LOP'
          elif rept['skip']:
            disp = 'SKP'
          elif rept['repeat']:
            disp = 'RPT'
          else:
            disp = 'NON'

          self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SET_TEXT, {'label': 'label_seq_parm_value', 'value': disp})

      ## MENU PROCESS
      # Select SMF file
      if enc_menu == self.ENC_SMF_FILE:
          # Select a MIDI file
          if delta != 0:
            self.message_center.send_message(self, self.message_center.MSGID_SMF_PLAYER_CHANGE_SMF_FILE_NO, {'delta': delta})

          # Play the selected MIDI file or stop playing
          if enc_button == True:
            self.message_center.send_message(self, self.message_center.MSGID_APPLICATION_PLAYER_CONTROL)

      # Set transpose for SMF player
      elif enc_menu == self.ENC_SMF_TRANSPORSE:
        if delta != 0:
          self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_CHANGE_TRANSPOSE, {'delta': delta})    

        # Pause/Restart SMF player in playing
        if enc_button == True:
          if self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_IS_PLAYING_SMF):
            if self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_SET_GET_PLAY_MODE) == 'PLAY':
              print('PAUSE MIDI PLAYER')
              self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_SET_GET_PLAY_MODE, {'set': 'PAUSE'})
            else:
              print('CONTINUE MIDI PLAYER')
              self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_SET_GET_PLAY_MODE, {'set': 'PLAY'})
          else:
            print('MIDI PLAYER NOT PLAYING')

      # Set volume for SMF player
      elif enc_menu == self.ENC_SMF_VOLUME:
        # Decade value button (toggle)
        if enc_button and self.enc_button_ch[enc_ch-1]:
          self.enc_volume_decade = not self.enc_volume_decade

        if self.enc_volume_decade:
          self.encoder8_0.set_led_rgb(enc_ch, 0xffa000)

        # Slide switch off: midi-in mode
        if slide_switch == False:
          pass

        # Slide switch on: SMF player mode
        else:
          if delta != 0:
            self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_CHANGE_VOLUME, {'delta': delta * (10 if self.enc_volume_decade else 1)})    

      # Set tempo for SMF player
      elif enc_menu == self.ENC_SMF_TEMPO:
        # Change MIDI play speed
        spf = self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_SET_GET_SPEED_FACTOR)
        if delta == -1:
          spf = spf - 0.1
          if spf < 0.1:
            spf = 0.1
        elif delta == 1:
          spf = spf + 0.1
          if spf > 5:
            spf = 5

        self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_SET_GET_SPEED_FACTOR, {'set': spf})
        if delta != 0:
          self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_TEMPO_SET_TEXT, {'value': spf})

      # Select parameter to edit
      elif enc_menu == self.ENC_SMF_PARAMETER:
        if delta != 0 or slide_switch_change:
          # Get parameter info of enc_parm
          (effector, prm_index) = application.get_enc_param_index(application.enc_parm)
          if not effector is None:
            pttl = effector['title']
            plbl = effector['params'][prm_index]['label']
            smf_settings = self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_GET_EFFECTOR_SETTINGS)
            disp = smf_settings[effector['key']][prm_index]
          else:
            pttl = '????'
            plbl = '????'
            disp = 999

          # Display the parameter
          self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_PARM_TITLE_SET_TEXT, {'value': pttl})
          self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_PARAMETER_SET_TEXT, {'value': plbl})
          self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_PARM_VALUE_SET_TEXT, {'value': disp})

      # Set parameter value
      elif enc_menu == self.ENC_SMF_CTRL:
        if delta != 0 or slide_switch_change:
          # Get parameter info of enc_parm
          (effector, prm_index) = application.get_enc_param_index(application.enc_parm)
          if not effector is None:
            smf_settings = self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_GET_EFFECTOR_SETTINGS)
            val = smf_settings[effector['key']][prm_index] + delta * (10 if self.enc_parm_decade and effector['params'][prm_index]['value'][1] else 1)
            if val < 0:
              val = effector['params'][prm_index]['value'][0]
            elif val > effector['params'][prm_index]['value'][0]:
              val = 0

            # Send MIDI message
            self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_SET_EFFECTOR_PARAMETER, {'effector': effector['key'], 'param_index': prm_index, 'value': val})
            smf_settings = self.message_center.phone_message(self, self.message_center.MSGID_SMF_PLAYER_GET_EFFECTOR_SETTINGS)
            effector['set_smf'](*smf_settings[effector['key']])
            disp = val
          else:
            disp = 999

          # Display the label
          self.message_center.phone_message(self, self.message_center.VIEW_SMF_PLAYER_PARM_VALUE_SET_TEXT, {'value': disp})

      # Select MIDI setting file
      elif enc_menu == self.ENC_MIDI_SET:
        # Decade value button (toggle)
        if enc_button and self.enc_button_ch[enc_ch-1]:
          self.enc_midi_set_decade = not self.enc_midi_set_decade

        if self.enc_midi_set_decade:
          self.encoder8_0.set_led_rgb(enc_ch, 0xffa000)

        # File number
        if delta != 0:
          num = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_GET_SET_NUMBER)
          num = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_GET_SET_NUMBER, {'set_number': num + delta * (10 if self.enc_midi_set_decade else 1)})
          self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_SET_SET_TEXT, {'value': num})

      # File operation (read/write)
      elif enc_menu == self.ENC_MIDI_FILE:
        # File control
        if delta != 0:
          self.message_center.send_message(self, self.message_center.MSGID_APPLICATION_MIDI_FILE_OPERATION, {'delta': delta})

        # File operation button
        if enc_button and self.enc_button_ch[enc_ch-1]:
          self.message_center.send_message(self, self.message_center.MSGID_APPLICATION_MIDI_FILE_LOAD_SAVE, None)

      # Select MIDI channel to edit
      elif enc_menu == self.ENC_MIDI_CHANNEL:
        # Select MIDI channel to MIDI-IN play
        if delta != 0:
          self.message_center.phone_message(self, self.message_center.MSGID_APPLICATION_SET_MIDI_IN_CHANNEL, {'delta': delta})
          self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_PROGRAM_DELTA, {'delta': 0})

        # All notes off of MIDI-IN player channel
        if enc_button == True:
          ch = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_GET_MIDI_IN_CHANNEL)
          self.message_center.phone_message(self, self.message_center.MSGID_MIDI_ALL_NOTES_OFF, {'channel': ch})
#PITCH BEND TEST          self.message_center.phone_message(self, self.message_center.MSGID_MIDI_SEND_PITCH_BEND, {'channel': ch, 'value': 1000})

      # Select program for MIDI channel
      elif enc_menu == self.ENC_MIDI_PROGRAM:
        # Decade value button (toggle)
        if enc_button and self.enc_button_ch[enc_ch-1]:
          self.enc_midi_prg_decade = not self.enc_midi_prg_decade

        if self.enc_midi_prg_decade:
          self.encoder8_0.set_led_rgb(enc_ch, 0xffa000)

        # Select program
        if delta != 0:
          self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_PROGRAM_DELTA, {'delta': delta * (10 if self.enc_midi_prg_decade else 1)})

        # All notes off of MIDI-IN player channel
        if enc_button == True:
          ch = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_GET_MIDI_IN_CHANNEL)
          self.message_center.phone_message(self, self.message_center.MSGID_MIDI_ALL_NOTES_OFF, {'channel': ch})

      # Select parameter to edit
      elif enc_menu == self.ENC_MIDI_PARAMETER:
        if delta != 0 or slide_switch_change:
          # Get parameter info of enc_parm
          (effector, prm_index) = application.get_enc_param_index(application.enc_parm)
          if not effector is None:
            pttl = effector['title']
            plbl = effector['params'][prm_index]['label']
            midi_in_settings = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_GET_MIDI_IN_SETTING)
            ch = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_GET_MIDI_IN_CHANNEL)
            disp = midi_in_settings[ch][effector['key']][prm_index]
          else:
            pttl = '????'
            plbl = '????'
            disp = 999

          # Display the parameter
          self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARM_TITLE_SET_TEXT, {'value': pttl})
          self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARAMETER_SET_TEXT, {'value': plbl})
          self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARM_VALUE_SET_TEXT, {'value': disp})

      # Set parameter value
      elif enc_menu == self.ENC_MIDI_CTRL:
        if delta != 0 or slide_switch_change:
          # Get parameter info of enc_parm
          (effector, prm_index) = application.get_enc_param_index(application.enc_parm)
          if not effector is None:
            midi_in_settings = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_GET_MIDI_IN_SETTING)
            ch = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_GET_MIDI_IN_CHANNEL)
            val = midi_in_settings[ch][effector['key']][prm_index] + delta * (10 if self.enc_parm_decade and effector['params'][prm_index]['value'][1] else 1)
            if val < 0:
              val = effector['params'][prm_index]['value'][0]
            elif val > effector['params'][prm_index]['value'][0]:
              val = 0

            # Send MIDI message
            self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_SET_SETTING4PARAMS, {'channel': ch, 'key': effector['key'], 'index': prm_index, 'value': val})
            midi_in_settings = self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_GET_MIDI_IN_SETTING)
            effector['set_midi'](*midi_in_settings[ch][effector['key']])
            disp = val
          else:
            disp = 999

          # Display the label
          self.message_center.phone_message(self, self.message_center.VIEW_MIDI_IN_PLAYER_PARM_VALUE_SET_TEXT, {'value': disp})

      # Change master volume
      elif enc_menu == self.ENC_SMF_MASTER_VOL or enc_menu == self.ENC_MIDI_MASTER_VOL or enc_menu == self.ENC_SEQ_MASTER_VOL1 or enc_menu == self.ENC_SEQ_MASTER_VOL2:
        # Decade value button (toggle)
        if enc_button and self.enc_button_ch[enc_ch-1]:
          self.enc_mastervol_decade = not self.enc_mastervol_decade

        if self.enc_mastervol_decade:
          self.encoder8_0.set_led_rgb(enc_ch, 0xffa000)

        # Change master volume
        if delta != 0: 
            master_volume_delta = delta * (10 if self.enc_mastervol_decade else 1)
            self.message_center.phone_message(self, self.message_center.MSGID_MIDI_IN_PLAYER_MASTER_VOLUME_DELTA, {'delta': master_volume_delta})
            self.message_center.send_message(self, self.message_center.MSGID_APPLICATION_SHOW_MASTER_VOLUME_VALUE, None)

        # All notes off
        if enc_button:
          self.message_center.phone_message(self, self.message_center.MSGID_MIDI_ALL_NOTES_OFF)

      ##### COMMON #####

      # Change screen mode
      elif enc_menu == self.ENC_SMF_SCREEN or enc_menu == self.ENC_MIDI_SCREEN or enc_menu == self.ENC_SEQ_SCREEN1 or enc_menu == self.ENC_SEQ_SCREEN2:
        if delta != 0:
          self.message_center.send_message(self, self.message_center.MSGID_APPLICATION_SCREEN_CHANGE, {'delta': delta})
          self.message_center.flush_messages()
          self.message_center.send_message(self, self.message_center.MSGID_APPLICATION_SWITCH_UPPER_LOWER, {'slide_switch_value': self.slide_switch_value})

      ##### SEQUENCER SREEN MODE #####

      # Select file / Play or Stop
      elif  enc_menu == self.ENC_SEQ_SET1 or enc_menu == self.ENC_SEQ_SET2:
        if delta != 0 or enc_button:
          self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SELECT_FILE, {'delta': delta, 'do_operation': enc_button})

      # File operation
      elif  enc_menu == self.ENC_SEQ_FILE1 or enc_menu == self.ENC_SEQ_FILE2:
        if delta != 0 or enc_button:
          self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_FILE_OP, {'delta': delta, 'do_operation': enc_button})

      # Move sequencer cursor
      elif enc_menu == self.ENC_SEQ_CURSOR1 or enc_menu == self.ENC_SEQ_CURSOR2:
        # Sequencer cursor is time or key (toggle)
        if enc_button and self.enc_button_ch[enc_ch-1]:
          self.seq_cursor_time_or_key = not self.seq_cursor_time_or_key

        if delta != 0:
          self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': False, 'disp_key': False})

          # Move time cursor
          if self.seq_cursor_time_or_key:
            self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_MOVE_TIME_CURSOR, {'delta': delta})

          # Move key cursor
          else:
            self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_MOVE_KEY_CURSOR, {'delta': delta})

          # Show cursor
          self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': True, 'disp_key': True})

          # Find a note on the cursor
          self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_FIND_NOTE_ON_CURSOR)

      # Set sequencer note length
      elif enc_menu == self.ENC_SEQ_NOTE_LEN1 or enc_menu == self.ENC_SEQ_NOTE_LEN2:
        # Is any note on the cursor
        if self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_NOTE_ON_CURSOR):
          # Find note on the cursor and change the duration
          if delta != 0:
            note_dur = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_NOTE_DURATION, {'delta': delta})

            # A note is found
            if not note_dur is None:
              if note_dur >= 0:
                self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)

          # Delete the highlited note
          else:
            if enc_button:
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_DELETE_NOTE_ON_CURSOR)
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)

        # Put new note
        else:
          if enc_button:
            self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_PUT_NOTE_ON_CURSOR)
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)

      # Select sequencer parameter to edit
      elif enc_menu == self.ENC_SEQ_PARAMETER1 or enc_menu == self.ENC_SEQ_PARAMETER2:
        if delta != 0 or slide_switch_change:
          # Show parameter value
          self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_PARM_NAME_SET_TEXT)
          self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_PARAMETER_VALUE)
          self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)

      # Set sequencer parameter value
      elif enc_menu == self.ENC_SEQ_CTRL1 or enc_menu == self.ENC_SEQ_CTRL2:
        if delta != 0 or slide_switch_change:
          # Change MIDI channel of the current track
          if   self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_CHANNEL):
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': False, 'disp_key': False})
            self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_MIDI_CHANNEL, {'delta': delta})
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': True, 'disp_key': True})
            self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_MIDI_CHANNEL_CHANGED)

          # Change time span
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_TIMESPAN):
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 0, 'disp_time': False, 'disp_key': False})
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 1, 'disp_time': False, 'disp_key': False})
            self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_TIME_SPAN, {'delta': delta})
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 0, 'disp_time': True, 'disp_key': True})
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 1, 'disp_time': True, 'disp_key': True})
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_TIMESPAN_SET_TEXT)

          # Change velocity of the note selected
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_VELOCITY):
            if self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_VELOCITY, {'delta': delta * (10 if self.enc_parm_decade else 1)}):
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK, {'editing_track': True})

          # Change start time to begining play
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_PLAY_START):
            if self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_PLAY_START, {'delta': delta * (10 if self.enc_parm_decade else 1)}):
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)

          # Change end time to finish play
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_PLAY_END):
            if self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_PLAY_END, {'delta': delta * (10 if self.enc_parm_decade else 1)}):
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)

          # Insert/Delete time at the time cursor on the current MIDI channel only
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_STRETCH_ONE):
            affected = False

            # Insert
            if delta > 0:
              affected = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_INSERT_TIME, {'delta': delta})
            # Delete
            elif delta < 0:
              affected = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_DELETE_TIME, {'delta': -delta})

            # Refresh screen
            if affected:
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': False, 'disp_key': False})
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_ADD_TIME_CURSOR, {'delta': delta})
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SET_NOTE_ON_CURSOR)
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK, {'editing_track': True})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': None, 'disp_time': True, 'disp_key': True})

          # Insert/Delete time at the time cursor on the all MIDI channels
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_STRETCH_ALL):
            affected = False

            # Insert
            if delta > 0:
              for ch in range(16):
                affected = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_INSERT_TIME, {'channel': ch, 'delta': delta}) or affected
            # Delete
            elif delta < 0:
              for ch in range(16):
                affected = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_DELETE_TIME, {'channel': ch, 'delta': -delta}) or affected

            # Refresh screen
            if affected:
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 0, 'disp_time': False, 'disp_key': False})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 1, 'disp_time': False, 'disp_key': False})
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_ADD_TIME_CURSOR, {'delta': delta})

              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SET_NOTE_ON_CURSOR)
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 0, 'disp_time': True, 'disp_key': True})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 1, 'disp_time': True, 'disp_key': True})

          # Clear all notes in the current MIDI channel
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_CLEAR_ONE):
            if delta != 0:
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CLEAR_TRACK)
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK, {'editing_track': True})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_PLAYTIME, {'editing_track': True})

          # Clear all notes in the all MIDI channel
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_CLEAR_ALL):
            if delta != 0:
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CLEAR_SCORE)
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_PLAYTIME)

          # Change number of the shortest length notes in a bar
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_NOTES_BAR):
            if delta != 0:
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_TIME_PER_BAR, {'delta': delta})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)

          # Resolution up
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_RESOLUTION):
            if delta != 0:
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_RESOLUTION, {'up': delta > 0})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 0, 'disp_time': False, 'disp_key': False})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 1, 'disp_time': False, 'disp_key': False})
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SET_NOTE_ON_CURSOR)
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 0, 'disp_time': True, 'disp_key': True})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_SHOW_CURSOR, {'edit_track': 1, 'disp_time': True, 'disp_key': True})

          # Change tempo
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_TEMPO):
            if delta != 0:
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_TEMPO, {'delta': delta * (10 if self.enc_parm_decade else 1)})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_TEMPO_SET_TEXT)

          # Change length of shortest note
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_MINIMUM_NOTE):
            if delta != 0:
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SET_MINIMUM_NOTE, {'delta': delta})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_MINIMUM_NOTE_SET_TEXT)

          # Change MIDI channnel program
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_PROGRAM):
            prg_num = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_PROGRAM, {'delta': delta * (10 if self.enc_parm_decade else 1)})
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_PROGRAM_NUMBER_SET_TEXT)
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_PROGRAM_NAME_SET_TEXT)

            self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SET_INSTRUMENT)
            self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_SEND_CHANNEL_SETTINGS)

          # Change a volume ratio of MIDI channel
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_CHANNEL_VOL):
            vol = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_VOLUME_RATIO, {'delta': delta * (10 if self.enc_parm_decade else 1)})
            self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_VOLUME_RATIO_SET_TEXT)

          # Set repeat signs (NONE/LOOP/SKIP/REPEAT)
          elif self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_IS_MENU_PARM_REPEAT):
            # Get the time cursor of the repeat flag control
            rept_cursor = self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_GET_SIGNS_CURSOR)

            # No repeat flag cursor (Only just after the application waked up)
            sign_change = True
            if rept_cursor is None:
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_REPEAT_SIGN_SET_TEXT)
              sign_change = False

            # Repeat flag cursor is at the top of score (Ignore any repeat sign)
            elif rept_cursor == 0:
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_REPEAT_SIGN_SET_TEXT)
              sign_change = False

            # Change the repeat sign on the cursor exists (except the top of score)
            if sign_change:
              # Change the repeat flag status.  A blank signs data will be prepared for the time cursor without any signs.
              self.message_center.phone_message(self, self.message_center.MSGID_SEQUENCER_CHANGE_REPEAT_SIGNS, {'time': rept_cursor, 'delta': delta})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_REPEAT_SIGN_SET_TEXT, {'time': rept_cursor})
              self.message_center.phone_message(self, self.message_center.VIEW_SEQUENCER_DRAW_TRACK)

################# End of 8Encoder Device Class Definition #################


##### Program Code #####

# Task loop
def loop():
  M5.update()

  # Receive MIDI-IN and send data to the synthesizer and MIDI-OUT
  received = midi_obj.midi_in_out()
  application.message_center.phone_message(application, application.message_center.MSGID_APPLICATION_FLUSH_MIDI_IN_SIGN, {'midi_in': received})

  # Scan device status and take actions
  device_manager.device_control()

  # Message delivery
  message_center.deliver_message()


# Main program
if __name__ == '__main__':
  try:
    # Initialize M5Stack CORE2
    M5.begin()
    Widgets.fillScreen(0x222222)

    # SD card object
    sdcard_obj = sdcard_class()
    sdcard_obj.setup()

    # Foundation class objects
    device_manager = device_manager_class()
    message_center = message_center_class()
    device_8encoder = device_8encoder_class(device_manager, message_center)

    # Generate a MIDI object with a Unit-MIDI synthesizer object
    midi_obj = midi_message_class(MIDIUnit(1, port=(13, 14)), sdcard_obj, message_center)
    midi_obj.setup()

    # MIDI-IN Player object
    midi_in_player_obj = midi_in_player_message_class(midi_obj, sdcard_obj, message_center)
    view_midi_in_player = view_midi_in_player_class(midi_in_player_obj, message_center)

    # Standard MIDI Player object
    smf_player_obj = smf_player_message_class(midi_obj, sdcard_obj, message_center)
    view_smf_player = view_smf_player_class(smf_player_obj, message_center)

    # Sequencer object
    sequencer_obj = sequencer_message_class(midi_obj, sdcard_obj, message_center)
    view_sequencer = view_sequencer_class(sequencer_obj, message_center)
    sequencer_obj.delegate_graphics(view_sequencer)
    sequencer_obj.setup_sequencer()
    sequencer_obj.message_center.phone_message(sequencer_obj, sequencer_obj.message_center.MSGID_SEQUENCER_SETUP, None)

    # Application object
    application = unit5c2_synth_application_class(message_center)

    application.message_center.phone_message(application, application.message_center.MSGID_APPLICATION_SETUP_PLAYER_SCREEN, None)
    application.message_center.flush_messages()
    application.message_center.phone_message(application, application.message_center.MSGID_SMF_PLAYER_MAKE_SMF_CATALOG)

    # Run the application
    while True:
      loop()

  except (Exception, KeyboardInterrupt) as e:
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print('please update to latest firmware')
