import json
import argparse

class Node:
    def __init__(self, op, args=None):
        self.op = op
        self.args = args if args is not None else []

def parse_json(filename):
    with open(filename, 'r') as file:
        return {'op': json.load(file)}

def convert_to_afnd(node):
    if isinstance(node, list):
        if len(node) == 1:
            return node[0]
        else:
            return node
    else:
        if node.op == "alt":
            return {"type": "alt", "args": [convert_to_afnd(arg) for arg in node.args]}
        elif node.op == "seq":
            return {"type": "seq", "args": [convert_to_afnd(arg) for arg in node.args]}
        elif node.op == "kle":
            return {"type": "kle", "arg": convert_to_afnd(node.args[0])}
        elif isinstance(node, str):
            return {"type": "symbol", "value": node}
        else:
            raise ValueError("Invalid node type")

def build_afnd(expression):
    expression = Node(**expression)  # Convertendo para Node
    symbols = set()
    states = set()
    transitions = []
    start_state = 'q0'
    final_states = set()

    def generate_state():
        nonlocal states
        new_state = f'q{len(states)}'
        states.add(new_state)
        return new_state

    def process_node(node):
        nonlocal symbols, transitions, final_states
        if isinstance(node, dict) and 'op' in node:
            if node['op'] == "alt":
                state = generate_state()
                transitions.append({'from': state, 'to': process_node(node['args'][0]), 'symbol': 'epsilon'})
                transitions.append({'from': state, 'to': process_node(node['args'][1]), 'symbol': 'epsilon'})
                return state
            elif node['op'] == "seq":
                state1 = process_node(node['args'][0])
                state2 = process_node(node['args'][1])
                transitions.append({'from': state1, 'to': state2, 'symbol': 'epsilon'})
                return state1
            elif node['op'] == "kle":
                state1 = generate_state()
                state2 = process_node(node['args'][0])
                transitions.append({'from': state1, 'to': state2, 'symbol': 'epsilon'})
                transitions.append({'from': state2, 'to': state1, 'symbol': 'epsilon'})
                return state1
        elif isinstance(node, str):
            symbols.add(node)
            return node
        else:
            raise ValueError("Invalid node type")

    final_state = process_node(expression)
    final_states.add(final_state)

    return {
        'V': list(symbols),
        'Q': list(states),
        'delta': transitions,
        'q0': start_state,
        'F': list(final_states)
    }

def save_afnd_to_json(afnd, filename):
    with open(filename, 'w') as file:
        json.dump(afnd, file, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Convert regular expression to AFND.')
    parser.add_argument('input', help='Input JSON file containing regular expression')
    parser.add_argument('--output', help='Output JSON file containing AFND')
    args = parser.parse_args()

    input_filename = args.input
    output_filename = args.output

    expression = parse_json(input_filename)
    afnd = build_afnd(expression)

    if output_filename:
        save_afnd_to_json(afnd, output_filename)
        print(f'AFND saved to {output_filename}')
    else:
        print(json.dumps(afnd, indent=4))

