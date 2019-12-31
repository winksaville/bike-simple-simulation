#!/usr/bin/env python3

# Typed Argument-Parser
from tap import Tap

import os
import tcx_track_list as tcx_tl
import csv_track_list as csx_tl
import track_point as tp
import path as p

class ArgumentsParser(Tap):
    in_filename: str # Input .tcx file name
    out_filename: str # Output .csv file name

    def add_arguments(self):
        self.add_argument('in_filename')
        self.add_argument('out_filename')

def main():
    try:
        extension: str
        trklist: List[tp.TrackList]
        path: p.Path

        args = ArgumentsParser(description="Convert tcx to csv file").parse_args();

        # Create trklist from tcx file
        _, extension = os.path.splitext(args.in_filename)
        if extension == '.tcx':
            path: p.Path = p.Path(tcx_tl.TcxTrackList(args.in_filename))
        else:
            raise ValueError(f"Unknown file extension:'{extension}' in {args.in_filename}, expecting '.tcx'")
        #print(f'total_distance={path.total_distance()}')

        # Validated output file has csv extension and write it
        _, extension = os.path.splitext(args.out_filename)
        if extension == '.csv':
            csx_tl.writeTrackListAsCsvToFile(path.trackList(), args.out_filename, header=tp.mkCsvHeader())
        else:
            raise ValueError(f"Unknown file extension:'{extension}' in {args.in_filename}, expecting '.csv'")
    except Exception as err:
        print(err)
    else:
        print('Done')

if __name__ == '__main__':
    main()
