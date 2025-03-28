import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Завантаження даних
def load_data(file_path):
    # Перевірка наявності файлу
    if not os.path.exists(file_path):
        st.error(
            "Файл не знайдено! Перевірте, будь ласка, наступне:\n"
            "1. Ви запускаєте скрипт з кореневої директорії репозиторію\n"
            "2. Ви виконали всі комірки в lab2.ipynb"

        )
        return None
    else:
        data = pd.read_csv(file_path)
        return data

def reset_filters():
    # Дефолтні значення
    st.session_state["selected_option"] = 'VCI'
    st.session_state["selected_PROVINCE_ID"] = PROVINCE_IDs[0]
    st.session_state["year_range"] = (int(data["Year"].min()), int(data["Year"].max()))
    st.session_state["week_range"] = (int(data["Week"].min()), int(data["Week"].max()))
    st.session_state["sort_asc"] = False
    st.session_state["sort_desc"] = False

file_path = os.path.join('lab2', 'Updated_Provinces.csv')
data = load_data(file_path)

# float to int для уникнення помилок
data["Week"] = data["Week"].astype(int) 
data["Year"] = data["Year"].astype(int)

# словник для заміни індексів(номерів) на відповідні імена регіонів
PROVINCE_ID_names = {
    1: "Вінницька",
    2: "Волинська",
    3: "Дніпропетровська",
    4: "Донецька",
    5: "Житомирська",
    6: "Закарпатська",
    7: "Запорізька",
    8: "Івано-Франківська",
    9: "Київ",
    10: "Київcька",
    11: "Кіровоградська",
    12: "Луганська",
    13: "Львівська",
    14: "Миколаївська",
    15: "Одеська",
    16: "Полтавська",
    17: "Рівненська",
    18: "Севастополь",
    19: "Сумська",
    20: "Тернопільська",
    21: "Харківська",
    22: "Херсонська",
    23: "Хмельницька",
    24: "Черкаська",
    25: "Чернівецька",
    26: "Чернігівська",
    27: "Республіка Крим"
}

