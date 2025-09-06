import json
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


class GameEngine:
    def __init__(self, games_path="games", prompt_path="prompts.md"):

        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        self.prompt = self.load_prompt(prompt_path)
        self.games = self.load_games(games_path)


    def load_prompt(self, path):
        prompt_file = Path(path)
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        
        return prompt_file.read_text(encoding="utf-8")

    def load_games(self, folder_path):
        games = []
        folder = Path(folder_path)
        
        if not folder.exists():
            raise FileNotFoundError(f"Games folder not found: {folder_path}")
        
        for file in folder.glob("*.json"):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                games.append(data) 
            except Exception as e:
                print(f"Failed to load {file.name}: {e}")
                
        return games

    def pick_game(self):
        print("\nAvailable games:")
        for i, g in enumerate(self.games, 1):
            print(f"{i}. {g['title']}")
        while True:
            choice = input("Pick a game number or type quit/exit: ")
            if choice.lower() in ["quit", "exit"]:
                return None
            try:
                idx = int(choice) - 1
                
                if 0 <= idx < len(self.games):
                    return self.games[idx]
                
            except Exception:
                pass
            
            print("Invalid choice, try again.")

    def build_chain(self, game):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt),
            ("system", f"The riddle is: {game['riddle']}"),
            ("system", f"The hidden solution is: {game['solution']}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return ConversationChain(llm=self.llm, prompt=prompt, memory=memory, verbose = False)

    def start(self):
        print("Welcome to Danetka game!")
        while True:
            game = self.pick_game()
            
            if game is None:
                print("Exiting...")
                break

            chain = self.build_chain(game)
            print(f"\nRiddle: {game['riddle']}\n")

            while True:
                user_input = input("Player: ")
                if user_input.lower() in ["quit", "exit"]:
                    print("Game ended by the player.\n")
                    break

                response = chain.run(input=user_input)
                print(f"LLM: {response}")

                if "game is over" in response.lower() or "correct" in response.lower():
                    print("\nYou've solved the riddle!!!\n")
                    break

            continue_the_game = input("Do you want to play another game? (y/n): ")
            if continue_the_game.lower() != "y":
                print("Ending the game...")
                break
