#####################################################################################################
# Standard MIDI file player and MIDI-IN player for M5Stack CORE2 with Unit-MIDI synthesizer.
#   Hardware:
#     M5Stack CORE2
#     Unit-MIDI synthesizer M5Stack (SAM2695)
#     8encoder unit for M5Stack (U153)
#     Micro SD card
#     MIDI-IN instruments (Optional)
#
#   Program: micropython for UIFlow2.0 (V2.1.4)
#
# Copyright (C) Shunsuke Ohira, 2024
#####################################################################################################
# Functions
#====================================================================================================
# Standard MIDI File PLAYER (8encoder slide switch ON)
#   Play a standard MIDI file in the SD-card.
#   MIDI channel settings for MIDI-IN PLAYER are changed by SMF in playing,
#   however the setting are restored when the play stops.
#
# MIDI-IN PLAYER (8encoder slide switch OFF)
#   Recieve MIDI data at MIDI-IN connector on Unit-MIDI,
#   and send the received raw data to Unit-MIDI synthesizer.
#====================================================================================================
# Operation
#====================================================================================================
# Standard MIDI File PLAYER (8encoder slide switch ON)
#   8encoder.CH1
#     VALUE : Master volume.
#     BUTTON: All notes off.
#
#   8encoder.CH2
#     VALUE : Select a MIDI file. (never works in playing a MIDI file.)
#     BUTTON: PLAY/STOP the MIDI file selected.z
#
#   8encoder.CH3
#     VALUE : SMF player key transpose.  (All notes off in advance of the transpose.)
#     BUTTON: PAUSE/RESTART the MIDI file playing.
#
#   8encoder.CH4
#     VALUE : SMF player volume.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH5
#     VALUE : Change SMF player tempo to play.
#     BUTTON: n/a
#
#   8encoder.CH6
#     VALUE : Change the parameter to edit. (SMF player reverb or chrus)
#     BUTTON: n/a
#
#   8encoder.CH7
#     VALUE : Change the parameter designated by CH6.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH8
#     VALUE : n/a
#     BUTTON: n/a
#
# MIDI-IN PLAYER (8encoder slide switch OFF)
#   8encoder.CH1
#     VALUE : Master volume.
#     BUTTON: All notes off.
#
#   8encoder.CH2
#     VALUE : Change MIDI channel of MIDI-IN play.
#     BUTTON: All notes off in the MIDI channel for MIDI-IN play.
#
#   8encoder.CH3
#     VALUE : Select a program.
#     BUTTON: n/a
#
#   8encoder.CH4
#     VALUE : n/a
#     BUTTON: n/a
#
#   8encoder.CH5
#     VALUE : n/a
#     BUTTON: n/a
#
#   8encoder.CH6
#     VALUE : Change the parameter to edit. (MIDI-IN player reverb or chrus)
#     BUTTON: n/a
#
#   8encoder.CH7
#     VALUE : Change the parameter designated by CH6.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH8
#     VALUE : n/a
#     BUTTON: n/a
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
#####################################################################################################

import os, sys, io
import M5
from M5 import *
from unit import CardKBUnit
from hardware import *
#from unit import SynthUnit
from unit import MIDIUnit
from unit import Encoder8Unit
import time
from hardware import sdcard
import _thread

# GUI
title_smf = None
title_smf_params = None
title_midi_in = None
title_midi_in_params = None
title_general = None

label_master_volume = None
label_smf_file = None
label_smf_fname = None
label_smf_fnum = None
label_smf_transp = None
label_smf_volume = None
label_smf_tempo = None
label_channel = None
label_program = None
label_program_name = None
label_reverb_level = None
label_chorus_level = None
label_smf_reverb_lv = None
label_smf_chorus_lv = None
label_midi_in = None

# I2C
i2c0 = None

# 8encoders unit
encoder8_0 = None
enc_button_ch = [False]*8
enc_slide_switch = None

ENC_MASTER_VOLUME = 1
EENC_SMF_MCH = 2
ENC_TRANSPORSE_PROGRAM = 3
ENC_VOLUME_na = 4
ENC_TEMPO_na = 5
ENC_PARAMETER = 6
ENC_CTRL1 = 7
ENC_CTRL2 = 8

enc_parameters = ['P','L','F','P','L','F','D']
enc_psmf_labels = [None]*7
enc_pmin_labels  = [None]*7
PARM_RVB_PROG  = 0
PARM_RVB_LEVEL = 1
PARM_RVB_FBACK = 2
PARM_CHR_PROG  = 3
PARM_CHR_LEVEL = 4
PARM_CHR_FBACK = 5
PARM_CHR_DELAY = 6
enc_parm = PARM_RVB_PROG
enc_parm_decade = False
enc_volume_decade = False
enc_mastervol_decade = False

# SYNTH Unit instance
synth_0 = None

# Parameter setting mode
parameter_value = 0

# MIDI-IN player
midi_in_settings = []
midi_in_ch = 0

# MIDI master volume
master_volume = 127

# SMF player
smf_file_path = '/sd//SYNTH/MIDIFILE/'
mf = None
playing_smf = False
playing_file = ''
smf_play_mode = 'PLAY'
smf_files = []
smf_file_selected = -1
smf_speed_factor = 1.0
smf_volume_delta = 0
smf_gmbank = 0
#smf_gmbank = 127
smf_transpose = 0
smf_reverb = [0,0,0]       # [program,level,feedback]
smf_chorus = [0,0,0,0]     # [program,level,feedback,delay]

# MIDI IN/OUT
midi_uart = False
midi_received = False


# Initialize SD Card device
def sdcard_init():
  global smf_file_path, mf

  print('SD CARD INIT.')
  smf_file_path = '/sd//SYNTH/MIDIFILE/'
  mf = None
  sdcard.SDCard(slot=2, width=1, sck=18, miso=38, mosi=23, cs=4, freq=1000000)
  print('SD CARD INIT done.')


