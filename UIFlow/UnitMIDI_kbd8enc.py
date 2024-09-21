#####################################################################################################
# MIDI Player and Keyboard Player for M5Stack CORE2 with Unit-MIDI synthesizer.
#   Hardware:
#     M5Stack CORE2
#     Unit-MIDI synthesizer M5Stack (SAM2695)
#     CardKB v1.1 for M5Stack
#     8encoder unit for M5Stack (U153)
#     Micro SD card
#     MIDI-IN instruments (Optional)
#
#   Program: micropython for UIFlow2.0 (V2.1.4)
#
# Copyright (C) Shunsuke Ohira, 2024
#####################################################################################################
# Operation
#====================================================================================================
# MIDI PLAYER (8encoder slide switch ON)
#   8encoder.CH1
#     VALUE : Master volume.
#     BUTTON: All notes off.
#
#   8encoder.CH2
#     VALUE : Select a MIDI file. (never works in playing a MIDI file.)
#     BUTTON: PLAY/STOP the MIDI file selected.z
#
#   8encoder.CH3
#     VALUE : MIDI player key transpose.  (All notes off in advance of the transpose.)
#     BUTTON: PAUSE/RESTART the MIDI file playing.
#
#   8encoder.CH4
#     VALUE : MIDI player volume.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH5
#     VALUE : Change MIDI player tempo to play.
#     BUTTON: Toggle sustain pedal effect.
#
#   8encoder.CH6
#     VALUE : Change the parameter to edit. (MIDI player reverb or chrus)
#     BUTTON: n/a
#
#   8encoder.CH7
#     VALUE : Change the parameter designated by CH6.
#     BUTTON: n/a
#
#   8encoder.CH8
#     VALUE : n/a
#     BUTTON: n/a
#
# MIDI IN
#   Recieve MIDI-IN data on Unit-MIDI and send the raw data to Unit-MIDI synthesizer.
#
# KEYBOARD PLAYER (8encoder slide switch OFF)
#   8encoder.CH1
#     VALUE : Master volume.
#     BUTTON: All notes off.
#
#   8encoder.CH2
#     VALUE : Select a program.
#     BUTTON: All notes off in the MIDI channel for keyboard play.
#
#   8encoder.CH3
#     VALUE : Keyboard player key transpose.
#     BUTTON: n/a
#
#   8encoder.CH4
#     VALUE : Keyboard player volume.
#     BUTTON: Change value by decade or 1. (toggle)
#
#   8encoder.CH5
#     VALUE : Change MIDI channel of keyboard play.
#     BUTTON: Toggle sustain pedal effect.
#
#   8encoder.CH6
#     VALUE : Change the parameter to edit. (Keyboard player reverb or chrus)
#     BUTTON: n/a
#
#   8encoder.CH7
#     VALUE : Change the parameter designated by CH6.
#     BUTTON: n/a
#
#   8encoder.CH8
#     VALUE : n/a
#     BUTTON: n/a
#
#   Card KB.fn=OFF/shift=OFF:
#     [c][d][e][f][g][a][b]   : Play a major code.
#
#   Card KB.fn=OFF/shift=ON:
#     [C][D][E][F][G][A][B]   : Play a minor code.
#
#   Card KB.fn=ON /shift=OFF:
#      [a][s]   [f][g][h]     : Play a tone.
#     [z][x][c][v][b][n][m][,]: Play a tone.
#
#     -- NOTE: Other keys ---> All notes off event will be sent to the keyboard channel.
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
title_midi = None
title_midi_params = None
title_keyboard = None
title_kbd_params = None
title_general = None

label_master_volume = None
label_keycode = None
label_parameter = None
label_file = None
label_midi_file = None
label_midi_fnum = None
label_midi_transp = None
label_midi_volume = None
label_midi_tempo = None
label_transp  = None
label_channel = None
label_volume = None
label_program = None
label_program_name = None
label_sustain = None
label_reverb_level = None
label_chorus_level = None
label_reverb_lvmidi = None
label_chorus_lvmidi = None
label_midi_in = None

# I2C
i2c0 = None

# Keyboard Unit instance and key string typed
cardkb_0 = None
kbstr = None
kbcmd = ''

# 8encoders unit
encoder8_0 = None
enc_button_ch = [False]*8
enc_slide_switch = None

ENC_MASTER_VOLUME = 1
ENC_MUSIC_PROGRAM = 2
ENC_TRANSPORSE = 3
ENC_VOLUME = 4
ENC_TEMPO_MIDI_CH = 5
ENC_PARAMETER = 6
ENC_CTRL1 = 7
ENC_CTRL2 = 8

enc_parameters = ['P','L','F','P','L','F','D']
enc_pmidi_labels = [None]*7
enc_pkbd_labels  = [None]*7
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
#midi_0 = None

# Playing tones in each MIDI CH ([0], [1])
tone_on = [[]]*16

