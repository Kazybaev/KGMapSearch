import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import pandas as pd
from folium.plugins import Fullscreen

st.set_page_config(page_title="Карта Кыргызстана", layout="wide")

st.title("🌍 Интерактивная карта Кыргызстана")

# Информация о регионах - ГЛАВНЫЙ СПРАВОЧНИК
REGION_INFO = {
    "Ысык-Кол": {"площадь": "43,100 км²", "центр": "Каракол", "население": "500,000 чел.",
                 "описание": "Область знаменита озером Ысык-Кол - вторым по величине высокогорным озером в мире"},
    "Чуй": {"площадь": "20,200 км²", "центр": "Бишкек", "население": "1,000,000 чел.",
            "описание": "Самый густонаселенный и экономически развитый регион Кыргызстана"},
    "Джалал-Абад": {"площадь": "33,700 км²", "центр": "Джалал-Абад", "население": "1,200,000 чел.",
                    "описание": "Крупнейший регион на юге Кыргызстана с богатой историей"},
    "Нарын": {"площадь": "45,200 км²", "центр": "Нарын", "население": "280,000 чел.",
              "описание": "Самая высокогорная область Кыргызстана"},
    "Ош": {"площадь": "29,200 км²", "центр": "Ош", "население": "1,300,000 чел.",
           "описание": "Древнейший регион с более чем 3000-летней историей"},
    "Талас": {"площадь": "11,400 км²", "центр": "Талас", "население": "260,000 чел.",
              "описание": "Родина великого кыргызского эпоса 'Манас'"},
    "Баткен": {"площадь": "17,000 км²", "центр": "Баткен", "население": "550,000 чел.",
               "описание": "Самая южная область Кыргызстана"},
    "Бишкек": {"площадь": "169 км²", "центр": "Бишкек", "население": "1,100,000 чел.",
               "описание": "Столица и крупнейший город Кыргызстана"},
}

# Районы по областям
DISTRICTS_BY_REGION = {
    "Ысык-Кол": ["Ак-Суу", "Джети-Огуз", "Ысык-Кол", "Тон", "Тюп"],
    "Ош": ["Алай", "Араван", "Кара-Суу", "Ноокат", "Узген", "Чон-Алай"],
    "Чуй": ["Аламудун", "Жайыл", "Кемин", "Москва", "Панфилов", "Сокулук", "Ысык-Ата"],
    "Джалал-Абад": ["Аксы", "Ала-Бука", "Базар-Коргон", "Ноокен", "Сузак", "Тогуз-Торо", "Токтогул", "Чаткал"],
    "Нарын": ["Ак-Талаа", "Ат-Башы", "Жумгал", "Кочкор", "Нарын"],
    "Талас": ["Бакай-Ата", "Кара-Буура", "Манас", "Талас"],
    "Баткен": ["Баткен", "Кадамжай", "Лейлек"],
}

# Перевод из английских названий в русские
NAME_MAPPING = {
    # Области Level 1
    "Ysyk-Köl": "Ысык-Кол",
    "Issyk-Kul": "Ысык-Кол",
    "Chüy": "Чуй",
    "Chuy": "Чуй",
    "Jalal-Abad": "Джалал-Абад",
    "Naryn": "Нарын",
    "Osh": "Ош",
    "Talas": "Талас",
    "Batken": "Баткен",
    "Bishkek": "Бишкек",

    # Районы Level 2
    "Ak-Suu": "Ак-Суу",
    "Ak-Suyskiy": "Ак-Суу",
    "Jeti-Ögüz": "Джети-Огуз",
    "Dzjeti-Oguz": "Джети-Огуз",
    "Ton": "Тон",
    "Tüp": "Тюп",
    "Tyup": "Тюп",
    "Alay": "Алай",
    "Alai": "Алай",
    "Aravan": "Араван",
    "Kara-Suu": "Кара-Суу",
    "Kara-Suy": "Кара-Суу",
    "Nookat": "Ноокат",
    "Nooken": "Ноокат",
    "Ùzgön": "Узген",
    "Uzgen": "Узген",
    "Chong-Alay": "Чон-Алай",
    "Alamüdùn": "Аламудун",
    "Alamüdün": "Аламудун",
    "Jaiyl": "Жайыл",
    "Jayyl": "Жайыл",
    "Kemin": "Кемин",
    "Moskva": "Москва",
    "Panfilov": "Панфилов",
    "Sokuluk": "Сокулук",
    "Ysyk-Ata": "Ысык-Ата",
}


def translate_name(name):
    """Переводит английское название в русское"""
    if pd.isna(name):
        return None
    # Проверяем прямое совпадение
    if name in NAME_MAPPING:
        return NAME_MAPPING[name]
    # Проверяем частичное совпадение
    for eng, rus in NAME_MAPPING.items():
        if eng.lower() in name.lower():
            return rus
    return name


@st.cache_data
def load_regions():
    """Загружает области (Level 1)"""
    try:
        gdf = gpd.read_file("gadm41_KGZ_shp/gadm41_KGZ_1.shp")
        gdf['NAME_RU'] = gdf['NAME_1'].apply(translate_name)
        return gdf
    except Exception as e:
        st.error(f"Ошибка загрузки областей: {e}")
        return None


