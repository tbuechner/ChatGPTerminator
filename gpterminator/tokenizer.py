import os
import sys
import time
import tiktoken
from pathlib import Path

def count_tokens_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            encoding = tiktoken.get_encoding("cl100k_base")
            num_tokens = len(encoding.encode(content))
            return num_tokens
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def count_large_files(directory_path, token_threshold):
    large_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.json'):
                file_path = Path(root) / file
                token_count = count_tokens_in_file(file_path)
                if token_count >= token_threshold:
                    large_files.append((file_path, token_count))

    # Sort the files by token count in descending order
    large_files.sort(key=lambda x: x[1], reverse=True)
    return large_files

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <directory_path> <token_threshold>")
        sys.exit(1)

    directory_path = sys.argv[1]
    token_threshold = int(sys.argv[2])

    start_time = time.time()
    large_files = count_large_files(directory_path, token_threshold)
    end_time = time.time()

    for file_path, token_count in large_files:
        print(f"{file_path}: {token_count} tokens")

    print(f"Number of files with more than {token_threshold} tokens: {len(large_files)}")
    print(f"Time spent: {end_time - start_time} seconds")