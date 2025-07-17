import re
import random


def analyze_fidelity_file(file_path):
    """
    Analyze the fidelity_new. c and calculate the proportion of various syntax types
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Warning: Cannot find file {file_path}, using default weights")
        return get_default_weights()

    # 按行分割并移除注释
    lines = []
    for line in content.split('\n'):

        if '//' in line:
            line = line.split('//')[0]

        line = re.sub(r'/\*.*?\*/', '', line)
        line = line.strip()
        if line and line not in ['{', '}']:
            lines.append(line)


    type_counts = {
        'assignment': 0,
        'addition': 0,
        'variable': 0,
        'return': 0,
        'loop': 0,
        'conditional': 0,
        'function': 0,
        '_TYPE': 0
    }

    for line in lines:

        if '=' in line and not any(keyword in line for keyword in ['for', 'while']):
            type_counts['assignment'] += 1

        if '+' in line:
            type_counts['addition'] += 1

        if re.search(r'\bint\b|\blong\b|\bchar\b|\bWORD\b|\bBYTE\b|\bvoid\b', line):
            type_counts['variable'] += 1

        if 'return' in line:
            type_counts['return'] += 1

        if 'for' in line or 'while' in line:
            type_counts['loop'] += 1

        if 'if' in line or 'else' in line:
            type_counts['conditional'] += 1

        if re.search(r'\w+\s*\(.*\)', line):
            type_counts['function'] += 1

        keywords = [r'\(_DWORD\b', r'\(_BYTE\b', r'\(_QWORD\b']
        if any(re.search(keyword, line) for keyword in keywords):
            type_counts['_TYPE'] += 1


    total_count = sum(type_counts.values())

    if total_count == 0:
        print("Warning: No syntax type found in the file, using default weights")
        return get_default_weights()


    weights = {}
    for type_name, count in type_counts.items():
        ratio = count / total_count

        weight = max(10, min(50, int(ratio * 100 + 10)))
        weights[type_name] = weight

    # print(f"The weights obtained from the analysis of {file_path}: ")
    # print(f"Total lines: {total_count}")
    # for type_name, weight in weights.items():
    #     count = type_counts[type_name]
    #     ratio = count / total_count if total_count > 0 else 0
    #     print(f"  {type_name}: {count} lines ({ratio:.2%}) -> weight: {weight}")

    return weights


def get_default_weights():
    """
    Return default weights
    """
    return {
        'assignment': 20,
        'addition': 25,
        'variable': 26,
        'return': 25,
        'loop': 25,
        'conditional': 25,
        'function': 20,
        '_TYPE': 26
    }


def calculate_max_semantic_strength(line, weights):
    """
    Calculate semantic strength based on dynamic weights
    """
    strengths = []


    if '=' in line and not any(keyword in line for keyword in ['for', 'while']):
        strengths.append(('assignment', weights['assignment']))
    if '+' in line:
        strengths.append(('addition', weights['addition']))
    if re.search(r'\bint\b|\blong\b|\bchar\b|\bWORD\b|\bBYTE\b|\bvoid\b', line):
        strengths.append(('variable', weights['variable']))
    if 'return' in line:
        strengths.append(('return', weights['return']))
    if 'for' in line or 'while' in line:
        strengths.append(('loop', weights['loop']))
    if 'if' in line or 'else' in line:
        strengths.append(('conditional', weights['conditional']))
    if re.search(r'\w+\s*\(.*\)', line):
        strengths.append(('function', weights['function']))


    keywords = [r'\(_DWORD\b', r'\(_BYTE\b', r'\(_QWORD\b']
    if any(re.search(keyword, line) for keyword in keywords):
        strengths.append(('_TYPE', weights['_TYPE']))

    return max(strengths, key=lambda x: x[1]) if strengths else (None, 0)


def match_patterns(query_lines, fidelity_file_path='fidelity_new.c'):
    """
    According to the dynamic weight matching mode
    """
    # Analyze the fidelity_new. c file to obtain weights
    weights = analyze_fidelity_file(fidelity_file_path)


    relevant_lines = [line for line in query_lines[1:] if line.strip() and line.strip() not in ['{', '}']]


    line_strengths = [(line, *calculate_max_semantic_strength(line, weights)) for line in relevant_lines]

    #
    # print("\nThe semantic values and strengths of each line: ")
    # for line, line_type, strength in line_strengths:
    #     print(f"Line: {line}")
    #     print(f"Type: {line_type}")
    #     print(f"Strength: {strength}\n")


    line_strengths.sort(key=lambda x: x[2], reverse=True)

    # 确定输出行数
    total_lines = len(relevant_lines)
    if total_lines <= 5:
        output_lines = total_lines
    else:
        output_lines = min(5 + (total_lines - 5) // 9, 10)


    print(f"Total lines: {total_lines}")
    print(f"Output lines:  {output_lines}")

    # Select the highest scoring row for each type
    selected_lines = []
    seen_types = set()


    for line, line_type, strength in line_strengths:
        if line_type and line_type not in seen_types:
            selected_lines.append(line)
            seen_types.add(line_type)
        if len(selected_lines) == output_lines:
            break


    if len(selected_lines) < output_lines:
        for line, line_type, strength in line_strengths:
            if line not in selected_lines:
                selected_lines.append(line)
            if len(selected_lines) == output_lines:
                break


    remaining_types = {'assignment', 'addition', 'variable', 'return', 'loop', 'conditional', 'function',
                       '_TYPE'} - seen_types
    if remaining_types:
        for line, line_type, strength in line_strengths:
            if line_type in remaining_types:
                selected_lines.append(line)
                remaining_types.remove(line_type)
            if not remaining_types:
                break

    return selected_lines


def select_random_lines(query_lines):
    """
    Randomly select 6 lines from the code as the reference group.
    """

    relevant_lines = [line for line in query_lines[1:] if line.strip() and line.strip() not in ['{', '}']]


    if len(relevant_lines) < 6:
        return relevant_lines


    random_lines = random.sample(relevant_lines, 6)
    return random_lines



if __name__ == "__main__":
    # Example
    code_input = """
    __fastcall binarySearch(__int64 a1, unsigned int a2, unsigned int a3, unsigned int a4)
    {
      __int64 result;
      unsigned int v5; // I4
      if ( (int)a3 < (int)a4 )
      {
        v5 = (int)(a4 - 1) / 2 + a3; // I3
        if ( a2 == *(_DWORD *)(4LL * (int)v5 + a1) ) // I1
        {
          result = v5 + 1; // I3
        }
        else if ( (signed int)a2 >= *(_DWORD *)(4LL * (int)v5 + a1) ) // I1
        {
          result = binarySearch(a1, a2, v5 + 1, a4);
        }
        else
        {
          result = binarySearch(a1, a2, a3, v5 - 1);
        }
      }
      else if ( (signed int)a2 <= *(_DWORD *)(4LL * (int)a3 + a1) ) // I1
      {
        result = a3;
      }
      else
      {
        result = a3 + 1; // I3
      }
      return result;
    }
    """


    query_lines = code_input.strip().split('\n')


    selected_lines = match_patterns(query_lines)


    print("\nSelected lines: ")
    for line in selected_lines:
        print(line)