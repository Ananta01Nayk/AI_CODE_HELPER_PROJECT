import sys
from ai_code_brain import process_and_ask

if __name__ == "__main__":
    file_path = sys.argv[1]
    question = sys.argv[2]
    print(process_and_ask(file_path, question))
