import librosa
import noisereduce as nr
import soundfile as sf


def reduce_noise(input_path, output_path):

    audio, sample_rate = librosa.load(
        input_path,
        sr=None
    )

    reduced_audio = nr.reduce_noise(
        y=audio,
        sr=sample_rate
    )

    sf.write(
        output_path,
        reduced_audio,
        sample_rate
    )

    print("NOISE REDUCTION COMPLETE")