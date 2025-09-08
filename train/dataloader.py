from torch.utils.data import DataLoader
from queue import Queue
import threading

class CandleDataLoader(DataLoader):
    def __init__(self, dataset, *args, **kwargs):
        super().__init__(dataset, *args, **kwargs)
        self.prefetch_queue = Queue(maxsize=1)
        self.prefetch_thread = None
        self._data_iter = iter(super().__iter__()) # iterator over the underlying DataLoader
    
    def prefetch(self):      
        if self.prefetch_thread is None or not self.prefetch_thread.is_alive():
            self.prefetch_thread = threading.Thread(target=self._prefetch_next)
            self.prefetch_thread.daemon = True
            self.prefetch_thread.start()

    def _prefetch_next(self):
        try:
            batch = next(self._data_iter)
            self.prefetch_queue.put(batch)
        except StopIteration:
            self.prefetch_queue.put(None)

    def __iter__(self):
        return self

    def __next__(self):
        batch = self.prefetch_queue.get()
        if batch is None:
            raise StopIteration
        return batch