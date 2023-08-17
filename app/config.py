class Config:
    DEBUG = True
    API_KEY = "AIzaSyCdgVOZfVHSb-OjcC2EfMkgbHztnY4pH_4"
    GEOCODE_API_URL = "https://maps.googleapis.com/maps/api/geocode/json?"
    DISTANCE_MATRIX_API_URL = (
        "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial"
    )
    BABEL_DEFAULT_TIMEZONE = "en"
    BABEL_TRANSLATION_DIRECTORIES = "app/translations"
    LANGUAGES = {
        "en": "English",
        "de": "German",
        "es": "Spanish",
        "fr": "French",
        "it": "Italian",
        "zh": "Chinese",
    }
