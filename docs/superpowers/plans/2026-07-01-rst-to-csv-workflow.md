# RST To CSV Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tested command-line workflow that converts backed-up Workbench metadata plus large in-place RST files into Workbench-compatible `FaceAccel_*.CSV` files and validates them against the three reference cases.

**Architecture:** Keep metadata parsing, CSV formatting, RST access, exporting, and validation in separate modules. Use a fake RST reader in unit tests, and keep real RST extraction behind a dependency-checked adapter.

**Tech Stack:** Python 3.12+, standard library, NumPy/Pandas where available, optional `ansys-mapdl-reader` or DPF reader for real RST access, pytest for tests.

---

### Task 1: Project Skeleton And CSV Format

**Files:**
- Create: `pyproject.toml`
- Create: `src/rst2csv/__init__.py`
- Create: `src/rst2csv/csv_format.py`
- Test: `tests/test_csv_format.py`

- [ ] Write tests for face/probe numbering and Workbench-style headers.
- [ ] Run the tests and confirm they fail because the module does not exist.
- [ ] Implement the smallest CSV formatting module that passes the tests.
- [ ] Run the tests and confirm they pass.

### Task 2: Metadata Parsing

**Files:**
- Create: `src/rst2csv/mapping.py`
- Test: `tests/test_mapping.py`

- [ ] Write tests for APDL integer range expansion, sensor body element parsing, and probe-to-node mapping.
- [ ] Run the tests and confirm they fail.
- [ ] Implement parsing from backed-up `ds.dat`.
- [ ] Run the tests and confirm they pass.

### Task 3: Export Pipeline With Fake Reader

**Files:**
- Create: `src/rst2csv/exporter.py`
- Create: `src/rst2csv/rst_reader.py`
- Test: `tests/test_exporter.py`

- [ ] Write tests that use a fake reader with known acceleration vectors.
- [ ] Run the tests and confirm they fail.
- [ ] Implement total acceleration magnitude, max aggregation, row generation, and CSV writing.
- [ ] Run the tests and confirm they pass.

### Task 4: Validation Report

**Files:**
- Create: `src/rst2csv/validator.py`
- Test: `tests/test_validator.py`

- [ ] Write tests for structural mismatch and numeric error metrics.
- [ ] Run the tests and confirm they fail.
- [ ] Implement validation against reference CSVs.
- [ ] Run the tests and confirm they pass.

### Task 5: CLI And User Documentation

**Files:**
- Create: `src/rst2csv/cli.py`
- Create: `scripts/rst2csv.py`
- Create: `Result/RST直接导出CSV工作流说明.md`

- [ ] Add CLI commands for mapping inspection, export, validate, and run.
- [ ] Add dependency detection and clear install guidance.
- [ ] Document backup policy, paths, usage examples, and validation interpretation.
- [ ] Run the full unit test suite.
- [ ] Run case-level verification where the available environment supports RST reading.

