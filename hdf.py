 #!/usr/bin/env python3.9

'''
    Calculation: Height Distribution Function (HDF).
    Description: Determines de HDF along Z axis when given a xsf file.
                Everything is in Angstrom.
    Written by: Ignacio J. Chevallier-Boutell.
    Dated: August, 2021.
'''

import argparse
from core import user_file_mono, hist_init
from numpy import array
from time import time

def main():
    start = time() # starting wall time

    dh = args.dh
    at = args.at

    total_frames, Lx, Ly, Lz, nAtTot, nAt, xyz_all = user_file_mono(args.input_file, at)

    nBin, Lz, HDF = hist_init(dh, Lz)

    frames_count = 0
    rows = nAtTot + 2

    frame_start = int(args.frames[0])
    if frame_start != 0:
        frame_start -= 1
    frame_end = int(args.frames[1])
    if frame_end == -1:
        frame_end = total_frames

    for frame in range(frame_start, frame_end):
        xyz = xyz_all.iloc[(frame*rows + 2):((frame+1)*rows) , :]
        xyz = xyz[xyz['idAt'] == at].to_numpy()

        dz = array(xyz[:,3])
        for i in range(nAt):
            binIdx = int(dz[i]/dh)
            HDF[binIdx] += 1

        frames_count += 1

    output_file = args.output_file
    if output_file == None:
        output_file = f'hdf_{at}'

    with open(f'{output_file}.dat', 'w') as f:
        for binIdx in range(nBin):
            h = (binIdx + 0.5) * dh
            HDF[binIdx] /= frames_count
            f.write(f'{h:.2f}, {HDF[binIdx]:.4f} \n')

    elapsed = time() - start # elapsed wall time
    print(f'Job done in {elapsed:.3f} seconds!')
    print(f'HDF for {at} was calculated.')
    print(f'Output file: {output_file}.dat')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', help = "Path to the xsf input file.")

    parser.add_argument('dh', type = float, help = "Increment to be considered.")

    parser.add_argument('at', help = "Atom to be analyzed.")

    parser.add_argument('-o', '--output_file', help = "Path to the output file. \
                        If not given, the default name will be used.")

    parser.add_argument('-f', '--frames', nargs = 2, default = [0, -1],
                        help = "Choose starting and ending frames to compute.")

    args = parser.parse_args()

    main()