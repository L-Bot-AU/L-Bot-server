from constants import CAMERA_SYSTEM_PORTS, WEBSITE_CLIENT_PORT, WEBSITE_PORT
import threading
import platform
import psutil
import signal
import os

# kill processes on ports, since 2 processes cannot run on the same port
def kill_port(port: int):
    # kill processes on ports, since 2 processes cannot run on the same port
    if platform.system() == "Linux":
        # TODO: define ports from constants
        os.system(f"kill $(lsof -ti tcp:{port})")

    elif platform.system() == "Windows":
        for proc in psutil.process_iter():
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == port:
                    try:
                        proc.send_signal(signal.SIGTERM)
                    except Exception:
                        pass
    else:
        raise Exception("cannot kill port on this platform")

if __name__ == "__main__":
    kill_port(CAMERA_SYSTEM_PORTS["jnr"])
    kill_port(CAMERA_SYSTEM_PORTS["snr"])
    kill_port(WEBSITE_CLIENT_PORT)
    kill_port(WEBSITE_PORT)
