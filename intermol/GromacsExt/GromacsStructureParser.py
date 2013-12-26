from collections import deque, defaultdict
import pdb

from intermol.Atom import *
from intermol.Molecule import *
from intermol.System import System

def readStructure(filename):
    """Read in a Gromacs structure file

    Args:
        filename (str): the file to be read in
    """

    fd = open(filename, 'r')
    lines = list(fd)
    fd.close()

    # struct to count number of a moleculetype already added
    count_mols = dict()
    for moleculetype in System._sys._molecules:
        count_mols[moleculetype] = 0

    #indices = dict()
    #line_num = 2
    #for mol_name, mol_num, mol_len in System._sys._components:
    #    if mol_name in indices:
    #        pass
    #    else:
    #        end = line_num + mol_num * mol_len
    #        indices[mol_name] = (line_num, end)
    #        line_num = end

    #pdb.set_trace()
    i = 2
    # only loop through molecules actually present in system
    #for moleculetype in System._sys._molecules.values():
    pdb.set_trace()
    for name, total_mols, mol_len in System._sys._components:
        moleculetype = System._sys._molecules[name]
        #try:
        #    span = component_indices[moleculetype.name]
        #except:
        #    # molecule defined in .top but not in system
        #    continue

        #if isinstance(span, tuple):
        #    i = span[0]
        #    end = span[1]
        #else:
        #    pass
        # keep track of how many read for cases with multiple of same name
        already_read = count_mols[moleculetype.name]
        #for molecule in moleculetype.moleculeSet:
        for m in xrange(already_read, total_mols + already_read):
            molecule = moleculetype.moleculeSet[m]
            count_mols[moleculetype.name] += 1
            for atom in molecule._atoms:
                if lines[i]:
                    line = lines[i]
                    atom.residueIndex=int(line[0:5])
                    atom.residueName = line[5:10].strip()
                    atom.atomName = line[10:15].strip()
                    atom.atomIndex = int(line[15:20])
                    x = float(line[20:28]) * units.nanometers
                    y = float(line[28:36]) * units.nanometers
                    z = float(line[36:44]) * units.nanometers
                    atom.setPosition(x, y, z)
                    try:
                        vx = float(line[44:52]) * units.nanometers / units.picoseconds
                        vy = float(line[52:60]) * units.nanometers / units.picoseconds
                        vz = float(line[60:68]) * units.nanometers / units.picoseconds
                    except:
                        vx = 0.0 * units.nanometers / units.picoseconds
                        vy = 0.0 * units.nanometers / units.picoseconds
                        vz = 0.0 * units.nanometers / units.picoseconds
                    atom.setVelocity(vx, vy, vz)
                    i += 1
                else:
                    raise Exception("Reached end of .gro file before all atoms were populated.")
        for molecule in moleculetype.moleculeSet:
            for atom in molecule._atoms:
                print atom._position

    #for moleculetype in System._sys._molecules.values():
    #    for molecule in moleculetype.moleculeSet:
    #        for atom in molecule._atoms:
    #            print atom._position

    rawBoxVector = lines[i].split()
    v1x = None
    v2x = None
    v3x = None
    v1y = None
    v2y = None
    v3y = None
    v1z = None
    v2z = None
    v3z = None
    if len(rawBoxVector) == 3:
        v1x = float(rawBoxVector[0]) * units.nanometers
        v2x = 0.0 * units.nanometers
        v3x = 0.0 * units.nanometers
        v1y = 0.0 * units.nanometers
        v2y = float(rawBoxVector[1]) * units.nanometers
        v3y = 0.0 * units.nanometers
        v1z = 0.0 * units.nanometers
        v2z = 0.0 * units.nanometers
        v3z = float(rawBoxVector[2]) * units.nanometers

    elif len(rawBoxVector) == 9:
        v1x = float(rawBoxVector[0:10]) * units.nanometers
        v2x = float(rawBoxVector[11:22]) * units.nanometers
        v3x = float(rawBoxVector[23:34]) * units.nanometers
        v1y = float(rawBoxVector[35:46]) * units.nanometers
        v2y = float(rawBoxVector[47:58]) * units.nanometers
        v3y = float(rawBoxVector[59:70]) * units.nanometers
        v1z = float(rawBoxVector[71:82]) * units.nanometers
        v2z = float(rawBoxVector[83:94]) * units.nanometers
        v3z = float(rawBoxVector[95:106]) * units.nanometers
    System._sys.setBoxVector(v1x, v2x, v3x, v1y, v2y, v3y, v1z, v2z, v3z)

def writeStructure(filename):
    """Write the system out  in a Gromacs 4.5.4 format

    Args:
        filename (str): the file to write out to
    """
    lines = list()
    i=0
    for moleculetype in System._sys._molecules.values():
        for molecule in moleculetype.moleculeSet:
            for atom in molecule._atoms:
                i += 1
                lines.append('%5d%-4s%6s%5d%8.3f%8.3f%8.3f%8.4f%8.4f%8.4f\n'
                        %(atom.residueIndex,
                        atom.residueName,
                        atom.atomName,
                        atom.atomIndex,
                        atom._position[0]._value,
                        atom._position[1]._value,
                        atom._position[2]._value,
                        atom._velocity[0]._value,
                        atom._velocity[1]._value,
                        atom._velocity[2]._value))
    lines.append('%10.6f %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f\n'
          %(System._sys._v1x._value,
            System._sys._v2y._value,
            System._sys._v3z._value,
            System._sys._v1y._value,
            System._sys._v1z._value,
            System._sys._v2x._value,
            System._sys._v2z._value,
            System._sys._v3x._value,
            System._sys._v3y._value))

    lines.insert(0, (System._sys._name+'\n'))
    lines.insert(1, str(i)+'\n')

    fout = open(filename, 'w')
    for line in lines:
        fout.write(line)
    fout.close()


