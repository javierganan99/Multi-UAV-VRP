import os


class Config:
    """
    Config class containing the configuration variables for the application.

    Attributes:
        APP_HOST (str): The host of the application. Default is "0.0.0.0".
        APP_PORT (int): The port of the application. Default is 5000.
        DEBUG (bool): The debug mode of the application. Default is True.
        API_KEY (str): The API key for the Google Maps API.
            Retrieved from the environment variable "MAPS_API_KEY".
        GEOCODE_API_URL (str): The URL for the geocode API of Google Maps.
        DISTANCE_MATRIX_API_URL (str): The URL for the distance matrix API of Google Maps.
        BABEL_DEFAULT_TIMEZONE (str): The default timezone for babel translations. Default is "en".
        BABEL_TRANSLATION_DIRECTORIES (str):
            The translation directories for babel translations. Default is "app/translations".
        LANGUAGES (dict): The supported languages for translations and their corresponding names.
    """

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
