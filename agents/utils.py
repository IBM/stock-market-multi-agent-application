from langgraph.graph import MessagesState

class Agent:
    def print_stream(self, stream):
        for message in stream['messages']:
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

class State(MessagesState):
    next: str
