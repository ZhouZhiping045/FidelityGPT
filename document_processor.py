class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}


def load_document(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"File content length: {len(content)}")
        return content
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit()
    except Exception as e:
        print(f"Error: {e}")
        exit()


def split_document(content):
    lines = content.splitlines()
    documents = [Document(line) for line in lines if line.strip()]
    return documents


def read_queries(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        queries = [query.strip() for query in content.split("/////") if query.strip()]
        split_queries = []

        for query in queries:
            lines = query.splitlines()
            while len(lines) > 500:
                split_queries.append("\n".join(lines[:500]))
                lines = lines[500:]
            split_queries.append("\n".join(lines))

        return split_queries
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit()
    except Exception as e:
        print(f"Error: {e}")
        exit()


def write_output(file_path, results):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(results)
    except Exception as e:
        print(f"Error: {e}")
        exit()
