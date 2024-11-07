from openai import OpenAI
import os
import streamlit as st
from gtts import gTTS
import soundfile as sf
import io
import tempfile
from sklearn.metrics.pairwise import cosine_similarity
import assemblyai as aai
import numpy as np


MODEL_VERSION = "gpt-4o-mini"
TEXT_MODEL = "text-embedding-ada-002"

# set up your OpenAI API key and Assembly AI key
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["ASSEMBLYAI_API_KEY"] = st.secrets["ASSEMBLYAI_API_KEY"]

# openai client creation
client = OpenAI()

# get embeddings
def get_openai_embeddings(text: str) -> list[float]:
    response = client.embeddings.create(input=text, model=TEXT_MODEL)

    return response.data[0].embedding


# generate a random sentence
def generate_random_sentence():

    response = client.chat.completions.create(
        model=MODEL_VERSION,
        messages=[{"role": "user", "content": "Please generate a random sentence"}],
        temperature = 0.8
    )

    # extract the generated text
    sentence = response.choices[0].message.content
    return sentence


# function to create an audio using a text part
def create_audio(sentence):
    tts = gTTS(sentence, lang='en')

    # Create a temporary file to save the audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        # Use an in-memory buffer
        with io.BytesIO() as f:
            # Save the audio to an in-memory file in MP3 format
            tts.write_to_fp(f)
            f.seek(0)

            # Read the audio data from the buffer
            audio_data, sample_rate = sf.read(f)

            # Save the data to the temporary WAV file
            sf.write(tmp_file.name, audio_data, sample_rate)

    return tmp_file


# function to save the audio as a wav
def save_audio_wav(audio_bytes, file_name):
    with open(file_name, 'wb') as new_wav_file:
        new_wav_file.write(audio_bytes)


# function get the transcript
def get_transcript(file_path):
    aai.settings.api_key = os.environ["ASSEMBLYAI_API_KEY"]
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_path)
    if transcript.status == aai.TranscriptStatus.error:
        return None
    else:
        return transcript.text


# caluclate cosine similarity
def cal_cosine(sent_one, sent_two):
    sent_one_embed = get_openai_embeddings(sent_one)
    sent_two_embed = get_openai_embeddings(sent_two)

    # convert to numpy and reshape
    array_one = np.array(sent_one_embed).reshape(1, -1)
    array_two = np.array(sent_two_embed).reshape(1, -1)

    # calculate cosine similarity
    cos_sim = cosine_similarity(array_one, array_two)

    return cos_sim[0][0]

