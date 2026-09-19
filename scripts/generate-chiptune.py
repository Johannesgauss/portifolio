#!/usr/bin/env python3
"""
Cetraminos 4-Channel NES-Style Chiptune Synthesizer & Composer
=============================================================
Emulates classic Nintendo Entertainment System (2A03) 4-channel audio:
  - Channel 1 (Pulse 1 - 50% square): Expressive Lead with singing vibrato & held notes
  - Channel 2 (Pulse 2 - 25% pulse): Harmonized Counterpoint & Rhythm Stabs
  - Channel 3 (Triangle): Deep, warm Sub-Bass walking line
  - Channel 4 (Noise/Drums): Punchy 8-bit Kick, Snare, Hi-Hats & Crash cymbals

Outputs:
  - CetraminosMusic.mp3: "Cetraminos Theme A (Arcade Folk Rush)" (140 BPM, A Minor)
  - CetraminosMusic2.mp3: "Cetraminos Theme B (Cyberpunk Journey)" (132 BPM, D Minor)
"""

import math
import os
import random
import struct
import sys

try:
    import lameenc
except ImportError:
    print("[!] Error: lameenc is required. Install via: pip install lameenc")
    sys.exit(1)

SAMPLE_RATE = 44100

NOTE_MAP = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9,
    'A#': 10, 'Bb': 10, 'B': 11
}

def note_freq(n):
    if not n or n == '-' or n == 'REST':
        return 0.0
    if isinstance(n, (int, float)):
        return 440.0 * (2.0 ** ((n - 69) / 12.0))
    name = n[:-1]
    octave = int(n[-1])
    midi = 12 * (octave + 1) + NOTE_MAP[name]
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))

def pulse_sample(phase, duty=0.5):
    p = phase % 1.0
    return 1.0 if p < duty else -1.0

def triangle_sample(phase):
    p = phase % 1.0
    return 2.0 * abs(2.0 * p - 1.0) - 1.0

def adsr(t, duration, attack=0.015, decay=0.08, sustain_level=0.82, release=0.04):
    if t < 0 or t > duration:
        return 0.0
    sustain_time = max(0.0, duration - attack - decay - release)
    if t < attack:
        return t / attack
    elif t < attack + decay:
        dt = t - attack
        return 1.0 - (1.0 - sustain_level) * (dt / decay)
    elif t < attack + decay + sustain_time:
        return sustain_level
    else:
        rt = t - (attack + decay + sustain_time)
        return max(0.0, sustain_level * (1.0 - rt / release))

