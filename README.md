Assumptions:
* Speed of sound in air of 343 m/s with density of 1.2 kg/m3 at 20C room temp.
* Air is ideal, IE: constant pressure, temp and speed in time and space, no turbulence, or noise.
* Element spacing: 8mm. Chosen as being ~wavelength, and minimum reasonable distanced based on off the shelf 40khz emitters found on digikey/mauser. λ/2 or ~4mm would be better if I found a cheap source of smaller emitters
* I chose 11x11 emitter grids. prime number N should help a little with side lobes. 
* No non-linear effects, I modeled solely superposition. while non-linear effects would cause wave distortion, but in the real world, these effects are dwarfed by boundary conditions, reflections, and air conditions. 
* Simulation is far field, but still close to the boundary. 


Next steps

2 hours: Adjust simulation to larger area and see further far field simulations potentially with variable grid sizing. going beyond my 500mm^2 area was starting to take longer than I wanted without performance improvements

4-8 hours: Monty carlo simulations to see effects of less-ideal medium. this includes a temperature gradient and flow. 

