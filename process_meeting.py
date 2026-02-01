import os
import whisper
import numpy as np
from transformers import MarianMTModel, MarianTokenizer, pipeline
from pydub import AudioSegment
from resemblyzer import VoiceEncoder, preprocess_wav
from sklearn.cluster import AgglomerativeClustering


OUTPUT_DIR = "output"
CHUNK_DURATION_MS = 5000   # 5 seconds
NUM_SPEAKERS = 2           # Prototype assumption

os.makedirs(OUTPUT_DIR, exist_ok=True)


def split_audio(audio_path, chunk_ms=5000):
    """Split audio into fixed-length chunks for diarization."""
    audio = AudioSegment.from_file(audio_path)
    chunk_files = []

    for i in range(0, len(audio), chunk_ms):
        chunk = audio[i:i + chunk_ms]
        chunk_path = f"temp_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunk_files.append(chunk_path)

    return chunk_files


def extract_speaker_embeddings(chunk_files):
    """Extract speaker embeddings using Resemblyzer."""
    encoder = VoiceEncoder()
    embeddings = []

    for chunk in chunk_files:
        wav = preprocess_wav(chunk)
        embedding = encoder.embed_utterance(wav)
        embeddings.append(embedding)

    return np.array(embeddings)


def cluster_speakers(embeddings, num_speakers=2):
    """Cluster speaker embeddings."""
    if len(embeddings) < num_speakers:
        num_speakers = len(embeddings)

    clustering = AgglomerativeClustering(
        n_clusters=num_speakers,
        metric="cosine",
        linkage="average"
    )
    return clustering.fit_predict(embeddings)


def assign_speakers_to_segments(segments, labels, chunk_duration_sec=5):
    """Assign speaker labels to Whisper segments."""
    speaker_lines = []

    for segment in segments:
        chunk_index = int(segment["start"] // chunk_duration_sec)
        chunk_index = min(chunk_index, len(labels) - 1)
        speaker_label = f"Speaker {labels[chunk_index] + 1}"
        speaker_lines.append(f"{speaker_label}: {segment['text']}")

    return "\n".join(speaker_lines)


# main processing function 

def process_meeting(audio_path):
    print("Loading Whisper model...")
    whisper_model = whisper.load_model("base")

    print("Transcribing audio...")
    transcription_result = whisper_model.transcribe(audio_path)

    transcript_text = transcription_result["text"]
    segments = transcription_result["segments"]

    with open(f"{OUTPUT_DIR}/transcript_raw.txt", "w", encoding="utf-8") as f:
        f.write(transcript_text)

    # Translation
    print("Translating transcript...")
    translation_model_name = "Helsinki-NLP/opus-mt-mul-en"
    tokenizer = MarianTokenizer.from_pretrained(translation_model_name)
    translator = MarianMTModel.from_pretrained(translation_model_name)

    inputs = tokenizer(transcript_text, return_tensors="pt", truncation=True)
    translated = translator.generate(**inputs)

    translated_text = tokenizer.decode(
        translated[0],
        skip_special_tokens=True
    )

    with open(f"{OUTPUT_DIR}/translated.txt", "w", encoding="utf-8") as f:
        f.write(translated_text)

    # Summarization
    print("Generating summary...")
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn"
    )

    summary_prompt = (
        "Summarize the following meeting and extract key action items:\n\n"
        + translated_text
    )

    summary = summarizer(
        summary_prompt,
        max_length=200,
        min_length=80,
        do_sample=False
    )[0]["summary_text"]

    with open(f"{OUTPUT_DIR}/summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)


    # Speaker Diarization
    print("Performing speaker diarization...")
    chunks = split_audio(audio_path, CHUNK_DURATION_MS)
    embeddings = extract_speaker_embeddings(chunks)
    labels = cluster_speakers(embeddings, NUM_SPEAKERS)

    speaker_transcript = assign_speakers_to_segments(
        segments,
        labels,
        chunk_duration_sec=CHUNK_DURATION_MS // 1000
    )

    with open(f"{OUTPUT_DIR}/speaker_transcript.txt", "w", encoding="utf-8") as f:
        f.write(speaker_transcript)

    print("Processing complete.")

    return {
        "transcript": transcript_text,
        "translated": translated_text,
        "summary": summary,
        "speaker_transcript": speaker_transcript
    }

