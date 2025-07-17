import os
import sys
import configparser
from typing import List
from document_processor import (
    load_document,
    split_document,
    read_queries,
    write_output
)
from pattern_matcher import match_patterns
from embedding_retriever import (
    create_embedding,
    create_vectorstore,
    create_retriever,
    retrieve_documents,
)
from prompt_templates import (
    create_RAG_prompt_template,
    create_RAG_promptwithvariable_template
)
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import variabledependency

# Get current directory and config file path
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(CUR_DIR, "config.ini")


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


# Set OpenAI environment variables
os.environ["OPENAI_API_BASE"] = load_config("LLM", "api_base")
os.environ["OPENAI_API_KEY"] = load_config("LLM", "api_key")


def format_docs(docs: List[str]) -> str:
    """Format document list to string"""
    return "\n\n".join(docs)


def append_to_retrieve_log(file_path: str, sub_query: str, context: str):
    """Append retrieval log to file"""
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"Sub-query:\n{sub_query}\n")
            f.write(f"Formatted context:\n{context}\n")
            f.write("/////\n")
    except IOError:
        pass


def split_into_blocks(lines: List[str], block_size: int = 50, overlap: int = 5) -> List[List[str]]:
    """Split long text into blocks with overlap support"""
    blocks = []
    total_lines = len(lines)

    start = 0
    while start < total_lines:
        end = min(start + block_size, total_lines)
        block = lines[start:end]
        blocks.append(block)
        start += block_size - overlap

    return blocks


def process_queries(
        file_path: str,
        output_dir: str,
        retriever,
        llm,
        RAG_prompt,
        RAG_prompt_with_variable,
):
    """Process all queries in the file"""
    try:
        queries = read_queries(file_path)
    except Exception:
        return

    RAG_results = []

    for query_index, query in enumerate(queries):
        sub_queries = query.strip().split("\n")
        query_line_count = len(sub_queries)

        # Decide processing method based on query line count
        if query_line_count > 50:
            # More than 50 lines, perform variable name extraction and block processing
            try:
                variable_names = variabledependency.generate_and_query_llm("\n".join(sub_queries))
            except Exception:
                variable_names = ""

            # Process queries in blocks
            blocks = split_into_blocks(sub_queries)

            for block_index, block in enumerate(blocks):
                # Pattern matching
                try:
                    matched_lines = match_patterns(block)
                except Exception:
                    continue

                # Retrieve relevant documents
                try:
                    retrieved_docs = retrieve_documents(retriever, matched_lines)
                except Exception:
                    continue

                # Remove duplicate documents
                unique_retrieved_docs = list(dict.fromkeys(retrieved_docs))

                context = format_docs(unique_retrieved_docs)

                # Log retrieval
                append_to_retrieve_log("retrieve-new.txt", "\n".join(block), context)

                # Build variables dictionary
                variables = {
                    "Variable_names": variable_names,
                    "context": context,
                    "question": "\n".join(block),
                }

                # Build RAG chain
                RAG_chain = (
                        {
                            "Variable_names": RunnablePassthrough(),
                            "context": RunnablePassthrough(),
                            "question": RunnablePassthrough(),
                        }
                        | RAG_prompt_with_variable
                        | llm
                        | StrOutputParser()
                )

                # Generate complete prompt and output
                full_prompt = RAG_prompt_with_variable.format(**variables)
                print(f"\n[Prompt for Query {query_index + 1}, Block {block_index + 1}]:\n{full_prompt}\n")

                # Call model to generate result
                try:
                    RAG_result = RAG_chain.invoke(variables).strip()
                    RAG_results.append(
                        f"Query {query_index + 1}, Block {block_index + 1}:\n{RAG_result}\n"
                    )
                except Exception:
                    continue
        else:
            # Less than or equal to 50 lines, process directly
            # Pattern matching
            try:
                matched_lines = match_patterns(sub_queries)
            except Exception:
                continue

            # Retrieve relevant documents
            try:
                retrieved_docs = retrieve_documents(retriever, matched_lines)
            except Exception:
                continue

            # Remove duplicate documents
            unique_retrieved_docs = list(dict.fromkeys(retrieved_docs))

            context = format_docs(unique_retrieved_docs)

            # Log retrieval
            append_to_retrieve_log("retrieve-new.txt", "\n".join(matched_lines), context)

            # Build variables dictionary
            variables = {
                "context": context,
                "question": query,
            }

            # Build RAG chain
            RAG_chain = (
                    {
                        "context": RunnablePassthrough(),
                        "question": RunnablePassthrough()
                    }
                    | RAG_prompt
                    | llm
                    | StrOutputParser()
            )

            # Generate complete prompt and output
            full_prompt = RAG_prompt.format(**variables)
            print(f"\n[Prompt for Query {query_index + 1}]:\n{full_prompt}\n")

            # Call model to generate result
            try:
                RAG_result = RAG_chain.invoke(variables).strip()
                RAG_results.append(f"Query {query_index + 1}:\n{RAG_result}\n")
            except Exception:
                continue

    # Write results to output file
    base_filename = os.path.basename(file_path).split('.')[0]
    RAG_output_path = os.path.join(output_dir, f"{base_filename}_RAG_answer.txt")
    try:
        write_output(RAG_output_path, "\n/////\n".join(RAG_results))
    except Exception:
        pass


def main():
    """Main function, initialize environment and process files"""
    current_dir = os.getcwd()

    # Load paths from config
    testdata_dir = os.path.join(current_dir, load_config("PATHS", "input_dir"))
    output_dir = os.path.join(current_dir, load_config("PATHS", "output_dir"))
    knowledge_base_file = os.path.join(current_dir, load_config("PATHS", "knowledge_base"))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load knowledge base
    try:
        fidelity_content = load_document(knowledge_base_file)
        fidelity_documents = split_document(fidelity_content)
        fidelity_texts = [doc.page_content for doc in fidelity_documents]
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        sys.exit(1)

    # Create embeddings and retriever
    try:
        embeddings = create_embedding(fidelity_texts)
        db = create_vectorstore(fidelity_texts, embeddings)
        retriever = create_retriever(db)
    except Exception as e:
        print(f"Error creating embeddings/retriever: {e}")
        sys.exit(1)

    # Initialize language model and prompt templates
    try:
        model_name = load_config("LLM", "model")
        temperature = float(load_config("LLM", "temperature"))
        llm = ChatOpenAI(model=model_name, temperature=temperature)
        RAG_prompt = create_RAG_prompt_template()
        RAG_prompt_with_variable = create_RAG_promptwithvariable_template()
    except Exception as e:
        print(f"Error initializing LLM or prompts: {e}")
        sys.exit(1)

    # Process test data
    for root, dirs, files in os.walk(testdata_dir):
        for file in files:
            file_path = os.path.join(root, file)
            process_queries(file_path, output_dir, retriever, llm, RAG_prompt, RAG_prompt_with_variable)


if __name__ == "__main__":
    main()