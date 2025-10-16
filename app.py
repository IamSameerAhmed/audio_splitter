import os
import math
import tempfile
import zipfile
from io import BytesIO
from pydub import AudioSegment
import streamlit as st
from pydub.utils import which
AudioSegment.converter = which(r"C:\ffmpeg\bin\ffmpeg.exe")
AudioSegment.ffprobe = which(r"C:\ffmpeg\bin\ffprobe.exe")


# --------------------
# CONFIG
# --------------------
st.set_page_config(page_title="Audio Splitter", layout="wide")

st.title("🎵 Audio Splitter App")
st.write("Split long audio files into smaller clips using open-source libraries — works fully offline!")

# --------------------
# USER INPUT
# --------------------
uploaded_file = st.file_uploader("Upload an audio file (MP3, WAV, etc.)", type=["mp3", "wav", "ogg", "flac"])
clip_length_min = st.number_input("Enter desired clip length (minutes)", min_value=1, max_value=60, value=3)
output_format = st.selectbox("Select output format", ["mp3", "wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/mp3')
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    # --------------------
    # PROCESSING
    # --------------------
    if st.button("Split Audio"):
        st.info("Processing... please wait.")
        audio = AudioSegment.from_file(input_path)
        duration_ms = len(audio)
        clip_length_ms = clip_length_min * 60 * 1000
        total_clips = math.ceil(duration_ms / clip_length_ms)

        progress = st.progress(0)
        output_files = []

        for i in range(total_clips):
            start = i * clip_length_ms
            end = min(start + clip_length_ms, duration_ms)
            clip = audio[start:end]

            output_filename = f"clip_{i+1}.{output_format}"
            output_path = os.path.join(temp_dir, output_filename)
            clip.export(output_path, format=output_format)
            output_files.append(output_path)

            progress.progress((i+1)/total_clips)

        st.success(f"✅ Done! {total_clips} clips created.")

        # --------------------
        # DOWNLOADS
        # --------------------
        with zipfile.ZipFile(os.path.join(temp_dir, "clips.zip"), "w") as zipf:
            for file in output_files:
                zipf.write(file, os.path.basename(file))

        with open(os.path.join(temp_dir, "clips.zip"), "rb") as zipf:
            st.download_button("📦 Download All Clips (ZIP)", data=zipf, file_name="audio_clips.zip")

        # Preview individual clips
        with st.expander("🎧 Preview Individual Clips"):
            for i, file in enumerate(output_files):
                st.audio(file, format=f"audio/{output_format}")
                with open(file, "rb") as f:
                    st.download_button(f"Download Clip {i+1}", data=f, file_name=os.path.basename(file))

else:
    st.warning("Please upload an audio file to begin.")
