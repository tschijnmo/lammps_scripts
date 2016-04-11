"""Compute the diffusion process from atom counts in two regions.

The diffusion of atoms from one region to another is modelled as a first-order
process.  The flow rate of atoms is considered to be proportional to the
difference of the number of atoms in the two regions.  By using this script,
the logarithm of the difference in the number of atoms is fitted linearly with
time.  The resulted slop can be a measure of the diffusion rate.
"""

import argparse
import math

import numpy as np
import numpy.linalg

import matplotlib.pyplot as plt


def main():
    """Drive the script."""

    # Parse the arguments.
    parser = argparse.ArgumentParser(description=globals()['__doc__'])
    parser.add_argument(
        'input', type=argparse.FileType('r'), metavar='INPUT',
        help='The input file, which contains time and number of atoms '
        'in the two regions as columns'
    )
    parser.add_argument(
        '--begin', '-b', type=float, metavar='TIME',
        help='The beginning time for the fitting'
    )
    parser.add_argument(
        '--end', '-e', type=float, metavar='TIME',
        help='The end time for the fitting'
    )
    parser.add_argument(
        '--graph', '-g', type=str, metavar='FILE', default='diffusion.png',
        help='The graph file for the graphics of the fitting.'
    )
    args = parser.parse_args()

    # Parse the filter the trajectory.
    traj = parse_traj(args.input)
    traj = filter_traj(traj, args.begin, args.end)

    # Perform the fit.
    diff_coeff, log_d0 = fit_traj(traj)
    print('Diffusion coefficient: {}'.format(diff_coeff))

    # Plot the graphics.
    plot_fit(args.graph, traj, diff_coeff, log_d0)

    return 0


def parse_traj(input_fp):
    """Parse the trajectory file.

    The atoms diffuse from the second region to the first region.
    """
    traj = [
        [float(i) for i in line.split()]
        for line in input_fp
    ]
    if traj[0][1] > traj[0][2]:
        traj = [[i[0], i[2], i[1]] for i in traj]
    return traj


def filter_traj(traj, begin_time, end_time):
    """Filter the trajectory for only steps within the time region."""
    filtered_traj = []
    for i in traj:
        time = i[0]
        if end_time is not None and time > end_time:
            break
        elif begin_time is None or time > begin_time:
            filtered_traj.append(i)
        else:
            continue
    return filtered_traj


def fit_traj(traj):
    """Fir the log of atom number difference against time."""
    time = np.array([[i[0], 1.0] for i in traj], dtype=np.float64)
    diff = np.log(np.array(
        [(i[2] - i[1]) for i in traj], dtype=np.float64
    ))

    return np.linalg.lstsq(time, diff)[0]


def plot_fit(file_name, traj, diff_coeff, log_d0):
    """Plots the fitting curve."""
    time = [i[0] for i in traj]
    orig_diff = [i[2] - i[1] for i in traj]
    fit_diff = [math.exp(diff_coeff * i + log_d0) for i in time]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Fit of the diffusion coefficient: {}'.format(diff_coeff))
    ax.set_xlabel('Time')
    ax.set_ylabel('Concentration difference')
    ax.semilogy(
        time, orig_diff, marker='x', linestyle='', label='Simulation'
    )
    ax.semilogy(
        time, fit_diff, linestyle='-', label='fit'
    )
    ax.legend(loc='best', fancybox=True, shadow=True)

    fig.savefig(file_name)

if __name__ == '__main__':
    main()
