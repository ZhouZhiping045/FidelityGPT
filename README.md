# FidelityGPT README

## Configuration
1. Configure the following in `config.ini`:
   - Set `model`, `temperature`, `api_key`, and `api_base`.
   - Specify input and output folders.
   - Input decompiled functions are stored in `.txt` files, with each function separated by `/////`.
   - For decompilation distortion database:
     - Use `fidelity_new.c` for IDA Pro.
     - Use `fidelity_ghidra.c` for Ghidra.

## Detection Phase
2. Run `FidelityGPT.py`:
   - Output results are saved to the output folder specified in `config.ini`.
   - Output functions are labeled with distortion types (I1 to I6), with each function separated by `/////`.

## Correction Phase
3. Run `correction.py`:
   - Output includes decompiled functions labeled with `//fix`.

## Evaluation
4. Evaluation setup:
   - Store ground truth in `ground_truth.txt`.
   - Store detection phase output in `model_output.txt`.
   - **Note**: Functions in both files must be aligned by line.
   - Run `Evaluation/Evaluation.py` for assessment.