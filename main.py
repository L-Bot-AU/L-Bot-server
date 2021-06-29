# NOTE: should be run from cmdline, not IDE
import threading
import platform
import psutil
import signal
import os

# kill processes on ports, since 2 processes cannot run on the same port
if platform.system() == "Linux":
    # TODO: define ports from constants
    os.system("kill $(lsof -ti tcp:80)")
    os.system("kill $(lsof -ti tcp:9482)")
    os.system("kill $(lsof -ti tcp:2910)")
    os.system("kill $(lsof -ti tcp:11498)")

elif platform.system() == "Windows":
    for proc in psutil.process_iter():
        for conns in proc.connections(kind='inet'):
            if conns.laddr.port in [80, 9482, 2910, 11498]:
                try:
                    proc.send_signal(signal.SIGTERM)
                except Exception:
                    pass
    
try:
    os.remove("library_usage.db")
except FileNotFoundError:
    pass

from database import database
engine, Base, Data, Count, PastData = database.genDatabase()


# start all database stuff in detached threads
from database import database_tasks, camera_system_interface, website_client_interface
threading.Thread(target=database_tasks.__init__, args=(engine, Base, Data, Count, PastData)).start()
threading.Thread(target=camera_system_interface.__init__, args=(engine, Base, Data, Count, PastData, "jnr")).start()
threading.Thread(target=camera_system_interface.__init__, args=(engine, Base, Data, Count, PastData, "snr")).start()
threading.Thread(target=website_client_interface.__init__, args=(engine, Base, Data, Count, PastData)).start()


# start website in main thread
from website import app
app.__init__()