class NES4ChannelMixer:
    def __init__(self, bpm=140, total_bars=32, beats_per_bar=4):
        self.bpm = bpm
        self.beat_sec = 60.0 / bpm
        self.step_sec = self.beat_sec / 4.0  # 16th note step
        self.total_bars = total_bars
        self.beats_per_bar = beats_per_bar
        self.total_steps = total_bars * beats_per_bar * 4
        self.total_sec = self.total_steps * self.step_sec
        self.num_samples = int(self.total_sec * SAMPLE_RATE)

    # -------------------------------------------------------------
    # Channel 1: Pulse 1 - Lead Instrument (50% Square Wave)
    # Features long held notes, expressive delayed vibrato, full body
    # -------------------------------------------------------------
    def render_channel1_lead(self, note_events, volume=0.42):
        """note_events: list of (start_step, duration_steps, note_name)"""
        buffer = [0.0] * self.num_samples
        duty = 0.50  # Pure square wave
        
        for start_step, dur_steps, note in note_events:
            freq = note_freq(note)
            if freq <= 0:
                continue
            start_t = start_step * self.step_sec
            dur_t = dur_steps * self.step_sec
            start_idx = int(start_t * SAMPLE_RATE)
            end_idx = min(self.num_samples, int((start_t + dur_t) * SAMPLE_RATE))
            phase = 0.0
            
            for i in range(start_idx, end_idx):
                t_note = (i - start_idx) / SAMPLE_RATE
                # Delayed singing vibrato (starts after 0.15s, gentle 5.2 Hz)
                if t_note > 0.15:
                    vib_amt = min(0.020, 0.020 * ((t_note - 0.15) / 0.2))
                    vib = 1.0 + vib_amt * math.sin(2.0 * math.pi * 5.2 * (t_note - 0.15))
                else:
                    vib = 1.0
                    
                phase += (freq * vib) / SAMPLE_RATE
                env = adsr(t_note, dur_t, attack=0.012, decay=0.06, sustain_level=0.85, release=0.035)
                buffer[i] += pulse_sample(phase, duty) * env * volume
        return buffer

    # -------------------------------------------------------------
    # Channel 2: Pulse 2 - Harmony & Rhythm Stabs (25% Pulse Wave)
    # Different duty cycle gives it a brighter, sharper distinct timbre
    # -------------------------------------------------------------
    def render_channel2_harmony(self, note_events, volume=0.30):
        """note_events: list of (start_step, duration_steps, note_name)"""
        buffer = [0.0] * self.num_samples
        duty = 0.25  # Brighter 25% duty cycle
        
        for start_step, dur_steps, note in note_events:
            freq = note_freq(note)
            if freq <= 0:
                continue
            start_t = start_step * self.step_sec
            dur_t = dur_steps * self.step_sec
            start_idx = int(start_t * SAMPLE_RATE)
            end_idx = min(self.num_samples, int((start_t + dur_t) * SAMPLE_RATE))
            phase = 0.0
            
            for i in range(start_idx, end_idx):
                t_note = (i - start_idx) / SAMPLE_RATE
                phase += freq / SAMPLE_RATE
                # Crisper attack for harmony/chords
                env = adsr(t_note, dur_t, attack=0.008, decay=0.05, sustain_level=0.75, release=0.025)
                buffer[i] += pulse_sample(phase, duty) * env * volume
        return buffer

    # -------------------------------------------------------------
    # Channel 3: Triangle Wave - Deep Walking Sub-Bass
    # Low octaves (Octaves 1-2), warm, punchy harmonic foundation
    # -------------------------------------------------------------
    def render_channel3_bass(self, bass_events, volume=0.55):
        """bass_events: list of (start_step, duration_steps, note_name)"""
        buffer = [0.0] * self.num_samples
        
        for start_step, dur_steps, note in bass_events:
            freq = note_freq(note)
            if freq <= 0:
                continue
            start_t = start_step * self.step_sec
            dur_t = dur_steps * self.step_sec
            start_idx = int(start_t * SAMPLE_RATE)
            end_idx = min(self.num_samples, int((start_t + dur_t) * SAMPLE_RATE))
            phase = 0.0
            
            for i in range(start_idx, end_idx):
                t_note = (i - start_idx) / SAMPLE_RATE
                phase += freq / SAMPLE_RATE
                # Smooth bass envelope: solid body, short release
                env = adsr(t_note, dur_t, attack=0.008, decay=0.04, sustain_level=0.88, release=0.02)
                buffer[i] += triangle_sample(phase) * env * volume
        return buffer

    # -------------------------------------------------------------
    # Channel 4: Noise & Drum Kit - 8-bit Percussion
    # Punchy kick, snappy snare, crisp hi-hats, and accent crash
    # -------------------------------------------------------------
    def render_channel4_drums(self, drum_events, volume=0.45):
        """drum_events: list of (start_step, drum_type) - 'K'=kick, 'S'=snare, 'H'=hihat, 'O'=openhh, 'C'=crash"""
        buffer = [0.0] * self.num_samples
        rng = random.Random(1337)
        
        for start_step, drum_type in drum_events:
            start_t = start_step * self.step_sec
            start_idx = int(start_t * SAMPLE_RATE)
            
            if drum_type == 'K':  # Kick drum: fast pitch-sweep punch (180Hz -> 42Hz)
                dur = 0.11
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                phase = 0.0
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    f = 42.0 + 138.0 * ((1.0 - t / dur) ** 2.2)
                    phase += f / SAMPLE_RATE
                    env = (1.0 - t / dur) ** 1.3
                    click = (rng.random() * 2.0 - 1.0) * 0.25 if t < 0.008 else 0.0
                    buffer[i] += (triangle_sample(phase) * 1.1 + click) * env * volume
                    
            elif drum_type == 'S':  # Snare drum: dual noise burst + pitched body
                dur = 0.16
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                phase = 0.0
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    # Snare tone body drops from 190Hz to 80Hz
                    f = 80.0 + 110.0 * (1.0 - t / dur)
                    phase += f / SAMPLE_RATE
                    body = triangle_sample(phase) * 0.5 * (1.0 - t / dur)
                    # Noise crack
                    noise = (rng.random() * 2.0 - 1.0) * ((1.0 - t / dur) ** 1.7)
                    buffer[i] += (noise * 0.85 + body) * volume
                    
            elif drum_type == 'H':  # Closed Hi-Hat: tight high-frequency noise tap
                dur = 0.045
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    noise = (rng.random() * 2.0 - 1.0) * ((1.0 - t / dur) ** 3.0)
                    buffer[i] += noise * (volume * 0.50)

            elif drum_type == 'O':  # Open Hi-Hat: sustained cymbal ring
                dur = 0.18
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    noise = (rng.random() * 2.0 - 1.0) * ((1.0 - t / dur) ** 1.8)
                    buffer[i] += noise * (volume * 0.60)
                    
            elif drum_type == 'C':  # Crash Cymbal: wide splash
                dur = 0.55
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    noise = (rng.random() * 2.0 - 1.0) * ((1.0 - t / dur) ** 1.9)
                    buffer[i] += noise * (volume * 0.70)
        return buffer

    def mix_and_export(self, ch1, ch2, ch3, ch4, output_file, bitrate=192):
        """Master stereo mixdown with subtle panning for clear instrument separation"""
        num_samples = self.num_samples
        stereo_pcm = bytearray()
        
        # Panning & Balancing:
        # Channel 1 (Lead 50% square): Center-Left (0.85 L, 0.70 R)
        # Channel 2 (Harmony 25% pulse): Center-Right (0.60 L, 0.90 R)
        # Channel 3 (Sub-Bass Triangle): Solid Center (0.85 L, 0.85 R)
        # Channel 4 (Drums): Center punch, slight hat spread
        
        mixed_l = [0.0] * num_samples
        mixed_r = [0.0] * num_samples
        max_amp = 0.0001
        
        for i in range(num_samples):
            sl = ch1[i] * 0.85 + ch2[i] * 0.60 + ch3[i] * 0.85 + ch4[i] * 0.80
            sr = ch1[i] * 0.70 + ch2[i] * 0.90 + ch3[i] * 0.85 + ch4[i] * 0.80
            mixed_l[i] = sl
            mixed_r[i] = sr
            max_amp = max(max_amp, abs(sl), abs(sr))
            
        target_gain = 0.94 / max_amp
        for i in range(num_samples):
            sl = int(max(-32767, min(32767, mixed_l[i] * target_gain * 32767.0)))
            sr = int(max(-32767, min(32767, mixed_r[i] * target_gain * 32767.0)))
            stereo_pcm.extend(struct.pack('<hh', sl, sr))
            
        encoder = lameenc.Encoder()
        encoder.set_bit_rate(bitrate)
        encoder.set_in_sample_rate(SAMPLE_RATE)
        encoder.set_channels(2)
        encoder.set_quality(2)
        mp3_data = encoder.encode(bytes(stereo_pcm)) + encoder.flush()
        
        with open(output_file, 'wb') as f:
            f.write(mp3_data)
        print(f"[✓] Successfully generated {output_file} ({len(mp3_data) / 1024:.1f} KB, duration: {num_samples / SAMPLE_RATE:.1f}s)")


