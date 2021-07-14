#!python3.9

'''
    Calculation: Radial Distribution Function (RDF).
    Description: using Angstrom.
    Written by: Ignacio J. Chevallier-Boutell.
    Dated: July, 2021.
'''

import pandas as pd
import numpy as np

def user_input():
    '''
    User queries.
    '''

    # System
    file_in = input("Enter your xsf file: ")
    xsf = pd.read_csv(file_in, header = None, delim_whitespace = True, names=['idAt', 'rx', 'ry', 'rz', 'fx', 'fy', 'fz'])

    total_frames = int(xsf.iloc[0,1])
    Lx, Ly, Lz = float(xsf.iloc[3,0]), xsf.iloc[4,1], xsf.iloc[5,2]
    nAtTot = int(xsf.iloc[7,0])
    idAt = xsf.iloc[8:(nAtTot+8),0].drop_duplicates().tolist()
    xyz_all = xsf.iloc[6:,0:4].reset_index(drop=True)

    print('>>> Information from the input file:')
    print(f'\t * There are {total_frames} frames in the file.')
    print(f'\t * Cell dimensions (in Angstrom): (x, y, z) = ({Lx:.2f}, {Ly:.2f}, {Lz:.2f}).')
    print(f'\t * There are {nAtTot} atoms whithin the cell.')
    print(f'\t * Atomic species: {", ".join(idAt)}.')

    # Atoms to compare
    at1 = input("Choose one element of the list of atomic species: ")
    at2 = input("Choose another element of the list of atomic species: ")

    nAt1 = xsf.iloc[8:(nAtTot+8),0].value_counts()[at1]
    nAt2 = xsf.iloc[8:(nAtTot+8),0].value_counts()[at2]

    # xyz1 = xyz_all[xyz_all['idAt'] == at1].to_numpy()
    # xyz2 = xyz_all[xyz_all['idAt'] == at2].to_numpy()

    # # Number of frames
    # frame_start = 0
    # frame_end = -1

    # Histogram parameters
    dr = 0.1 # increment
    Rcut = 10.0 # maximum radius to be considered (max Value of the histogram)

    # Output file_out
    file_out = f'{file_in.split(".")[0]}_rdf-simple'

    return total_frames, Lx, Ly, Lz, nAtTot, xyz_all, at1, at2, nAt1, nAt2, dr, Rcut, file_out

def hist_init(dr, Rcut):
    '''
    Initialize the histogram.
    '''

    nBin = int(Rcut/dr) + 1 # number of bins
    Rcut = nBin * dr # adjust maximum
    H = np.zeros(nBin) # initialize array of zeros

    return nBin, Rcut, H

def PBC(dist, length): # Nacho
    '''
    Correct a distance using Periodic Boundary Conditions (PBC).
    '''

    if dist < -0.5 * length:
        dist += length
    elif dist > 0.5 * length:
        dist -= length

    return dist

# def PBC(dist, length): # Frenkel
#     '''
#     Correct a distance using Periodic Boundary Conditions (PBC).
#     '''
#
#     return dist - length * int(dist/length)

def hist_up(data, dr, H):
    '''
    Updates the existing histogram.

    It's considered that "data" is squared.
    '''

    binIdx = int(np.sqrt(data)/dr)
    H[binIdx] += 2 # contribution of i and j particles

def sample_diff(Lx, Ly, Lz, xyz1, xyz2, dr, Rcut, RDF, nAt1, nAt2):
    Rcut2 = Rcut * Rcut

    rx1 = np.array(xyz1[:,1])
    ry1 = np.array(xyz1[:,2])
    rz1 = np.array(xyz1[:,3])

    rx2 = np.array(xyz2[:,1])
    ry2 = np.array(xyz2[:,2])
    rz2 = np.array(xyz2[:,3])

    # Apply PBC and updates the histogram
    for i in range(nAt1):
        for j in range(nAt2):
            dx = rx1[i] - rx2[j]
            dx = PBC(dx, Lx)

            dy = ry1[i] - ry2[j]
            dy = PBC(dy, Ly)

            dz = rz1[i] - rz2[j]
            dz = PBC(dz, Lz)

            r2 = dx * dx + dy * dy + dz * dz

            if r2 <= Rcut2:
                # acá tiene 0.5 L siendo L el largo de la caja
                hist_up(r2, dr, RDF)

def normalize(Lx, Ly, Lz, nAt1, nAt2, dr, nBin, frames_count, RDF, file_out):
    '''
    Determine the normalize RDF.
    '''

    nAt = nAt1 + nAt2 # number of atoms compared
    rho = nAt / (Lx * Ly * Lz) # ideal (uniform) density
    prefact = 4 * np.pi
    dr3 = dr * dr * dr

    with open(f'{file_out}.dat', 'w') as f:
        for binIdx in range(nBin):
            # the distance is r = dr * (i + 0.5)
            volBin = prefact * ( (binIdx + 0.5) * (binIdx + 0.5) ) * dr3
            nIdeal = volBin * rho
            RDF[binIdx] /= frames_count * nIdeal * nAt
            f.write(f'{RDF[binIdx]} \n')

def main():

    total_frames, Lx, Ly, Lz, nAtTot, xyz_all, at1, at2, nAt1, nAt2, dr, Rcut, file_out = user_input()

    nBin, Rcut, RDF = hist_init(dr, Rcut)

    frames_count = 0
    rows = nAtTot + 2
    for frame in range(total_frames):
        xyz = xyz_all.iloc[(frame*rows + 2):((frame+1)*rows) , :]
        xyz1 = xyz[xyz['idAt'] == at1].to_numpy()
        xyz2 = xyz[xyz['idAt'] == at2].to_numpy()
        sample_diff(Lx, Ly, Lz, xyz1, xyz2, dr, Rcut, RDF, nAt1, nAt2)
        frames_count += 1

    normalize(Lx, Ly, Lz, nAt1, nAt2, dr, nBin, frames_count, RDF, file_out)

    print(f'Job done! The RDF file is: {file_out}.')
    
if __name__ == "__main__":
    main()