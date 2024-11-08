import streamlit as st
from streamlit_mic_recorder import mic_recorder

from Utils import generate_random_sentence, create_audio, save_audio_wav, get_transcript, cal_cosine, senetnce_comparer


# constants
IMAGE_ADDRESS = "https://img.freepik.com/free-vector/hand-drawn-speech-therapy-scenes-collection_52683-78405.jpg"
AUDIO_FILE = "output.wav"
SCORE_BENCHMARK = 0.98
GUIDES = [
    "App will generate a random sentence and its audio. You can play the audio or view the sentence or you can do both.",
    "The you can click on the **Start Recording** button and start speaking out the text you see.",
    "Then click on **Stop Recording** to start the evaluations.",
    "Based on the evaluation you can start again if you like."
]


# functions
def shuffle_sentence_and_disable_audio():
    st.session_state.random_sentence = ""
    st.session_state.recorder = False


def recreate_audio_recorder_session():
    st.session_state.recorder = True


def disable_audio_recorder_session():
    st.session_state.recorder = False


def markdown_creators(*args):
    for chunks in args:
        st.markdown(f"- {chunks}")


# Initialize session state variables
if 'random_sentence' not in st.session_state:
    st.session_state.random_sentence = ""

if 'recorder' not in st.session_state:
    st.session_state.recorder = False


# title of the web app
st.title("Speech Therapist")

# web image
st.image(IMAGE_ADDRESS, caption = "Speech Therapist")

# project steps
st.subheader("User Guide: How to Use the App 📒")
markdown_creators(*GUIDES)

# generated audio and sentence
st.header("Generated Audio and Senetence 🆎")
if not st.session_state.random_sentence:
    # generate a sentence using openai
    text_output = generate_random_sentence()
    # get the audio
    audio_output = create_audio(text_output)
    # set the session state
    st.session_state.random_sentence = text_output
    # set the audio
    st.audio(audio_output.name, format='audio/wav')
    st.header("Transcript")
    st.subheader(text_output)
else:
    # in case when the web app re runs, stays with the same data
    audio_rerun_output = create_audio(st.session_state.random_sentence)
    # create the audio from the same text and display
    st.audio(audio_rerun_output.name, format='audio/wav')
    st.header("Transcript")
    st.subheader(st.session_state.random_sentence)
        

# start recording
st.header("Record ⏺️")
# mic
audio = mic_recorder(
    start_prompt="Start Recording 🎙️",
    stop_prompt="Stop Recording 🛑",
    just_once=False,
    use_container_width=False,
    callback=recreate_audio_recorder_session,
    args=(),
    kwargs={},
    key=None
)
if st.session_state.recorder:
    if audio:
        # ssve the audio
        save_audio_wav(audio['bytes'], AUDIO_FILE)
        st.audio(audio['bytes'])

        # evaluating the responses
        with st.spinner("Evaulating Your Response..... ✅"):
            # get the transcript
            user_audio_transcript = get_transcript(AUDIO_FILE)
            if not user_audio_transcript:
                st.error("Ouch..Error has occured! Please contact the developer.", icon = "🛑")
                st.stop()
            # calculate the cosine similarity
            cosine_score = cal_cosine(user_audio_transcript, st.session_state.random_sentence)

        # evaluations
        st.header("Evaluations 🗒")
        if cosine_score > SCORE_BENCHMARK:
            st.subheader("Good Work Mate! 😍")
            st.subheader("Your score is {}".format(cosine_score))
            st.markdown("### Your Transcript!")
            st.write("Missing/Incorrect words are highlighted in red color for you!")
            st.markdown(f"#### {senetnce_comparer(user_audio_transcript, st.session_state.random_sentence)}")
            st.subheader("You have Good Speaking Capabilities! Keep up ✅")
            # create a button re try
            st.button("Wanna Tray Again 🤔", on_click=shuffle_sentence_and_disable_audio, key='success_btn')
        else:
            st.header("Having Little Bit of Trouble! 🤗")
            st.subheader("Your score is {}".format(cosine_score))
            st.markdown("### Your Transcript!")
            st.write("Missing/Incorrect words are highlighted in red color for you!")
            st.markdown(f"#### {senetnce_comparer(user_audio_transcript, st.session_state.random_sentence)}")
            st.subheader("Let's Try Again 💪")
            # create a button re try
            st.button("Please Tray Again 😊", on_click=shuffle_sentence_and_disable_audio, key='failure_btn')
