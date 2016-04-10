"""
Concatenates dumps from a LAMMPS script.

All dumps in the given LAMMPS script will be concatenated into single files
separately, which are to be written in the current working directory.
"""

import argparse
import re
import os.path
import glob


def main():
    """Drive the script."""

    parser = argparse.ArgumentParser(description=globals()['__doc__'])
    parser.add_argument(
        'input', type=argparse.FileType(mode='r'), metavar='INPUT',
        help='The LAMMPS input file whose dumps are to be concatenated.'
    )
    args = parser.parse_args()

    dump_cater = DumpCater(args.input)
    args.input.close()
    dump_cater.cat_dumps()

    return 0


class DumpCater(object):
    """Concatenator of LAMMPS dump files."""

    __slots__ = [
        'base_path',
        'vars',
        'dumps'
    ]

    def __init__(self, input_fp):
        """Initialize the concatenator from the input file object."""

        self.base_path = os.path.dirname(input_fp.name)
        self.vars = {}
        self.dumps = []

        for line in input_fp:
            fields = line.split()
            if len(fields) == 0:
                continue
            cmd = fields[0]

            if cmd == 'variable':
                self.vars[fields[1]] = fields[-1]
            elif cmd == 'dump':
                self.dumps.append(
                    self.subst_vars(fields[-1])
                )
            else:
                pass  # Skip all other lines.

        return

    def subst_vars(self, inp_str):
        """Substitute all variable references in the given string."""
        var_ref = re.compile(r'\$\{(?P<name>\w*)\}')

        # The string is going to be substituted for variable reference
        # repeatedly.
        curr = inp_str

        while True:
            match = var_ref.search(curr)
            if not match:
                break
            else:
                var_name = match.group('name')
                try:
                    curr = curr.replace(
                        ''.join(['${', var_name, '}']), self.vars[var_name]
                    )
                except KeyError:
                    print('Undefined variable {} in script!'.format(var_name))
                continue

        return curr

    def cat_dumps(self):
        """Concatenates all the dumps in the input script."""
        for dump in self.dumps:

            # Get all the file names and sort according to step number.
            file_names = sorted(glob.glob(
                os.path.join(self.base_path, dump)
            ), key=self.form_step_getter(dump))

            with open(dump.replace('*', ''), 'w') as out_fp:
                for name in file_names:
                    with open(name, 'r') as inp_fp:
                        out_fp.write(inp_fp.read())
                    continue

            continue
        return

    @staticmethod
    def form_step_getter(dump):
        """Form the function to get the step number from a file name."""
        patt = re.compile(
            dump.replace('.', r'\.').replace('*', r'(?P<step>\d+)')
        )

        def get_step(name):
            """Get the step number from the file name."""
            match = patt.search(os.path.basename(name))
            return int(match.group('step'))

        return get_step


if __name__ == '__main__':
    main()