# Initialize 8encoder unit
def encoder_init():
  global encoder8_0

  encoder8_0 = Encoder8Unit(i2c0, 0x41)
  for enc_ch in range(1, 9):
    encoder8_0.set_counter_value(enc_ch, 0)


# MIDI: Get a delta time in integer
def delta_time(btime):
#  print('delta_time=' + str(len(btime)))
  dt = 0
  for b in btime:
    dt = dt << 7
    dt = dt | int(b & 0x7f)

#  print('btime=' + str(dt))
  return dt


# MIDI EVENT: Note off
def midiev_note_off(ch, rb):
  notes_off(ch, rb)


# MIDI EVENT: Note on
def midiev_note_on(ch, rb):
  global smf_volume_delta
  
  if rb[1] == 0:
    notes_off(ch, [rb[0]])
  else:
    vol = int(rb[1]) + smf_volume_delta
    if vol <= 0:
      vol = 1
    elif vol > 127:
      vol = 127
    note(ch, int(rb[0]), vol)


# MIDI EVENT: Polyphonic key pressure
def midiev_polyphonic_key_pressure(ch, rb):
  pass


# MIDI EVENT: Control change
#   rb[0]: Control Number
#   rb[1]: Data
def midiev_control_change(ch, rb):
  global synth_0

  # Reverb
  if rb[0] == 0x91:
    # synth_0.set_reverb(channel, program0-7, level0-127, feedback0-255)
    synth_0.set_reverb(channel, 0, rb[1], 127)
  # Chorus
  elif rb[0] == 0x93:
    # synth_0.set_chorus(channel, program0-7, level0-127, feedback0-255, delay0-255)
    synth_0.set_chorus(channel, 0, rb[1], 127, 127)


# MIDI EVENT: Program change
def midiev_program_change(ch, rb):
  global synth_0, smf_gmbank
  synth_0.set_instrument(smf_gmbank, int(ch), int(rb[0]))


# MIDI EVENT: channel pressure
def midiev_channel_pressure(ch, rb):
  pass


# MIDI EVENT: Pitch bend
def midiev_pitch_bend(ch, rb):
  pass


# MIDI EVENT: SysEx F0
def midiev_sysex_f0(rb):
  pass


# MIDI EVENT: SysEx F7
def midiev_sysex_f7(rb):
  pass


# MIDI EVENT: SysEx FF (Meta data)
def midiev_meta_data(et, rb):
  pass


# Copy a byte list into an integer list
def to_int_list(blist):
  ilist = []
  for b in blist:
    ilist.append(int(b))
  return ilist


# Play a MIDI file class for SYNTH Unit
def play_midi(fname):
  global smf_file_path, mf, synth_0
  global playing_smf, playing_file, smf_play_mode, smf_speed_factor
  global label_smf_file

  def read_delta_time():
    dt = []
    rd = [0x80]
    while rd[0] & 0x80 == 0x80:
      rd = read_track_data(1, 0, 0)
      dt.append(rd[0])

    return dt


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
      dt = dt + to_int_list(rd)
    else:
      dt = to_int_list(rd)
#    print('RET=' + str(len(dt)))
    return dt


  # Now playing
  if playing_smf == True:
    print('Now playing...')
    return

  # Start SMF player
  print('MIDI PLAYER:' + fname)
  playing_smf = True
  smf_play_mode = 'PLAY'
  playing_file = fname
  label_smf_file.setText(str('PLAY:'))

  filename = smf_file_path + fname
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
#        if midi_format < 0 or midi_format > 2:
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
          if smf_play_mode == 'STOP':
            print('--->STOP PLAYER')
            f.close()
            playing_smf = False
            label_smf_file.setText(str('FILE:'))
            send_all_midi_in_settings()
            return

          # SMF player thread control: PAUSE
          if smf_play_mode == 'PAUSE':
            print('--->PAUSE MODE')
            synth_0.set_master_volume(0)
            label_smf_file.setText(str('PAUS:'))
            while True:
              print('WAITING:' + smf_play_mode)
              time.sleep(0.5)
              if smf_play_mode == 'PLAY':
                synth_0.set_master_volume(master_volume)
                label_smf_file.setText(str('PLAY:'))
                break
              if smf_play_mode == 'STOP':
                f.close()
                playing_smf = False
                synth_0.set_master_volume(master_volume)
                label_smf_file.setText(str('FILE:'))
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
          dtime = delta_time(dtbytes)
#          print('DELTA TIME=' + str(dtime))
          if dtime > 0:
#            time.sleep(dtime/200.0)
            time.sleep(dtime/200.0/time_unit/smf_speed_factor)