# Key code to tone number
tone_map = {}
# Tone name in alphabet to tone number (C4-->60 etc)
name_map = {}
# Code name to tones composing
code_map = { 'c': ['c4', 'e4', 'g4'], 'C': ['c4', 'd#4', 'g4'],
             'd': ['d4', 'f4', 'a4'], 'D': ['d4', 'f#4', 'a4'],
             'e': ['e4', 'g#4', 'b4'], 'E': ['e4', 'g4', 'b4'],
             'f': ['f4', 'a4', 'c4'], 'F': ['f4', 'g#4', 'c4'],
             'g': ['g4', 'b4', 'd5'], 'G': ['g4', 'a#4', 'd5'],
             'a': ['a4', 'c5', 'e5'], 'A': ['a4', 'c#5', 'e5'],
             'b': ['b3', 'd#4', 'f#4'], 'B': ['b3', 'd4', 'f#4']
            }
# Parameter setting mode
parameter_value = 0

# Keyboard player
kbd_tone_ch = 15
kbd_volume = 127
kbd_program = 0
kbd_gmbabnk = 0
kbd_transpose = 0
sustain = True
kbd_reverb  = [0,0,0]        # [program,level,feedback]
kbd_chorus  = [0,0,0,0]      # [program,level,feedback,delay]
midi_reverb = [0,0,0]       # [program,level,feedback]
midi_chorus = [0,0,0,0]     # [program,level,feedback,delay]

# MIDI master volume
master_volume = 64

# MIDI player
midi_file_path = '/sd//SYNTH/MIDIFILE/'
mf = None
playing_midi = False
playing_file = ''
midi_play_mode = 'PLAY'
midi_files = []
midi_file_selected = -1
speed_factor = 1.0
midi_volume_delta = 0
midi_gmbank = 0
#midi_gmbank = 127
midi_transpose = 0

# MIDI IN/OUT
midi_uart = False
midi_received = False


# Initialize SD Card device
def sdcard_init():
  global midi_file_path, mf

  print('SD CARD INIT.')
  midi_file_path = '/sd//SYNTH/MIDIFILE/'
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
  global midi_volume_delta
  
  if rb[1] == 0:
    notes_off(ch, [rb[0]])
  else:
    vol = int(rb[1]) + midi_volume_delta
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
  global synth_0, midi_gmbank
  synth_0.set_instrument(midi_gmbank, int(ch), int(rb[0]))


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
  global midi_file_path, mf, synth_0
  global playing_midi, playing_file, midi_play_mode, speed_factor
  global label_file

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
  if playing_midi == True:
    print('Now playing...')
    return

  # Start MIDI player
  print('MIDI PLAYER:' + fname)
  playing_midi = True
  midi_play_mode = 'PLAY'
  playing_file = fname
  label_file.setText(str('PLAY:'))

  filename = midi_file_path + fname
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
          # MIDI player thread control: STOP
          if midi_play_mode == 'STOP':
            print('--->STOP PLAYER')
            f.close()
            playing_midi = False
            label_file.setText(str('FILE:'))
            return

          # MIDI player thread control: PAUSE
          if midi_play_mode == 'PAUSE':
            print('--->PAUSE MODE')
            synth_0.set_master_volume(0)
            label_file.setText(str('PAUS:'))
            while True:
              print('WAITING:' + midi_play_mode)
              time.sleep(0.5)
              if midi_play_mode == 'PLAY':
                synth_0.set_master_volume(master_volume)
                label_file.setText(str('PLAY:'))
                break
              if midi_play_mode == 'STOP':
                f.close()
                playing_midi = False
                synth_0.set_master_volume(master_volume)
                label_file.setText(str('FILE:'))
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
            time.sleep(dtime/200.0/time_unit/speed_factor)

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


          # Delay
#          time.sleep(0.01)

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

  playing_file = ''
  playing_midi = False
  midi_play_mode = 'STOP'


# Prepare global data.
def set_name_map():
  # Tone name and its number in MIDI
  tone = 12
  for sc in range(8):
    for cd in ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']:
      name_map[cd + str(sc)] = tone
      tone += 1

  # fn+? key and its tone number in MIDI
  #  A S   F G H
  # Z X C V B N M ,
  tone = 60
  for tn in [0xA6, 0x9a, 0xa7, 0x9b, 0xa8, 0xa9, 0x9d, 0xaa, 0x9e, 0xab, 0x9f, 0xac, 0xad]:
    tone_map[chr(tn)] = tone
    tone += 1


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


# Convert tone names to tone numbers ([C4,D4] --> [60,62])
def names_to_tones(names):
  tones = []
  for nm in names:
    if nm in name_map:
      tones.append(name_map[nm])

  return tones


# Note on a tone in a channel with vol volume.
def note(channel, tone, vol):
  global synth_0, tone_on, midi_transpose

  synth_0.set_note_on(channel, tone + midi_transpose, vol)
  if not tone in tone_on[channel]:
    tone_on[channel].append(tone + midi_transpose) 


