import streamlit as st
import serial
from serial.tools import list_ports
import numpy as np

def initialize_grid(size):
    return np.random.choice(np.array([-1, 1],dtype=np.int8), size=(size, size))

def update_grid(grid, temperature):
    i,j = np.random.randint(grid.shape)
    #new_grid = grid.copy()
    hc = -grid[i,j] * (grid[(i - 1) % grid.shape[0], j] +
                       grid[(i + 1) % grid.shape[0], j] +
                       grid[i, (j - 1) % grid.shape[1]] +
                       grid[i, (j + 1) % grid.shape[1]])
    de = -2 * hc
    if de < 0 or np.random.random() < np.exp(- de / temperature):
        grid[i,j] *= -1
    return grid

st.title('Ising Model Simulation')

with st.sidebar:
    st.write('Simulation parameters')
    port_name = st.selectbox("Select PORT", [port.device for port in list_ports.comports()])
    temperature = st.slider('Temperature', 1, 100, 10)

start_button = st.button('Start Simulation')
chart = st.empty()

if start_button:
    grid_state = initialize_grid(100)
    ser = serial.Serial(port_name, 115200)
    first_contact = False
    step = 0
    while True:
        if not first_contact:
            print("Wait for start signal")
            start_signal = ser.read(1)
            print(start_signal)
            if start_signal == b'A':
                first_contact = True
        else:
            grid_state = update_grid(grid_state, temperature)
            step += 1
            if step % 150 == 0:
                print("Step: ", step)
                # Serialize the grid state and send it over serial
                ser.write(b'S')  # Send synchronization signal
                ser.write(grid_state.tobytes())
                # Wait for synchronization signal from MatrixPortal
                while ser.read(1) != b'S':
                    continue
