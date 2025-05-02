import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons # === 1 ===

# === 2 ===
# === Функція генерації сигналу === 
def generate_signal():
    return current_params["amp"] * np.sin(2 * np.pi * current_params["freq"] * x + current_params["phase"])

# === 4 ===
# === Початкові параметри ===
x = np.linspace(0, 10, 1000)
init_params = {
    "amp": 1.0,
    "freq": 1.0,
    "phase": 0.0,
    "noise_mean": 0.0,
    "noise_cov": 0.2,
}
current_params = init_params.copy()
show_noise = [False]
saved_noise = np.random.normal(init_params["noise_mean"], init_params["noise_cov"], len(x))

# === 6 ===
# === Оновлення графіка ===
def update(val=None):
    clean = generate_signal()
    line_clean.set_ydata(clean)
    line_noisy.set_ydata(clean + saved_noise)
    show_noise = check.get_status()[0]
    line_noisy.set_visible(show_noise)

    fig.canvas.draw_idle()

# === Оновлення параметрів ===
def update_param(name, val):
    current_params[name] = val
    update()

def update_noise_param(name, val):
    current_params[name] = val
    global saved_noise
    saved_noise = np.random.normal(current_params["noise_mean"], current_params["noise_cov"], len(x))
    update()

# === 3 ===
# === Побудова графіка ===
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.45)
ax.set_ylim(-2, 2)
line_noisy, = ax.plot(x, generate_signal() + saved_noise, 'orange')
line_clean, = ax.plot(x, generate_signal(), 'b--')
ax.legend(["noisy", "signal"], loc='upper right')
line_noisy.set_visible(False)

# === Слайдери ===
def create_slider(y, label, vmin, vmax, valinit, callback):
    ax_slider = plt.axes([0.25, y, 0.65, 0.03])
    slider = Slider(ax_slider, label, vmin, vmax, valinit=valinit)
    slider.on_changed(callback)
    return slider

sliders = {
    "amp": create_slider(0.35, "Amplitude", 0.0, 2.0, init_params["amp"], lambda v: update_param("amp", v)),
    "freq": create_slider(0.30, "Frequency", 0.1, 5.0, init_params["freq"], lambda v: update_param("freq", v)),
    "phase": create_slider(0.25, "Phase", 0.0, 2 * np.pi, init_params["phase"], lambda v: update_param("phase", v)),
    "noise_mean": create_slider(0.20, "Noise Mean", -1.0, 1.0, init_params["noise_mean"], lambda v: update_noise_param("noise_mean", v)),
    "noise_cov": create_slider(0.15, "Noise Cov", 0.0, 1.0, init_params["noise_cov"], lambda v: update_noise_param("noise_cov", v))
}

# === 5 ===
# === Чекбокс ===
ax_check = plt.axes([0.8, 0.05, 0.1, 0.04])
check = CheckButtons(ax_check, ['Show Noise'], [False])
def toggle_noise(label):
    show_noise[0] = not show_noise[0]
    update()
check.on_clicked(toggle_noise)

# === 7 ===
# === Кнопка Reset ===
reset_ax = plt.axes([0.4, 0.05, 0.1, 0.04])
button = Button(reset_ax, 'Reset')
def reset(event):
    for name, slider in sliders.items():
        slider.reset()
    global saved_noise
    saved_noise = np.random.normal(init_params["noise_mean"], init_params["noise_cov"], len(x))
    if check.get_status()[0]:  
        check.set_active(0)
    update()
button.on_clicked(reset)

plt.show()
