from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor

class TasksQueue:
   def __init__(self, max_threads:int=1):
      self._queue = Queue()
      self._threadPool = ThreadPoolExecutor(max_threads, "SpeedDB_TasksQueue")
   
   def add_task_and_execute(self, task, *args, **kwargs):
      unfinished_tasks = self._queue.unfinished_tasks

      self._queue.put({
         "task": task,
         "args": args,
         "kwargs": kwargs
      })
      
      if unfinished_tasks == 0:
         self._threadPool.submit(self._clear_queue)

   def _clear_queue(self):
      try:
         while not self._queue.empty():
            task, args, kwargs = map(self._queue.get_nowait().get, ("task", "args", "kwargs"))
            task(*args, **kwargs)
            self._queue.task_done()
      except Empty:
         pass