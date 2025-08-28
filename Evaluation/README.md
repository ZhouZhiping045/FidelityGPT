# Manual Alignment Guide for Evaluation

During **distortion detection**, functions longer than 50 lines are automatically split into **chunks** with a 5-line overlap.  
Before running **Correction** or **Evaluation**, these chunked functions must be **manually merged** back into a single function.  
This ensures line-alignment with the ground truth.

---

## Steps for Manual Alignment

1. **Identify Split Blocks**
   - Functions are split into multiple blocks (e.g., *Query 1, Block 1* and *Query 1, Block 2*).
   - Each block may share overlapping lines due to the 5-line sliding window.

2. **Merge Blocks**
   - Concatenate the split blocks in order.
   - **Remove overlapping duplicate lines** caused by the chunking.

3. **Preserve Function Separator**
   - After merging, ensure that functions are still separated by  
     ```
     /////
     ```

4. **Check Alignment with Ground Truth**
   - The merged function should correspond line-by-line with the ground truth.
   - Verify alignment using an Excel sheet or side-by-side comparison if needed.

---

## Example

### Query 1, Block 1:
```c
__cdecl main(int argc, const char **argv, const char **envp)
{
  char *v3; //I4
  char *v4; //I4
  void *v5; //I4
  const char *v6; //I4
  char v10;
  char v11;
  const char *v12;
  int v13; //I4
  v10 = 0;
  v11 = 0;
  v12 = 0;
  set_program_name(*argv);
  setlocale(6, byte_177CC); //I2
  bindtextdomain("coreutils", "/usr/local/share/locale");
  textdomain("coreutils");
  atexit((void (__fastcall *)(void *))close_stdout); //I6
  while ( 1 )
  {
    v13 = rpl_getopt_long(argc, argv, "+as:z", (const char **)&longopts, 0); //I6
    if ( v13 == -1 )
      break;
    if ( v13 == 97 ) //I2
      goto LABEL_12;
    if ( v13 <= 97 )
    {
      if ( v13 == -3 )
      {
        version_etc((FILE *)stdout, "basename", "GNU coreutils", Version, "David MacKenzie", 0); //I6
        exit(0);
      }
      if ( v13 == -2 )
        usage(0);
LABEL_16:
      usage(1);
    }
    if ( v13 == 115 ) //I2
    {
      v12 = (const char *)rpl_optarg; //I6
LABEL_12:
      v10 = 1;
    }
    else
    {
      if ( v13 != 122 ) //I2
        goto LABEL_16;
      v11 = 1;
    }
  }
}
```
### Query 1, Block 2:
```c
      if ( v13 != 122 ) //I4
        goto LABEL_16;
      v11 = 1;
    }
  }
  if ( argc < rpl_optind + 1 )
  {
    v3 = gettext("missing operand");
    error(0, 0, v3);
    usage(1);
  }
  if ( v10 != 1 && argc > rpl_optind + 2 )
  {
    v4 = gettext("extra operand %s");
    v5 = quote((int)argv[rpl_optind + 2]); //I1
    error(0, 0, v4, v5);
    usage(1);
  }
  if ( v10 )
  {
    while ( argc > rpl_optind )
    {
      perform_basename((char *)argv[rpl_optind], v12, v11); //I1
      ++rpl_optind;
    }
  }
  else
  {
    if ( argc == rpl_optind + 2 )
      v6 = argv[rpl_optind + 1];
    else
      v6 = 0;
    perform_basename((char *)argv[rpl_optind], v6, v11); //I1
  }
  return 0;
```
✅ Merged Function
```c
__cdecl main(int argc, const char **argv, const char **envp)
{
  char *v3; //I4
  char *v4; //I4
  void *v5; //I4
  const char *v6; //I4
  char v10;
  char v11;
  const char *v12;
  int v13; //I4
  v10 = 0;
  v11 = 0;
  v12 = 0;
  set_program_name(*argv);
  setlocale(6, byte_177CC); //I2
  bindtextdomain("coreutils", "/usr/local/share/locale");
  textdomain("coreutils");
  atexit((void (__fastcall *)(void *))close_stdout); //I6
  while ( 1 )
  {
    v13 = rpl_getopt_long(argc, argv, "+as:z", (const char **)&longopts, 0); //I6
    if ( v13 == -1 )
      break;
    if ( v13 == 97 ) //I2
      goto LABEL_12;
    if ( v13 <= 97 )
    {
      if ( v13 == -3 )
      {
        version_etc((FILE *)stdout, "basename", "GNU coreutils", Version, "David MacKenzie", 0); //I6
        exit(0);
      }
      if ( v13 == -2 )
        usage(0);
LABEL_16:
      usage(1);
    }
    if ( v13 == 115 ) //I2
    {
      v12 = (const char *)rpl_optarg; //I6
LABEL_12:
      v10 = 1;
    }
    else
    {
      if ( v13 != 122 ) //I2
        goto LABEL_16;
      v11 = 1;
    }
  }
  if ( argc < rpl_optind + 1 )
  {
    v3 = gettext("missing operand");
    error(0, 0, v3);
    usage(1);
  }
  if ( v10 != 1 && argc > rpl_optind + 2 )
  {
    v4 = gettext("extra operand %s");
    v5 = quote((int)argv[rpl_optind + 2]); //I1
    error(0, 0, v4, v5);
    usage(1);
  }
  if ( v10 )
  {
    while ( argc > rpl_optind )
    {
      perform_basename((char *)argv[rpl_optind], v12, v11); //I1
      ++rpl_optind;
    }
  }
  else
  {
    if ( argc == rpl_optind + 2 )
      v6 = argv[rpl_optind + 1];
    else
      v6 = 0;
    perform_basename((char *)argv[rpl_optind], v6, v11); //I1
  }
  return 0;
}
```
Key Notes:

- Always merge before running Correction and Evaluation.
- Remove only the overlapping lines, not the unique ones.
- Keep the ///// separator intact between functions.
