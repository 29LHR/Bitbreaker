import string


def index_of_coincidence(text: str) -> float:
    # Keep only alphabetic characters and convert to uppercase
    filtered_text = [ch.upper() for ch in text if ch.isalpha()]
    N = len(filtered_text)

    if N < 2:
        raise ValueError("Text must contain at least two letters to compute IC.")

    # Count letter frequencies
    freq = {letter: 0 for letter in string.ascii_uppercase}
    for ch in filtered_text:
        freq[ch] += 1

    # Calculate IC
    numerator = sum(f * (f - 1) for f in freq.values())
    denominator = N * (N - 1)
    return numerator / denominator


