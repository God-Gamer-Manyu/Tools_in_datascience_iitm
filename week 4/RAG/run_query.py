import sys
from rag import cli

def main():
    q = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else "What does the author affectionately call the => syntax?"
    sys.argv = ['rag.cli', q]
    cli.__main__()

if __name__ == '__main__':
    main()