# Note off all tones in a channel (tones: [60,62,...] etc)
def notes_off(channel, tones):
  global synth_0, tone_on

  for t in tones:
    synth_0.set_note_off(channel, t + midi_transpose)
    if t in tone_on[channel]:
      tone_on[channel].remove(t)


# All notes off in a channel.
def all_notes_off(channel = None):
  global tone_on
  if channel is None:
    for ch in range(len(tone_on)):
      all_notes_off(ch)
  else:
    synth_0.set_all_notes_off(channel)


# Note on tones in a channel with vol volume.
# Note off the channel tones in advance if Argument 'off' is True. 
def notes(channel, tones, vol, off=True):
  global synth_0, tone_on, sustain

  print('note:' + str(tones) + ',' + str(vol))
  if vol > 0:
    if len(tones) > 0:
      if len(tone_on[channel]) > 0 and sustain == False and off == True:
        print('NOTES OFF:', channel, '=', tone_on[channel])
        notes_off(channel, tone_on[channel])

      for t in tones:
        if t in tone_on[channel]:
          notes_off(channel, [t])

        note(channel, t, vol)
        print('note on:' + str(t) + ',' + str(vol))

  elif len(tones) > 0:
    note_off(channel, tones)

  else:
      if len(tone_on[channel]) > 0:
        notes_off(channel, tone_on[channel])


# Note on code tones named cd_name with vol volume.
def code(cd_name, vol):
  global synth_0, tone_on, sustain, kbd_tone_ch, kbd_transpose

#  print('code:' + cd_name + ',' + str(vol))
  if vol > 0:
    if cd_name in code_map:
      notes_off(kbd_tone_ch, tone_on[kbd_tone_ch])

      # Base tone
      notes(kbd_tone_ch, shitf_notes(names_to_tones([octaver(code_map[cd_name][0], -1)]), kbd_transpose), vol)
#      print('tone_on B=' + str(tone_on[kbd_tone_ch]))

      # Code tones
      notes(kbd_tone_ch, shitf_notes(names_to_tones(code_map[cd_name]), kbd_transpose), vol, False)
#      print('tone_on C=' + str(tone_on[kbd_tone_ch]))
  else:
    notes_off(kbd_tone_ch, tone_on[kbd_tone_ch])


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
  with open(midi_file_path + 'GM0.TXT') as f:
    for mf in f:
      mf = mf.strip()
      if len(mf) > 0:
        if program == 0:
          f.close()
          return mf
      program = program - 1

  f.close()
  return 'UNKNOWN'


# Set and show volume delta value for MIDI player
def set_midi_volume_delta(dlt):
  global midi_volume_delta, label_midi_volume

  midi_volume_delta = midi_volume_delta + dlt
  label_midi_volume.setText('{:0=+3d}'.format(midi_volume_delta))


# Set and show transpose value for MIDI player
def set_midi_transpose(dlt):
  global midi_transpose, label_midi_transp

  midi_transpose = midi_transpose + dlt
  if midi_transpose == -13:
    midi_transpose = 0
  elif midi_transpose == 13:
    midi_transpose = 0
  label_midi_transp.setText('{:0=+3d}'.format(midi_transpose))


# Set and show transpose value for keyboard player
def set_keyboard_transpose(dlt):
  global kbd_transpose, label_transp

  kbd_transpose = kbd_transpose + dlt
  if kbd_transpose == -13:
    kbd_transpose = 0
  elif kbd_transpose == 13:
    kbd_transpose = 0
  label_transp.setText('{:0=+3d}'.format(kbd_transpose))


# Set and show volume value for keyboard player
def set_keyboard_volume(dlt):
  global kbd_volume, label_volume

  kbd_volume = kbd_volume + dlt
  if kbd_volume < 1:
    kbd_volume = 1
  elif kbd_volume > 127:
    kbd_volume = 127
  label_volume.setText('{:0>3d}'.format(kbd_volume))


# Set and show channel for keyboard player
def set_keyboard_channel(dlt):
  global kbd_tone_ch, label_channel

  kbd_tone_ch = (kbd_tone_ch + dlt) % 16
  label_channel.setText('{:0>2d}'.format(kbd_tone_ch))


# Set and show program for keyboard player
def set_keyboard_program(dlt):
  global synth_0, kbd_program, kbd_gmbank, label_program, label_program_name

  kbd_program = (kbd_program + dlt) % 128
  label_program.setText('{:0>3d}'.format(kbd_program))
  prg = get_gm_program_name(kbd_gmbabnk, kbd_program)
  label_program_name.setText(prg)
  synth_0.set_instrument(kbd_gmbabnk, kbd_tone_ch, kbd_program)


# Set and show master volume value
def set_synth_master_volume(dlt):
  global synth_0, master_volume, label_master_volume

  master_volume = master_volume + dlt
  if master_volume < 1:
    master_volume = 0
  elif master_volume > 100:
    master_volume = 100
  synth_0.set_master_volume(master_volume)
  label_master_volume.setText('{:0>3d}'.format(master_volume))


