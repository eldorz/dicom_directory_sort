# convert from folder structure outputted by storescp to study/series/*

# takes a top-level directory containing multiple studies

import argparse
import logging
import pydicom
from shutil import copyfile
import os
import glob

def get_dirs(input_dir):
    return glob.glob(os.path.join(input_dir, "*"))

def make_dir(d):
    # ensure output dir exists
    if not os.path.isdir(d):
        if os.path.exists(d):
            raise RuntimeError("{0} exists but is not a directory".\
                format(d))
        else:
            os.mkdir(d)

def get_dcms_from_dir(d):
    files = glob.glob(os.path.join(d, "*"))
    if len(files) == 0:
        raise RuntimeError("No files in {0}".format(d))
    dcms = []
    for f in files:
        try:
            pydicom.filereader.dcmread(f, stop_before_pixels=True)
        except pydicom.errors.InvalidDicomError:
            logging.warning('{0} is not a valid dicom file'.format(f))
            continue
        dcms.append(f)
    return dcms

def process_dirs(d, output_dir):
    dcms = get_dcms_from_dir(d)
    currentAccession = None
    currentSeries = None
    for dcm in dcms:
        ds = pydicom.filereader.dcmread(dcm, stop_before_pixels=True)
        accessionDir = os.path.join(output_dir, str(ds.AccessionNumber))
        seriesDir = os.path.join(accessionDir, str(ds.SeriesNumber))
        if currentAccession != str(ds.AccessionNumber):
            make_dir(accessionDir)
            currentAccession = str(ds.AccessionNumber)
        if currentSeries != str(ds.SeriesNumber):
            make_dir(seriesDir)
            currentSeries = str(ds.SeriesNumber)
        newfilename = os.path.join(seriesDir, os.path.basename(dcm))
        if not os.path.exists(newfilename):
            copyfile(dcm, newfilename)

def main(args):
    logging.basicConfig(level=logging.DEBUG)
    dirs = get_dirs(args.input_dir)
    make_dir(args.output_dir)
    for d in dirs:
        process_dirs(d, args.output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    main(args)