import datetime
import random
import socket

DEBUG = True
PORT = {
    "jnr": 9482,
    "snr": 11498
}

def updateCount(engine, lib):
    # start session with database
    Session = sessionmaker(bind=engine)
    session = Session()

    if lib == "jnr":
        session.query(Count).first().jnrvalue += inc
    elif lib == "snr":
        session.query(Count).first().snrvalue += inc
    else:
        raise Exception("what sorta library is this?!?!")
    
    session.commit()

def receive_loop(engine, Count, lib):
    # once verification has succeeded, no time limit is required
    sock.settimeout(None)

    # receive the update to the number of people in the senior library (+x or -x)
    msg = client.recv(1024)
    inc = eval(msg + b"0") # add a "+0" at the end in case the string has a trailing + or - (due to weird bug where requests get merged)
    print(__name__, "Recieved message:", inc)
    
    updateCount(engine, lib)
    
    if DEBUG:
        # if verification is failed, raise an error and let the try/except statement catch it
        open(f"log{lib}.txt", "a").write(f"{session.query(Count).first().snrvalue} {datetime.datetime.now()}\n")

def __init__(engine, Base, Data, Count, PastData, lib):
    print(__name__, f"Starting {lib}_updater")
    
    # create socket and listen
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", PORT[lib]))
    sock.listen(10)
    
    while True:
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
            if msg == KEY:
                print(__name__, lib, "Verification succeeded")
                while True:
                    receive_loop(lib)
            else:
                raise Exception("Verification failed")
            
        except Exception as e:
            sock.settimeout(None)
            # print the error (due to verification taking too long, verification being unsuccessful, client closing the connection or some other unknown error
            print(__name__, lib, repr(e))
        client.close()

