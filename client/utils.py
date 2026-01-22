_socket_buffers = {}

def recv_line(sock):
    buf = _socket_buffers.get(sock, "")
    try:
        while "|" not in buf:
            data = sock.recv(4096)
            if not data:
                return None
            buf += data.decode()
        line, buf = buf.split("|", 1)
        _socket_buffers[sock] = buf
        return line
    except (ConnectionAbortedError, ConnectionResetError, OSError):
        return None

