"""
Interactive chat with the fine-tuned MiClone model.
Usage: python chat.py [--relationship friend|sister|lover]
"""
import argparse
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

MODEL = "mlx-community/Phi-3-mini-4k-instruct-4bit"
ADAPTER_PATH = "./adapters"
END_TOKEN = "<|end|>"


def build_prompt(message: str, relationship: str) -> str:
    return f"<|user|>\n[{relationship}] {message}{END_TOKEN}\n<|assistant|>\n"


def chat(relationship: str = "friend"):
    print(f"Loading model... (relationship: [{relationship}])")
    model, tokenizer = load(MODEL, adapter_path=ADAPTER_PATH)

    print(f"Model ready. Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input or user_input.lower() == "quit":
            break

        prompt = build_prompt(user_input, relationship)

        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=150,
            sampler=make_sampler(temp=0.7, top_p=0.9),
            verbose=False,
        )

        # Strip trailing <|end|> and whitespace
        clean = response.replace(END_TOKEN, "").strip()
        print(f"Prasanga: {clean}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--relationship", default="friend",
                        choices=["friend", "sister", "lover"])
    args = parser.parse_args()
    chat(args.relationship)
