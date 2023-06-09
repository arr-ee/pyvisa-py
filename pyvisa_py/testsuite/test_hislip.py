import logging
from pathlib import Path
import pprint
import select
import socket
import threading
import time
from typing import ByteString, List
import unittest

from pyvisa_py.protocols import hislip

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def read_responses(base_path: Path) -> List[ByteString]:
    res: List[ByteString] = []
    for i in range(1, 6):
        res.append((base_path / f"hislip_resp_{i}.bin").read_bytes())

    return res


testloc = Path(__file__).parent
server_address = ("127.0.0.1", 6666)
responses = read_responses(testloc / "resources")
print(responses)

conns = []


def serve(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(addr)
    sock.listen()

    while True:
        conn, _ = sock.accept()
        conns.append(conn)


def handle():
    handled = 0
    while True:
        conn, *_ = select.select(conns, [], [], 1)
        if not conn:
            continue
        else:
            conn = conn[0]
        data = conn.recv(1024)
        logger.info(f"RECEIVED: {data!r}")
        if handled == 3:  # robust
            time.sleep(3)
        conn.sendall(responses[handled])
        logger.info(f"RESPONDED: {responses[handled]!r}")
        handled += 1


class TestHislip(unittest.TestCase):
    handler_thread = None
    server_thread = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.server_thread = threading.Thread(target=lambda: serve(server_address))
        cls.handler_thread = threading.Thread(target=handle)
        # Exit the server thread when the main thread terminates
        cls.server_thread.daemon = True
        cls.handler_thread.daemon = True
        cls.handler_thread.start()
        cls.server_thread.start()
        print("Server loop running in thread:", cls.server_thread.name)

    @classmethod
    def cleanupClass(cls) -> None:
        pass

    def test_message_ordering(self):
        inst = hislip.Instrument(server_address[0], port=server_address[1], timeout=2)
        logger.info(inst)
        inst.send("*RST\n".encode("ascii"))
        inst.send("*OPC?\n".encode("ascii"))
        logger.info(pprint.pformat(inst.__dict__))
        try:
            logger.info(f"POST-OPC: {inst.receive()!r}")
        except TimeoutError as e:
            logger.info("POST-OPC: timeout")
        logger.info(pprint.pformat(inst.__dict__))
        inst.send("*IDN?\n".encode("ascii"))
        logger.info(pprint.pformat(inst.__dict__))
        logger.info(f"POST-IDN: {inst.receive()!r}")