# ==============================================================================
# Track 1: "Cetraminos Theme A (Arcade Folk Rush)"
# Key: A Minor | Tempo: 140 BPM | Total: 32 Bars (~54.8 seconds loop)
# Structure:
#   - Channel 1 (Lead): Catchy folk-arcade melody with expressive half/whole notes
#   - Channel 2 (Harmony): 3rds/6ths counterpoint & rhythmic syncopated stabs
#   - Channel 3 (Bass): Walking bassline in octaves 1 & 2 (A1, C2, D2, E2, F2, G2)
#   - Channel 4 (Drums): Solid 8-bit drum beat with kicks on 1 & 3, snares on 2 & 4
# ==============================================================================
def compose_track_1(output_path, bpm=132):
    print(f"[*] Composing Track 1 (4 NES Channels @ {bpm} BPM) -> {output_path}...")
    total_bars = 32
    mixer = NES4ChannelMixer(bpm=bpm, total_bars=total_bars)
    
    # 1. Drums (Channel 4)
    drums = []
    for b in range(total_bars):
        s = b * 16
        # Crash on sections
        if b in (0, 8, 16, 24):
            drums.append((s, 'C'))
            
        for step in range(16):
            cur = s + step
            # Kick on beats 1 and 3
            if step in (0, 8):
                drums.append((cur, 'K'))
            # Snare on beats 2 and 4
            elif step in (4, 12):
                drums.append((cur, 'S'))
                
            # Hi-hat on 8th note offbeats & 16ths
            if step in (2, 6, 10):
                drums.append((cur, 'H'))
            elif step == 14:
                drums.append((cur, 'O' if (b + 1) % 4 != 0 else 'S'))  # Open hat or fill
                
    # 2. Bass (Channel 3 - Triangle Sub-Bass in Octaves 1 & 2)
    # 32-bar harmonic progression:
    # Bars 0-7: Main Theme (Am - Dm - G - C - F - Dm - E - E7)
    # Bars 8-15: Main Theme High Octave (Am - Dm - G - C - F - Dm - E - Am)
    # Bars 16-23: B-Section / Bridge (F - G - Em - Am - Dm - G - C - E)
    # Bars 24-31: Climax & Turnaround (F - G - Am - Em - F - Dm - E7 - Am)
    chords = [
        ('A1', 'E2'), ('D2', 'A2'), ('G1', 'D2'), ('C2', 'G2'),
        ('F1', 'C2'), ('D2', 'A2'), ('E1', 'B1'), ('E1', 'G#2'),
        
        ('A1', 'E2'), ('D2', 'A2'), ('G1', 'D2'), ('C2', 'G2'),
        ('F1', 'C2'), ('D2', 'A2'), ('E1', 'B1'), ('A1', 'E2'),
        
        ('F1', 'C2'), ('G1', 'D2'), ('E1', 'B1'), ('A1', 'E2'),
        ('D2', 'A2'), ('G1', 'D2'), ('C2', 'G2'), ('E1', 'G#2'),
        
        ('F1', 'C2'), ('G1', 'D2'), ('A1', 'E2'), ('E1', 'B1'),
        ('F1', 'C2'), ('D2', 'A2'), ('E1', 'G#2'), ('A1', 'E2'),
    ]
    
    bass = []
    for b, (root, fifth) in enumerate(chords):
        s = b * 16
        # Solid walking quarter-note bass groove (4 steps each = full quarter note!)
        bass.append((s + 0,  4, root))
        bass.append((s + 4,  4, fifth))
        bass.append((s + 8,  4, root))
        bass.append((s + 12, 4, fifth))
        
    # 3. Channel 1: Lead (50% Square Wave with LONG HELD NOTES and Expressive Vibrato!)
    # Note lengths:
    # 8 steps = Half note (0.86s!)
    # 12 steps = Dotted half note (1.29s!)
    # 16 steps = Full whole note (1.71s!)
    lead = [
        # --- Section 1: Melodic Folk Theme (Bars 0-7) ---
        # Bar 0 (Am): E5 (half note), C5 (quarter), D5 (quarter)
        (0 * 16 + 0, 8, 'E5'), (0 * 16 + 8, 4, 'C5'), (0 * 16 + 12, 4, 'D5'),
        # Bar 1 (Dm): F5 (dotted half note!), E5 (quarter)
        (1 * 16 + 0, 12, 'F5'), (1 * 16 + 12, 4, 'E5'),
        # Bar 2 (G): D5 (half note), B4 (quarter), C5 (quarter)
        (2 * 16 + 0, 8, 'D5'), (2 * 16 + 8, 4, 'B4'), (2 * 16 + 12, 4, 'C5'),
        # Bar 3 (C): E5 (dotted half note!), D5 (quarter)
        (3 * 16 + 0, 12, 'E5'), (3 * 16 + 12, 4, 'D5'),
        # Bar 4 (F): C5 (half note), A4 (half note!)
        (4 * 16 + 0, 8, 'C5'), (4 * 16 + 8, 8, 'A4'),
        # Bar 5 (Dm): D5 (half note), F5 (quarter), E5 (quarter)
        (5 * 16 + 0, 8, 'D5'), (5 * 16 + 8, 4, 'F5'), (5 * 16 + 12, 4, 'E5'),
        # Bar 6 (E): B4 (dotted half note!), C5 (quarter)
        (6 * 16 + 0, 12, 'B4'), (6 * 16 + 12, 4, 'C5'),
        # Bar 7 (E7): B4 (whole note - singing sustain!)
        (7 * 16 + 0, 16, 'B4'),
        
        # --- Section 2: Soaring High Octave Melody (Bars 8-15) ---
        # Bar 8 (Am): A5 (whole note - powerful high lead with vibrato!)
        (8 * 16 + 0, 16, 'A5'),
        # Bar 9 (Dm): G5 (half note), F5 (half note)
        (9 * 16 + 0, 8, 'G5'), (9 * 16 + 8, 8, 'F5'),
        # Bar 10 (G): G5 (dotted half note), F5 (quarter)
        (10 * 16 + 0, 12, 'G5'), (10 * 16 + 12, 4, 'F5'),
        # Bar 11 (C): E5 (whole note!)
        (11 * 16 + 0, 16, 'E5'),
        # Bar 12 (F): F5 (half note), E5 (quarter), D5 (quarter)
        (12 * 16 + 0, 8, 'F5'), (12 * 16 + 8, 4, 'E5'), (12 * 16 + 12, 4, 'D5'),
        # Bar 13 (Dm): F5 (half note), A5 (half note)
        (13 * 16 + 0, 8, 'F5'), (13 * 16 + 8, 8, 'A5'),
        # Bar 14 (E): G#5 (dotted half note), B5 (quarter)
        (14 * 16 + 0, 12, 'G#5'), (14 * 16 + 12, 4, 'B5'),
        # Bar 15 (Am): A5 (whole note - glorious resolution!)
        (15 * 16 + 0, 16, 'A5'),
        
        # --- Section 3: B-Section / Harmonic Journey (Bars 16-23) ---
        # Bar 16 (F): C6 (half note), A5 (half note)
        (16 * 16 + 0, 8, 'C6'), (16 * 16 + 8, 8, 'A5'),
        # Bar 17 (G): B5 (half note), G5 (half note)
        (17 * 16 + 0, 8, 'B5'), (17 * 16 + 8, 8, 'G5'),
        # Bar 18 (Em): G5 (dotted half note), E5 (quarter)
        (18 * 16 + 0, 12, 'G5'), (18 * 16 + 12, 4, 'E5'),
        # Bar 19 (Am): E5 (whole note!)
        (19 * 16 + 0, 16, 'E5'),
        # Bar 20 (Dm): F5 (half note), D5 (quarter), F5 (quarter)
        (20 * 16 + 0, 8, 'F5'), (20 * 16 + 8, 4, 'D5'), (20 * 16 + 12, 4, 'F5'),
        # Bar 21 (G): G5 (dotted half note), B5 (quarter)
        (21 * 16 + 0, 12, 'G5'), (21 * 16 + 12, 4, 'B5'),
        # Bar 22 (C): C6 (whole note!)
        (22 * 16 + 0, 16, 'C6'),
        # Bar 23 (E): B5 (half note), G#5 (half note)
        (23 * 16 + 0, 8, 'B5'), (23 * 16 + 8, 8, 'G#5'),
        
        # --- Section 4: Climax & Seamless Loop Turnaround (Bars 24-31) ---
        # Bar 24 (F): A5 (dotted half note), C6 (quarter)
        (24 * 16 + 0, 12, 'A5'), (24 * 16 + 12, 4, 'C6'),
        # Bar 25 (G): B5 (dotted half note), D6 (quarter)
        (25 * 16 + 0, 12, 'B5'), (25 * 16 + 12, 4, 'D6'),
        # Bar 26 (Am): C6 (half note), E6 (half note - soaring peak!)
        (26 * 16 + 0, 8, 'C6'), (26 * 16 + 8, 8, 'E6'),
        # Bar 27 (Em): B5 (whole note!)
        (27 * 16 + 0, 16, 'B5'),
        # Bar 28 (F): A5 (half note), F5 (half note)
        (28 * 16 + 0, 8, 'A5'), (28 * 16 + 8, 8, 'F5'),
        # Bar 29 (Dm): D5 (half note), F5 (half note)
        (29 * 16 + 0, 8, 'D5'), (29 * 16 + 8, 8, 'F5'),
        # Bar 30 (E7): E5 (dotted half note), G#5 (quarter)
        (30 * 16 + 0, 12, 'E5'), (30 * 16 + 12, 4, 'G#5'),
        # Bar 31 (Am): A5 (whole note - loops seamlessly back to Bar 0!)
        (31 * 16 + 0, 16, 'A5'),
    ]
    
    # 4. Channel 2: Harmony & Counterpoint (25% Pulse Wave)
    # Plays lower 3rds/6ths and harmonic support
    harmony = [
        # Bars 0-7: Warm 3rds harmony under the lead
        (0 * 16 + 0, 8, 'C5'), (0 * 16 + 8, 4, 'A4'), (0 * 16 + 12, 4, 'B4'),
        (1 * 16 + 0, 12, 'D5'), (1 * 16 + 12, 4, 'C5'),
        (2 * 16 + 0, 8, 'B4'), (2 * 16 + 8, 4, 'G4'), (2 * 16 + 12, 4, 'A4'),
        (3 * 16 + 0, 12, 'C5'), (3 * 16 + 12, 4, 'B4'),
        (4 * 16 + 0, 8, 'A4'), (4 * 16 + 8, 8, 'F4'),
        (5 * 16 + 0, 8, 'F4'), (5 * 16 + 8, 4, 'D5'), (5 * 16 + 12, 4, 'C5'),
        (6 * 16 + 0, 12, 'G#4'), (6 * 16 + 12, 4, 'A4'),
        (7 * 16 + 0, 16, 'G#4'),
        
        # Bars 8-15: Counterpoint underneath the soaring A5
        (8 * 16 + 0, 8, 'C5'), (8 * 16 + 8, 8, 'E5'),
        (9 * 16 + 0, 8, 'D5'), (9 * 16 + 8, 8, 'A4'),
        (10 * 16 + 0, 8, 'B4'), (10 * 16 + 8, 8, 'D5'),
        (11 * 16 + 0, 16, 'C5'),
        (12 * 16 + 0, 8, 'A4'), (12 * 16 + 8, 8, 'F4'),
        (13 * 16 + 0, 8, 'A4'), (13 * 16 + 8, 8, 'D5'),
        (14 * 16 + 0, 12, 'E5'), (14 * 16 + 12, 4, 'G#5'),
        (15 * 16 + 0, 16, 'E5'),
        
        # Bars 16-23: Rich harmony
        (16 * 16 + 0, 8, 'A5'), (16 * 16 + 8, 8, 'F5'),
        (17 * 16 + 0, 8, 'G5'), (17 * 16 + 8, 8, 'D5'),
        (18 * 16 + 0, 12, 'E5'), (18 * 16 + 12, 4, 'B4'),
        (19 * 16 + 0, 16, 'C5'),
        (20 * 16 + 0, 8, 'D5'), (20 * 16 + 8, 8, 'A4'),
        (21 * 16 + 0, 12, 'B4'), (21 * 16 + 12, 4, 'G5'),
        (22 * 16 + 0, 16, 'G5'),
        (23 * 16 + 0, 8, 'G#5'), (23 * 16 + 8, 8, 'E5'),
        
        # Bars 24-31: Turnaround harmony
        (24 * 16 + 0, 12, 'F5'), (24 * 16 + 12, 4, 'A5'),
        (25 * 16 + 0, 12, 'G5'), (25 * 16 + 12, 4, 'B5'),
        (26 * 16 + 0, 8, 'A5'), (26 * 16 + 8, 8, 'C6'),
        (27 * 16 + 0, 16, 'G5'),
        (28 * 16 + 0, 8, 'F5'), (28 * 16 + 8, 8, 'C5'),
        (29 * 16 + 0, 8, 'A4'), (29 * 16 + 8, 8, 'D5'),
        (30 * 16 + 0, 12, 'B4'), (30 * 16 + 12, 4, 'E5'),
        (31 * 16 + 0, 16, 'C5'),
    ]
    
    ch1 = mixer.render_channel1_lead(lead, volume=0.44)
    ch2 = mixer.render_channel2_harmony(harmony, volume=0.30)
    ch3 = mixer.render_channel3_bass(bass, volume=0.55)
    ch4 = mixer.render_channel4_drums(drums, volume=0.45)
    
    mixer.mix_and_export(ch1, ch2, ch3, ch4, output_path, bitrate=192)


