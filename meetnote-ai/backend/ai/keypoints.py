
def generate_keypoints(transcript):

    lines = transcript.split(".")

    keypoints = []

    for line in lines[:5]:

        line = line.strip()

        if line:
            keypoints.append("• " + line)

    return "\n".join(keypoints)