from scrapy_redis.queue import Base


class RandomQueue(Base):
    """ Random access the value (with blocking)"""

    def __len__(self):
        """Return the length of the stack"""
        return self.server.smembers(self.key)

    def push(self, request):
        """Push a request"""
        self.server.sadd(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        data = None
        while data is None:
            data = self.server.spop(self.key)

        return self._decode_request(data)
