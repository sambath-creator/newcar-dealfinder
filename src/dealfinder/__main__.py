import sys
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .cli import main

if __name__ == "__main__":
    main()
