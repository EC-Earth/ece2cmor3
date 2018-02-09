#!/usr/bin/env python
import argparse
import csv

import os

from ece2cmor3 import grib_file


def main():
    parser = argparse.ArgumentParser(description="Create csv file of grib field description parameters (for testing "
                                                 "only)")
    parser.add_argument("input", metavar="FILE", type=str, help="Input grib file (Required)")

    args = parser.parse_args()

    os.environ["GRIB_API_PYTHON_NO_TYPE_CHECKS"] = "1"

    with open(args.input, 'r') as input_file, open(os.path.basename(args.input) + ".csv", 'w') as output_file:
        reader = grib_file.ecmwf_grib_api(input_file)
        writer = csv.writer(output_file)
        while reader.read_next(headers_only=True):
            row = [reader.get_field(name) for name in grib_file.csv_grib_mock.columns]
            if row[2] in [38, 42, 236]:
                row[4] = 289
            writer.writerow(row)
            reader.release()


if __name__ == "__main__":
    main()
