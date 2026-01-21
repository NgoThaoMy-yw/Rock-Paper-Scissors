import datetime

_socket_buffers = {}

def log(message: str):
    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {message}")

def send(conn, message: str):
    try:
        if not message.endswith("|"):
            message += "|"
        conn.sendall(message.encode("utf-8"))
    except (BrokenPipeError, ConnectionResetError, OSError):
        pass


def recv_line(conn):
    buf = _socket_buffers.get(conn, "")
    try:
        while "|" not in buf:
            data = conn.recv(4096)
            if not data:
                _socket_buffers.pop(conn, None)
                return None
            buf += data.decode("utf-8", errors="ignore")

        line, buf = buf.split("|", 1)
        _socket_buffers[conn] = buf
        return line.strip()
    except Exception:
        _socket_buffers.pop(conn, None)
        return None
