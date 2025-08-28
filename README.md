# FidelityGPT Artifact README

## 📁 Artifact Structure

```
├── Dataset/                     # Decompiled functions (///// separated)
├── Ground truth/               # Ground truth functions (///// separated)
├── Evaluation/                 # Evaluation script
├── testdata/                   # Raw test data (txt)
├── config.ini                  # System configuration
├── FidelityGPT.py              # Distortion detection
├── Correction.py               # Distortion correction
├── prompt_templates.py         # Prompt templates for all LLM tasks
├── pattern_matcher.py          # Dynamic Semantic Intensity Retrieval Algorithm
├── variabledependency.py       # Variable Dependency Algorithm
├── document_processor.py       # Utility for document formatting
├── embedding_retriever.py      # RAG embedding retrieval logic
├── fidelity_new.c              # Distortion DB (for IDA Pro)
├── fidelity_ghidra.c           # Distortion DB (for Ghidra)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
```

## ⚙️ Configuration

Before running the system, update `config.ini`:

```ini
[LLM]
model = gpt-4o
temperature = 0
api_key = sk-XXXX             
api_base = XXXX 

[PATHS]
input_dir = Dataset_4_AE              ; Folder for input decompiled functions
output_dir = Dataset_4_AE_output      ; Folder for storing detection/correction results
knowledge_base = fidelity_new.c       ; Use `fidelity_ghidra.c` if using Ghidra
```

- Input functions: `.txt` files, each with functions separated by `/////`
- Distortion DB: `fidelity_new.c` (IDA Pro) or `fidelity_ghidra.c` (Ghidra)

## 🧪 Step-by-Step Execution

### 1. Prepare Input Files

Move test functions into the input folder:

```bash
mkdir Dataset_4_AE
cp testdata/*.txt Dataset_4_AE/
```

> You may also copy `Dataset/*.txt` into `Dataset_4_AE/` if needed:
```bash
cp Dataset/*.txt Dataset_4_AE/
```

### 2. Run Distortion Detection

```bash
python FidelityGPT.py
```

- Input: Files from `Dataset_4_AE/`
- Output: Stored in `Dataset_4_AE_output/`
- Each line is labeled with distortion type `I1`–`I6`
- Functions are separated using `/////`

> ℹ️ For functions longer than 50 lines, the system uses **chunk-based detection** with a 5-line overlap.  
After detection (before running Correction or Evaluation):

After detection:
- Manually merge chunked functions
- Remove overlapping duplicate lines
- Preserve the ///// separator

⚠️ Ensure line alignment: each line in model_output.txt should correspond exactly to the same function segment in ground_truth.txt. Since functions longer than 50 lines were split into chunks during preprocessing, manual alignment may be required.

👉 In our practice, we place ground_truth.txt and model_output.txt in two columns of an Excel sheet to ensure proper alignment before running Correction or Evaluation.

### 3. Run Correction

```bash
python Correction.py
```

### 4. Run Evaluation

Ensure the following:
- `Ground truth/ground_truth.txt`: aligned reference results
- `model_output.txt`: post-processed output from detection (line-aligned)

Then run:

```bash
python Evaluation/Evaluation.py

For the correction phase, manual evaluation is required. Please refer to Table I in the paper as the guideline for manual assessment.

## 🧠 Key Components

| Script | Description |
|--------|-------------|
| `FidelityGPT.py` | Main detection pipeline |
| `Correction.py` | Fixes distorted code lines |
| `prompt_templates.py` | LLM prompt templates |
| `pattern_matcher.py` | Semantic intensity retrieval |
| `variabledependency.py` | Variable dependency analysis |
| `Evaluation/Evaluation.py` | Compares against ground truth |
| `fidelity_new.c` / `fidelity_ghidra.c` | RAG knowledge base |

## ✅ Requirements

```bash
pip install -r requirements.txt
```
