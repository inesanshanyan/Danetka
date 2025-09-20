import json
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from llm_answers import LLMAnswer
from langchain.output_parsers import PydanticOutputParser
from game_answer import GameAnswer



class GameEngine:
    def __init__(self, games_path="games", prompt_path="prompts.md"):

        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        self.prompt = self.load_prompt(prompt_path)
        self.games = self.load_games(games_path)
        self.parser = PydanticOutputParser(pydantic_object=GameAnswer)


    def load_prompt(self, path: str):
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
            ("human", "{input}"),
            ("system", "{format_instructions}")
        ])
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        
        return ConversationChain(
            llm=self.llm,
            prompt=prompt.partial(format_instructions=self.parser.get_format_instructions()),
            memory=memory,
            verbose=False
        )

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
                try:
                    parsed: GameAnswer = self.parser.parse(response)
                except Exception as e:
                    print("Failed to parse LLM response:", e)
                    continue 

                print("LLM:", parsed.answer)

                if parsed.hint:
                    if parsed.hint_count and parsed.hint_count > 3:
                        print("LLM: No more hints, just ask yes/no questions")
                    else:
                        print("Hint:", parsed.hint, f"(Hints used: {parsed.hint_count})")
                

                if parsed.solution:
                    print("Solution:", parsed.solution, "Game over")

                if parsed.answer == "you won! game over" or parsed.solution:
                    break
                

            continue_the_game = input("Do you want to play another game? (y/n): ")
            if continue_the_game.lower() != "y":
                print("Ending the game...")
                break
