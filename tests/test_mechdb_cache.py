import csv
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from rst2csv.mechdb_cache import (
    decompress_chunked_zlib_stream,
    extract_probe_histories_from_simulation_stream,
    export_cached_probe_csvs,
)


def chunked(*chunks):
    stream = bytearray()
    for chunk in chunks:
        compressed = zlib.compress(chunk)
        stream.extend(struct.pack("<I", len(compressed)))
        stream.extend(compressed)
    return bytes(stream)


def fake_probe_record(probe_number, values):
    name = f"Face_Accel_Probe_{probe_number}".encode("utf-16le")
    offset = 8158 + 2 * (len(str(probe_number)) - 1)
    record = bytearray(name)
    record.extend(b"\x00" * (offset - len(record)))
    record.extend(struct.pack(f"<{len(values)}d", *values))
    return bytes(record)


class MechdbCacheTests(unittest.TestCase):
    def test_decompress_chunked_zlib_stream_joins_all_chunks(self):
        stream = chunked(b"abc", b"defgh")

        self.assertEqual(decompress_chunked_zlib_stream(stream), b"abcdefgh")

    def test_extract_probe_histories_uses_digit_adjusted_value_offset(self):
        simulation_stream = (
            b"prefix"
            + fake_probe_record(1, [0.1, 0.2, 0.3])
            + b"between"
            + fake_probe_record(10, [1.1, 1.2, 1.3])
        )

        histories = extract_probe_histories_from_simulation_stream(
            simulation_stream,
            result_count=3,
        )

        self.assertEqual(histories[1], (0.1, 0.2, 0.3))
        self.assertEqual(histories[10], (1.1, 1.2, 1.3))

    def test_export_cached_probe_csvs_writes_workbench_shaped_face_file(self):
        histories = {probe: (float(probe), float(probe) + 0.5) for probe in list(range(1, 51)) + list(range(101, 151))}
        result_sets = [(1, 0.1), (2, 2.0001)]
        with tempfile.TemporaryDirectory() as tmp:
            written = export_cached_probe_csvs(
                histories,
                result_sets,
                Path(tmp),
                faces=("A",),
            )

            with written[0].open("r", encoding="gb2312", newline="") as stream:
                rows = list(csv.reader(stream))

        self.assertEqual(written[0].name, "FaceAccel_A.CSV")
        self.assertEqual(len(rows), 3)
        self.assertIn("Face_Accel_Probe_1", rows[0][3])
        self.assertIn("Face_Accel_Probe_101", rows[0][53])
        self.assertEqual(rows[1][:5], ["1", "1", "0.1", "1", "2"])
        self.assertEqual(rows[2][:5], ["2", "2", "2.0001", "1.5", "2.5"])


if __name__ == "__main__":
    unittest.main()
