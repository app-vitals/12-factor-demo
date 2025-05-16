#!/usr/bin/env python
import sys
import warnings
import os
import argparse
import logging
import openlit

# Fix import for both package mode and direct execution
try:
    from chatbot.crew import Chatbot  # When installed as a package
except ImportError:
    from src.chatbot.crew import Chatbot  # When running directly

# Configure logging
log_level = logging.DEBUG if os.environ.get("DEVOPS_DEBUG", "").lower() in ["1", "true", "yes"] else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('devops_assistant_main')

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Initialize OpenLit OpenTelemetry instrumentation
openlit.init()

def run():
    """
    Run the DevOps Knowledge Assistant chatbot.
    
    This function can run in two modes:
    1. Interactive mode - when run directly by the user
    2. Single question mode - when run through crewai run
    """
    # Detect if we're running through crewai run
    import sys
    running_through_crewai = not sys.stdin.isatty() or "--non-interactive" in sys.argv
    
    # Create chatbot crew instance
    chatbot = Chatbot()
    crew_instance = chatbot.crew()
    
    if running_through_crewai:
        # When running through crewai run, use a default question or get from environment variable
        default_question = os.environ.get(
            "DEVOPS_QUESTION", 
            "What is blue-green deployment? Keep your answer brief."
        )
        print(f"\nRunning in non-interactive mode with question: '{default_question}'\n")
        
        try:
            # Use native crewAI to execute the crew with the question
            inputs = {"user_question": default_question}
            result = crew_instance.kickoff(inputs=inputs)
            print(f"\nAnswer: {result}\n")
        except Exception as e:
            logger.error(f"Error running crew: {str(e)}")
            print(f"\nError: {str(e)}")
        
        return
    
    # Interactive mode
    print("\nDevOps Knowledge Assistant 🤖")
    print("Ask me anything about DevOps, deployments, Kubernetes, or engineering practices.")
    print("Type 'exit', 'quit', or Ctrl+C to end the conversation.\n")
    
    try:
        while True:
            try:
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
                print("\nThinking...\n")
                inputs = {"user_question": user_input}
                result = crew_instance.kickoff(inputs=inputs)
                print(f"Assistant: {result}")
            except EOFError:
                # Handle EOF error (happens when stdin is closed)
                print("\nDetected closed input stream. Exiting.")
                break
            except Exception as e:
                logger.error(f"Error processing question: {str(e)}")
                print(f"\nSorry, I encountered an error: {str(e)}")
                print("Please try asking your question in a different way.")
                
    except KeyboardInterrupt:
        print("\n\nThank you for using the DevOps Knowledge Assistant. Goodbye!")
        
def ask_question(question):
    """
    Ask a single question to the DevOps Knowledge Assistant.
    
    Args:
        question: The user's question to ask the assistant
    """
    try:
        # Create chatbot crew instance
        chatbot = Chatbot()
        crew_instance = chatbot.crew()
        
        # Use native crewAI to execute the crew with the question
        inputs = {"user_question": question}
        result = crew_instance.kickoff(inputs=inputs)
        print(f"\nQ: {question}\n\nA: {result}\n")
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        print(f"Error: {str(e)}")

def process_command_line():
    """Process command line arguments and route to appropriate function."""
    parser = argparse.ArgumentParser(description="DevOps Knowledge Assistant")
    parser.add_argument("-q", "--question", help="Ask a single question and exit")
    
    args = parser.parse_args()
    
    if args.question:
        ask_question(args.question)
    else:
        run()

if __name__ == "__main__":
    process_command_line()
