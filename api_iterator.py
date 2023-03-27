from basecampy3.exc import Basecamp3Error

class BasecampAPIIterator(object):
    def __init__(self, iterable):
        self._iter = iter(iterable)
        self.handlers = []
    def __iter__(self):
        return self
    def __next__(self):
        try:
            return next(self._iter)
        except StopIteration as e:
            raise e
        except Basecamp3Error as e:
            if e.response.status_code == 429:
                sleep(1.1)
                return self.__next__()
            else:
                raise e
        except Exception as e:
            raise e