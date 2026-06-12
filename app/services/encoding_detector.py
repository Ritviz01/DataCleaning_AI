# Library jo file ki encoding detect karti hai
import chardet


def detect_encoding(file_path):

    # File ko binary mode mein open kar rahe hain
    with open(file_path, "rb") as f:

        # First 100KB read karenge
        # Pure file read karne ki zarurat nahi
        raw_data = f.read(100000)

    # Encoding detect karo
    result = chardet.detect(raw_data)

    # Example:
    # {
    #   'encoding': 'Windows-1252',
    #   'confidence': 0.73
    # }

    return result["encoding"]