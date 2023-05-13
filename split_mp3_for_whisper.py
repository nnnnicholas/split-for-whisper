import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

# Load the long MP3 file
audio_file_path = "path_to_your_audio_file.mp3"
audio = AudioSegment.from_mp3(audio_file_path)

# Find the points where silence occurs, split on those points
min_silence_len = 500  # Adjust this value if needed (in milliseconds)
silence_thresh = -30  # Adjust this value according to your background noise (in dBFS)

nonsilent_chunks = detect_nonsilent(audio, min_silence_len, silence_thresh, seek_step=1)

chunks = []
start_point = 0
for chunk in nonsilent_chunks:
    if chunk[0] - start_point > 1:
        chunks.append(audio[start_point:chunk[0]])
    start_point = chunk[1]
chunks.append(audio[start_point:])

# Save each chunk to a separate file
base_filename, file_extension = os.path.splitext(audio_file_path)
for i, chunk in enumerate(chunks):
    output_filename = f"{base_filename}_chunk{i}{file_extension}"
    
    while len(chunk.raw_data) > 25 * 1024 * 1024:  # While chunk size is more than 25MB
        half = len(chunk) // 2  # Find the middle point
        chunk_1 = chunk[:half]  # First half
        chunk_2 = chunk[half:]  # Second half
        
        # Check which half is less than 25MB, save it and continue with the other half
        if len(chunk_1.raw_data) < 25 * 1024 * 1024:
            chunk_1.export(output_filename, format="mp3")
            chunk = chunk_2
        elif len(chunk_2.raw_data) < 25 * 1024 * 1024:
            chunk_2.export(f"{base_filename}_chunk{i+1}{file_extension}", format="mp3")
            chunk = chunk_1
        else:  # If both halves are more than 25MB, just split in the middle
            chunk_1.export(output_filename, format="mp3")
            chunk = chunk_2
            
    # Save the chunk that is now less than 25MB
    chunk.export(output_filename, format="mp3")
