import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt

# --- Початкові параметри ---
time = np.linspace(0, 10, 1000)
fs = len(time) / 10  # Частота дискретизацiї
params = {
    "amp": 1.0,
    "freq": 1.0,
    "phase": 0.0,
    "noise_mean": 0.0,
    "noise_cov": 0.2,
    "filter_cutoff": 2.0,
}
noise = np.random.normal(params["noise_mean"], params["noise_cov"], len(time))
show_noise = [False]
show_filtered = [False]

# --- Генерацiя сигналiв ---
def generate_clean():
    return params["amp"] * np.sin(2 * np.pi * params["freq"] * time + params["phase"])

def generate_noisy():
    return generate_clean() + noise

def apply_filter(signal):
    b, a = butter(N=4, Wn=params["filter_cutoff"], btype='low', fs=fs)
    return filtfilt(b, a, signal)

# --- Оновлення графiка ---
def update(val=None):
    clean = generate_clean()
    noisy = generate_noisy()
    filtered = apply_filter(noisy)
    
    line_clean.set_ydata(clean)
    line_noisy.set_ydata(noisy)
    line_filtered.set_ydata(filtered)

    line_noisy.set_visible(show_noise[0])
    line_filtered.set_visible(show_filtered[0])

    fig.canvas.draw_idle()

def update_param(name, val):
    params[name] = val
    update()

def update_noise(name, val):
    params[name] = val
    global noise
    noise = np.random.normal(params["noise_mean"], params["noise_cov"], len(time))
    update()

# --- Побудова графiка ---
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.6)
ax.set_ylim(-2, 2)
line_clean, = ax.plot(time, generate_clean(), 'b--', label='Signal')
line_noisy, = ax.plot(time, generate_noisy(), 'orange', label='Noisy')
line_filtered, = ax.plot(time, apply_filter(generate_noisy()), 'g', label='Filtered')
ax.legend(loc='upper right')
line_noisy.set_visible(False)
line_filtered.set_visible(False)

# --- Слайдери ---
def create_slider(y, label, minv, maxv, val, callback):
    ax_slider = plt.axes([0.25, y, 0.65, 0.03])
    slider = Slider(ax_slider, label, minv, maxv, valinit=val)
    slider.on_changed(callback)
    return slider

sliders = {
    "amp": create_slider(0.48, "Amplitude", 0.0, 2.0, params["amp"], lambda v: update_param("amp", v)),
    "freq": create_slider(0.44, "Frequency", 0.1, 5.0, params["freq"], lambda v: update_param("freq", v)),
    "phase": create_slider(0.40, "Phase", 0.0, 2 * np.pi, params["phase"], lambda v: update_param("phase", v)),
    "noise_mean": create_slider(0.36, "Noise Mean", -1.0, 1.0, params["noise_mean"], lambda v: update_noise("noise_mean", v)),
    "noise_cov": create_slider(0.32, "Noise Cov", 0.0, 1.0, params["noise_cov"], lambda v: update_noise("noise_cov", v)),
    "filter_cutoff": create_slider(0.28, "Filter Cutoff", 0.1, 10.0, params["filter_cutoff"], lambda v: update_param("filter_cutoff", v)),
}

# --- Чекбокси ---
check_ax1 = plt.axes([0.8, 0.15, 0.1, 0.04])
check = CheckButtons(check_ax1, ['Show Noise'], [False])
check_ax2 = plt.axes([0.8, 0.2, 0.1, 0.04])
check2 = CheckButtons(check_ax2, ['Show Filtered'], [False])

def toggle_noise(label):
    show_noise[0] = not show_noise[0]
    update()

check.on_clicked(toggle_noise)

def toggle_filtered(label):
    show_filtered[0] = not show_filtered[0]
    update()

check2.on_clicked(toggle_filtered)

# --- Reset ---
reset_ax = plt.axes([0.4, 0.15, 0.1, 0.04])
button = Button(reset_ax, 'Reset')
def reset(event):
    for name, slider in sliders.items():
        slider.reset()
    global noise
    noise = np.random.normal(params["noise_mean"], params["noise_cov"], len(time))
    if check.get_status()[0]:
        check.set_active(0)
    if check2.get_status()[0]:
        check2.set_active(0)
    show_noise[0] = False
    show_filtered[0] = False
    update()

button.on_clicked(reset)

plt.show()
