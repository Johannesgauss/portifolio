#!/usr/bin/env python3
"""
Cetraminos 8-Bit Retro Chiptune Synthesizer & Composer
=====================================================
Generates 100% royalty-free, original retro arcade soundtracks for Cetraminos.
Emulates classic NES/Arcade sound chips (2A03 style):
- Pulse Channel 1: Lead Melody (variable duty cycle, vibrato, envelope)
- Pulse Channel 2: Arpeggios & Counterpoint (25% / 50% duty cycle, delay)
- Triangle Channel: Driving Walking Bass
- Noise Channel: 8-bit Percussion (Kick, Snare, Hi-Hats, Crash)

Requires: python3, lameenc (pip install lameenc)
Output:
  - CetraminosMusic.mp3 ("Cetraminos Rush" - 152 BPM, A Minor Arcade Classic)
  - CetraminosMusic2.mp3 ("Cetraminos Cyber Pulse" - 140 BPM, D Minor Cyberpunk)
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

def transpose_octave(note_str, oct_diff=1):
    name = note_str[:-1]
    octave = int(note_str[-1])
    return f"{name}{octave + oct_diff}"

def pulse_sample(phase, duty=0.5):
    return 1.0 if (phase % 1.0) < duty else -1.0

def triangle_sample(phase):
    p = phase % 1.0
    return 2.0 * abs(2.0 * p - 1.0) - 1.0

def adsr(t, duration, attack=0.01, decay=0.05, sustain_level=0.7, release=0.03):
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

class TrackBuilder:
    def __init__(self, bpm=150, total_bars=32, beats_per_bar=4):
        self.bpm = bpm
        self.beat_sec = 60.0 / bpm
        self.step_sec = self.beat_sec / 4.0  # 16th note step
        self.total_bars = total_bars
        self.beats_per_bar = beats_per_bar
        self.total_steps = total_bars * beats_per_bar * 4
        self.total_sec = self.total_steps * self.step_sec
        self.num_samples = int(self.total_sec * SAMPLE_RATE)

    def render_lead(self, notes_events, duty=0.5, vibrato_speed=6.0, vibrato_depth=0.015, volume=0.35):
        buffer = [0.0] * self.num_samples
        for start_step, dur_steps, note in notes_events:
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
                if t_note > 0.08:
                    vib = 1.0 + vibrato_depth * math.sin(2.0 * math.pi * vibrato_speed * (t_note - 0.08))
                else:
                    vib = 1.0
                phase += (freq * vib) / SAMPLE_RATE
                
                env = adsr(t_note, dur_t, attack=0.008, decay=0.04, sustain_level=0.75, release=0.02)
                buffer[i] += pulse_sample(phase, duty) * env * volume
        return buffer

    def render_arp(self, chords_events, duty=0.25, volume=0.25, pattern=(0, 1, 2, 1)):
        buffer = [0.0] * self.num_samples
        for start_step, dur_steps, chord in chords_events:
            start_t = start_step * self.step_sec
            dur_t = dur_steps * self.step_sec
            start_idx = int(start_t * SAMPLE_RATE)
            end_idx = min(self.num_samples, int((start_t + dur_t) * SAMPLE_RATE))
            
            chord_notes = [note_freq(n) for n in chord]
            if not chord_notes:
                continue
            phase = 0.0
            
            for i in range(start_idx, end_idx):
                t_rel = (i - start_idx) / SAMPLE_RATE
                step_idx = int(t_rel / self.step_sec)
                note_i = pattern[step_idx % len(pattern)] % len(chord_notes)
                f = chord_notes[note_i]
                
                t_sub = (t_rel % self.step_sec)
                env = adsr(t_sub, self.step_sec, attack=0.005, decay=0.02, sustain_level=0.6, release=0.015)
                phase += f / SAMPLE_RATE
                buffer[i] += pulse_sample(phase, duty) * env * volume
        return buffer

    def render_bass(self, bass_events, volume=0.45):
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
                env = adsr(t_note, dur_t, attack=0.005, decay=0.06, sustain_level=0.8, release=0.02)
                buffer[i] += triangle_sample(phase) * env * volume
        return buffer

    def render_drums(self, drum_events, volume=0.35):
        buffer = [0.0] * self.num_samples
        rng = random.Random(42)
        
        for start_step, drum_type in drum_events:
            start_t = start_step * self.step_sec
            start_idx = int(start_t * SAMPLE_RATE)
            
            if drum_type == 'K':  # Kick
                dur = 0.09
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                phase = 0.0
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    f = 40.0 + 120.0 * (1.0 - t / dur) ** 2
                    phase += f / SAMPLE_RATE
                    env = (1.0 - t / dur) ** 1.5
                    click = (rng.random() * 2.0 - 1.0) * 0.3 if t < 0.01 else 0.0
                    buffer[i] += (triangle_sample(phase) + click) * env * (volume * 1.1)
                    
            elif drum_type == 'S':  # Snare
                dur = 0.13
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                phase = 0.0
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    f = 140.0 * (1.0 - t / dur)
                    phase += f / SAMPLE_RATE
                    body = triangle_sample(phase) * 0.4 * (1.0 - t / dur)
                    noise = (rng.random() * 2.0 - 1.0) * ((1.0 - t / dur) ** 2)
                    buffer[i] += (noise + body) * (volume * 0.9)
                    
            elif drum_type == 'H':  # Closed Hi-Hat
                dur = 0.04
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    noise = (rng.random() * 2.0 - 1.0) * ((1.0 - t / dur) ** 3)
                    buffer[i] += noise * (volume * 0.45)

            elif drum_type == 'O':  # Open Hi-Hat
                dur = 0.12
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    noise = (rng.random() * 2.0 - 1.0) * ((1.0 - t / dur) ** 1.8)
                    buffer[i] += noise * (volume * 0.5)
                    
            elif drum_type == 'C':  # Crash
                dur = 0.40
                end_idx = min(self.num_samples, int((start_t + dur) * SAMPLE_RATE))
                for i in range(start_idx, end_idx):
                    t = (i - start_idx) / SAMPLE_RATE
                    noise = (rng.random() * 2.0 - 1.0) * ((1.0 - t / dur) ** 2)
                    buffer[i] += noise * (volume * 0.6)
        return buffer

def mix_and_export_mp3(lead, arp, bass, drums, output_file, bitrate=192):
    num_samples = len(lead)
    stereo_pcm = bytearray()
    max_amp = 0.0001
    mixed_l = [0.0] * num_samples
    mixed_r = [0.0] * num_samples
    delay_samples = int(0.12 * SAMPLE_RATE)
    
    for i in range(num_samples):
        l_lead = lead[i] * 0.85
        r_lead = lead[i] * 0.75
        
        l_arp = arp[i] * 0.5
        r_arp = arp[i] * 0.85
        if i >= delay_samples:
            l_arp += arp[i - delay_samples] * 0.25
        
        l_bass = bass[i] * 0.8
        r_bass = bass[i] * 0.8
        l_drums = drums[i] * 0.8
        r_drums = drums[i] * 0.8
        
        sl = l_lead + l_arp + l_bass + l_drums
        sr = r_lead + r_arp + r_bass + r_drums
        mixed_l[i] = sl
        mixed_r[i] = sr
        max_amp = max(max_amp, abs(sl), abs(sr))
        
    target_gain = 0.92 / max_amp
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

def build_drums_for_bars(total_bars, crash_bars=(0, 4, 12, 20, 28)):
    drums = []
    for b in range(total_bars):
        bar_start = b * 16
        if b in crash_bars:
            drums.append((bar_start, 'C'))
        for step in range(16):
            s = bar_start + step
            if step in (0, 8):
                drums.append((s, 'K'))
            elif step in (4, 12):
                drums.append((s, 'S'))
            if step in (2, 6, 10):
                drums.append((s, 'H'))
            elif step == 14:
                if (b + 1) % 4 == 0 and step >= 12:
                    drums.append((s, 'S'))
                else:
                    drums.append((s, 'O'))
    return drums

def generate_track_1(output_path):
    print(f"Generating Track 1 (Cetraminos Rush) -> {output_path}...")
    bpm = 152
    total_bars = 32
    builder = TrackBuilder(bpm=bpm, total_bars=total_bars)
    drums = build_drums_for_bars(total_bars, crash_bars=(0, 4, 12, 20, 28))
    
    bar_chords = [
        ('Am', 'A2', ['A3', 'C4', 'E4', 'A4']),
        ('F',  'F2', ['F3', 'A3', 'C4', 'F4']),
        ('C',  'C3', ['C3', 'E3', 'G3', 'C4']),
        ('G',  'G2', ['G3', 'B3', 'D4', 'G4']),
        ('Am', 'A2', ['A3', 'C4', 'E4', 'A4']),
        ('Dm', 'D2', ['D3', 'F3', 'A3', 'D4']),
        ('G',  'G2', ['G3', 'B3', 'D4', 'G4']),
        ('C',  'C3', ['C3', 'E3', 'G3', 'C4']),
        ('F',  'F2', ['F3', 'A3', 'C4', 'F4']),
        ('Dm', 'D2', ['D3', 'F3', 'A3', 'D4']),
        ('E',  'E2', ['E3', 'G#3', 'B3', 'E4']),
        ('E7', 'E2', ['E3', 'G#3', 'D4', 'E4']),
        ('Am', 'A2', ['A3', 'C4', 'E4', 'A4']),
        ('F',  'F2', ['F3', 'A3', 'C4', 'F4']),
        ('G',  'G2', ['G3', 'B3', 'D4', 'G4']),
        ('Em', 'E2', ['E3', 'G3', 'B3', 'E4']),
        ('F',  'F2', ['F3', 'A3', 'C4', 'F4']),
        ('Dm', 'D2', ['D3', 'F3', 'A3', 'D4']),
        ('E',  'E2', ['E3', 'G#3', 'B3', 'E4']),
        ('E',  'E2', ['E3', 'G#3', 'B3', 'E4']),
        ('C',  'C3', ['C3', 'E3', 'G3', 'C4']),
        ('G',  'G2', ['G3', 'B3', 'D4', 'G4']),
        ('Am', 'A2', ['A3', 'C4', 'E4', 'A4']),
        ('Em', 'E2', ['E3', 'G3', 'B3', 'E4']),
        ('F',  'F2', ['F3', 'A3', 'C4', 'F4']),
        ('C',  'C3', ['C3', 'E3', 'G3', 'C4']),
        ('Dm', 'D2', ['D3', 'F3', 'A3', 'D4']),
        ('E',  'E2', ['E3', 'G#3', 'B3', 'E4']),
        ('F',  'F2', ['F3', 'A3', 'C4', 'F4']),
        ('G',  'G2', ['G3', 'B3', 'D4', 'G4']),
        ('E',  'E2', ['E3', 'G#3', 'B3', 'E4']),
        ('Am', 'A2', ['A3', 'C4', 'E4', 'A4']),
    ]
    
    bass = []
    for b_idx, (name, root, chord_notes) in enumerate(bar_chords):
        base_step = b_idx * 16
        octave_root = transpose_octave(root, 1)
        fifth = chord_notes[2][:-1] + root[-1]
        pattern = [root, octave_root, root, fifth, root, octave_root, fifth, root]
        for s_idx, note_name in enumerate(pattern):
            bass.append((base_step + s_idx * 2, 2, note_name))
            
    arps = []
    for b_idx, (name, root, chord_notes) in enumerate(bar_chords):
        arps.append((b_idx * 16, 16, chord_notes))
        
    leads = [
        (2 * 16 + 8, 4, 'E4'), (2 * 16 + 12, 4, 'G4'),
        (3 * 16 + 0, 4, 'A4'), (3 * 16 + 4, 4, 'B4'),
        (3 * 16 + 8, 4, 'C5'), (3 * 16 + 12, 4, 'B4'),
        (4 * 16 + 0, 3, 'A4'), (4 * 16 + 3, 3, 'C5'), (4 * 16 + 6, 4, 'E5'), (4 * 16 + 10, 3, 'D5'), (4 * 16 + 13, 3, 'C5'),
        (5 * 16 + 0, 4, 'D5'), (5 * 16 + 4, 4, 'F5'), (5 * 16 + 8, 4, 'E5'), (5 * 16 + 12, 4, 'D5'),
        (6 * 16 + 0, 4, 'B4'), (6 * 16 + 4, 4, 'D5'), (6 * 16 + 8, 4, 'C5'), (6 * 16 + 12, 4, 'B4'),
        (7 * 16 + 0, 6, 'C5'), (7 * 16 + 6, 6, 'E5'), (7 * 16 + 12, 4, 'G5'),
        (8 * 16 + 0, 4, 'A5'), (8 * 16 + 4, 4, 'F5'), (8 * 16 + 8, 4, 'E5'), (8 * 16 + 12, 4, 'D5'),
        (9 * 16 + 0, 4, 'F5'), (9 * 16 + 4, 4, 'D5'), (9 * 16 + 8, 4, 'C5'), (9 * 16 + 12, 4, 'B4'),
        (10 * 16 + 0, 4, 'G#4'), (10 * 16 + 4, 4, 'B4'), (10 * 16 + 8, 4, 'E5'), (10 * 16 + 12, 4, 'D5'),
        (11 * 16 + 0, 4, 'C5'), (11 * 16 + 4, 4, 'B4'), (11 * 16 + 8, 4, 'A4'), (11 * 16 + 12, 4, 'G#4'),
        (12 * 16 + 0, 4, 'A5'), (12 * 16 + 4, 2, 'G5'), (12 * 16 + 6, 2, 'A5'), (12 * 16 + 8, 4, 'E5'), (12 * 16 + 12, 4, 'C5'),
        (13 * 16 + 0, 4, 'F5'), (13 * 16 + 4, 2, 'E5'), (13 * 16 + 6, 2, 'F5'), (13 * 16 + 8, 4, 'A5'), (13 * 16 + 12, 4, 'F5'),
        (14 * 16 + 0, 4, 'G5'), (14 * 16 + 4, 2, 'F5'), (14 * 16 + 6, 2, 'G5'), (14 * 16 + 8, 4, 'D5'), (14 * 16 + 12, 4, 'B4'),
        (15 * 16 + 0, 4, 'E5'), (15 * 16 + 4, 2, 'D5'), (15 * 16 + 6, 2, 'E5'), (15 * 16 + 8, 4, 'G5'), (15 * 16 + 12, 4, 'E5'),
        (16 * 16 + 0, 4, 'C5'), (16 * 16 + 4, 4, 'D5'), (16 * 16 + 8, 4, 'E5'), (16 * 16 + 12, 4, 'F5'),
        (17 * 16 + 0, 4, 'D5'), (17 * 16 + 4, 4, 'E5'), (17 * 16 + 8, 4, 'F5'), (17 * 16 + 12, 4, 'A5'),
        (18 * 16 + 0, 4, 'B5'), (18 * 16 + 4, 4, 'A5'), (18 * 16 + 8, 4, 'G#5'), (18 * 16 + 12, 4, 'F#5'),
        (19 * 16 + 0, 4, 'E5'), (19 * 16 + 4, 4, 'G#5'), (19 * 16 + 8, 4, 'B5'), (19 * 16 + 12, 4, 'D6'),
        (20 * 16 + 0, 4, 'C6'), (20 * 16 + 4, 4, 'G5'), (20 * 16 + 8, 4, 'E5'), (20 * 16 + 12, 4, 'C5'),
        (21 * 16 + 0, 4, 'B5'), (21 * 16 + 4, 4, 'G5'), (21 * 16 + 8, 4, 'D5'), (21 * 16 + 12, 4, 'B4'),
        (22 * 16 + 0, 4, 'A5'), (22 * 16 + 4, 4, 'E5'), (22 * 16 + 8, 4, 'C5'), (22 * 16 + 12, 4, 'A4'),
        (23 * 16 + 0, 4, 'G5'), (23 * 16 + 4, 4, 'E5'), (23 * 16 + 8, 4, 'B4'), (23 * 16 + 12, 4, 'G4'),
        (24 * 16 + 0, 4, 'A5'), (24 * 16 + 4, 4, 'C6'), (24 * 16 + 8, 4, 'A5'), (24 * 16 + 12, 4, 'F5'),
        (25 * 16 + 0, 4, 'G5'), (25 * 16 + 4, 4, 'C6'), (25 * 16 + 8, 4, 'G5'), (25 * 16 + 12, 4, 'E5'),
        (26 * 16 + 0, 4, 'F5'), (26 * 16 + 4, 4, 'A5'), (26 * 16 + 8, 4, 'F5'), (26 * 16 + 12, 4, 'D5'),
        (27 * 16 + 0, 4, 'E5'), (27 * 16 + 4, 4, 'G#5'), (27 * 16 + 8, 4, 'B5'), (27 * 16 + 12, 4, 'E6'),
        (28 * 16 + 0, 4, 'F6'), (28 * 16 + 4, 4, 'E6'), (28 * 16 + 8, 4, 'D6'), (28 * 16 + 12, 4, 'C6'),
        (29 * 16 + 0, 4, 'D6'), (29 * 16 + 4, 4, 'C6'), (29 * 16 + 8, 4, 'B5'), (29 * 16 + 12, 4, 'A5'),
        (30 * 16 + 0, 4, 'B5'), (30 * 16 + 4, 4, 'C6'), (30 * 16 + 8, 4, 'D6'), (30 * 16 + 12, 4, 'B5'),
        (31 * 16 + 0, 8, 'A5'), (31 * 16 + 8, 4, 'E5'), (31 * 16 + 12, 4, 'C5'),
    ]
    
    lead_buf = builder.render_lead(leads, duty=0.5, vibrato_speed=6.2, vibrato_depth=0.018, volume=0.38)
    arp_buf = builder.render_arp(arps, duty=0.25, volume=0.22, pattern=(0, 1, 2, 3, 2, 1, 0, 1))
    bass_buf = builder.render_bass(bass, volume=0.48)
    drum_buf = builder.render_drums(drums, volume=0.40)
    mix_and_export_mp3(lead_buf, arp_buf, bass_buf, drum_buf, output_path, bitrate=192)

def generate_track_2(output_path):
    print(f"Generating Track 2 (Cetraminos Cyber Pulse) -> {output_path}...")
    bpm = 140
    total_bars = 32
    builder = TrackBuilder(bpm=bpm, total_bars=total_bars)
    drums = build_drums_for_bars(total_bars, crash_bars=(0, 4, 12, 20, 28))
    
    bar_chords = [
        ('Dm', 'D2', ['D3', 'F3', 'A3', 'D4']),
        ('Bb', 'Bb1', ['D3', 'F3', 'Bb3', 'D4']),
        ('C',  'C2', ['C3', 'E3', 'G3', 'C4']),
        ('Am', 'A1', ['C3', 'E3', 'A3', 'C4']),
        ('Dm', 'D2', ['D3', 'F3', 'A3', 'D4']),
        ('Bb', 'Bb1', ['D3', 'F3', 'Bb3', 'D4']),
        ('F',  'F1', ['C3', 'F3', 'A3', 'C4']),
        ('C',  'C2', ['C3', 'E3', 'G3', 'C4']),
    ] * 4
    
    bass = []
    for b_idx, (name, root, chord_notes) in enumerate(bar_chords):
        base_step = b_idx * 16
        octave_root = transpose_octave(root, 1)
        for s in range(16):
            if s % 4 != 1:
                n = root if (s % 2 == 0) else octave_root
                bass.append((base_step + s, 1, n))
                
    arps = []
    for b_idx, (name, root, chord_notes) in enumerate(bar_chords):
        arps.append((b_idx * 16, 16, chord_notes))
        
    leads = []
    for section in range(2):
        sec_start = (section * 16 + 4) * 16
        leads.extend([
            (sec_start + 0 * 16 + 0, 4, 'D5'), (sec_start + 0 * 16 + 4, 4, 'F5'), (sec_start + 0 * 16 + 8, 4, 'A5'), (sec_start + 0 * 16 + 12, 4, 'G5'),
            (sec_start + 1 * 16 + 0, 6, 'F5'), (sec_start + 1 * 16 + 6, 2, 'D5'), (sec_start + 1 * 16 + 8, 4, 'Bb4'), (sec_start + 1 * 16 + 12, 4, 'C5'),
            (sec_start + 2 * 16 + 0, 4, 'E5'), (sec_start + 2 * 16 + 4, 4, 'G5'), (sec_start + 2 * 16 + 8, 4, 'F5'), (sec_start + 2 * 16 + 12, 4, 'E5'),
            (sec_start + 3 * 16 + 0, 6, 'C5'), (sec_start + 3 * 16 + 6, 2, 'A4'), (sec_start + 3 * 16 + 8, 4, 'C5'), (sec_start + 3 * 16 + 12, 4, 'E5'),
            (sec_start + 4 * 16 + 0, 4, 'F5'), (sec_start + 4 * 16 + 4, 4, 'A5'), (sec_start + 4 * 16 + 8, 4, 'D6'), (sec_start + 4 * 16 + 12, 4, 'C6'),
            (sec_start + 5 * 16 + 0, 4, 'D6'), (sec_start + 5 * 16 + 4, 4, 'Bb5'), (sec_start + 5 * 16 + 8, 4, 'A5'), (sec_start + 5 * 16 + 12, 4, 'G5'),
            (sec_start + 6 * 16 + 0, 4, 'A5'), (sec_start + 6 * 16 + 4, 4, 'C6'), (sec_start + 6 * 16 + 8, 4, 'A5'), (sec_start + 6 * 16 + 12, 4, 'F5'),
            (sec_start + 7 * 16 + 0, 4, 'G5'), (sec_start + 7 * 16 + 4, 4, 'E5'), (sec_start + 7 * 16 + 8, 4, 'C5'), (sec_start + 7 * 16 + 12, 4, 'A4'),
        ])
        
    lead_buf = builder.render_lead(leads, duty=0.25, vibrato_speed=5.5, vibrato_depth=0.015, volume=0.36)
    arp_buf = builder.render_arp(arps, duty=0.5, volume=0.24, pattern=(0, 2, 1, 3, 2, 0, 1, 2))
    bass_buf = builder.render_bass(bass, volume=0.46)
    drum_buf = builder.render_drums(drums, volume=0.40)
    mix_and_export_mp3(lead_buf, arp_buf, bass_buf, drum_buf, output_path, bitrate=192)

if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '/home/cloud/my_projects/Cetraminos/Cetraminos/src'
    t1_path = os.path.join(target_dir, 'CetraminosMusic.mp3')
    t2_path = os.path.join(target_dir, 'CetraminosMusic2.mp3')
    
    generate_track_1(t1_path)
    generate_track_2(t2_path)
    print(f"\n[✓] Both tracks synthesized into: {target_dir}")
