"""
Main entry point — Exam Helper Multi-Agent System
Run: python main.py
"""

from dotenv import load_dotenv

load_dotenv()

from multi_agentic_workflow import MultiAgentWorkflow


def run_interactive_session() -> None:
    """Start an interactive terminal chat session."""
    workflow = MultiAgentWorkflow()

    print("\n" + "=" * 55)
    print("  Welcome to the Exam Helper — Multi-Agent System")
    print("  Type 'quit' or 'exit' to end the session")
    print("=" * 55 + "\n")

    greeting = workflow.get_greeting()
    print(f"Assistant: {greeting}\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in {"quit", "exit", "bye", "goodbye"}:
                print("\nAssistant: All the best! You will do great. Goodbye! 👋\n")
                break

            response = workflow.chat(user_input)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\n\nAssistant: All the best! Goodbye! 👋\n")
            break
        except EOFError:
            print("\nSession ended.\n")
            break


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        wf = MultiAgentWorkflow()
        response = wf.chat(query)
        print(f"\nAssistant: {response}\n")
    else:
        run_interactive_session()
