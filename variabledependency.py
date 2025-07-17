import os
import re
import networkx as nx
from langchain.schema import HumanMessage
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import configparser

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(CUR_DIR, 'config.ini')

def load_config(field: str, value: str) -> str:
    """Load parameters from config file"""
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG, encoding='utf-8')
        return config[field][value]
    except KeyError:
        print(f"Error: Cannot find [{field}] {value} in config file")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: Config file encoding issue. Please save config.ini as UTF-8")
        sys.exit(1)


os.environ["OPENAI_API_BASE"] = load_config('LLM', 'api_base')
os.environ["OPENAI_API_KEY"] = load_config('LLM', 'api_key')

# Function to generate the control flow graph (CFG)
def generate_cfg(c_code):
    cfg = nx.DiGraph()
    lines = c_code.split('\n')
    current_node = None

    for i, line in enumerate(lines):
        line = line.strip()
        if line:
            cfg.add_node(i, code=line, type='statement')  # Add code information to node attributes
            if current_node is not None:
                cfg.add_edge(current_node, i)
            current_node = i
    return cfg, lines

# Compute post-dominators
def compute_post_dominators(cfg):
    post_dominators = nx.immediate_dominators(cfg.reverse(), list(cfg.nodes)[-1])
    return post_dominators

# Generate control dependence subgraph
def generate_control_dependence_subgraph(cfg, post_dominators):
    cdg = nx.DiGraph()
    for node in cfg.nodes:
        for succ in cfg.successors(node):
            if post_dominators[succ] != node:
                cdg.add_edge(node, succ, type='control_dependence')
    return cdg

# Generate data dependence subgraph
def generate_data_dependence_subgraph(lines):
    ddg = nx.DiGraph()
    var_def = {}

    valid_variable_pattern = re.compile(r'^[a-zA-Z_]\w*$')

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        if '=' in line:
            var, expr = line.split('=', 1)
            var, expr = var.strip(), expr.strip()
            ddg.add_node(i, code=line, type='assignment')  # Add code information to node attributes
            var_names = extract_variables(var)
            for var_name in var_names:
                if valid_variable_pattern.match(var_name):
                    ddg.add_node(var_name, type='variable')
                    ddg.add_edge(i, var_name, type='data_dependence')
                    var_def[var_name] = i
        else:
            ddg.add_node(i, code=line, type='statement')  # Add code information to node attributes
            for var in var_def:
                if var in line and valid_variable_pattern.match(var):
                    ddg.add_edge(var_def[var], i, type='data_dependence')
    return ddg

# Extract all variables from expressions
def extract_variables(expression):
    return re.findall(r'\b\w+\b', expression)

# Extract variable definitions from C code
def extract_variable_definitions(c_code):
    variable_pattern = re.compile(r'\b(?:\w+\s+)+(?:\*+\s*)?(\w+)(?:\[\d*\])?\s*;')
    keywords = {"return", "goto", "if", "else", "while", "for", "sizeof", "switch", "case", "break", "continue"}
    matches = variable_pattern.findall(c_code)
    return [match for match in matches if match not in keywords]

# Generate the PDG
def generate_pdg(c_code):
    cfg, lines = generate_cfg(c_code)
    post_dominators = compute_post_dominators(cfg)
    cdg = generate_control_dependence_subgraph(cfg, post_dominators)
    ddg = generate_data_dependence_subgraph(lines)

    pdg = nx.compose(cdg, ddg)
    return pdg, lines

# Find variable dependencies
def find_variable_dependencies(pdg, variable_name, lines):
    dependencies = set()
    dep_info = []

    def recursive_find(var_name):
        for node, data in pdg.nodes(data=True):
            if isinstance(node, str) and node == var_name:
                for pred in pdg.predecessors(node):
                    if pred not in dependencies:
                        dependencies.add(pred)
                        if isinstance(pred, int):
                            expr = lines[pred].split('=', 1)[1].strip() if '=' in lines[pred] else ''
                            dep_info.append(lines[pred])
                            vars_in_expr = extract_variables(expr)
                            for var in vars_in_expr:
                                if var != var_name:  # Avoid circular dependencies
                                    recursive_find(var)

    recursive_find(variable_name)
    return dep_info

# Generate the prompt template
def create_variable_template():
    template = """
As a program analysis expert, you possess excellent program analysis skills. Below are the variable dependencies extracted from decompiled code. During the decompilation process, new variables are defined due to register usage, which leads to a large number of redundant variables compared to the all_source_code code. Redundant variables refer to those that are temporary, intermediate, or represent the same data. These variables are often generated during the decompilation process due to register operations or temporary storage needs. Considering temporary or intermediate calculation results, these variables are only used for intermediate steps in computations or operations and are not utilized multiple times or have no significant independent meaning. Repetitively, these variables store the same or similar information and can logically be merged with other statements. The task is to directly output potentially redundant variables without any explanation. The output format is as follows:
**Potential redundant variables:** {all_vars}.
    Question: {question}      
    Helpful Answer:
    """
    return PromptTemplate.from_template(template)

# Format prompt with all dependencies
def format_prompt(all_dependencies):
    prompt_template = create_variable_template()
    question = "Dependencies for all variables:\n" + "\n".join(all_dependencies)
    return prompt_template.format(all_vars="All variables", question=question)

# Function to call the OpenAI LLM (ChatGPT)
def call_llm(prompt):
    llm = ChatOpenAI(model='gpt-4o', temperature=0.5)  
    response = llm([HumanMessage(content=prompt)])
    return response.content

def generate_and_query_llm(c_code):
    """

    """
    pdg, lines = generate_pdg(c_code)


    all_vars = set(extract_variable_definitions(c_code))


    all_dependencies = []
    for var in sorted(all_vars):
        dependencies = find_variable_dependencies(pdg, var, lines)
        if dependencies:
            all_dependencies.append(f"\nDependencies for variable '{var}':\n" + "\n".join(dependencies))


    if all_dependencies:
        prompt = format_prompt(all_dependencies)
        # print("\nGenerated Prompt:\n", prompt)


        response = call_llm(prompt)
        return response


if __name__ == "__main__":
    main()