@st.cache_data
def load_districts():
    """Загружает районы (Level 2)"""
    try:
        gdf = gpd.read_file("gadm41_KGZ_shp/gadm41_KGZ_2.shp")
        gdf['NAME_RU'] = gdf['NAME_2'].apply(translate_name)
        gdf['OBLAST_RU'] = gdf['NAME_1'].apply(translate_name)
        return gdf
    except Exception as e:
        st.error(f"Ошибка загрузки районов: {e}")
        return None


# Загрузка данных
gdf_regions = load_regions()
gdf_districts = load_districts()

if gdf_regions is not None and gdf_districts is not None:

    # Создаем списки для выбора
    regions_list = list(REGION_INFO.keys())

    # Интерфейс выбора
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        selected_region = st.selectbox(
            "📍 Выберите область:",
            options=["Не выбрано"] + regions_list,
            key="region_select"
        )

    with col2:
        # Показываем районы только если область выбрана
        if selected_region != "Не выбрано" and selected_region in DISTRICTS_BY_REGION:
            district_options = ["Вся область"] + DISTRICTS_BY_REGION[selected_region]
            selected_district = st.selectbox(
                "🏘️ Район:",
                options=district_options,
                key="district_select"
            )
        else:
            st.selectbox(
                "🏘️ Район:",
                options=["Сначала выберите область"],
                disabled=True,
                key="district_select_disabled"
            )
            selected_district = None

    with col3:
        st.write("")
        st.write("")
        search_clicked = st.button("🔍 Найти", type="primary", use_container_width=True)

    # ПОКАЗЫВАЕМ ИНФОРМАЦИЮ О РЕГИОНЕ
    if selected_region != "Не выбрано" and selected_region in REGION_INFO:
        info = REGION_INFO[selected_region]

        with st.expander(f"ℹ️ Информация: {selected_region}", expanded=True):
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric("📏 Площадь", info["площадь"])

            with col_b:
                st.metric("🏛️ Центр", info["центр"])

            with col_c:
                st.metric("👥 Население", info["население"])

            st.info(f"📖 {info['описание']}")

            # Список районов
            if selected_region in DISTRICTS_BY_REGION:
                st.markdown("**🗺️ Районы:**")
                districts_text = ", ".join(DISTRICTS_BY_REGION[selected_region])
                st.write(districts_text)

    # Поиск на карте
    selected_data = None
    search_level = None

    if search_clicked:
        if selected_district and selected_district != "Вся область":
            # Поиск района
            found = False
            for idx, row in gdf_districts.iterrows():
                if row['NAME_RU'] == selected_district:
                    selected_data = gdf_districts[gdf_districts['NAME_RU'] == selected_district]
                    search_level = 2
                    found = True
                    break

            if not found:
                st.warning(f"⚠️ Район '{selected_district}' не найден на карте")

        elif selected_region != "Не выбрано":
            # Поиск области
            found = False
            for idx, row in gdf_regions.iterrows():
                if row['NAME_RU'] == selected_region:
                    selected_data = gdf_regions[gdf_regions['NAME_RU'] == selected_region]
                    search_level = 1
                    found = True
                    break

            if not found:
                st.warning(f"⚠️ Область '{selected_region}' не найдена на карте")

    # Параметры карты
    if selected_data is not None and not selected_data.empty:
        bounds = selected_data.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        zoom = 9 if search_level == 1 else 11
    else:
        center_lat = 41.20
        center_lon = 74.77
        zoom = 7

    # Кнопки выбора типа карты
    st.markdown("---")
    map_col1, map_col2, map_col3 = st.columns([1, 1, 8])

    with map_col1:
        if st.button("🌍 Спутник", use_container_width=True):
            st.session_state['map_type'] = 'satellite'

    with map_col2:
        if st.button("🗺️ Обычная", use_container_width=True):
            st.session_state['map_type'] = 'normal'

    # Инициализация типа карты
    if 'map_type' not in st.session_state:
        st.session_state['map_type'] = 'satellite'

    # Создание карты
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles=None if st.session_state['map_type'] == 'satellite' else 'OpenStreetMap',
        control_scale=True
    )

    # Спутниковый слой
    if st.session_state['map_type'] == 'satellite':
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='ESRI',
            name='Satellite'
        ).add_to(m)

    # Границы областей
    folium.GeoJson(
        gdf_regions,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#FFD700' if st.session_state['map_type'] == 'satellite' else '#666666',
            'weight': 2,
            'fillOpacity': 0
        }
    ).add_to(m)

    # Границы районов
    folium.GeoJson(
        gdf_districts,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#FFD700' if st.session_state['map_type'] == 'satellite' else '#999999',
            'weight': 1,
            'fillOpacity': 0,
            'dashArray': '3, 3'
        }
    ).add_to(m)

    # Выделение выбранного региона
    if selected_data is not None and not selected_data.empty and search_clicked:
        folium.GeoJson(
            selected_data,
            style_function=lambda x: {
                'fillColor': '#FF0000',
                'color': '#FF0000',
                'weight': 4,
                'fillOpacity': 0.4
            }
        ).add_to(m)

    Fullscreen(position='topright').add_to(m)

    folium_static(m, width=1400, height=700)

else:
    st.error("❌ Не удалось загрузить данные. Проверьте наличие файлов gadm41_KGZ_1.shp и gadm41_KGZ_2.shp")