#          print('EVT=' + str(hex(ev)) + '/ CH=' + str(ch) + '/ RSR=' + str(rsr) + '/ DTM =' + str(dtime))

          # Note off
          if ev == 0x80:
            rb = read_track_data(2, rsr, rsr_bt)
            midiev_note_off(ch, rb)
          # Note on (Note off if volume equals zero)
          elif ev == 0x90:
            rb = read_track_data(2, rsr, rsr_bt)
            midiev_note_on(ch, rb)
          # Polyphonic key pressure
          elif ev == 0xa0:
            rb = read_track_data(2, rsr, rsr_bt)
            midiev_polyphonic_key_pressure(ch, rb)
          # Control change
          elif ev == 0xb0:
            rb = read_track_data(2, rsr, rsr_bt)
            midiev_control_change(ch, rb)
          # Program change
          elif ev == 0xc0:
            rb = read_track_data(1, rsr, rsr_bt)
            midiev_program_change(ch, rb)
          # channel pressure
          elif ev == 0xd0:
            rb = read_track_data(1, rsr, rsr_bt)
            midiev_channel_pressure(ch, rb)
          # Pitch bend
          elif ev == 0xe0:
            rb = read_track_data(2, rsr, rsr_bt)
            midiev_pitch_bend(ch, rb)
          # SysEx
          elif ev == 0xf0:
            print('Fx EVENT=' + str(ch))
            # F0
            if ch == 0:
              rb = read_track_data(1, rsr, rsr_bt)
              
              # Read data to send
              dlen = int(rb[0])
              rb = read_track_data(dlen, 0, 0)
              midiev_sysex_f0(rb)

            # F7
            elif ch == 7:
              rb = read_track_data(1, rsr, rsr_bt)
              
              # Read data to send
              dlen = int(rb[0])
              rb = read_track_data(dlen, 0, 0)
              midiev_sysex_f7(rb)

            # FF (Meta data)
            elif ch == 0x0f:
              # Event type
              rb = read_track_data(1, rsr, rsr_bt)
              et = rb[0]

              # Data length
              dtbytes = read_delta_time()
              dlength = delta_time(dtbytes)
              print('Data length bytes=' + str(len(dtbytes)) + '/ length=' + str(dlength))
              if dlength > 0:
                rb = read_track_data(dlength, 0, 0)
              else:
                rb = []

              print('FF event=' + str(hex(et)) + '/ data=' + str(len(rb)) + '/ data_len=' + str(data_len))
              midiev_meta_data(et, rb)
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
    print('FILE ERROR:' + e)
  finally:
      all_notes_off()
      send_all_midi_in_settings()

  playing_file = ''
  playing_smf = False
  smf_play_mode = 'STOP'


# Get a transposed tone name (C4, -1 --> C3)
def octaver(name, sft):
  print('octarver')
  oct = int(name[-1]) + sft
  if oct < 0:
    oct = 0
  elif oct > 7:
    oct = 7

  print('oct=' + str(oct))

  if len(name) == 2:
    return name[0] + str(oct)
  else:
    return name[0:2] + str(oct)


# Shift notes
def shitf_notes(notes_list, sft):
  sft_list = []
  for nt in notes_list:
    sft_list.append(nt + sft)
  return sft_list


# Note on a tone in a channel with vol volume.
def note(channel, tone, vol):
  global synth_0, smf_transpose
  synth_0.set_note_on(channel, tone + smf_transpose, vol)


# Note off all tones in a channel (tones: [60,62,...] etc)
def notes_off(channel, tones):
  global synth_0

  for t in tones:
    synth_0.set_note_off(channel, t + smf_transpose)


# All notes off in a channel.
def all_notes_off(channel = None):
  if channel is None:
    for ch in range(16):
      all_notes_off(ch)
  else:
    synth_0.set_all_notes_off(channel)


# Reverb
def control_reverb(ch, prog, level, fback):
  global synth_0
  synth_0.set_reverb(ch, prog, level, fback)


# Chorus
def control_chorus(ch, prog, level, fback, delay):
  global synth_0
  synth_0.set_chorus(ch, prog, level, fback, delay)


# Get GM prgram name
def get_gm_program_name(gmbabnk, program):
  with open(smf_file_path + 'GM0.TXT') as f:
    for mf in f:
      mf = mf.strip()
      if len(mf) > 0:
        if program == 0:
          f.close()
          return mf
      program = program - 1

  f.close()
  return 'UNKNOWN'


# Set and show volume delta value for SMF player
def set_smf_volume_delta(dlt):
  global smf_volume_delta, label_smf_volume

  smf_volume_delta = smf_volume_delta + dlt
  label_smf_volume.setText('{:0=+3d}'.format(smf_volume_delta))


# Set and show transpose value for SMF player
def set_smf_transpose(dlt):
  global smf_transpose, label_smf_transp

  smf_transpose = smf_transpose + dlt
  if smf_transpose == -13:
    smf_transpose = 0
  elif smf_transpose == 13:
    smf_transpose = 0
  label_smf_transp.setText('{:0=+3d}'.format(smf_transpose))


# Send a MIDI channel settings
def send_midi_in_settings(ch):
  synth_0.set_instrument(midi_in_settings[ch]['gmbank'], ch, midi_in_settings[ch]['program'])
  control_reverb(midi_in_ch, midi_in_settings[ch]['reverb'][0], midi_in_settings[ch]['reverb'][1], midi_in_settings[ch]['reverb'][2])
  control_chorus(ch, midi_in_settings[ch]['chorus'][0], midi_in_settings[ch]['chorus'][1], midi_in_settings[ch]['chorus'][2], midi_in_settings[ch]['chorus'][3])


# Send all MIDI channel settings
def send_all_midi_in_settings():
  for ch in range(16):
    send_midi_in_settings(ch)


# Set and show channel for MIDI-IN player
def set_midi_in_channel(dlt):
  global midi_in_ch, label_channel
  global midi_in_settings, enc_psmf_labels, enc_parm

  midi_in_ch = (midi_in_ch + dlt) % 16
  label_channel.setText('{:0>2d}'.format(midi_in_ch))

  set_midi_in_program(0)

  midi_in_reverb = midi_in_settings[midi_in_ch]['reverb']
  set_midi_in_reverb(midi_in_reverb[0], midi_in_reverb[1], midi_in_reverb[2])

  midi_in_chorus = midi_in_settings[midi_in_ch]['chorus']
  set_midi_in_chorus(midi_in_chorus[0], midi_in_chorus[1], midi_in_chorus[2], midi_in_chorus[3])

  # Reset the parameter to edit
  enc_parm = PARM_RVB_PROG
  label_reverb_level.setText('P{:03d}'.format(midi_in_settings[midi_in_ch]['reverb'][0]))
  label_chorus_level.setText('P{:03d}'.format(midi_in_settings[midi_in_ch]['chorus'][0]))
  label_reverb_level.setColor(0x00ffcc, 0x222222)
  label_chorus_level.setColor(0xffffff, 0x222222)


