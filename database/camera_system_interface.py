from constants import CAMERA_SYSTEM_INTERFACE_DEBUG, CAMERA_SYSTEM_PORTS, CAMERA_KEY
from sqlalchemy.orm import sessionmaker
from database import database
from Crypto.Cipher import AES
import kill_port
import datetime
import random
import socket

engine, Base, Data, Count, PastData = database.genDatabase()
aesenc = AES.new(CAMERA_KEY, AES.MODE_ECB)

def updateCount(lib, incr):
    # start session with database
    Session = sessionmaker(bind=engine)
    session = Session()
    
    if lib == "jnr":
        session.query(Count).first().jnrvalue += incr
        if CAMERA_SYSTEM_INTERFACE_DEBUG:
            with open(f"log{lib}.txt", "a") as f:
                f.write(f"{session.query(Count).first().jnrvalue} {datetime.datetime.now()}\n")
    
    elif lib == "snr":
        session.query(Count).first().snrvalue += incr
        if CAMERA_SYSTEM_INTERFACE_DEBUG:
            with open(f"log{lib}.txt", "a") as f:
                f.write(f"{session.query(Count).first().snrvalue} {datetime.datetime.now()}\n")
    
    else:
        raise Exception("what sorta library is this?!?!")
    
    session.commit()

def getMsg(lib, client):
    # receive the update to the number of people in the senior library (+x or -x)
    msg = client.recv(1024)
    incr = eval(msg + b"+0") # add a "+0" at the end in case the string has a trailing + or - (due to weird bug where requests get merged)
    print(__name__, "Recieved message:", incr)
    return incr

def handleConnection(lib, sock):
    # wait for connection
    client, address = sock.accept()

    # timeout the connection if the client takes to long to send a response
    sock.settimeout(6)

    print(__name__, lib, f"Connection from {address[0]}")
    
    try:
        print(__name__, lib, "Sending verification string")
        # TODO: replace this verification system with SSL
        # create random string of bytes for verification
        plaintext = bytes([random.randint(0, 0xff) for _ in range(16)])
        client.send(aesenc.encrypt(plaintext) + b"\n")
        msg = client.recv(16)
        
        # if verification is failed, raise an error and let the try/except statement catch it
        assert msg == CAMERA_KEY, "Verification failed"
        
        print(__name__, lib, "Verification succeeded")
        while True:
            # once verification has succeeded, no time limit is required
            sock.settimeout(None)
            
            incr = getMsg(lib, client)
            updateCount(lib, incr)
        
    except Exception as e:
        sock.settimeout(None)
        # print the error (due to verification taking too long, verification being unsuccessful, client closing the connection or some other unknown error
        print(__name__, lib, repr(e))
        
    client.close()

def __init__(lib):
    print(__name__, f"Starting {lib}_updater")
    kill_port.kill_port(CAMERA_SYSTEM_PORTS[lib])
    
    # create socket and listen
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", CAMERA_SYSTEM_PORTS[lib]))
    sock.listen(10)
    
    while True:
        handleConnection(lib, sock)

