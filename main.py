
import numpy as np
import matplotlib.pyplot as plt

from kwave.data import Vector
from kwave.kgrid import kWaveGrid
from kwave.kmedium import kWaveMedium
from kwave.ksensor import kSensor
from kwave.ksource import kSource
from kwave.kspaceFirstOrder import kspaceFirstOrder
from kwave.utils.filters import filter_time_series


FREQUENCY = 40e3 #hz
V_SOUND_IN_AIR = 343 #m/s


class TransducerArray():
    """
    Class containing Transducer arrays
    """
    def __init__(self, grid: kWaveGrid, center: set, spacing: set, Nx: int, Ny: int):
        """
        Class Constructor for TransducerArray. creates array of transducers
        args:
        - grid: kWaveGrid of simulation space
        - center: (X, Y) set where 2d array is centered on grid
        - spacing: (dx, dy) set of how spacing between each element in grid points
        - Nx: number of elements in X dir
        - Ny: number of elements in Y dir
        """
        self.grid = grid
        self.center = center
        self.spacing = spacing
        self.Nx = Nx
        self.Ny = Ny
        
        # Calculate transducer positions
        center_x, center_y = center
        spacing_x, spacing_y = spacing
        
        # Create grid of positions relative to center
        x_offsets = np.arange(Nx) - (Nx - 1) / 2
        y_offsets = np.arange(Ny) - (Ny - 1) / 2
        
        # Scale by spacing and add center offset
        self.positions_x = center_x + x_offsets * spacing_x
        self.positions_y = center_y + y_offsets * spacing_y
        
        # Create mesh grid of all transducer positions
        self.mesh_x, self.mesh_y = np.meshgrid(self.positions_x, self.positions_y, indexing='ij')
        
        # Flatten for easier iteration
        self.positions = np.column_stack((self.mesh_x.flatten(), self.mesh_y.flatten())).astype(int)

        # Create mask grid for kSource
        self.mask = np.zeros((grid.N), dtype=float)

        # builds masks
        for pos in self.positions:
            x, y = pos
            if 0 <= x < grid.Nx and 0 <= y < grid.Ny:
                self.mask[grid.Ny - y, x] = 1



    def beam_stear(self, point: set = None):
        """
        function for focusing the beam on a given point on the grid. leave point blank for no steering
        args: 
        point: (X, Y) point on grid to focus on
        output:
        phase and amplidude masks of beam array
        """

        # builds delay and amplidute masks
        delay_mask = np.ones((self.grid.N), dtype=float)*-1
        amplitude_mask = np.zeros((self.grid.N), dtype=float)


        # gets default beam
        if not point:
            for pos in self.positions:
                x, y = pos
                delay_mask[self.grid.Ny-y, x] = 0
                amplitude_mask[self.grid.Ny-y, x] = 1

            return delay_mask, amplitude_mask


        # gets coords from point
        px, py = point

        # finds distance from each array element to focus point 
        distances = np.sqrt(
            (self.positions[:, 0] - px)**2 * self.grid.dx**2 +
            (self.positions[:, 1]  - py)**2 * self.grid.dy**2
        )

        # divides distance array by speed of sound in air to get times
        tof = distances / V_SOUND_IN_AIR

        # finds longest time and bases times around it
        delay_times = np.max(tof) - tof  

        # samples time for delay to be "on the grid"
        delays = np.round(delay_times / self.grid.dt).astype(int)

        # uses hanning window to reduce side lobes
        window = np.ravel(np.outer(np.hanning(self.Nx), np.hanning(self.Ny)))

        for pos, delay, win in zip(self.positions, delays, window):
            x, y = pos
            delay_mask[self.grid.Ny-y, x] = delay
            amplitude_mask[self.grid.Ny-y, x] = win


        return delay_mask, amplitude_mask



def build_source_signals(delay_mask, amplitude_mask, base_signal, Nt):
    """
    args

    delay_mask  : (N, N) array — integer delay in samples per element, -1 = inactive
    base_signal : (Nt,) array — the undelayed waveform
    Nt          : int — total number of time steps

    Returns
    -------
    active_signals : (num_active, Nt) array — one row per active element, 
                     in the same flattened (row-major) order as delay_mask
    """
    base = base_signal.flatten()
    signals = []

    for d, a in zip(delay_mask.flatten(), amplitude_mask.flatten()):
        
        if d == -1:
            continue  # inactive element, skip
        
        d = int(d)

        if d == 0:
            delayed = base[:Nt]
        else:
            delayed = np.concatenate([np.zeros(d), base[:-d]])

        #print(d)
        signals.append(a*delayed[:Nt])  # guard against length drift

        
    return np.vstack(signals)  # shape: (num_active, Nt)



if __name__ == "__main__":
    # sets # of grid points in each direction
    Nx, Ny = 512, 512
    
    # sets grid spacing in each direction
    # a 40khz in air has a wavelength of ~8.5mm. 
    # 1mm should be plenty of fidelity
    dx, dy = 1e-3, 1e-3

    # defines grid
    kgrid = kWaveGrid(Vector([Nx, Ny]), Vector([dx, dy]))

    # define the properties of the propagation medium (air)
    medium = kWaveMedium(
        sound_speed=V_SOUND_IN_AIR,  # [m/s]
        density=1.2 #kg/m^3
    )

    # create the time array
    kgrid.makeTime(medium.sound_speed)

    # defines arrays
    arr1 = TransducerArray(kgrid, (100,100), (4,4), 13, 13)
    arr2 = TransducerArray(kgrid, (100,400), (4,4), 13, 13)

    # defines point
    px, py = 500, 200

    # gets beam focus information
    delay_mask1, amplitude_mask1 = arr1.beam_stear()
    delay_mask2, amplitude_mask2 = arr2.beam_stear()

    # defines source and adds arrays to source
    source = kSource()
    p_mask = np.zeros((Nx, Ny), dtype=float)

    source.p_mask = p_mask+ arr1.mask + arr2.mask

    source_mag = 2  # [Pa]
    base_signal = source_mag * np.sin(2 * np.pi * FREQUENCY * kgrid.t_array)

    # builds source signals
    source.p = build_source_signals(delay_mask1 + delay_mask2 +1,amplitude_mask1+amplitude_mask2, base_signal, kgrid.Nt)



    # adds ksensor
    sensor_mask = np.zeros((Nx, Ny), dtype=float)
    sensor_mask[px, py] = 1
    sensor = kSensor(mask=sensor_mask, record=["p", "p_final"])

    # runs sim
    result = kspaceFirstOrder(
        kgrid,
        medium,
        source,
        sensor,
        device='gpu',
        quiet=False,
        pml_inside=True,
    )
    p_final = np.asarray(result["p_final"])

    # plot and show Figure 1: final wave-field 
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    extent = [
        kgrid.x_vec[0] * 1e3,
        kgrid.x_vec[-1] * 1e3,
        kgrid.y_vec[0] * 1e3,
        kgrid.y_vec[-1] * 1e3,
    ]
    print(extent)
    ax1.imshow(p_final, extent=extent, vmin=-1, vmax=1, cmap="RdBu_r")
    # mark the beam steering target point
    target_x_mm, target_y_mm = kgrid.x_vec[px] * 1e3, kgrid.y_vec[py] * 1e3
    ax1.scatter(target_x_mm, target_y_mm, c='yellow', s=80, edgecolor='black', marker='o', label='Focal Point')
    ax1.legend(loc='upper right')
    ax1.set_xlabel("x-position [mm]")
    ax1.set_ylabel("y-position [mm]")
    ax1.set_title("2D Pressure Plot")
    ax1.set_aspect("equal")
    plt.show()