if data is not None:
    # Колонки
    col1, col2 = st.columns([2,3])

    # Колонка 1
    with col1:
        PROVINCE_IDs = list(PROVINCE_ID_names.values()) # список з регіонами
        # Ініціалізація session_state (призначення значень за замовчуванням, при ініціалізації session_state)
        st.session_state.setdefault("selected_option", 'VCI')
        st.session_state.setdefault("selected_PROVINCE_ID", PROVINCE_IDs[0])
        st.session_state.setdefault("year_range", (int(data["Year"].min()), int(data["Year"].max())))
        st.session_state.setdefault("week_range", (int(data["Week"].min()), int(data["Week"].max())))
        st.session_state.setdefault("sort_asc", False)
        st.session_state.setdefault("sort_desc", False)

        # 1. Dropdown для вибору часових рядів
        options = ['VCI', 'TCI', 'VHI']
        # key - ідентифікатор віджета (selectbox) у session_state
        # Він використовується для збереження стану віджета. Автоматично зберігається в session_state
        selected_option = st.selectbox('Виберіть часовий ряд:', options, key="selected_option")

        # 2. Dropdown для вибору області
        if st.session_state["selected_PROVINCE_ID"] not in PROVINCE_IDs:
            st.session_state["selected_PROVINCE_ID"] = PROVINCE_IDs[0]

        index = PROVINCE_IDs.index(st.session_state["selected_PROVINCE_ID"])

        selected_PROVINCE_ID = st.selectbox('Виберіть регіон України:', PROVINCE_IDs, index=index, key="selected_PROVINCE_ID")

        # 3. Slider для вибору інтервалу тижнів
        min_week = data['Week'].min()
        max_week = data['Week'].max()
        
        week_range = st.slider('Виберіть проміжок тижнів:', min_week, max_week, (min_week, max_week), key="week_range")

        # 4. Slider для вибору інтервалу років
        min_year = data['Year'].min()
        max_year = data['Year'].max()

        year_range = st.slider('Виберіть проміжок років:', min_year, max_year, (min_year, max_year), key="year_range")

        # Фільтрація даних за обраними параметрами
        # знаходить для регіону відповідний номер, наприклад 1 для 'Вінницька'
        PROVINCE_ID_index = next((key for key, value in PROVINCE_ID_names.items() if value == st.session_state["selected_PROVINCE_ID"]), None)
        filtered_data = data[
            (data['Year'] >= year_range[0]) &
            (data['Year'] <= year_range[1]) &
            (data['Week'] >= week_range[0]) &
            (data['Week'] <= week_range[1]) &
            (data['PROVINCE_ID'] == PROVINCE_ID_index)
        ]

        # 8. Два checkbox для сортування даних
        sort_asc = st.checkbox('Сортування за зростанням', key="sort_asc")
        sort_desc = st.checkbox('Сортування за спаданням', key="sort_desc")

        if sort_asc and sort_desc:
            st.warning("Обидва чек-бокси вибрано! Виберіть, будь ласка, один із них")
            sort_desc = False
        elif sort_asc:
            filtered_data = filtered_data.sort_values(by=st.session_state["selected_option"], ascending=True)
        elif sort_desc:
            filtered_data = filtered_data.sort_values(by=st.session_state["selected_option"], ascending=False)

        # 5. Button для скидання фільтрів
        st.button('Reset Filters', on_click=reset_filters)

    # Колонка 2
    with col2:
        # Tabs для таблиці та графіка з відфільтрованими даними, графіка порівнянь даних по областях
        tab1, tab2, tab3 = st.tabs(["Таблиця з відсортованими даними", "Графік часових рядів", "Порівняння регіонів України"])

        #  Таблиця з відфільтрованими даними
        with tab1:
            st.write(filtered_data)

        # Графік з відфільтрованими даними
        with tab2:
            # Ковзне середнє для згладжування
            window_size = 50  # вікно згладжування
            filtered_data["Smoothed"] = filtered_data[selected_option].rolling(window=window_size).mean()

            plt.figure(figsize=(8, 5)) 

            # Побудова лінійного графіку
            sns.lineplot(data=filtered_data, x="Year", y="Smoothed")

            plt.title(f"Часовиц ряд {selected_option} для регіону {selected_PROVINCE_ID} ")
            plt.xlabel("Year")
            plt.ylabel(selected_option)

            plt.grid(True)

            # Налаштування осі X
            years = sorted(filtered_data["Year"].dropna().unique())
            step = 1
            selected_years = years[::step] 
            plt.xticks(selected_years, rotation=90)

            plt.tight_layout()
            st.pyplot(plt)


        # Графік порівняння даних по областях
        with tab3:
            comparison_data = data[
                (data['Year'] >= year_range[0]) & (data['Year'] <= year_range[1]) &
                (data['Week'] >= week_range[0]) & (data['Week'] <= week_range[1])
            ]
            
            # Групування даних по PROVINCE_ID
            comparison_data_grouped = comparison_data.groupby('PROVINCE_ID')[selected_option].mean()
            comparison_data_grouped = comparison_data_grouped.sort_values(ascending=True)

            # Заміна індексів на назви регіонів
            comparison_data_grouped.index = comparison_data_grouped.index.map(PROVINCE_ID_names)

            # Побудова графіка через matplotlib
            plt.figure(figsize=(8, 7))
            plt.bar(comparison_data_grouped.index, comparison_data_grouped.values)
            plt.xticks(rotation=90)
            plt.xlabel('Регіон')
            plt.ylabel(f'Середнє {selected_option}')
            plt.title(f'Середнє {selected_option} по регіонам')
            plt.tight_layout()

            # Виведення графіка на сторінці Streamlit
            st.pyplot(plt)
