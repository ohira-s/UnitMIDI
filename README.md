# Sample programs for Unit-MIDI Synthesizer with M5Stack CORE2.
===
## Programs:
### UIFlow/UnitMIDI_kbd8enc.py
    CPU: M5Stack CORE2
          PORT-A: 8encoder, CardKB Mini V1.1 (I2C, needs I2C hub)
          PORT-C: Unit-MIDI (UART)
          Micro SD: MIDI Files(format0) and GM programe names list.
    Unit-MIDI:
          MIDI IN: Not available.
          MIDI OUT: Send MIDI data.
    Functions:
          Play standard MIDI files in SD card.
          Play the synthesizer with CardKB Mini V1.1 keyboard.
---
### UIFlow/UnitMIDI_SMF_MIDIin.py
    CPU: M5Stack CORE2
          PORT-A: 8encoder, (I2C)
          PORT-C: Unit-MIDI (UART)
          Micro SD: MIDI Files(format0), GM program names list and MIDI channel settings.
    Unit-MIDI:
          MIDI IN: Receive MIDI data (DIN5)
          MIDI OUT: Send MIDI data (DIN5)
    Functions:
          Play standard MIDI files in SD card.
          Play the synthesizer by MIDI data received via MIDI IN.
          Save and load MIDI channel settings.
