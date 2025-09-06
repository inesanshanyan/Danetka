from game_engine import GameEngine
from pathlib import Path
from dotenv import load_dotenv
import os
import warnings

def main():
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    load_dotenv()  
    if "OPENAI_API_KEY" not in os.environ:
        raise RuntimeError("OPENAI_API_KEY is not found")
    
    games_folder = Path("games")
    prompt_file = Path("prompt.md")

    game_controller = GameEngine(games_path=games_folder, prompt_path=prompt_file)

    game_controller.start()


if __name__ == "__main__":
    main()
