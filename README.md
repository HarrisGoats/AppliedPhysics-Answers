# Guide to run
    uv sync 
    uv run python main.py

## Adjust array details with 

    TransducerArray(kgrid, (100,100), (8,8), 13, 13)

(100,100): center point

(8,8)    : x and y element spacing on grid

13, 13   : points in x and y direction

## Set array focal point with:

    delay_mask1, amplitude_mask1 = arr1.beam_stear((px,py))

leave args empty for no steering

### Final note:

    source.p = build_source_signals(delay_mask1 + delay_mask2 +1,amplitude_mask1+amplitude_mask2, base_signal, kgrid.Nt)

we add +1 to the masks to account for using -1 as no element. include an +(# of arrays - 1) to the sum of masks


# Results

![No Beam Steering](/images/Figure_3.png)


Beam steering was done through calculating distance from each element to focal point and setting phase accordingly. a hanning window was applied to element amplitudes to reduce side lobes. See code for full implementation.

![Beam Steering](/images/Figure_4.png)

dB version

![Beam Steering](/images/Figure_5.png)


# Assumptions:
* Speed of sound in air of 343 m/s with density of 1.2 kg/m3 at 20C room temp.
* Air is ideal, IE: constant pressure, temp and speed in time and space, no turbulence, or noise.
* Elements are point sources and omnidirectional emitters in the 2D plane
* Element spacing: 8mm. Chosen as being ~wavelength, and minimum reasonable distanced based on off the shelf 40khz emitters found on digikey/mauser. λ/2 or ~4mm would be better if I found a cheap source of smaller emitters
* I chose 13x13 emitter grids. prime number N should help a little with side lobes. 
* No non-linear effects, I modeled solely superposition. while non-linear effects would cause wave distortion, but in the real world, these effects are dwarfed by object reflections and air conditions. 
* Simulation is far field, but still close to the near/far boundary. 


# Next steps

2 hours: Adjust simulation to larger area and see further far field simulations. Simulation area beyond 500mm^2 was starting to take longer than I prefer for a problem with a quicker turnaround. With extra time, I would add a variable grid with grid adaption based on how dB pressure and pressure delta. Looking at the last plot, I could adjust the grid to be 2mm in much of the dark blue areas, and leave it at 1mm in the main beams and beam intersection. This would also require changing my TransducerArray class to be less directly ties to the kgrid. 

4-8 hours: Monty Carlo simulations to see effects of less-ideal medium. This would mean random distributions of temperature gradient and flow, with extra time to work these distributions could be time dependant. This information could then be used to help adapt the beam steering algorithm and understand uncertainty in how well we can target a point. 

