"""
Tally atoms in each given region.

Regions are given by X, Y, or Z coordinates dividing the space up.  The number
of atoms will be counted and written to the output.
"""

import argparse


def main():
    """Drive the main functionality."""

    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=globals()['__doc__'])
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), default='tally.dat',
        metavar='FILE', help='The output file.'
    )
    parser.add_argument(
        '-t', '--types', type=int, default=None, nargs='*', metavar='TYPES',
        help='The atomic types to be included in counting.'
    )
    parser.add_argument(
        '-a', '--axis', type=str, default='Z', choices=['X', 'Y', 'Z'],
        metavar='LABEL', help='The coordinate axis for the regions.'
    )
    parser.add_argument(
        '-s', '--time-step', type=float, default=1.0, metavar='TIME',
        help='The size of each time step.'
    )
    parser.add_argument(
        '-n', '--n-atoms', type=int, default=1, metavar='NUMBER',
        help='The number of atoms to be counted as a unit.'
    )
    parser.add_argument(
        'input', type=argparse.FileType('r'), metavar='INPUT',
        help='Concatenation of XYZ files from LAMMPS run'
    )
    parser.add_argument(
        'coordinates', type=float, nargs='+', metavar='COORDINATES',
        help='The separation coordinates on the axis'
    )
    args = parser.parse_args()

    # Parse the trajectory from the given XYZ file.
    traj = parse_traj(args.input)
    args.input.close()

    # Tally the atoms in each region.
    raw_tally = tally_atoms(traj, args.coordinates, args.axis, args.types)

    # Decorate the tallies.
    tally = [
        (s * args.time_step, [i / args.n_atoms for i in t])
        for s, t in raw_tally
    ]

    # Dump the output.
    output_tally(tally, args.output)
    args.output.close()

    return 0


def parse_traj(input_file):
    """Parse the trajectory XYZ file.

    The given file should be concatenation of XYZ file from LAMMPS.  The last
    field of the comment lines are interpreted as the time step count.
    """

    traj = []
    while True:
        first_line = input_file.readline()
        if first_line == '':
            break
        n_atoms = int(first_line)
        time_step = int(input_file.readline().split()[-1])

        coords = []
        for _ in range(0, n_atoms):
            fields = input_file.readline().split()
            coords.append((
                int(fields[0]),
                tuple(float(i) for i in fields[1:])
            ))
            continue

        traj.append((time_step, coords))
        continue

    return traj


def tally_atoms(traj, coords, axis, types):
    """Tally the atoms in each region.

    When the types is None, all atoms are counted.
    """

    idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]
    if types is not None:
        types = set(types)

    tallies = []
    for time, atoms in traj:
        tally = [0 for _ in range(0, len(coords) + 1)]
        for atom in atoms:
            if types is None or atom[0] in types:
                coord = atom[1][idx]
                region = 0
                for i in coords:
                    if coord > i:
                        break
                    else:
                        region += 1
                tally[region] += 1
            continue
        tallies.append((time, tally))
        continue

    return tallies


def output_tally(tally, out_fp):
    """Dumps the tally to a file in textual form."""
    for i in tally:
        fields = [i[0]]
        fields.extend(i[1])
        print(' '.join(str(i) for i in fields), file=out_fp)
        continue
    return


if __name__ == '__main__':
    main()
