CAMERA_SYSTEM_INTERFACE_DEBUG = True
CAMERA_SYSTEM_PORTS = {
    "jnr": 9482,
    "snr": 11498
}
CAMERA_KEY = b"automate_egggggg"

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
TIMES = ["Morning", "Break 1", "Break 2"]
OPENING_TIMES = {
    "jnr": {
        "monday": (7, 30),
        "tuesday": (7, 30),
        "wednesday": (7, 30),
        "thursday": (7, 30),
        "friday": (7, 30)
    },
    "snr": {
        "monday": (8, 0),
        "tuesday": (8, 0),
        "wednesday": (8, 0),
        "thursday": (8, 0),
        "friday": (8, 0)
    }
}
CLOSING_TIMES = {
    "jnr": {
        "monday": (15, 30),
        "tuesday": (15, 30),
        "wednesday": (15, 30),
        "thursday": (15, 30),
        "friday": (15, 30)
    },
    "snr": {
        "monday": (14, 30),
        "tuesday": (14, 30),
        "wednesday": (12, 30),
        "thursday": (15, 15),
        "friday": (14, 30)
    }
}

MAX_CAPS  = {
    "jnr": 108,
    "snr": 84
}

LIBRARIANS = {
    "jnr": ["Ms Crothers"],
    "snr": ["Ms Meredith", "Mr Wiramihardja"]
}

WEBSITE_CLIENT_PORT = 2910
WEBSITE_UPDATE_TIMEOUT = 10.0 # time between each dynamic data update (in seconds)
DATABASE_TASKS_TIMEOUT = 60

WEBSITE_HOST = "0.0.0.0"
WEBSITE_PORT = 80
WEBSITE_DEBUG = True


DO_RESTARTDB = False