# ==============================================================================
# Track 2: "Cetraminos Theme B (Cyberpunk Journey)"
# Key: D Minor | Tempo: 132 BPM | Total: 32 Bars (~58.1 seconds loop)
# Structure:
#   - Channel 1 (Lead): Smooth, heroic synth lead with long expressive tones
#   - Channel 2 (Harmony): 25% pulse counterpoint & arpeggiated echoes
#   - Channel 3 (Bass): Heavy sub-bass synthwave groove in D1/D2
#   - Channel 4 (Drums): Tight 8-bit retro funk beat with syncopated kicks
# ==============================================================================
def compose_track_2(output_path):
    print(f"[*] Composing Track 2 (4 NES Channels) -> {output_path}...")
    bpm = 132
    total_bars = 32
    mixer = NES4ChannelMixer(bpm=bpm, total_bars=total_bars)
    
    # 1. Drums (Channel 4)
    drums = []
    for b in range(total_bars):
        s = b * 16
        if b in (0, 8, 16, 24):
            drums.append((s, 'C'))
        for step in range(16):
            cur = s + step
            # Syncopated electro/arcade kick
            if step in (0, 6, 10):
                drums.append((cur, 'K'))
            # Snare on 4 and 12
            elif step in (4, 12):
                drums.append((cur, 'S'))
            # 8th-note hi-hats
            if step in (2, 6, 10, 14):
                drums.append((cur, 'H'))
                
    # 2. Bass (Channel 3 - Triangle Sub-Bass in Octaves 1 & 2)
    # Progression: Dm - Bb - C - Am - Dm - Bb - F - C (repeated 4 times)
    bass_roots = [
        ('D1', 'A1'), ('Bb0', 'F1'), ('C1', 'G1'), ('A0', 'E1'),
        ('D1', 'A1'), ('Bb0', 'F1'), ('F1', 'C2'), ('C1', 'G1'),
    ] * 4
    
    bass = []
    for b, (root, fifth) in enumerate(bass_roots):
        s = b * 16
        # Driving synthwave bassline: root (6 steps), octave/fifth (2 steps), root (4 steps)...
        bass.append((s + 0,  6, root))
        bass.append((s + 6,  2, fifth))
        bass.append((s + 8,  4, root))
        bass.append((s + 12, 4, fifth))
        
    # 3. Channel 1: Lead (50% Square Wave with LONG HELD NOTES)
    lead = []
    # Two full 16-bar melodic phrases
    for cycle in range(2):
        base = cycle * 16
        lead.extend([
            # Bar 0 (Dm): D5 (half note), F5 (quarter), A5 (quarter)
            ((base + 0) * 16 + 0, 8, 'D5'), ((base + 0) * 16 + 8, 4, 'F5'), ((base + 0) * 16 + 12, 4, 'A5'),
            # Bar 1 (Bb): Bb5 (dotted half note!), A5 (quarter)
            ((base + 1) * 16 + 0, 12, 'Bb5'), ((base + 1) * 16 + 12, 4, 'A5'),
            # Bar 2 (C): G5 (half note), E5 (quarter), G5 (quarter)
            ((base + 2) * 16 + 0, 8, 'G5'), ((base + 2) * 16 + 8, 4, 'E5'), ((base + 2) * 16 + 12, 4, 'G5'),
            # Bar 3 (Am): A5 (whole note - long held singing note!)
            ((base + 3) * 16 + 0, 16, 'A5'),
            
            # Bar 4 (Dm): F5 (half note), D5 (quarter), F5 (quarter)
            ((base + 4) * 16 + 0, 8, 'F5'), ((base + 4) * 16 + 8, 4, 'D5'), ((base + 4) * 16 + 12, 4, 'F5'),
            # Bar 5 (Bb): D6 (dotted half note!), C6 (quarter)
            ((base + 5) * 16 + 0, 12, 'D6'), ((base + 5) * 16 + 12, 4, 'C6'),
            # Bar 6 (F): A5 (half note), C6 (half note)
            ((base + 6) * 16 + 0, 8, 'A5'), ((base + 6) * 16 + 8, 8, 'C6'),
            # Bar 7 (C): G5 (whole note!)
            ((base + 7) * 16 + 0, 16, 'G5'),
            
            # Bar 8 (Dm): D6 (whole note - peak emotional sustain!)
            ((base + 8) * 16 + 0, 16, 'D6'),
            # Bar 9 (Bb): C6 (half note), Bb5 (half note)
            ((base + 9) * 16 + 0, 8, 'C6'), ((base + 9) * 16 + 8, 8, 'Bb5'),
            # Bar 10 (C): G5 (dotted half note), A5 (quarter)
            ((base + 10) * 16 + 0, 12, 'G5'), ((base + 10) * 16 + 12, 4, 'A5'),
            # Bar 11 (Am): E5 (whole note!)
            ((base + 11) * 16 + 0, 16, 'E5'),
            
            # Bar 12 (Dm): F5 (half note), G5 (quarter), A5 (quarter)
            ((base + 12) * 16 + 0, 8, 'F5'), ((base + 12) * 16 + 8, 4, 'G5'), ((base + 12) * 16 + 12, 4, 'A5'),
            # Bar 13 (Bb): Bb5 (dotted half note), D6 (quarter)
            ((base + 13) * 16 + 0, 12, 'Bb5'), ((base + 13) * 16 + 12, 4, 'D6'),
            # Bar 14 (F): C6 (half note), A5 (half note)
            ((base + 14) * 16 + 0, 8, 'C6'), ((base + 14) * 16 + 8, 8, 'A5'),
            # Bar 15 (C): D5 (whole note - resolving into loop!)
            ((base + 15) * 16 + 0, 16, 'D5'),
        ])
        
    # 4. Channel 2: Harmony (25% Pulse Wave)
    harmony = []
    for cycle in range(2):
        base = cycle * 16
        harmony.extend([
            ((base + 0) * 16 + 0, 8, 'A4'), ((base + 0) * 16 + 8, 4, 'D5'), ((base + 0) * 16 + 12, 4, 'F5'),
            ((base + 1) * 16 + 0, 12, 'G5'), ((base + 1) * 16 + 12, 4, 'F5'),
            ((base + 2) * 16 + 0, 8, 'E5'), ((base + 2) * 16 + 8, 4, 'C5'), ((base + 2) * 16 + 12, 4, 'E5'),
            ((base + 3) * 16 + 0, 16, 'E5'),
            
            ((base + 4) * 16 + 0, 8, 'D5'), ((base + 4) * 16 + 8, 4, 'A4'), ((base + 4) * 16 + 12, 4, 'D5'),
            ((base + 5) * 16 + 0, 12, 'Bb5'), ((base + 5) * 16 + 12, 4, 'A5'),
            ((base + 6) * 16 + 0, 8, 'F5'), ((base + 6) * 16 + 8, 8, 'A5'),
            ((base + 7) * 16 + 0, 16, 'E5'),
            
            ((base + 8) * 16 + 0, 16, 'Bb5'),
            ((base + 9) * 16 + 0, 8, 'A5'), ((base + 9) * 16 + 8, 8, 'G5'),
            ((base + 10) * 16 + 0, 12, 'E5'), ((base + 10) * 16 + 12, 4, 'F5'),
            ((base + 11) * 16 + 0, 16, 'C5'),
            
            ((base + 12) * 16 + 0, 8, 'D5'), ((base + 12) * 16 + 8, 4, 'E5'), ((base + 12) * 16 + 12, 4, 'F5'),
            ((base + 13) * 16 + 0, 12, 'G5'), ((base + 13) * 16 + 12, 4, 'Bb5'),
            ((base + 14) * 16 + 0, 8, 'A5'), ((base + 14) * 16 + 8, 8, 'F5'),
            ((base + 15) * 16 + 0, 16, 'A4'),
        ])
        
    ch1 = mixer.render_channel1_lead(lead, volume=0.44)
    ch2 = mixer.render_channel2_harmony(harmony, volume=0.30)
    ch3 = mixer.render_channel3_bass(bass, volume=0.55)
    ch4 = mixer.render_channel4_drums(drums, volume=0.45)
    
    mixer.mix_and_export(ch1, ch2, ch3, ch4, output_path, bitrate=192)


if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '/home/cloud/my_projects/Cetraminos/Cetraminos/src'
    
    speed1_path = os.path.join(target_dir, 'CetraminosMusic_speed1.mp3')
    speed2_path = os.path.join(target_dir, 'CetraminosMusic_speed2.mp3')
    speed3_path = os.path.join(target_dir, 'CetraminosMusic_speed3.mp3')
    t1_path = os.path.join(target_dir, 'CetraminosMusic.mp3')
    t2_path = os.path.join(target_dir, 'CetraminosMusic2.mp3')
    
    # Speed Tier 1: 132 BPM (Levels 1-3)
    compose_track_1(speed1_path, bpm=132)
    # Speed Tier 2: 154 BPM (Levels 4-6)
    compose_track_1(speed2_path, bpm=154)
    # Speed Tier 3: 178 BPM (Levels 7+)
    compose_track_1(speed3_path, bpm=178)
    
    # Fallback / Default track (copy of speed1)
    import shutil
    shutil.copyfile(speed1_path, t1_path)
    
    # Theme B
    compose_track_2(t2_path)
    print(f"\n[✓] Progressive 4-channel NES soundtracks generated in: {target_dir}")

