DEBUG = False # turn to false during production

import threading

# start website in a detached thread
from website import app
t = threading.Thread(target=app.app.run, kwargs={"host": "0.0.0.0", "port": 80, "debug": DEBUG})
if DEBUG:
    # cannot start in seperate thread
    # start website in main thread
    t.run()

else:
    # start website in seperate thread
    t.start()
    # start database in main thread
    from database import client_side_interface
