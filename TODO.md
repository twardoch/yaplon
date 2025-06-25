# Yaplon Project TODO List

This file tracks tasks for the Yaplon project.

## Phase 1: Initial Setup & Review (Completed)

-   [x] Create `PLAN.md`
-   [x] Create `TODO.md` (this file)
-   [x] Create `CHANGELOG.md`
-   [x] **Codebase Review:**
    -   [x] Review `yaplon/reader.py`
    -   [x] Review `yaplon/writer.py`
    -   [x] Review `yaplon/__main__.py`
    -   [x] Review `yaplon/ojson.py`
    -   [x] Review `yaplon/oplist.py`
    -   [x] Review `yaplon/oyaml.py`
    -   [x] Review `yaplon/file_strip/`
    -   [x] Review `tests/` directory
    -   [x] Review `README.md`
    -   [x] Review `setup.py`, `requirements.txt`, `Makefile`, `dist.sh`.

## Phase 2: Refactoring and Enhancements

-   **Core Logic & CLI:**
    -   [ ] **JSON Sanitization:**
        -   [ ] Decide if `yaplon.file_strip.json.sanitize_json` (for comments/trailing commas) should be used in `reader.json`.
        -   [ ] If yes, integrate it and add tests for JSON with comments/trailing commas.
        -   [ ] If no (strict JSON only), consider removing `yaplon/file_strip/json.py` and the "json" style from `yaplon/file_strip/comments.py`.
    -   [ ] **Output Stream Handling (`__main__.py`, `writer.py`):**
        -   [ ] Standardize output stream management. Preferable: Click commands in `__main__.py` should always pass open, mode-correct file streams to `writer.py` functions.
        -   [ ] Refactor `writer.plist()` and `writer.xml()` to expect open streams, removing their internal `click.File()` / `open()` logic.
    -   [ ] **CLI Error Handling (`__main__.py`):**
        -   [ ] Wrap calls to reader/writer functions in `try-except` blocks within each CLI command.
        -   [ ] Use `click.echo(click.style(..., fg='red'))` for user-friendly error messages and `ctx.exit(1)` on error.
    -   [ ] **CSV `-k KEY` option (`__main__.py`, `reader.py`):**
        -   [ ] Investigate `default=0` for the Click option vs. likely 1-based indexing expectation in `reader.csv`.
        -   [ ] Adjust default or handling in `reader.csv` to prevent errors/unexpected behavior. Add explicit error for out-of-bounds key.
    -   [ ] **`oplist.strip_plist_comments`:**
        -   [ ] Clarify purpose or remove if redundant/unused (as `plistlib.load` handles XML comments).
    -   [ ] **Type Consistency for XML Conversions:**
        -   [ ] Decide if `reader.xml()` should attempt to convert string values (e.g., "true", "123") to Python types (bool, int, float) like `oplist._prepare_obj_for_plist` does, to ensure data read from XML is typed consistently before being passed to writers.
        -   [ ] Alternatively, or additionally, ensure `writer.xml()`'s `_prepare_obj_for_xml` (or a similar function) also converts stringified types from input Python objects to typed XML (if desired, current `_prepare_obj_for_xml` focuses on bytes/datetime).
        -   [ ] Consider if `writer.json()` and `writer.yaml()` should also have a pre-processing step for stringified numbers/booleans if data originates from `reader.xml()`.
    -   [ ] **Binary Data Handling in `x2j`:**
        -   [ ] Re-evaluate if a `-b` option (similar to `p2j`/`y2j`) should be added to `x2j` to convert base64 strings in XML to `{"__bytes__": ...}` or keep them as strings. Update help text accordingly.
    -   [ ] **`oplist.plist_convert_to` `none_handler='fail'`:** Clarify in docstrings how `plistlib.dumps` actually handles `None` when this option is chosen (it becomes an empty string value).

-   **Testing:**
    -   [ ] **CSV Conversion Tests:**
        -   [ ] Create `tests/test_csv_to_json.py`.
        -   [ ] Create `tests/test_csv_to_yaml.py`.
        -   [ ] Create `tests/test_csv_to_plist.py`.
        -   [ ] Create `tests/test_csv_to_xml.py`.
        -   [ ] Include tests for various dialects, headers, `-k` option, sorting, minification.
    -   [ ] **Address Skipped Tests:**
        -   [ ] `tests/test_json_to_plist.py`: `test_j2p_cli_binary_pipe_integrity`
        -   [ ] `tests/test_plist_to_json.py`: `test_p2j_cli_binary_pipe_preserve_binary`
        -   [ ] `tests/test_plist_to_xml.py`: `test_p2x_cli_pipe_binary_plist_input_default`
        -   [ ] `tests/test_plist_to_yaml.py`: `test_p2y_cli_pipe_binary_input_default`
    -   [ ] **Fulfill Test TODOs:**
        -   [ ] `tests/test_xml_to_plist.py`: Add sorting, namespace, error handling, None value, attribute tests.
        -   [ ] `tests/test_xml_to_yaml.py`: Add namespace, error handling, attribute representation tests.
    -   [ ] **XML Assertion:** Review `assert_xml_strings_equal_for_j2x` postprocessor. Determine if its type conversion is specific to J2X testing or if a more general XML assertion without this specific postprocessor is needed for other X2* tests where types are expected to be strings.

-   **Documentation & Minor Refinements:**
    -   [ ] Review and improve docstrings across all modules for clarity and completeness, especially for complex internal functions or behaviors (e.g., `oyaml.py` dumper, `oplist.py` None handling).
    -   [ ] Consider making `_cpp` and `_python` in `yaplon/file_strip/comments.py` static or regular methods of the `Comments` class for cleaner style.

## Phase 3: Documentation & Finalization
-   [ ] Update `README.md` with any new features or changes to CLI options.
-   [ ] Verify `CHANGELOG.md` is comprehensive.
-   [ ] Final test run for all modules.
-   [ ] Update `llms.txt` with `npx repomix -o ./llms.txt .`

## Future Considerations (Post-MVP Enhancements)
-   [ ] Explore alternative XML parsing/writing libraries if current ones have limitations.
-   [ ] Add support for more data formats (e.g., TOML, INI).
-   [ ] Performance profiling and optimization for large files.
-   [ ] More sophisticated type conversion options (e.g., user-defined schemas).