# Set and show program for MIDI-IN player
def set_midi_in_program(dlt):
  global synth_0, label_program, label_program_name
  global midi_in_settings, midi_in_ch

  midi_in_settings[midi_in_ch]['program'] = (midi_in_settings[midi_in_ch]['program'] + dlt) % 128
  midi_in_program = midi_in_settings[midi_in_ch]['program']
  label_program.setText('{:0>3d}'.format(midi_in_program))

  prg = get_gm_program_name(midi_in_settings[midi_in_ch]['gmbank'], midi_in_program)
  label_program_name.setText(prg)
  synth_0.set_instrument(midi_in_settings[midi_in_ch]['gmbank'], midi_in_ch, midi_in_program)


# Set and show master volume value
def set_synth_master_volume(dlt):
  global synth_0, master_volume, label_master_volume

  master_volume = master_volume + dlt
  if master_volume < 1:
    master_volume = 0
  elif master_volume > 127:
    master_volume = 127
  synth_0.set_master_volume(master_volume)
  label_master_volume.setText('{:0>3d}'.format(master_volume))


# Set reverb for MIDI-IN player
def set_midi_in_reverb(prog=None, level=None, fback=None):
  global midi_in_ch
  global midi_in_settings, midi_in_ch

  disp = None
  if not prog is None:
    midi_in_settings[midi_in_ch]['reverb'][0] = prog
    disp = prog

  if not level is None:
    midi_in_settings[midi_in_ch]['reverb'][1] = level
    disp = level
    
  if not fback is None:
    midi_in_settings[midi_in_ch]['reverb'][2] = fback
    disp = fback

  midi_in_reverb = midi_in_settings[midi_in_ch]['reverb']
  if not disp is None:
    control_reverb(midi_in_ch, midi_in_reverb[0], midi_in_reverb[1], midi_in_reverb[2])


# Set reverb for SMF player
def set_smf_reverb(prog=None, level=None, fback=None):
  global label_smf_reverb_lv, smf_reverb, midi_in_ch

  disp = None
  if not prog is None:
    smf_reverb[0] = prog
    disp = prog

  if not level is None:
    smf_reverb[1] = level
    disp = level
    
  if not fback is None:
    smf_reverb[2] = fback
    disp = fback

  if not disp is None:
    for ch in range(16):
      if ch != midi_in_ch:
        control_reverb(ch, smf_reverb[0], smf_reverb[1], smf_reverb[2])


# Set chorus for MIDI-IN player
def set_midi_in_chorus(prog=None, level=None, fback=None, delay=None):
  global midi_in_ch
  global midi_in_settings

  send = False
  if not prog is None:
    midi_in_settings[midi_in_ch]['chorus'][0] = prog
    send = True

  if not level is None:
    midi_in_settings[midi_in_ch]['chorus'][1] = level
    send = True
    
  if not fback is None:
    midi_in_settings[midi_in_ch]['chorus'][2] = fback
    send = True
    
  if not delay is None:
    midi_in_settings[midi_in_ch]['chorus'][3] = delay
    send = True

  midi_in_chorus = midi_in_settings[midi_in_ch]['chorus']
  if send:
    control_chorus(midi_in_ch, midi_in_chorus[0], midi_in_chorus[1], midi_in_chorus[2], midi_in_chorus[3])


# Set chorus for SMF player
def set_smf_chorus(prog=None, level=None, fback=None, delay=None):
  global label_smf_chorus_lv, smf_chorus, midi_in_ch

  send = False
  if not prog is None:
    smf_chorus[0] = prog
    send = True

  if not level is None:
    smf_chorus[1] = level
    send = True
    
  if not fback is None:
    smf_chorus[2] = fback
    send = True
    
  if not delay is None:
    smf_chorus[3] = delay
    send = True

  if send:
    for ch in range(16):
      if ch != midi_in_ch:
        control_chorus(ch, smf_chorus[0], smf_chorus[1], smf_chorus[2], smf_chorus[3])


# MIDI IN
def midi_in():
  global midi_uart, midi_received, label_midi_in

  midi_rcv_bytes = midi_uart.any()
  if midi_rcv_bytes > 0:
    midi_in_data = midi_uart.read()
    print('MIDI IN:', midi_in_data)
    midi_uart.write(midi_in_data)
    if midi_received == False:
      label_midi_in.setVisible(True)
      midi_received = True

  elif midi_received == True:
    label_midi_in.setVisible(False)
    midi_received = False


# Make the midi file catalog
def midi_file_catalog():
  global label_smf_fname, smf_file_selected
  with open(smf_file_path + 'LIST.TXT') as f:
    for mf in f:
      mf = mf.strip()
      if len(mf) > 0:
        cat = mf.split(',')
        if len(cat) == 3:
          smf_files.append(cat)

  f.close()
  if len(smf_files) > 0:
    smf_file_selected = 0
    label_smf_fname.setText(smf_files[0][0])
    for i in range(len(smf_files)):
      smf_files[i][2] = float(smf_files[i][2])


