import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons

# --- Початкові параметри ---
time = np.linspace(0, 10, 1000)
params = {
    "amp": 1.0,
    "freq": 1.0,
    "phase": 0.0,
    "noise_mean": 0.0,
    "noise_cov": 0.2,
}
noise = np.random.normal(params["noise_mean"], params["noise_cov"], len(time))
show_noise = [False]

# --- Генерація сигналів ---
def generate_clean():
    return params["amp"] * np.sin(2 * np.pi * params["freq"] * time + params["phase"])

def generate_noisy():
    return generate_clean() + noise

# --- Оновлення графіка ---
def update(val=None):
    line_clean.set_ydata(generate_clean())
    line_noisy.set_ydata(generate_noisy())
    line_noisy.set_visible(show_noise[0])
    fig.canvas.draw_idle()

# --- Оновлення параметрів ---
def update_param(name, val):
    params[name] = val
    update()

def update_noise(name, val):
    params[name] = val
    global noise
    noise = np.random.normal(params["noise_mean"], params["noise_cov"], len(time))
    update()

# --- Побудова графіка ---
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.45)
ax.set_ylim(-2, 2)
line_clean, = ax.plot(time, generate_clean(), 'b--', label='Signal')
line_noisy, = ax.plot(time, generate_noisy(), 'orange', label='Noisy')
ax.legend()
line_noisy.set_visible(False)

# --- Слайдери ---
def create_slider(y, label, minv, maxv, val, callback):
    ax_slider = plt.axes([0.25, y, 0.65, 0.03])
    slider = Slider(ax_slider, label, minv, maxv, valinit=val)
    slider.on_changed(callback)
    return slider

sliders = {
    "amp": create_slider(0.35, "Amplitude", 0.0, 2.0, params["amp"], lambda v: update_param("amp", v)),
    "freq": create_slider(0.30, "Frequency", 0.1, 5.0, params["freq"], lambda v: update_param("freq", v)),
    "phase": create_slider(0.25, "Phase", 0.0, 2 * np.pi, params["phase"], lambda v: update_param("phase", v)),
    "noise_mean": create_slider(0.20, "Noise Mean", -1.0, 1.0, params["noise_mean"], lambda v: update_noise("noise_mean", v)),
    "noise_cov": create_slider(0.15, "Noise Cov", 0.0, 1.0, params["noise_cov"], lambda v: update_noise("noise_cov", v)),
}

# --- Чекбокс ---
ax_check = plt.axes([0.8, 0.05, 0.1, 0.04])
check = CheckButtons(ax_check, ['Show Noise'], [False])
check.on_clicked(lambda label: toggle_noise())

def toggle_noise():
    show_noise[0] = not show_noise[0]
    update()

# --- Reset ---
reset_ax = plt.axes([0.4, 0.05, 0.1, 0.04])
button = Button(reset_ax, 'Reset')
def reset(event):
    for name, slider in sliders.items():
        slider.reset()
    global noise
    noise = np.random.normal(params["noise_mean"], params["noise_cov"], len(time))
    if check.get_status()[0]:
        check.set_active(0)
    show_noise[0] = False
    update()
button.on_clicked(reset)

plt.show()