# Set and show sustain mode toggled for keyboard player
def toggle_sustain():
  global sustain, label_sustain, kbd_tone_ch, tone_on

  sustain = not sustain
  label_sustain.setText('S' if sustain else '_')
  if sustain == False:
    all_notes_off(kbd_tone_ch)
    tone_on[kbd_tone_ch] = []


# Set reverb for keyboard player
def set_keyboard_reverb(prog=None, level=None, fback=None):
  global label_reverb_level, kbd_reverb, kbd_tone_ch

  disp = None
  if not prog is None:
    kbd_reverb[0] = prog
    disp = prog

  if not level is None:
    kbd_reverb[1] = level
    disp = level
    
  if not fback is None:
    kbd_reverb[2] = fback
    disp = fback

  if not disp is None:
    control_reverb(kbd_tone_ch, kbd_reverb[0], kbd_reverb[1], kbd_reverb[2])


# Set reverb for MIDI player
def set_midi_reverb(prog=None, level=None, fback=None):
  global label_reverb_lvmidi, midi_reverb, kbd_tone_ch

  disp = None
  if not prog is None:
    midi_reverb[0] = prog
    disp = prog

  if not level is None:
    midi_reverb[1] = level
    disp = level
    
  if not fback is None:
    midi_reverb[2] = fback
    disp = fback

  if not disp is None:
    for ch in range(len(tone_on)):
      if ch != kbd_tone_ch:
        control_reverb(ch, midi_reverb[0], midi_reverb[1], midi_reverb[2])


# Set chorus for keyboard player
def set_keyboard_chorus(prog=None, level=None, fback=None, delay=None):
  global label_chorus_level, kbd_chorus, kbd_tone_ch

  send = False
  if not prog is None:
    kbd_chorus[0] = prog
    send = True

  if not level is None:
    kbd_chorus[1] = level
    send = True
    
  if not fback is None:
    kbd_chorus[2] = fback
    send = True
    
  if not delay is None:
    kbd_chorus[3] = delay
    send = True

  if send:
    control_chorus(kbd_tone_ch, kbd_chorus[0], kbd_chorus[1], kbd_chorus[2], kbd_chorus[3])


# Set chorus for MIDI player
def set_midi_chorus(prog=None, level=None, fback=None, delay=None):
  global label_chorus_lvmidi, midi_chorus, kbd_tone_ch

  send = False
  if not prog is None:
    midi_chorus[0] = prog
    send = True

  if not level is None:
    midi_chorus[1] = level
    send = True
    
  if not fback is None:
    midi_chorus[2] = fback
    send = True
    
  if not delay is None:
    midi_chorus[3] = delay
    send = True

  if send:
    for ch in range(len(tone_on)):
      if ch != kbd_tone_ch:
        control_chorus(ch, midi_chorus[0], midi_chorus[1], midi_chorus[2], midi_chorus[3])


# Keyboard input interrupt function.
def cardkb_0_pressed_event(kb):
  global label_keycode, cardkb_0, kbstr, kbcmd, tone_on, tone_map, code_map
  global kbd_tone_ch, kbd_volume, kbd_transpose
  global playing_midi, playing_file, midi_play_mode
  global midi_file_selected, midi_files, label_midi_file, speed_factor
  global parameter_value, kbd_reverb, kbd_chorus, label_parameter

  kbval = cardkb_0.get_key()
  kbstr = chr(kbval)
  label_keycode.setText(str(hex(ord(kbstr))) + ':' + str(kbstr))

  # KEY: Notes of a code
  if kbstr in code_map:
    notes_off(kbd_tone_ch, tone_on[0])
    code(kbstr, kbd_volume)
  
  # fn+KEY: Note of a tone
  elif kbstr in tone_map:
    print('single tone=' + str(kbstr))
    notes(kbd_tone_ch, shitf_notes([tone_map[kbstr]], kbd_transpose), kbd_volume)

  # [BS]: All notes in all channels off
  elif kbstr == chr(0x08) or  kbstr == chr(0x7f) or  kbstr == chr(0x8b):
    all_notes_off()
    tone_on[kbd_tone_ch] = []

  # Notes off
  else:
    all_notes_off(kbd_tone_ch)
    tone_on[kbd_tone_ch] = []


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
  global label_midi_file, midi_file_selected
  with open(midi_file_path + 'LIST.TXT') as f:
    for mf in f:
      mf = mf.strip()
      if len(mf) > 0:
        cat = mf.split(',')
        if len(cat) == 3:
          midi_files.append(cat)

  f.close()
  if len(midi_files) > 0:
    midi_file_selected = 0
    label_midi_file.setText(midi_files[0][0])
    for i in range(len(midi_files)):
      midi_files[i][2] = float(midi_files[i][2])