# Read 8encoder values
def encoder_read():
  global encoder8_0, enc_button_ch, enc_slide_switch, enc_parm, enc_parm_decade, enc_volume_decade, enc_mastervol_decade
  global midi_in_ch, playing_smf, smf_speed_factor, smf_file_selected, smf_files, smf_play_mode
  global midi_in_settings

  # Slide switch
  slide_switch_change = False
  slide_switch = encoder8_0.get_switch_status()
  if enc_slide_switch is None:
    enc_slide_switch = slide_switch
    slide_switch_change = True
  elif slide_switch != enc_slide_switch:
    enc_slide_switch = slide_switch
    slide_switch_change = True
  
  if slide_switch_change:
    title_smf_params.setColor(0xff4040 if enc_slide_switch else 0xff8080, 0x555555 if enc_slide_switch else 0x222222)
    title_midi_in_params.setColor(0xff8080 if enc_slide_switch else 0xff4040, 0x222222 if enc_slide_switch else 0x555555)

  # Scan encoders
  for enc_ch in range(1,9):
    enc_count = encoder8_0.get_counter_value(enc_ch)
    enc_button = not encoder8_0.get_button_status(enc_ch)

    # Get an edge trigger of the encoder button
    if enc_button == True:
      if enc_button_ch[enc_ch-1] == True:
        enc_button = False
      else:
        enc_button_ch[enc_ch-1] = True
        encoder8_0.set_led_rgb(enc_ch, 0x40ff40)
    else:
      if enc_button_ch[enc_ch-1] == True:
        encoder8_0.set_led_rgb(enc_ch, 0x000000)
        enc_button_ch[enc_ch-1] = False

    # Encoder rotations
    if enc_count >= 2:
      delta = 1
    elif  enc_count <= -2:
      delta = -1
    else:
      delta = 0

    # Reset the encoder counter
    if delta != 0:
      encoder8_0.set_counter_value(enc_ch, 0)

    # Master volume
    if   enc_ch == ENC_MASTER_VOLUME:
      # Decade value button (toggle)
      if enc_button and enc_button_ch[enc_ch-1]:
        enc_mastervol_decade = not enc_mastervol_decade

      if enc_mastervol_decade:
        encoder8_0.set_led_rgb(enc_ch, 0xffa000)

      # Change master volume
      if delta != 0: 
          set_synth_master_volume(delta * (10 if enc_mastervol_decade else 1))

      # All notes off
      if enc_button:
        all_notes_off()

    # SMF file / MIDI channel
    elif enc_ch == EENC_SMF_MCH:
      # Slide switch off: midi-in mode
      if slide_switch == False:
        # Select MIDI channel to MIDI-IN play
        if delta != 0:
          set_midi_in_channel(delta)

        # All notes off of MIDI-IN player channel
        if enc_button == True:
          all_notes_off(midi_in_ch)

      # Slide switch on: SMF player mode
      else:
        # Select a MIDI file
        if playing_smf == False:
          if smf_file_selected >= 0:
            if delta == -1:
              smf_file_selected = smf_file_selected - 1
              if smf_file_selected == -1:
                smf_file_selected = len(smf_files) - 1
            elif delta == 1:
              smf_file_selected = smf_file_selected + 1
              if smf_file_selected == len(smf_files):
                smf_file_selected = 0

            if delta != 0:
              label_smf_fnum.setText('{:03d}'.format(smf_file_selected))
              label_smf_fname.setText(smf_files[smf_file_selected][0])

        # Play the selected MIDI file or stop playing
        if enc_button == True:
          if playing_smf == True:
            print('STOP MIDI PLAYER')
            smf_play_mode = 'STOP'
          else:
            print('REPLAY MIDI PLAYER')
            if smf_file_selected >= 0:
              smf_speed_factor = smf_files[smf_file_selected][2]
              label_smf_tempo.setText('x{:3.1f}'.format(smf_speed_factor))
              _thread.start_new_thread(play_midi, (smf_files[smf_file_selected][1],))

    # Transpose / Program
    elif enc_ch == ENC_TRANSPORSE_PROGRAM:
      # Slide switch off: midi-in mode
      if slide_switch == False:
        # Select program
        if delta != 0:
          set_midi_in_program(delta)

        # All notes off of MIDI-IN player channel
        if enc_button == True:
          all_notes_off(midi_in_ch)

      # Slide switch on: SMF player mode
      else:
        if delta != 0:
          all_notes_off()
          set_smf_transpose(delta)

        # Pause/Restart SMF player in playing
        if enc_button == True:
          if playing_smf == True:
            if smf_play_mode == 'PLAY':
              print('PAUSE MIDI PLAYER')
              smf_play_mode = 'PAUSE'
            else:
              print('CONTINUE MIDI PLAYER')
              smf_play_mode = 'PLAY'
          else:
            print('MIDI PLAYER NOT PLAYING')

    # MIDI Channel volume / Button to pause or Restart SMF player, to all notes off of MIDI-IN play
    elif enc_ch == ENC_VOLUME_na:
      # Decade value button (toggle)
      if enc_button and enc_button_ch[enc_ch-1]:
        enc_volume_decade = not enc_volume_decade

      if enc_volume_decade:
        encoder8_0.set_led_rgb(enc_ch, 0xffa000)

      # Slide switch off: midi-in mode
      if slide_switch == False:
        pass

      # Slide switch on: SMF player mode
      else:
        if delta != 0:
          set_smf_volume_delta(delta * (10 if enc_volume_decade else 1))

    # SMF player tempo / MIDI-IN play MIDI channel
    elif enc_ch == ENC_TEMPO_na:
      # Slide switch off: midi-in mode
      if slide_switch == False:
        pass

      # Slide switch on: SMF player mode
      else:
        # Change MIDI play speed
        if delta == -1:
          smf_speed_factor = smf_speed_factor - 0.1
          if smf_speed_factor < 0.1:
            smf_speed_factor = 0.1
        elif delta == 1:
          smf_speed_factor = smf_speed_factor + 0.1
          if smf_speed_factor > 5:
            smf_speed_factor = 5

        if delta != 0:
          label_smf_tempo.setText('x{:3.1f}'.format(smf_speed_factor))

    # Select a parameter
    elif enc_ch == ENC_PARAMETER:
      if delta != 0 or slide_switch_change:
        # Change the target parameter to edit with CTRL1
        parms = len(enc_parameters)
        enc_parm = enc_parm + delta
        if enc_parm < 0:
          enc_parm = parms -1
        elif enc_parm >= parms:
          enc_parm = 0

        # Make the color of the parameter labels in default color
        for p in range(parms):
          enc_pmin_labels[p].setColor(0xffffff, 0x222222)
          enc_psmf_labels[p].setColor(0xffffff, 0x222222)

        # Slide switch off: midi-in mode
        if slide_switch == False:
          # Display the label
          if   enc_parm == PARM_RVB_PROG:
            disp = midi_in_settings[midi_in_ch]['reverb'][0]
          elif enc_parm == PARM_RVB_LEVEL:
            disp = midi_in_settings[midi_in_ch]['reverb'][1]
          elif enc_parm == PARM_RVB_FBACK:
            disp = midi_in_settings[midi_in_ch]['reverb'][2]
          elif enc_parm == PARM_CHR_PROG:
            disp = midi_in_settings[midi_in_ch]['chorus'][0]
          elif enc_parm == PARM_CHR_LEVEL:
            disp = midi_in_settings[midi_in_ch]['chorus'][1]
          elif enc_parm == PARM_CHR_FBACK:
            disp = midi_in_settings[midi_in_ch]['chorus'][2]
          elif enc_parm == PARM_CHR_DELAY:
            disp = midi_in_settings[midi_in_ch]['chorus'][3]

          enc_pmin_labels[enc_parm].setColor(0x00ffcc, 0x222222)
          enc_pmin_labels[enc_parm].setText(enc_parameters[enc_parm] + '{:03d}'.format(disp))

        # Slide switch on: SMF player mode
        else:
          # Display the label
          if   enc_parm == PARM_RVB_PROG:
            disp = smf_reverb[0]
          elif enc_parm == PARM_RVB_LEVEL:
            disp = smf_reverb[1]
          elif enc_parm == PARM_RVB_FBACK:
            disp = smf_reverb[2]
          elif enc_parm == PARM_CHR_PROG:
            disp = smf_chorus[0]
          elif enc_parm == PARM_CHR_LEVEL:
            disp = smf_chorus[1]
          elif enc_parm == PARM_CHR_FBACK:
            disp = smf_chorus[2]
          elif enc_parm == PARM_CHR_DELAY:
            disp = smf_chorus[3]

          enc_psmf_labels[enc_parm].setColor(0x00ffcc, 0x222222)
          enc_psmf_labels[enc_parm].setText(enc_parameters[enc_parm] + '{:03d}'.format(disp))

    # Parameter-CTRL1
    elif enc_ch == ENC_CTRL1:
      # Decade value button (toggle)
      if enc_button and enc_button_ch[enc_ch-1]:
        enc_parm_decade = not enc_parm_decade

      if enc_parm_decade:
        encoder8_0.set_led_rgb(enc_ch, 0xffa000)

      if delta != 0 or slide_switch_change:
        send_to = 0

        # Slide switch off: midi-in mode
        if slide_switch == False:
          if   enc_parm == PARM_RVB_PROG:
            midi_in_settings[midi_in_ch]['reverb'][0] = midi_in_settings[midi_in_ch]['reverb'][0] + delta
            if midi_in_settings[midi_in_ch]['reverb'][0] < 0:
              midi_in_settings[midi_in_ch]['reverb'][0] = 7
            elif midi_in_settings[midi_in_ch]['reverb'][0] > 7:
              midi_in_settings[midi_in_ch]['reverb'][0] = 0
            disp = midi_in_settings[midi_in_ch]['reverb'][0]
            send_to = 1

          elif enc_parm == PARM_RVB_LEVEL:
            midi_in_settings[midi_in_ch]['reverb'][1] = midi_in_settings[midi_in_ch]['reverb'][1] + delta * (10 if enc_parm_decade else 1)
            if midi_in_settings[midi_in_ch]['reverb'][1] < 0:
              midi_in_settings[midi_in_ch]['reverb'][1] = 0
            elif midi_in_settings[midi_in_ch]['reverb'][1] > 255:
              midi_in_settings[midi_in_ch]['reverb'][1] = 255
            disp = midi_in_settings[midi_in_ch]['reverb'][1]
            send_to = 1

          elif enc_parm == PARM_RVB_FBACK:
            midi_in_settings[midi_in_ch]['reverb'][2] = midi_in_settings[midi_in_ch]['reverb'][2] + delta * (10 if enc_parm_decade else 1)
            if midi_in_settings[midi_in_ch]['reverb'][2] < 0:
              midi_in_settings[midi_in_ch]['reverb'][2] = 0
            elif midi_in_settings[midi_in_ch]['reverb'][2] > 255:
              midi_in_settings[midi_in_ch]['reverb'][2] = 255
            disp = midi_in_settings[midi_in_ch]['reverb'][2]
            send_to = 1

          elif enc_parm == PARM_CHR_PROG:
            midi_in_settings[midi_in_ch]['chorus'][0] = midi_in_settings[midi_in_ch]['chorus'][0] + delta
            if midi_in_settings[midi_in_ch]['chorus'][0] < 0:
              midi_in_settings[midi_in_ch]['chorus'][0] = 7
            elif midi_in_settings[midi_in_ch]['chorus'][0] > 7:
              midi_in_settings[midi_in_ch]['chorus'][0] = 0
            disp = midi_in_settings[midi_in_ch]['chorus'][0]
            send_to = 2

          elif enc_parm == PARM_CHR_LEVEL:
            midi_in_settings[midi_in_ch]['chorus'][1] = midi_in_settings[midi_in_ch]['chorus'][1] + delta * (10 if enc_parm_decade else 1)
            if midi_in_settings[midi_in_ch]['chorus'][1] < 0:
              midi_in_settings[midi_in_ch]['chorus'][1] = 0
            elif midi_in_settings[midi_in_ch]['chorus'][1] > 255:
              midi_in_settings[midi_in_ch]['chorus'][1] = 255
            disp = midi_in_settings[midi_in_ch]['chorus'][1]
            send_to = 2

          elif enc_parm == PARM_CHR_FBACK:
            midi_in_settings[midi_in_ch]['chorus'][2] = midi_in_settings[midi_in_ch]['chorus'][2] + delta * (10 if enc_parm_decade else 1)
            if midi_in_settings[midi_in_ch]['chorus'][2] < 0:
              midi_in_settings[midi_in_ch]['chorus'][2] = 0
            elif midi_in_settings[midi_in_ch]['chorus'][2] > 255:
              midi_in_settings[midi_in_ch]['chorus'][2] = 255
            disp = midi_in_settings[midi_in_ch]['chorus'][2]
            send_to = 2

          elif enc_parm == PARM_CHR_DELAY:
            midi_in_settings[midi_in_ch]['chorus'][3] = midi_in_settings[midi_in_ch]['chorus'][3] + delta * (10 if enc_parm_decade else 1)
            if midi_in_settings[midi_in_ch]['chorus'][3] < 0:
              midi_in_settings[midi_in_ch]['chorus'][3] = 0
            elif midi_in_settings[midi_in_ch]['chorus'][3] > 255:
              midi_in_settings[midi_in_ch]['chorus'][3] = 255
            disp = midi_in_settings[midi_in_ch]['chorus'][3]
            send_to = 2

          # Display the label
          enc_pmin_labels[enc_parm].setText(enc_parameters[enc_parm] + '{:03d}'.format(disp))

          # Send MIDI message
          if delta != 0:
            if send_to == 1:
              set_midi_in_reverb(midi_in_settings[midi_in_ch]['reverb'][0], midi_in_settings[midi_in_ch]['reverb'][1], midi_in_settings[midi_in_ch]['reverb'][2])
            elif send_to == 2:
              set_midi_in_chorus(midi_in_settings[midi_in_ch]['chorus'][0], midi_in_settings[midi_in_ch]['chorus'][1], midi_in_settings[midi_in_ch]['chorus'][2], midi_in_settings[midi_in_ch]['chorus'][3])

        # Slide switch on: SMF player mode
        else:
          if   enc_parm == PARM_RVB_PROG:
            smf_reverb[0] = smf_reverb[0] + delta
            if smf_reverb[0] < 0:
              smf_reverb[0] = 7
            elif smf_reverb[0] > 7:
              smf_reverb[0] = 0
            disp = smf_reverb[0]
            send_to = 1

          elif enc_parm == PARM_RVB_LEVEL:
            smf_reverb[1] = smf_reverb[1] + delta * (10 if enc_parm_decade else 1)
            disp = smf_reverb[1]

          elif enc_parm == PARM_RVB_FBACK:
            smf_reverb[2] = smf_reverb[2] + delta * (10 if enc_parm_decade else 1)
            if smf_reverb[2] < 0:
              smf_reverb[2] = 0
            elif smf_reverb[2] > 255:
              smf_reverb[2] = 255
            disp = smf_reverb[2]
            send_to = 1

          elif enc_parm == PARM_CHR_PROG:
            smf_chorus[0] = smf_chorus[0] + delta
            if smf_chorus[0] < 0:
              smf_chorus[0] = 7
            elif smf_chorus[0] > 7:
              smf_chorus[0] = 0
            disp = smf_chorus[0]
            send_to = 2

          elif enc_parm == PARM_CHR_LEVEL:
            smf_chorus[1] = smf_chorus[1] + delta * (10 if enc_parm_decade else 1)
            if smf_chorus[1] < 0:
              smf_chorus[1] = 0
            elif smf_chorus[1] > 255:
              smf_chorus[1] = 255
            disp = smf_chorus[1]
            send_to = 2

          elif enc_parm == PARM_CHR_FBACK:
            smf_chorus[2] = smf_chorus[2] + delta * (10 if enc_parm_decade else 1)
            if smf_chorus[2] < 0:
              smf_chorus[2] = 0
            elif smf_chorus[2] > 255:
              smf_chorus[2] = 255
            disp = smf_chorus[2]
            send_to = 2

          elif enc_parm == PARM_CHR_DELAY:
            smf_chorus[3] = smf_chorus[3] + delta * (10 if enc_parm_decade else 1)
            if smf_chorus[3] < 0:
              smf_chorus[3] = 0
            elif smf_chorus[3] > 255:
              smf_chorus[3] = 255
            disp = smf_chorus[3]
            send_to = 2

          # Display the label
          enc_psmf_labels[enc_parm].setText(enc_parameters[enc_parm] + '{:03d}'.format(disp))

          # Send MIDI message
          if delta != 0:
            if send_to == 1:
              set_smf_reverb(smf_reverb[0], smf_reverb[1], smf_reverb[2])
            elif send_to == 2:
              set_smf_chorus(smf_chorus[0], smf_chorus[1], smf_chorus[2], smf_chorus[3])

    # Parameter-CTRL2
    elif enc_ch == ENC_CTRL2:
      # Slide switch off: midi-in mode
      if slide_switch == False:
        pass

      # Slide switch on: SMF player mode
      else:
        pass


