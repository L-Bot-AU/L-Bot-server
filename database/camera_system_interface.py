from constants import CAMERA_SYSTEM_INTERFACE_DEBUG, CAMERA_SYSTEM_PORTS, CAMERA_KEY
from sqlalchemy.orm import sessionmaker
from database import database
from Crypto.Cipher import AES
import kill_port
import datetime
import random
import socket
from loguru import logger

engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts = database.genDatabase()
aesenc = AES.new(CAMERA_KEY, AES.MODE_ECB)

def updateCount(lib, incr):
    """
    Updates the count of the database

    :param lib: The library whose occupancy should be updated
    :param incr: The amount to increment/decrement the occupancy by (positive for increase, negative for decrease)
    :return:
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    

    # check which library to update, update the occupancy and log the information (if debugging is set) 
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
        raise Exception("Invalid library")
    
    session.commit()

def getMsg(lib, client):
    """
    Returns the number of people entering or exiting the library from the person counter

    :param lib: The library which the entrance(s)/exit(s) are from (+x for entrances or -x for exits)
    :param client: The client (person counter) sending the data to the server
    :return: Returns an integer which represents the processed increment of the request
    """

    # receive the update to the number of people in the senior library (+x or -x)
    msg = client.recv(1024)
    incr = eval(msg + b"+0") # add a "+0" at the end in case the string has a trailing + or - (due to weird bug where requests get merged)
    logger.info(f"Recieved message: {incr}")
    return incr

def handleConnection(lib, sock):
    """
    Handler which facilitates the connection between the person counter and this server

    :param lib: The library which this function will receive calls requests from
    :param sock: The socket object (a combination of this server's host and port)
    :return:
    """

    # wait for connection
    client, address = sock.accept()

    # timeout the connection if the client takes to long to send a response
    sock.settimeout(6)

    logger.info(f"{lib}: Connection from {address[0]}")
    
    try:
        # We don't want the person counter to simply send the key over since, if a third-party was
        # to intercept our connection, they'd be able to view the key and verify themselves. Thus,
        # we should verify by checking whether or not the connecting client is able to decrypt streams
        # with a key using a symmetric, one-way algorithm (e.g. AES)
        logger.info(f"{lib}: Sending verification string")
        
        # create random string of bytes for verification
        plaintext = bytes([random.randint(0, 0xff) for _ in range(16)])
        client.send(aesenc.encrypt(plaintext) + b"\n")
        msg = client.recv(16)
        
        # if verification is failed, raise an error and let the try/except statement catch it
        assert msg == CAMERA_KEY, "Verification failed"
        
        logger.info(f"{lib}: Verification succeeded")
        while True:
            # once verification has succeeded, no time limit is required
            sock.settimeout(None)
            
            incr = getMsg(lib, client)
            updateCount(lib, incr)
        
    except Exception as e:
        sock.settimeout(None)
        # print the error (due to verification taking too long, verification being unsuccessful, client closing the connection or some other unknown error
        logger.debug(f"{lib}: {e!r}")
        
    client.close()

def __init__(lib):
    logger.info(f"Starting {lib}_updater")
    kill_port.kill_port(CAMERA_SYSTEM_PORTS[lib])
    
    # create socket and listen
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", CAMERA_SYSTEM_PORTS[lib]))
    sock.listen(10)
    
    while True:
        handleConnection(lib, sock)

