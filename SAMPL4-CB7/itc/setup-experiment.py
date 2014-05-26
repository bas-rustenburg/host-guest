# Plan ITC experiment.

import itc


from simtk.unit import *

# Define solvents.
from automation import Solvent
water = Solvent('water', density=0.9970479*grams/milliliter)
buffer = Solvent('buffer', density=1.014*grams/milliliter)

# Define compounds.
from automation import Compound
nguests = 14 # number of guest compounds
nguests = 7 # number of guest compounds # DEBUG (one source plate only)
host = Compound('host', molecular_weight=1162.9632*daltons, purity=0.7133)
guest_molecular_weights = [209.12, 123.62, 153.65, 189.13, 187.11, 151.63, 135.64, 149.66, 163.69, 238.59, 147.65, 189.73, 173.68, 203.71]
guests = [ Compound(name='guest%02d' % (guest_index+1), molecular_weight=guest_molecular_weights[guest_index]*daltons, purity=0.975) for guest_index in range(nguests) ]

# Define troughs on the instrument.
from labware import Labware
water_trough = Labware(RackLabel='Water', RackType='Trough 100ml')
buffer_trough = Labware(RackLabel='Buffer', RackType='Trough 100ml')

# Define source labware.
#source_plate = Labware(RackLabel='SourcePlate', RackType='12WellVialHolder')
source_plate = Labware(RackLabel='SourcePlate', RackType='5x3 Vial Holder')

# Define source solutions on the deck.one
# TODO : Use actual compound and solvent masses.
# NOTE: Host solution is diluted by 10x.
from automation import SimpleSolution, PipettingLocation
host_solution = SimpleSolution(compound=host, compound_mass=1.6304*milligrams, solvent=buffer, solvent_mass=10.0*grams, location=PipettingLocation(source_plate.RackLabel, source_plate.RackType, 1))
guest_solutions = list()
guest_compound_masses = Quantity([2.145, 1.268, 1.576, 1.940, 1.919, 1.555, 1.391, 1.535, 1.679, 2.447, 1.514, 1.946, 1.781, 2.089], milligrams)
for guest_index in range(nguests):
    guest_solutions.append( SimpleSolution(compound=guests[guest_index], compound_mass=guest_compound_masses[guest_index], solvent=buffer, solvent_mass=10.0*grams, location=PipettingLocation(source_plate.RackLabel, source_plate.RackType, 2+guest_index)) )

# Define ITC protocol.
from itc import ITCProtocol
# Protocol for 'control' titrations (water-water, buffer-buffer, titrations into buffer, etc.)
control_protocol = ITCProtocol('control protocol', sample_prep_method='chodera.setup', itc_method='jdcwater.inj', analysis_method='Control')
# Protocol for 1:1 binding analyis
binding_protocol = ITCProtocol('1:1 binding protocol', sample_prep_method='chodera.setup', itc_method='jdcwater.inj', analysis_method='Onesite')

# Define ITC Experiment.
from itc import ITCExperimentSet, ITCExperiment
itc_experiment_set = ITCExperimentSet(name='SAMPL4-CB7 host-guest experiments') # use specified protocol by default
# Add available plates for experiments.
itc_experiment_set.addDestinationPlate(Labware(RackLabel='DestinationPlate', RackType='ITC Plate'))
itc_experiment_set.addDestinationPlate(Labware(RackLabel='DestinationPlate2', RackType='ITC Plate'))

nreplicates = 1 # number of replicates of each experiment

# Add water control titrations.
for replicate in range(nreplicates):
    name = 'water into water %d' % (replicate+1)
    itc_experiment_set.addExperiment( ITCExperiment(name=name, syringe_source=water_trough, cell_source=water_trough, protocol=control_protocol) )

# Host into buffer.
for replicate in range(nreplicates):
    name = 'buffer into buffer %d' % (replicate+1)
    itc_experiment_set.addExperiment( ITCExperiment(name=name, syringe_source=host_solution, cell_source=buffer_trough, protocol=control_protocol) )

# Host into guests.
for guest_index in range(nguests):
    # Buffer into guest.
    for replicate in range(nreplicates):
        name = 'buffer into %s' % guests[guest_index].name
        itc_experiment_set.addExperiment( ITCExperiment(name=name, syringe_source=buffer_trough, cell_source=guest_solutions[guest_index], protocol=control_protocol, cell_concentration=0.2*millimolar, buffer_source=buffer_trough) )
    # Host into guest.
    for replicate in range(nreplicates):
        name = 'host into %s' % guests[guest_index].name
        itc_experiment_set.addExperiment( ITCExperiment(name=name, syringe_source=host_solution, cell_source=guest_solutions[guest_index], protocol=control_protocol, cell_concentration=0.2*millimolar, buffer_source=buffer_trough) )

# Water control titrations.
nfinal = 3
for replicate in range(nfinal):
    name = 'water into water %d' % (replicate+1)
    itc_experiment_set.addExperiment( ITCExperiment(name=name, syringe_source=water_trough, cell_source=water_trough, protocol=control_protocol) )

# Check that the experiment can be carried out using available solutions and plates.
itc_experiment_set.validate()

# Write Tecan EVO pipetting operations.
worklist_filename = 'setup-itc.gwl'
itc_experiment_set.writeTecanWorklist(worklist_filename)

# Write Auto iTC-200 experiment spreadsheet.
excel_filename = 'run-itc.xls'
itc_experiment_set.writeAutoITCExcel(excel_filename)