def setup():
  global title_smf, title_smf_params, title_midi_in, title_midi_in_params, title_general
  global label_channel, i2c0, kbstr, label_smf_fnum, label_smf_tempo
  global label_smf_file, label_smf_fname, label_smf_transp, label_smf_volume, label_program, label_program_name, label_master_volume
  global label_reverb_level, label_chorus_level, label_smf_reverb_lv, label_smf_chorus_lv
  global enc_ch_val, enc_psmf_labels, enc_pmin_labels
  global midi_uart, label_midi_in
  global midi_in_settings, midi_in_ch

  M5.begin()
  Widgets.fillScreen(0x222222)
  sdcard_init()

  # Titles
  title_smf = Widgets.Label("title_smf", 0, 0, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
  title_smf_params = Widgets.Label("title_smf_params", 0, 20, 1.0, 0xff8080, 0x222222, Widgets.FONTS.DejaVu18)
  title_midi_in = Widgets.Label("title_midi_in", 0, 100, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
  title_midi_in_params = Widgets.Label("title_midi_in_params", 0, 120, 1.0, 0xff8080, 0x222222, Widgets.FONTS.DejaVu18)
  title_general = Widgets.Label("title_general", 0, 200, 1.0, 0xff8080, 0x222222, Widgets.FONTS.DejaVu18)

  # GUI for SMF player
  label_smf_fnum = Widgets.Label("label_smf_fnum", 0, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_smf_transp = Widgets.Label("label_smf_transp", 46, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_smf_volume = Widgets.Label("label_smf_volume", 94, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_smf_tempo = Widgets.Label("label_smf_tempo", 150, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_smf_reverb_lv = Widgets.Label("label_smf_reverb_lv", 202, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_smf_chorus_lv = Widgets.Label("label_smf_chorus_lv", 262, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_smf_file = Widgets.Label("label_smf_file", 0, 60, 1.0, 0x00ffcc, 0x222222, Widgets.FONTS.DejaVu18)
  label_smf_fname = Widgets.Label("label_smf_fname", 60, 60, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  # GUI for MIDI-IN play
  label_channel = Widgets.Label("label_channel", 0, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_program = Widgets.Label("label_program", 46, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_reverb_level = Widgets.Label("label_reverb_level", 202, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_chorus_level = Widgets.Label("label_chorus_level", 262, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  label_program_name = Widgets.Label("label_program_name", 0, 160, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  # MIDI IN
  label_midi_in = Widgets.Label("label_midi_in", 200, 100, 1.0, 0x00ffcc, 0x222222, Widgets.FONTS.DejaVu18)

  # Master Volume
  label_master_volume = Widgets.Label("label_master_volume", 0, 220, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  # Labels to edit in the parameter selector
  enc_psmf_labels = [label_smf_reverb_lv,label_smf_reverb_lv,label_smf_reverb_lv,label_smf_chorus_lv,label_smf_chorus_lv,label_smf_chorus_lv,label_smf_chorus_lv]
  enc_pmin_labels = [label_reverb_level,label_reverb_level,label_reverb_level,label_chorus_level,label_chorus_level,label_chorus_level,label_chorus_level]

  # I2C
  i2c0 = I2C(0, scl=Pin(33), sda=Pin(32), freq=100000)
  i2c_list = i2c0.scan()
  print('I2C:', i2c_list)
  encoder_init()

  # SYNTH settings
  for ch in range(16):
    midi_in_settings.append({'program':0, 'gmbank':0, 'reverb':[0,0,0], 'chorus':[0,0,0,0]})

  # SYNTH unit
  global synth_0
  synth_0 = MIDIUnit(1, port=(13, 14))
  midi_uart = synth_0._uart

  synth_0.set_instrument(midi_in_settings[midi_in_ch]['gmbank'], midi_in_ch, midi_in_settings[midi_in_ch]['program'])
  synth_0.set_master_volume(master_volume)
  for ch in range(16):
    synth_0.set_reverb(ch, 0, 0, 0)
    synth_0.set_chorus(ch, 0, 0, 0, 0)

  # Initialize GUI display
  title_smf.setText('SMF PLAYER')
  title_smf_params.setText('NO. TRN VOL TEMP REVB CHOR')
  title_midi_in.setText('MIDI-IN PLAYER')
  title_midi_in_params.setText('CH. PRG  n/a   n/a   REVB CHOR')
  title_general.setText('VOL')

  label_midi_in.setText('M-IN')
  label_midi_in.setVisible(False)

  set_synth_master_volume(0)

  label_smf_file.setText('FILE:')
  label_smf_file.setVisible(True)
  label_smf_fname.setText('none')
  label_smf_fname.setVisible(True)
  label_smf_fnum.setText('{:03d}'.format(0))

  set_smf_transpose(0)
  set_smf_volume_delta(0)
  label_smf_tempo.setText('x{:3.1f}'.format(smf_speed_factor))
  set_smf_reverb()
  set_smf_chorus()

  set_midi_in_channel(0)
  set_midi_in_program(0)
  set_midi_in_reverb()
  set_midi_in_chorus()
  label_smf_reverb_lv.setText('P{:03d}'.format(smf_reverb[0]))
  label_smf_chorus_lv.setText('P{:03d}'.format(smf_chorus[0]))
  label_reverb_level.setText('P{:03d}'.format(midi_in_settings[midi_in_ch]['reverb'][0]))
  label_chorus_level.setText('P{:03d}'.format(midi_in_settings[midi_in_ch]['chorus'][0]))

  # Initialize 8encoder
  for ch in range(1,9):
    encoder8_0.set_led_rgb(ch, 0x000000)

  # Prepare SYNTH data and all notes off
  all_notes_off()


def loop():
  global i2c0
  M5.update()
  midi_in()
  encoder_read()


if __name__ == '__main__':
  try:
    setup()
    midi_file_catalog()

#    _thread.start_new_thread(play_midi, ('DANCINGQ.MID',))
    while True:
      loop()
      time.sleep(0.1)

  except (Exception, KeyboardInterrupt) as e:
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")