# Read 8encoder values
def encoder_read():
  global encoder8_0, enc_button_ch, enc_slide_switch, enc_parm, enc_parm_decade, enc_volume_decade, enc_mastervol_decade
  global tone_on, kbd_tone_ch, playing_midi, speed_factor, midi_file_selected, midi_files, midi_play_mode

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
    title_midi_params.setColor(0xff4040 if enc_slide_switch else 0xff8080, 0x555555 if enc_slide_switch else 0x222222)
    title_kbd_params.setColor(0xff8080 if enc_slide_switch else 0xff4040, 0x222222 if enc_slide_switch else 0x555555)

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
        tone_on[kbd_tone_ch] = []

    # MIDI file or program
    elif enc_ch == ENC_MUSIC_PROGRAM:
      # Slide switch off: keyboard mode
      if slide_switch == False:
        # Select program
        if delta != 0:
          set_keyboard_program(delta)

        # All notes off of keyboard player channel
        if enc_button == True:
          all_notes_off(kbd_tone_ch)
          tone_on[kbd_tone_ch] = []

      # Slide switch on: MIDI player mode
      else:
        # Select a MIDI file
        if playing_midi == False:
          if midi_file_selected >= 0:
            if delta == -1:
              midi_file_selected = midi_file_selected - 1
              if midi_file_selected == -1:
                midi_file_selected = len(midi_files) - 1
            elif delta == 1:
              midi_file_selected = midi_file_selected + 1
              if midi_file_selected == len(midi_files):
                midi_file_selected = 0

            if delta != 0:
              label_midi_fnum.setText('{:03d}'.format(midi_file_selected))
              label_midi_file.setText(midi_files[midi_file_selected][0])

        # Play the selected MIDI file or stop playing
        if enc_button == True:
          if playing_midi == True:
            print('STOP MIDI PLAYER')
            midi_play_mode = 'STOP'
          else:
            print('REPLAY MIDI PLAYER')
            if midi_file_selected >= 0:
              speed_factor = midi_files[midi_file_selected][2]
              label_midi_tempo.setText('x{:3.1f}'.format(speed_factor))
              _thread.start_new_thread(play_midi, (midi_files[midi_file_selected][1],))

    # Transpose
    elif enc_ch == ENC_TRANSPORSE:
      # Slide switch off: keyboard mode
      if slide_switch == False:
        if delta != 0:
          all_notes_off(kbd_tone_ch)
          tone_on[kbd_tone_ch] = []
          set_keyboard_transpose(delta)

      # Slide switch on: MIDI player mode
      else:
        if delta != 0:
          all_notes_off()
          tone_on[kbd_tone_ch] = []
          set_midi_transpose(delta)

        # Pause/Restart MIDI player in playing
        if enc_button == True:
          if playing_midi == True:
            if midi_play_mode == 'PLAY':
              print('PAUSE MIDI PLAYER')
              midi_play_mode = 'PAUSE'
            else:
              print('CONTINUE MIDI PLAYER')
              midi_play_mode = 'PLAY'
          else:
            print('MIDI PLAYER NOT PLAYING')

    # MIDI Channel volume / Button to pause or Restart MIDI player, to all notes off of keyboard play
    elif enc_ch == ENC_VOLUME:
      # Decade value button (toggle)
      if enc_button and enc_button_ch[enc_ch-1]:
        enc_volume_decade = not enc_volume_decade

      if enc_volume_decade:
        encoder8_0.set_led_rgb(enc_ch, 0xffa000)

      # Slide switch off: keyboard mode
      if slide_switch == False:
        if delta != 0:
          set_keyboard_volume(delta * (10 if enc_volume_decade else 1))

      # Slide switch on: MIDI player mode
      else:
        if delta != 0:
          set_midi_volume_delta(delta * (10 if enc_volume_decade else 1))

    # MIDI player tempo / Keyboard play MIDI channel / Button for sustain pedal
    elif enc_ch == ENC_TEMPO_MIDI_CH:
      # Slide switch off: keyboard mode
      if slide_switch == False:
        # Select MIDI channel to keyboard play
        if delta != 0:
          set_keyboard_channel(delta)

      # Slide switch on: MIDI player mode
      else:
        # Change MIDI play speed
        if delta == -1:
          speed_factor = speed_factor - 0.1
          if speed_factor < 0.1:
            speed_factor = 0.1
        elif delta == 1:
          speed_factor = speed_factor + 0.1
          if speed_factor > 5:
            speed_factor = 5

        if delta != 0:
          label_midi_tempo.setText('x{:3.1f}'.format(speed_factor))

      # Sustain pedal
      if enc_button == True:
        toggle_sustain()

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
          enc_pkbd_labels[p].setColor(0xffffff, 0x222222)
          enc_pmidi_labels[p].setColor(0xffffff, 0x222222)

        # Slide switch off: keyboard mode
        if slide_switch == False:
          # Display the label
          if   enc_parm == PARM_RVB_PROG:
            disp = kbd_reverb[0]
          elif enc_parm == PARM_RVB_LEVEL:
            disp = kbd_reverb[1]
          elif enc_parm == PARM_RVB_FBACK:
            disp = kbd_reverb[2]
          elif enc_parm == PARM_CHR_PROG:
            disp = kbd_chorus[0]
          elif enc_parm == PARM_CHR_LEVEL:
            disp = kbd_chorus[1]
          elif enc_parm == PARM_CHR_FBACK:
            disp = kbd_chorus[2]
          elif enc_parm == PARM_CHR_DELAY:
            disp = kbd_chorus[3]

          enc_pkbd_labels[enc_parm].setColor(0x00ffcc, 0x222222)
          enc_pkbd_labels[enc_parm].setText(enc_parameters[enc_parm] + '{:03d}'.format(disp))

        # Slide switch on: MIDI player mode
        else:
          # Display the label
          if   enc_parm == PARM_RVB_PROG:
            disp = midi_reverb[0]
          elif enc_parm == PARM_RVB_LEVEL:
            disp = midi_reverb[1]
          elif enc_parm == PARM_RVB_FBACK:
            disp = midi_reverb[2]
          elif enc_parm == PARM_CHR_PROG:
            disp = midi_chorus[0]
          elif enc_parm == PARM_CHR_LEVEL:
            disp = midi_chorus[1]
          elif enc_parm == PARM_CHR_FBACK:
            disp = midi_chorus[2]
          elif enc_parm == PARM_CHR_DELAY:
            disp = midi_chorus[3]

          enc_pmidi_labels[enc_parm].setColor(0x00ffcc, 0x222222)
          enc_pmidi_labels[enc_parm].setText(enc_parameters[enc_parm] + '{:03d}'.format(disp))

    # Parameter-CTRL1
    elif enc_ch == ENC_CTRL1:
      # Decade value button (toggle)
      if enc_button and enc_button_ch[enc_ch-1]:
        enc_parm_decade = not enc_parm_decade

      if enc_parm_decade:
        encoder8_0.set_led_rgb(enc_ch, 0xffa000)

      if delta != 0 or slide_switch_change:
        send_to = 0

        # Slide switch off: keyboard mode
        if slide_switch == False:
          if   enc_parm == PARM_RVB_PROG:
            kbd_reverb[0] = kbd_reverb[0] + delta
            if kbd_reverb[0] < 0:
              kbd_reverb[0] = 7
            elif kbd_reverb[0] > 7:
              kbd_reverb[0] = 0
            disp = kbd_reverb[0]
            send_to = 1

          elif enc_parm == PARM_RVB_LEVEL:
            kbd_reverb[1] = kbd_reverb[1] + delta * (10 if enc_parm_decade else 1)
            if kbd_reverb[1] < 0:
              kbd_reverb[1] = 0
            elif kbd_reverb[1] > 255:
              kbd_reverb[1] = 255
            disp = kbd_reverb[1]
            send_to = 1

          elif enc_parm == PARM_RVB_FBACK:
            kbd_reverb[2] = kbd_reverb[2] + delta * (10 if enc_parm_decade else 1)
            if kbd_reverb[2] < 0:
              kbd_reverb[2] = 0
            elif kbd_reverb[2] > 255:
              kbd_reverb[2] = 255
            disp = kbd_reverb[2]
            send_to = 1

          elif enc_parm == PARM_CHR_PROG:
            kbd_chorus[0] = kbd_chorus[0] + delta
            if kbd_chorus[0] < 0:
              kbd_chorus[0] = 7
            elif kbd_chorus[0] > 7:
              kbd_chorus[0] = 0
            disp = kbd_chorus[0]
            send_to = 2

          elif enc_parm == PARM_CHR_LEVEL:
            kbd_chorus[1] = kbd_chorus[1] + delta * (10 if enc_parm_decade else 1)
            if kbd_chorus[1] < 0:
              kbd_chorus[1] = 0
            elif kbd_chorus[1] > 255:
              kbd_chorus[1] = 255
            disp = kbd_chorus[1]
            send_to = 2

          elif enc_parm == PARM_CHR_FBACK:
            kbd_chorus[2] = kbd_chorus[2] + delta * (10 if enc_parm_decade else 1)
            if kbd_chorus[2] < 0:
              kbd_chorus[2] = 0
            elif kbd_chorus[2] > 255:
              kbd_chorus[2] = 255
            disp = kbd_chorus[2]
            send_to = 2

          elif enc_parm == PARM_CHR_DELAY:
            kbd_chorus[3] = kbd_chorus[3] + delta * (10 if enc_parm_decade else 1)
            if kbd_chorus[3] < 0:
              kbd_chorus[3] = 0
            elif kbd_chorus[3] > 255:
              kbd_chorus[3] = 255
            disp = kbd_chorus[3]
            send_to = 2

          # Display the label
          enc_pkbd_labels[enc_parm].setText(enc_parameters[enc_parm] + '{:03d}'.format(disp))

          # Send MIDI message
          if delta != 0:
            if send_to == 1:
              set_keyboard_reverb(kbd_reverb[0], kbd_reverb[1], kbd_reverb[2])
            elif send_to == 2:
              set_keyboard_chorus(kbd_chorus[0], kbd_chorus[1], kbd_chorus[2], kbd_chorus[3])

        # Slide switch on: MIDI player mode
        else:
          if   enc_parm == PARM_RVB_PROG:
            midi_reverb[0] = midi_reverb[0] + delta
            if midi_reverb[0] < 0:
              midi_reverb[0] = 7
            elif midi_reverb[0] > 7:
              midi_reverb[0] = 0
            disp = midi_reverb[0]
            send_to = 1

          elif enc_parm == PARM_RVB_LEVEL:
            midi_reverb[1] = midi_reverb[1] + delta * (10 if enc_parm_decade else 1)
            disp = midi_reverb[1]

          elif enc_parm == PARM_RVB_FBACK:
            midi_reverb[2] = midi_reverb[2] + delta * (10 if enc_parm_decade else 1)
            if midi_reverb[2] < 0:
              midi_reverb[2] = 0
            elif midi_reverb[2] > 255:
              midi_reverb[2] = 255
            disp = midi_reverb[2]
            send_to = 1

          elif enc_parm == PARM_CHR_PROG:
            midi_chorus[0] = midi_chorus[0] + delta
            if midi_chorus[0] < 0:
              midi_chorus[0] = 7
            elif midi_chorus[0] > 7:
              midi_chorus[0] = 0
            disp = midi_chorus[0]
            send_to = 2

          elif enc_parm == PARM_CHR_LEVEL:
            midi_chorus[1] = midi_chorus[1] + delta * (10 if enc_parm_decade else 1)
            if midi_chorus[1] < 0:
              midi_chorus[1] = 0
            elif midi_chorus[1] > 255:
              midi_chorus[1] = 255
            disp = midi_chorus[1]
            send_to = 2

          elif enc_parm == PARM_CHR_FBACK:
            midi_chorus[2] = midi_chorus[2] + delta * (10 if enc_parm_decade else 1)
            if midi_chorus[2] < 0:
              midi_chorus[2] = 0
            elif midi_chorus[2] > 255:
              midi_chorus[2] = 255
            disp = midi_chorus[2]
            send_to = 2

          elif enc_parm == PARM_CHR_DELAY:
            midi_chorus[3] = midi_chorus[3] + delta * (10 if enc_parm_decade else 1)
            if midi_chorus[3] < 0:
              midi_chorus[3] = 0
            elif midi_chorus[3] > 255:
              midi_chorus[3] = 255
            disp = midi_chorus[3]
            send_to = 2

          # Display the label
          enc_pmidi_labels[enc_parm].setText(enc_parameters[enc_parm] + '{:03d}'.format(disp))

          # Send MIDI message
          if delta != 0:
            if send_to == 1:
              set_midi_reverb(midi_reverb[0], midi_reverb[1], midi_reverb[2])
            elif send_to == 2:
              set_midi_chorus(midi_chorus[0], midi_chorus[1], midi_chorus[2], midi_chorus[3])

    # Parameter-CTRL2
    elif enc_ch == ENC_CTRL2:
      # Slide switch off: keyboard mode
      if slide_switch == False:
        pass

      # Slide switch on: MIDI player mode
      else:
        pass


