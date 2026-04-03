# Guide to run
    uv sync 
    uv run python main.py

## adjust array details with 

    TransducerArray(kgrid, (100,100), (8,8), 13, 13)

(100,100): center point

(8,8)    : x and y element spacing on grid

13, 13   : points in x and y direction

## set array focal point with:

    delay_mask1, amplitude_mask1 = arr1.beam_stear((px,py))

leave args empty for no steering

### final note:

    source.p = build_source_signals(delay_mask1 + delay_mask2 +1,amplitude_mask1+amplitude_mask2, base_signal, kgrid.Nt)

we add +1 to the masks to account for using -1 as no element. include an +(# of arrays - 1) to the sum of masks


# Results

![No Beam Steering](/images/Figure_3.png)
*Arrays without any beam steering*

Beam steering was done through calculating distance from each element to focal point and setting phase accordingly. a hanning window was applied to element amplitudes to reduce side lobes.

![Beam Steering](/images/Figure_4.png)
*Arrays any beam steering*

dB version

![Beam Steering](/images/Figure_5.png)
*Arrays any beam steering*

# Assumptions:
* Speed of sound in air of 343 m/s with density of 1.2 kg/m3 at 20C room temp.
* Air is ideal, IE: constant pressure, temp and speed in time and space, no turbulence, or noise.
* Element spacing: 8mm. Chosen as being ~wavelength, and minimum reasonable distanced based on off the shelf 40khz emitters found on digikey/mauser. λ/2 or ~4mm would be better if I found a cheap source of smaller emitters
* I chose 13x13 emitter grids. prime number N should help a little with side lobes. 
* No non-linear effects, I modeled solely superposition. while non-linear effects would cause wave distortion, but in the real world, these effects are dwarfed by boundary conditions, reflections, and air conditions. 
* Simulation is far field, but still close to the boundary. 


# Next steps

2 hours: Adjust simulation to larger area and see further far field simulations potentially with variable grid sizing. going beyond my 500mm^2 area was starting to take longer than I wanted without performance improvements

4-8 hours: Monty carlo simulations to see effects of less-ideal medium. This includes a temperature gradient and flow. 

