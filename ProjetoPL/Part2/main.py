import json
import sys

class Concatenation:
    def __init__(self, *args):
        self.args = args

    def to_dict(self):
        return {"op": "seq", "args": [arg.to_dict() if hasattr(arg, 'to_dict') else {"simb": arg} for arg in self.args]}

class Alternation:
    def __init__(self, *args):
        self.args = args

    def to_dict(self):
        return {"op": "alt", "args": [arg.to_dict() if hasattr(arg, 'to_dict') else {"simb": arg} for arg in self.args]}

class KleeneClosure:
    def __init__(self, arg):
        self.arg = arg

    def to_dict(self):
        return {"op": "kle", "args": [self.arg.to_dict() if hasattr(self.arg, 'to_dict') else {"simb": self.arg}]}

class AFND:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.transitions = {}
        self.start_state = None
        self.final_states = set()

    def add_state(self, state):
        self.states.add(state)

    def add_transition(self, state_from, symbol, state_to):
        if state_from not in self.transitions:
            self.transitions[state_from] = {}
        if symbol not in self.transitions[state_from]:
            self.transitions[state_from][symbol] = set()
        self.transitions[state_from][symbol].add(state_to)

    def set_start_state(self, state):
        self.start_state = state

    def add_final_state(self, state):
        self.final_states.add(state)

    def to_dict(self):
        return {
            "V": list(self.states),
            "alphabet": list(self.alphabet),
            "delta": {state: {symbol: list(destinations) for symbol, destinations in transitions.items()} for state, transitions in self.transitions.items()},
            "q0": self.start_state,
            "F": list(self.final_states)
        }

def parse_regular_expression(json_data):
    if isinstance(json_data, dict):
        if "op" in json_data:
            if json_data["op"] == "seq":
                return Concatenation(*[parse_regular_expression(arg) for arg in json_data["args"]])
            elif json_data["op"] == "alt":
                return Alternation(*[parse_regular_expression(arg) for arg in json_data["args"]])
            elif json_data["op"] == "kle":
                return KleeneClosure(parse_regular_expression(json_data["args"][0]))
        elif "simb" in json_data:
            return json_data["simb"]
        elif "epsilon" in json_data:
            return None
    raise ValueError("Invalid expression")

def generate_afnd(expression):
    afnd = AFND()

    def explore(expression):
        if isinstance(expression, Concatenation):
            for i in range(len(expression.args) - 1):
                explore(expression.args[i])
                explore(expression.args[i + 1])
                afnd.add_transition(expression.args[i], None, expression.args[i + 1])
        elif isinstance(expression, Alternation):
            for arg in expression.args:
                explore(arg)
        elif isinstance(expression, KleeneClosure):
            explore(expression.arg)
            afnd.add_transition(expression.arg, None, expression.arg)
        elif isinstance(expression, str):
            afnd.add_state(expression)
            afnd.add_transition(expression, None, expression)  # Adicionar transição vazia do estado final para si mesmo

    explore(expression)
    afnd.start_state = expression.args[0]
    afnd.add_final_state(expression.args[-1])
    afnd.alphabet = set(afnd.states) - {None}

    # Adicionando transições padrão para transições vazias
    for state in afnd.states:
        if state not in afnd.transitions:
            afnd.transitions[state] = {}
        afnd.transitions[state][None] = set()  # Adicionando transição vazia para o estado

    return afnd

def main():
    if len(sys.argv) != 4 or sys.argv[2] != '--output':
        print("Usage: python main.py <input_file>.json --output <output_file>.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[3]

    try:
        with open(input_file, 'r') as f:
            json_data = json.load(f)
            print("Input JSON data:", json_data)
            expression = parse_regular_expression(json_data)
            print("Parsed expression:", expression)
            afnd = generate_afnd(expression)
            afnd_json = afnd.to_dict()
            with open(output_file, 'w') as output:
                json.dump(afnd_json, output, indent=2)
            print("AFND generated successfully and saved to", output_file)
    except FileNotFoundError:
        print("File not found:", input_file)
    except json.JSONDecodeError:
        print("Invalid JSON format in input file:", input_file)
    except ValueError as ve:
        print("Error parsing regular expression:", ve)
    except Exception as e:
        print("An error occurred:", e)