def setup():
  global title_midi, title_midi_params, title_keyboard, title_kbd_params, title_general
  global label_keycode, label_transp, label_channel, i2c0, cardkb_0, kbstr, sustain, label_parameter, label_midi_fnum, label_midi_tempo
  global label_file, label_midi_file, label_midi_transp, label_midi_volume, label_volume, label_program, kbd_gmbabnk, label_program_name, label_sustain, label_master_volume
  global label_reverb_level, label_chorus_level, label_reverb_lvmidi, label_chorus_lvmidi
  global enc_ch_val, enc_pmidi_labels, enc_pkbd_labels
  global midi_uart, label_midi_in

  M5.begin()
  Widgets.fillScreen(0x222222)
  sdcard_init()

  # Titles
  title_midi = Widgets.Label("title_midi", 0, 0, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
  title_midi_params = Widgets.Label("title_midi_params", 0, 20, 1.0, 0xff8080, 0x222222, Widgets.FONTS.DejaVu18)
  title_keyboard = Widgets.Label("title_keyboard", 0, 100, 1.0, 0x00ccff, 0x222222, Widgets.FONTS.DejaVu18)
  title_kbd_params = Widgets.Label("title_kbd_params", 0, 120, 1.0, 0xff8080, 0x222222, Widgets.FONTS.DejaVu18)
  title_general = Widgets.Label("title_general", 0, 200, 1.0, 0xff8080, 0x222222, Widgets.FONTS.DejaVu18)

  # GUI for MIDI player
  label_midi_fnum = Widgets.Label("label_midi_fnum", 0, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_midi_transp = Widgets.Label("label_midi_transp", 46, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_midi_volume = Widgets.Label("label_midi_volume", 94, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_midi_tempo = Widgets.Label("label_midi_tempo", 150, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_reverb_lvmidi = Widgets.Label("label_reverb_lvmidi", 202, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_chorus_lvmidi = Widgets.Label("label_chorus_lvmidi", 262, 40, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_file = Widgets.Label("label_file", 0, 60, 1.0, 0x00ffcc, 0x222222, Widgets.FONTS.DejaVu18)
  label_midi_file = Widgets.Label("label_midi_file", 60, 60, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  # GUI for keyboard play
  label_program = Widgets.Label("label_program", 0, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_transp = Widgets.Label("label_transp", 46, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_volume = Widgets.Label("label_volume", 96, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_sustain = Widgets.Label("label_sustain", 146, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_channel = Widgets.Label("label_channel", 168, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_reverb_level = Widgets.Label("label_reverb_level", 202, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_chorus_level = Widgets.Label("label_chorus_level", 262, 140, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  label_program_name = Widgets.Label("label_program_name", 0, 160, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  # MIDI IN
  label_midi_in = Widgets.Label("label_midi_in", 200, 100, 1.0, 0x00ffcc, 0x222222, Widgets.FONTS.DejaVu18)

  # Master Volume
  label_master_volume = Widgets.Label("label_master_volume", 0, 220, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  # For DEBUG
  label_keycode = Widgets.Label("label_keycode", 45, 220, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)
  label_parameter = Widgets.Label("label_parameter", 120, 220, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu18)

  # Labels to edit in the parameter selector
  enc_pmidi_labels = [label_reverb_lvmidi,label_reverb_lvmidi,label_reverb_lvmidi,label_chorus_lvmidi,label_chorus_lvmidi,label_chorus_lvmidi,label_chorus_lvmidi]
  enc_pkbd_labels = [label_reverb_level,label_reverb_level,label_reverb_level,label_chorus_level,label_chorus_level,label_chorus_level,label_chorus_level]

  # I2C
  i2c0 = I2C(0, scl=Pin(33), sda=Pin(32), freq=100000)
  i2c_list = i2c0.scan()
  print('I2C:', i2c_list)
  cardkb_0 = CardKBUnit(i2c0)
  cardkb_0.set_callback(cardkb_0_pressed_event)
  encoder_init()

  # SYNTH unit
  global synth_0
#  synth_0 = SynthUnit(1, port=(13, 14))
  synth_0 = MIDIUnit(1, port=(13, 14))
  midi_uart = synth_0._uart

  synth_0.set_instrument(kbd_gmbabnk, kbd_tone_ch, kbd_program)
  synth_0.set_master_volume(master_volume)
  for ch in range(len(tone_on)):
    synth_0.set_reverb(ch, 0, 0, 0)
    synth_0.set_chorus(ch, 0, 0, 0, 0)

  # Initialize GUI display
  title_midi.setText('MIDI PLAYER')
  title_midi_params.setText('NO. TRN VOL TEMP REVB  CHOR')
  title_keyboard.setText('KEYBOARD PLAYER')
  title_kbd_params.setText('PRG TRN VOL S CH REVB  CHOR')
  title_general.setText('VOL KEYCD PRM')

  label_midi_in.setText('M-IN')
  label_midi_in.setVisible(False)

  label_keycode.setText(str('---'))
  label_parameter.setText(str('---'))
  set_synth_master_volume(0)

  label_file.setText('FILE:')
  label_file.setVisible(True)
  label_midi_file.setText('none')
  label_midi_file.setVisible(True)
  label_midi_fnum.setText('{:03d}'.format(0))

  set_midi_transpose(0)
  set_midi_volume_delta(0)
  label_midi_tempo.setText('x{:3.1f}'.format(speed_factor))
  set_midi_reverb()
  set_midi_chorus()

  set_keyboard_program(0)
  set_keyboard_transpose(0)
  set_keyboard_volume(0)
  toggle_sustain()
  set_keyboard_channel(0)
  set_keyboard_reverb()
  set_keyboard_chorus()
  label_reverb_lvmidi.setText('P{:03d}'.format(midi_reverb[0]))
  label_chorus_lvmidi.setText('P{:03d}'.format(midi_chorus[0]))
  label_reverb_level.setText('P{:03d}'.format(kbd_reverb[0]))
  label_chorus_level.setText('P{:03d}'.format(kbd_chorus[0]))

  # Initialize 8encoder
  for ch in range(1,9):
    encoder8_0.set_led_rgb(ch, 0x000000)


  # Prepare SYNTH data and all notes off
  set_name_map()
  all_notes_off()


def loop():
  global label_keycode, i2c0, cardkb_0, kbstr
  M5.update()
  midi_in()
  cardkb_0.tick()
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
