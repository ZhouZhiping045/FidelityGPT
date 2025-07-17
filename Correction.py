import argparse
from document_processor import read_queries, write_output
from prompt_templates import create_RAG_correction_template
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import configparser
import os

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(CUR_DIR, 'config.ini')

def load_config(field: str, value: str) -> str:
    config = configparser.ConfigParser()
    config.read(CONFIG)
    return config[field][value]


os.environ["OPENAI_API_BASE"] = load_config('LLM', 'api_base')
os.environ["OPENAI_API_KEY"] = load_config('LLM', 'api_key')

def read_and_split_queries(file_path):
    print(f"Reading and splitting queries from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    queries = content.split('/////')
    print(f"Total {len(queries)} queries found.")
    return queries

def process_file(file_path, output_dir, llm, rag_correction_template):
    queries = read_and_split_queries(file_path)
    results = []

    for query_index, query in enumerate(queries):
        query = query.strip()
        if not query:
            continue

        print(f"Processing query {query_index + 1}: {query}")

        
        prompt_text = rag_correction_template.format(context="", question=query)
        print(f"RAG correction prompt: {prompt_text}")

        result = llm.invoke([HumanMessage(content=prompt_text)]).content.strip()
        results.append(f"Query {query_index + 1}:\n{result}\n")

        print(f"Results for query {query_index + 1} have been processed.")

   
    base_filename = os.path.basename(file_path).split('.')[0]
    output_path = os.path.join(output_dir, f"{base_filename}_RAG_Correct.txt")
    print(f"Writing results to {output_path}")
    write_output(output_path, "\n/////\n".join(results))

def main():
    parser = argparse.ArgumentParser(description="Process text queries with RAG correction.")
    parser.add_argument('--input_dir', type=str, default='correction_input', help="Input directory containing query files.")
    parser.add_argument('--output_dir', type=str, default='correction_output', help="Output directory for results.")
    args = parser.parse_args()

    current_dir = os.getcwd()
    testdata_dir = os.path.join(current_dir, args.input_dir)
    output_dir = os.path.join(current_dir, args.output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    model_name = load_config("LLM", "model")
    temperature = float(load_config("LLM", "temperature"))
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    rag_correction_template = create_RAG_correction_template()

    for root, dirs, files in os.walk(testdata_dir):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            process_file(file_path, output_dir, llm, rag_correction_template)

    print("All files have been processed and results have been written to the output directory.")

if __name__ == "__main__":
    main()
