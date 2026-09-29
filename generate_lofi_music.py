import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal

def generate_upbeat_lofi(filename="lofi_background_music.wav", duration_sec=45.0, bpm=86.0):
    sample_rate = 44100
    total_samples = int(sample_rate * duration_sec)
    
    sec_per_beat = 60.0 / bpm
    sec_per_measure = sec_per_beat * 4.0
    num_measures = int(np.ceil(duration_sec / sec_per_measure))
    
    # Note frequencies (Hz)
    notes = {
        'C3': 130.81, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99
    }
    
    # Chords progression: Cmaj7 -> Am7 -> Dm7 -> G7
    chords = [
        ['C4', 'E4', 'G4', 'B4'],  # Cmaj7
        ['A3', 'C4', 'E4', 'G4'],  # Am7
        ['D4', 'F4', 'A4', 'C5'],  # Dm7
        ['G3', 'B3', 'D4', 'F4']   # G7
    ]
    
    bass_notes = ['C3', 'A3', 'D3', 'G3']
    bass_freqs = [130.81/2, 220.00/2, 146.83/2, 196.00/2]
    
    # Buffer initialization
    left = np.zeros(total_samples, dtype=np.float64)
    right = np.zeros(total_samples, dtype=np.float64)
    
    t_full = np.arange(total_samples) / sample_rate
    
    # 1. Generate Rhodes Electric Piano Chords
    for m in range(num_measures):
        measure_start_t = m * sec_per_measure
        chord = chords[m % len(chords)]
        
        # Strum/Arpeggio timing within measure (e.g., hit on beat 1 and beat 2.5)
        hit_offsets = [0.0, sec_per_beat * 1.5, sec_per_beat * 3.0]
        for offset in hit_offsets:
            hit_t = measure_start_t + offset
            if hit_t >= duration_sec:
                continue
            
            start_idx = int(hit_t * sample_rate)
            dur = sec_per_beat * 2.2
            num_s = int(dur * sample_rate)
            end_idx = min(start_idx + num_s, total_samples)
            actual_len = end_idx - start_idx
            if actual_len <= 0:
                continue
            
            t_env = np.arange(actual_len) / sample_rate
            # ADSR envelope
            attack = 0.015
            decay = 1.0
            env = np.where(t_env < attack, t_env / attack, np.exp(-(t_env - attack) / decay))
            
            # Rhodes sound generation (harmonics + tremolo)
            chord_sig_l = np.zeros(actual_len)
            chord_sig_r = np.zeros(actual_len)
            
            for idx, note_name in enumerate(chord):
                f = notes[note_name]
                # Slight detuning & panning for warmth
                pan = 0.3 + 0.4 * (idx / (len(chord) - 1)) # 0.3 to 0.7
                
                # Tremolo LFO
                lfo = 1.0 + 0.12 * np.sin(2 * np.pi * 5.5 * t_env)
                
                # Harmonics
                tone = (1.00 * np.sin(2 * np.pi * f * t_env) +
                        0.35 * np.sin(2 * np.pi * f * 2 * t_env) +
                        0.12 * np.sin(2 * np.pi * f * 3 * t_env) +
                        0.04 * np.sin(2 * np.pi * f * 4 * t_env))
                
                wave = tone * env * lfo * 0.12
                chord_sig_l += wave * (1.0 - pan)
                chord_sig_r += wave * pan
                
            left[start_idx:end_idx] += chord_sig_l
            right[start_idx:end_idx] += chord_sig_r

    # 2. Generate Bassline
    for m in range(num_measures):
        measure_start_t = m * sec_per_measure
        bfreq = bass_freqs[m % len(bass_freqs)]
        
        bass_hits = [0.0, sec_per_beat * 1.5, sec_per_beat * 2.0, sec_per_beat * 3.5]
        for b_off in bass_hits:
            hit_t = measure_start_t + b_off
            if hit_t >= duration_sec:
                continue
            start_idx = int(hit_t * sample_rate)
            num_s = int(sec_per_beat * 1.2 * sample_rate)
            end_idx = min(start_idx + num_s, total_samples)
            actual_len = end_idx - start_idx
            if actual_len <= 0:
                continue
            
            t_env = np.arange(actual_len) / sample_rate
            env = np.exp(-t_env / 0.6)
            
            bass_wave = (np.sin(2 * np.pi * bfreq * t_env) + 0.2 * np.sin(2 * np.pi * bfreq * 2 * t_env)) * env * 0.22
            left[start_idx:end_idx] += bass_wave
            right[start_idx:end_idx] += bass_wave

    # 3. Generate Upbeat Lo-Fi Drum Beat (Kick, Snare, Hi-Hat)
    total_beats = int(np.ceil(duration_sec / sec_per_beat))
    for b in range(total_beats):
        beat_t = b * sec_per_beat
        beat_in_meas = b % 4
        
        # Kick on Beat 1, Beat 3 (with swing beat 3.5)
        kicks = [beat_t] if beat_in_meas in [0, 2] else []
        if beat_in_meas == 2:
            kicks.append(beat_t + sec_per_beat * 0.75) # syncopated kick
            
        for kt in kicks:
            if kt >= duration_sec:
                continue
            start_idx = int(kt * sample_rate)
            num_s = int(0.25 * sample_rate)
            end_idx = min(start_idx + num_s, total_samples)
            actual_len = end_idx - start_idx
            if actual_len <= 0:
                continue
            t_k = np.arange(actual_len) / sample_rate
            freq_sweep = 110.0 * np.exp(-t_k / 0.04) + 45.0
            phase = 2 * np.pi * np.cumsum(freq_sweep) / sample_rate
            kick_wave = np.sin(phase) * np.exp(-t_k / 0.08) * 0.45
            left[start_idx:end_idx] += kick_wave
            right[start_idx:end_idx] += kick_wave
            
        # Snare / Rimshot on Beat 2 and 4
        if beat_in_meas in [1, 3]:
            st = beat_t
            if st < duration_sec:
                start_idx = int(st * sample_rate)
                num_s = int(0.2 * sample_rate)
                end_idx = min(start_idx + num_s, total_samples)
                actual_len = end_idx - start_idx
                if actual_len > 0:
                    t_s = np.arange(actual_len) / sample_rate
                    # Noise body + tonal snap
                    noise = np.random.normal(0, 1, actual_len)
                    b_filter, a_filter = signal.butter(2, [800 / (sample_rate/2), 4500 / (sample_rate/2)], btype='band')
                    filt_noise = signal.lfilter(b_filter, a_filter, noise)
                    snap = np.sin(2 * np.pi * 180 * t_s) * np.exp(-t_s / 0.03)
                    snare_wave = (filt_noise * np.exp(-t_s / 0.12) * 0.7 + snap * 0.4) * 0.28
                    left[start_idx:end_idx] += snare_wave
                    right[start_idx:end_idx] += snare_wave
                    
        # Hi-Hats on 8th notes with swing
        hat_offsets = [0.0, sec_per_beat * 0.5 + 0.02] # 0.02s swing!
        for h_off in hat_offsets:
            ht = beat_t + h_off
            if ht < duration_sec:
                start_idx = int(ht * sample_rate)
                num_s = int(0.06 * sample_rate)
                end_idx = min(start_idx + num_s, total_samples)
                actual_len = end_idx - start_idx
                if actual_len > 0:
                    t_h = np.arange(actual_len) / sample_rate
                    noise = np.random.normal(0, 1, actual_len)
                    b_filter, a_filter = signal.butter(2, 5000 / (sample_rate/2), btype='highpass')
                    filt_noise = signal.lfilter(b_filter, a_filter, noise)
                    hat_wave = filt_noise * np.exp(-t_h / 0.03) * 0.09
                    # Pan hats slightly to left
                    left[start_idx:end_idx] += hat_wave * 0.7
                    right[start_idx:end_idx] += hat_wave * 0.4

    # 4. Vinyl crackle & low-pass filtering for lo-fi aesthetic
    crackle = np.random.normal(0, 0.008, total_samples)
    # Add random clicks
    pop_indices = np.random.choice(total_samples, size=int(duration_sec * 8), replace=False)
    crackle[pop_indices] += np.random.uniform(0.04, 0.12, size=len(pop_indices))
    
    b_lp, a_lp = signal.butter(2, 3200 / (sample_rate/2), btype='lowpass')
    left = signal.lfilter(b_lp, a_lp, left + crackle)
    right = signal.lfilter(b_lp, a_lp, right + crackle)
    
    # 5. Master compression / soft clipping (tanh)
    left = np.tanh(left * 1.5) * 0.8
    right = np.tanh(right * 1.5) * 0.8
    
    # Convert to 16-bit PCM WAV
    audio_stereo = np.column_stack((left, right))
    audio_pcm = np.int16(audio_stereo * 32767)
    
    wav.write(filename, sample_rate, audio_pcm)
    print(f"Upbeat lo-fi track generated successfully: {filename} ({duration_sec}s)")

if __name__ == "__main__":
    generate_upbeat_lofi()
