import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import Slider, Button, ColumnDataSource, Select, Spacer

# === Генерація шуму та сигналу ===
def generate_noise(mean, cov, t):
    return np.random.normal(mean, np.sqrt(cov), len(t))

def harmonic(amplitude, frequency, phase, t):
    return amplitude * np.sin(2 * np.pi * frequency * t + phase)

def harmonic_with_noise(amplitude, frequency, phase, noise, t):
    return harmonic(amplitude, frequency, phase, t) + noise

# === Ковзне середнє — власний фільтр ===
def moving_average(signal, window_size):
    filtered = np.zeros_like(signal)
    for i in range(len(signal)):
        start = max(0, i - window_size // 2)
        end = min(len(signal), i + window_size // 2 + 1)
        filtered[i] = np.mean(signal[start:end])
    return filtered

# === Початкові параметри ===
init_amplitude = 1.0
init_frequency = 1.0
init_phase = 0.0
init_noise_mean = 0.0
init_noise_cov = 0.2
init_window = 11

t = np.linspace(0, 10, 1000)
noise = generate_noise(init_noise_mean, init_noise_cov, t)
y_clean = harmonic(init_amplitude, init_frequency, init_phase, t)
y_noisy = harmonic_with_noise(init_amplitude, init_frequency, init_phase, noise, t)
y_filtered = moving_average(y_noisy, init_window)

source = ColumnDataSource(data=dict(x=t, y_clean=y_clean, y_noisy=y_noisy, y_filtered=y_filtered))

# === Функції оновлення ===
def update_signal(attr, old, new):
    y_clean = harmonic(amp_slider.value, freq_slider.value, phase_slider.value, t)
    y_noisy = harmonic_with_noise(amp_slider.value, freq_slider.value, phase_slider.value, noise, t)
    y_filtered = moving_average(y_noisy, window_slider.value)
    source.data = dict(x=t, y_clean=y_clean, y_noisy=y_noisy, y_filtered=y_filtered)
    update_visibility(None, None, None)

def update_noise(attr, old, new):
    global noise
    noise = generate_noise(nmean_slider.value, ncov_slider.value, t)
    update_signal(attr, old, new)

def update_visibility(attr, old, new):
    mode = visibility_select.value
    if mode == "Тільки шум":
        line_noise.visible = True
        line_filtered.visible = False
        line_noise2.visible = True
        line_filtered2.visible = False
    elif mode == "Тільки фільтр":
        line_noise.visible = False
        line_filtered.visible = True
        line_noise2.visible = False
        line_filtered2.visible = True
    elif mode == "Шум і фільтр":
        line_noise.visible = True
        line_filtered.visible = True
        line_noise2.visible = True
        line_filtered2.visible = True
    else:  # Сховати все
        line_noise.visible = False
        line_filtered.visible = False
        line_noise2.visible = False
        line_filtered2.visible = False

def reset():
    amp_slider.value = init_amplitude
    freq_slider.value = init_frequency
    phase_slider.value = init_phase
    nmean_slider.value = init_noise_mean
    ncov_slider.value = init_noise_cov
    window_slider.value = init_window
    visibility_select.value = "Сховати все"

# === Віджети ===
amp_slider = Slider(title="Амплітуда", value=init_amplitude, start=0.0, end=2.0, step=0.1)
freq_slider = Slider(title="Частота", value=init_frequency, start=0.1, end=5.0, step=0.1)
phase_slider = Slider(title="Фаза", value=init_phase, start=0.0, end=2*np.pi, step=0.1)
nmean_slider = Slider(title="Середнє шуму", value=init_noise_mean, start=-1.0, end=1.0, step=0.1)
ncov_slider = Slider(title="Дисперсія шуму", value=init_noise_cov, start=0.0, end=1.0, step=0.05)
window_slider = Slider(title="Розмір вікна фільтра", value=init_window, start=3, end=21, step=2)
visibility_select = Select(value="Сховати все", options=["Сховати все", "Тільки шум", "Тільки фільтр", "Шум і фільтр"])
reset_button = Button(label="Скинути", button_type="success")

# === Події ===
for s in [amp_slider, freq_slider, phase_slider, window_slider]:
    s.on_change('value', update_signal)

for s in [nmean_slider, ncov_slider]:
    s.on_change('value', update_noise)

visibility_select.on_change('value', update_visibility)
reset_button.on_click(reset)

# === Побудова графіків ===
plot1 = figure(height=350, width=800, title="Сигнал з шумом та фільтром", x_axis_label="Час", y_axis_label="Амплітуда")
line_clean = plot1.line('x', 'y_clean', source=source, color="blue", legend_label="Чистий")
line_noise = plot1.line('x', 'y_noisy', source=source, color="orange", legend_label="Шум")
line_filtered = plot1.line('x', 'y_filtered', source=source, color="green", legend_label="Фільтр")
plot1.legend.location = "top_left"
line_noise.visible = False
line_filtered.visible = False

plot2 = figure(height=350, width=800, title="Лише шум і фільтр", x_axis_label="Час", y_axis_label="Амплітуда")
line_noise2 = plot2.line('x', 'y_noisy', source=source, color="orange", legend_label="Шум")
line_filtered2 = plot2.line('x', 'y_filtered', source=source, color="green", legend_label="Фільтрований")
plot2.legend.location = "top_left"
line_noise2.visible = False
line_filtered2.visible = False

# === Розміщення ===
controls = column(
    amp_slider,
    freq_slider,
    phase_slider,
    nmean_slider,
    ncov_slider,
    window_slider,
    visibility_select,
    reset_button
)
plots = column(plot1, plot2)

# Пробіл між колонками (ширина в пікселях)
spacer = Spacer(width=50)
# Об'єднання з відступом
layout = row(plots, spacer, controls)

curdoc().add_root(layout)
curdoc().title = "Гармоніка з шумом і фільтром"