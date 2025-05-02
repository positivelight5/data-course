import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt

# === 1. Функція генерації сигналу ===
def generate_signal():
    return current_params["amp"] * np.sin(2 * np.pi * current_params["freq"] * x + current_params["phase"])

# === 2. Фільтр Butterworth ===
def apply_filter(signal, cutoff):
    b, a = butter(N=4, Wn=cutoff, btype='low', fs=fs)
    return filtfilt(b, a, signal)

# === 3. Початкові параметри ===
x = np.linspace(0, 10, 1000)
fs = len(x) / 10  # частота дискретизації (100 Гц)
init_params = {
    "amp": 1.0,
    "freq": 1.0,
    "phase": 0.0,
    "noise_mean": 0.0,
    "noise_cov": 0.2,
    "filter_cutoff": 2.0,
}
current_params = init_params.copy()
show_noise = [False]
show_filtered = [False]
saved_noise = np.random.normal(init_params["noise_mean"], init_params["noise_cov"], len(x))

# === 4. Оновлення графіка ===
def update(val=None):
    clean = generate_signal()
    noisy = clean + saved_noise
    filtered = apply_filter(noisy, current_params["filter_cutoff"])

    line_clean.set_ydata(clean)
    line_noisy.set_ydata(noisy)
    line_filtered.set_ydata(filtered)

    line_noisy.set_visible(check.get_status()[0])
    line_filtered.set_visible(check2.get_status()[0])

    fig.canvas.draw_idle()

def update_param(name, val):
    current_params[name] = val
    update()

def update_noise_param(name, val):
    current_params[name] = val
    global saved_noise
    saved_noise = np.random.normal(current_params["noise_mean"], current_params["noise_cov"], len(x))
    update()

# === 5. Побудова графіка ===
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.6)
ax.set_ylim(-2, 2)
line_clean, = ax.plot(x, generate_signal(), 'b--', label='Signal')
line_noisy, = ax.plot(x, generate_signal() + saved_noise, 'orange', label='Noisy')
line_filtered, = ax.plot(x, apply_filter(generate_signal() + saved_noise, init_params["filter_cutoff"]), 'g', label='Filtered')
ax.legend(loc='upper right')
line_noisy.set_visible(False)
line_filtered.set_visible(False)

# === 6. Слайдери ===
def create_slider(y, label, vmin, vmax, valinit, callback):
    ax_slider = plt.axes([0.25, y, 0.65, 0.03])
    slider = Slider(ax_slider, label, vmin, vmax, valinit=valinit)
    slider.on_changed(callback)
    return slider

sliders = {
    "amp": create_slider(0.48, "Amplitude", 0.0, 2.0, init_params["amp"], lambda v: update_param("amp", v)),
    "freq": create_slider(0.44, "Frequency", 0.1, 5.0, init_params["freq"], lambda v: update_param("freq", v)),
    "phase": create_slider(0.40, "Phase", 0.0, 2 * np.pi, init_params["phase"], lambda v: update_param("phase", v)),
    "noise_mean": create_slider(0.36, "Noise Mean", -1.0, 1.0, init_params["noise_mean"], lambda v: update_noise_param("noise_mean", v)),
    "noise_cov": create_slider(0.32, "Noise Cov", 0.0, 1.0, init_params["noise_cov"], lambda v: update_noise_param("noise_cov", v))
}
slider_filter = create_slider(0.28, "Filter Cutoff", 0.1, 10.0, init_params["filter_cutoff"], lambda v: update_param("filter_cutoff", v))

# === 7. Чекбокси ===
ax_check = plt.axes([0.8, 0.15, 0.1, 0.04])
check = CheckButtons(ax_check, ['Show Noise'], [False])
check2 = CheckButtons(plt.axes([0.8, 0.2, 0.1, 0.04]), ['Show Filtered'], [False])

def toggle_noise(label):
    show_noise[0] = not show_noise[0]
    update()
check.on_clicked(toggle_noise)

def toggle_filtered(label):
    show_filtered[0] = not show_filtered[0]
    update()
check2.on_clicked(toggle_filtered)

# === 8. Кнопка Reset ===
reset_ax = plt.axes([0.4, 0.15, 0.1, 0.04])
button = Button(reset_ax, 'Reset')
def reset(event):
    for name, slider in sliders.items():
        slider.reset()
    slider_filter.reset()
    global saved_noise
    saved_noise = np.random.normal(init_params["noise_mean"], init_params["noise_cov"], len(x))
    if check.get_status()[0]:
        check.set_active(0)
    if check2.get_status()[0]:
        check2.set_active(0)
    update()
button.on_clicked(reset)

plt.show()
