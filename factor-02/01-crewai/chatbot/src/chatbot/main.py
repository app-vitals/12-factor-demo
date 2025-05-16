import logging
import os

import openlit
from dotenv import load_dotenv

from chatbot.crew import Chatbot

# Configure logging
# log_level = logging.DEBUG if os.environ.get("DEVOPS_DEBUG", "").lower() in ["1", "true", "yes"] else logging.ERROR
# logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()


# Initialize OpenLit OpenTelemetry instrumentation
openlit.init()

def run():
    """
    Run the DevOps Knowledge Assistant chatbot.
    """
    print("\nDevOps Knowledge Assistant 🤖")
    print("Ask me anything about DevOps, deployments, Kubernetes, or engineering practices.")
    print("Type 'exit', 'quit', or Ctrl+C to end the conversation.\n")

    try:
        while True:
            # Get user question
            user_input = input("\nYou: ")

            # Check if user wants to exit
            if user_input.lower() in ["exit", "quit", "q", "bye"]: 
                print("\nThank you for using the DevOps Knowledge Assistant. Goodbye!")
                break

            # Skip empty inputs
            if not user_input.strip():
                continue

            # Process the question using native crewAI
            inputs = {'user_question': user_input}
            result = Chatbot().crew().kickoff(inputs=inputs)
            print(f"Assistant: {result.raw}")
    except EOFError:
        print("\nDetected closed input stream. Exiting.")
    except KeyboardInterrupt:
        print("\n\nThank you for using the DevOps Knowledge Assistant. Goodbye!")

if __name__ == "__main__":
    run()
