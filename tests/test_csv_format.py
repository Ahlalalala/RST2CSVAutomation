import unittest

from rst2csv.csv_format import (
    FACE_ORDER,
    csv_header_for_face,
    excel_column_name,
    format_probe_value,
    format_time_value,
    probe_numbers_for_face,
)


class CsvFormatTests(unittest.TestCase):
    def test_probe_numbers_follow_face_and_side_gaps(self):
        self.assertEqual(FACE_ORDER, ("A", "B", "C", "D", "E", "F", "G"))
        self.assertEqual(probe_numbers_for_face("A")[:5], [1, 2, 3, 4, 5])
        self.assertEqual(
            probe_numbers_for_face("A")[45:55],
            [46, 47, 48, 49, 50, 101, 102, 103, 104, 105],
        )
        self.assertEqual(probe_numbers_for_face("G")[:3], [1201, 1202, 1203])
        self.assertEqual(probe_numbers_for_face("G")[-3:], [1348, 1349, 1350])

    def test_excel_column_names_match_workbench_export(self):
        self.assertEqual(excel_column_name(1), "A")
        self.assertEqual(excel_column_name(26), "Z")
        self.assertEqual(excel_column_name(27), "AA")
        self.assertEqual(excel_column_name(52), "AZ")
        self.assertEqual(excel_column_name(53), "AAA")
        self.assertEqual(excel_column_name(100), "AAAV")

    def test_csv_header_matches_reference_shape_and_text(self):
        header = csv_header_for_face("A")

        self.assertEqual(len(header), 103)
        self.assertEqual(header[:3], ["", "步骤", "时间 [s]"])
        self.assertEqual(header[3], "[A] Face_Accel_Probe_1  (总体) [m/s?]")
        self.assertEqual(header[52], "[AX] Face_Accel_Probe_50  (总体) [m/s?]")
        self.assertEqual(header[53], "[AY] Face_Accel_Probe_101  (总体) [m/s?]")
        self.assertEqual(header[-1], "[AAAV] Face_Accel_Probe_150  (总体) [m/s?]")


    def test_format_probe_value_matches_workbench_display_style(self):
        self.assertEqual(format_probe_value(0.0), "0")
        self.assertEqual(format_probe_value(0.0001044), "1.04E-04")
        self.assertEqual(format_probe_value(0.0003114951775039915), "3.12E-04")
        self.assertEqual(format_probe_value(6.524951844818996e-05), "6.53E-05")
        self.assertEqual(format_probe_value(0.008324666701642058), "8.32E-03")
        self.assertEqual(format_probe_value(0.0177495018924389), "1.78E-02")
        self.assertEqual(format_probe_value(0.10082), "0.10082")
        self.assertEqual(format_probe_value(1.0052), "1.0052")
        self.assertEqual(format_probe_value(10.7094978564581), "10.709")

    def test_format_time_value_matches_workbench_display_style(self):
        self.assertEqual(format_time_value(2.0001000000000002), "2.0001")
        self.assertEqual(format_time_value(2.00015), "2.0002")
        self.assertEqual(format_time_value(2.0025459908770276), "2.0025")
        self.assertEqual(format_time_value(2.0095545839206324), "2.0096")
        self.assertEqual(format_time_value(1.9500000000000006), "1.95")
        self.assertEqual(format_time_value(2.0), "2")
        self.assertEqual(format_time_value(0.15000000000000002), "0.15")


if __name__ == "__main__":
    unittest.main()
