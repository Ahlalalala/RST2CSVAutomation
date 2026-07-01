# RST To CSV Workflow Design

## Goal

Build a repeatable workflow that converts ANSYS transient `.rst` files into the same seven `FaceAccel_*.CSV` files currently exported manually from Workbench, then verifies generated CSVs against the three backed-up reference cases.

## Inputs

- Large result files stay in place at `E:/WCL/AnsysTunnel/RSTVoidBatch/<case>.rst`.
- All non-RST inputs are copied into this workspace before use:
  - `Backup/OriginData/<case>/FaceAccel_*.CSV`
  - `Backup/Workbench/<case>/ds.dat`
  - `Backup/Workbench/<case>/CAERep.xml`
  - `Backup/Workbench/<case>/<case>.wbpj`

The workflow must not modify `OriginData/` or `E:/WCL/AnsysTunnel/`.

## Architecture

The workflow is split into small Python modules:

- `mapping.py` parses the backed-up Workbench/APDL metadata and builds the probe mapping.
- `csv_format.py` owns the Workbench-compatible CSV shape, column names, encoding, and face/probe numbering.
- `rst_reader.py` hides the result-reader dependency behind a small interface.
- `exporter.py` combines RST acceleration values with probe mappings and writes CSVs.
- `validator.py` compares generated CSVs with the backed-up reference CSVs and writes a report.
- `cli.py` exposes `export`, `validate`, and `run` commands.

## Data Flow

1. Discover case names from `Backup/Workbench`, `Backup/OriginData`, or explicit command-line arguments.
2. Parse each backed-up `ds.dat` to find sensor body element blocks and node IDs.
3. Map Workbench probe numbers to those sensor node scopes using the documented face/side numbering.
4. Read nodal acceleration from the `.rst` at all result sets.
5. Compute total acceleration magnitude for each scoped sensor and apply Workbench's `SpatialResolution=Max` aggregation.
6. Write one GB2312 CSV per face with the same 103-column layout as the reference exports.
7. Validate generated files against `Backup/OriginData` and write per-file error metrics.

## Error Handling

- Missing backed-up metadata, missing RST files, missing reader dependency, or unmatched probe scopes fail with actionable messages.
- Generated output is written under `Generated/` by default and never overwrites references unless the user passes an explicit output path.
- Validation reports both structural mismatches and numeric differences.

## Testing

Tests cover CSV layout, CMBLOCK expansion, sensor element parsing, probe numbering, validation metrics, and dependency error messages. A small fake RST reader is used for unit tests so tests do not require loading 300 GB result files.

Integration verification uses the three backed-up cases. If the ANSYS result reader dependency is unavailable, the report records that numeric RST extraction could not be run and explains how to install the dependency.

