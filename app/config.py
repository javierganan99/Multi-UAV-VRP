import os


class Config:
    APP_HOST = "0.0.0.0"
    APP_PORT = 5000
    DEBUG = True
    API_KEY = os.getenv("MAPS_API_KEY")
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
