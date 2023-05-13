import multiprocessing


class Sender:
    __slots__ = ["q", ]
    q: multiprocessing.Queue

    def __init__(self, q: multiprocessing.Queue):
        self.q = q

    def send_message(self,
                     channel: int,
                     message=None, *_, **kwargs):
        self.q.put(
            {
                "type": "send_mess",
                "body": {
                    channel: {
                        "content": f"{message}",
                    }}
            }
        )
