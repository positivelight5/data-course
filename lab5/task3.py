import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import Slider, Button, ColumnDataSource, Select, Spacer

# === Початкові параметри ===
params = {
    "amp": 1.0,
    "freq": 1.0,
    "phase": 0.0,
    "noise_mean": 0.0,
    "noise_cov": 0.2,
    "window": 11
}

# === Дані ===
time = np.linspace(0, 10, 1000)

# === Генерація шуму та сигналу ===
def generate_noise():
    return np.random.normal(params["noise_mean"], np.sqrt(params["noise_cov"]), len(time))

def generate_clean():
    return params["amp"] * np.sin(2 * np.pi * params["freq"] * time + params["phase"])

def generate_clean_with_noise(noise):
    return generate_clean() + noise

def moving_average(data, window_size):
    result = np.zeros_like(data, dtype=float)
    half = window_size // 2
    for i in range(len(data) - window_size + 1):
        window = data[i:i + window_size]
        avg = sum(window) / window_size
        result[i + half] = avg  # результат записується в центр вікна
    return result

noise = generate_noise()
y_clean = generate_clean()
y_noisy = generate_clean_with_noise(noise)
y_filtered = moving_average(y_noisy, params["window"])

source = ColumnDataSource(data=dict(x=time, y_clean=y_clean, y_noisy=y_noisy, y_filtered=y_filtered))

# === Оновлення ===
def update_signal(attr, old, new):
    y_clean = generate_clean()
    y_noisy = generate_clean_with_noise(noise)
    y_filtered = moving_average(y_noisy, int(params["window"]))
    source.data = dict(x=time, y_clean=y_clean, y_noisy=y_noisy, y_filtered=y_filtered)
    update_visibility(None, None, None)

def update_noise(attr, old, new):
    global noise
    noise = generate_noise()
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
    else:
        line_noise.visible = False
        line_filtered.visible = False
        line_noise2.visible = False
        line_filtered2.visible = False

    # === Обробник зміни параметра ===
def on_param_change(param_name, update_fn):
    def callback(attr, old, new):
        params[param_name] = new
        update_fn(attr, old, new)
    return callback

def reset():
    # Встановлення значень прямо всередині функції
    params["amp"] = 1.0
    params["freq"] = 1.0
    params["phase"] = 0.0
    params["noise_mean"] = 0.0
    params["noise_cov"] = 0.2
    params["window"] = 11

    # Скидання слайдерів до тих самих значень
    amp_slider.value = 1.0
    freq_slider.value = 1.0
    phase_slider.value = 0.0
    nmean_slider.value = 0.0
    ncov_slider.value = 0.2
    window_slider.value = 11

    # Скидання режиму візуалізації
    visibility_select.value = "Сховати все"

# === Слайдери ===
amp_slider = Slider(title="Амплітуда", value=params["amp"], start=0.0, end=2.0, step=0.1)
freq_slider = Slider(title="Частота", value=params["freq"], start=0.1, end=5.0, step=0.1)
phase_slider = Slider(title="Фаза", value=params["phase"], start=0.0, end=2*np.pi, step=0.1)
nmean_slider = Slider(title="Середнє шуму", value=params["noise_mean"], start=-1.0, end=1.0, step=0.1)
ncov_slider = Slider(title="Дисперсія шуму", value=params["noise_cov"], start=0.0, end=1.0, step=0.05)
window_slider = Slider(title="Розмір вікна фільтра", value=params["window"], start=3, end=21, step=2)

visibility_select = Select(value="Сховати все", options=["Сховати все", "Тільки шум", "Тільки фільтр", "Шум і фільтр"])
reset_button = Button(label="Скинути", button_type="success")
reset_button.on_click(reset)

# === Події ===
# === Події для слайдерів сигналу ===
signal_sliders = {
    amp_slider: "amp",
    freq_slider: "freq",
    phase_slider: "phase",
    window_slider: "window"
}

for slider, key in signal_sliders.items():
    slider.on_change('value', on_param_change(key, update_signal))

# === Події для слайдерів шуму ===
noise_sliders = {
    nmean_slider: "noise_mean",
    ncov_slider: "noise_cov"
}

for slider, key in noise_sliders.items():
    slider.on_change('value', on_param_change(key, update_noise))

# Додаємо подію для випадаючого списку
visibility_select.on_change("value", update_visibility)

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
spacer = Spacer(width=50)
layout = row(plots, spacer, controls)

curdoc().add_root(layout)
curdoc().title = "Гармоніка з шумом і фільтром"
