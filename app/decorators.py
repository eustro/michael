# *-- coding: utf-8 --*


def asynchronous(func):
    """
    Spawns a thread to delegate a function for execution.
    Used for emails to send the asynchronous.
    :param func: Function to execute in a separate thread.
    :return: Thread for execution.
    """
    def threaded_task(*args, **kwargs) -> None:
        """
        Returns a threaded task that is being spawned in background.

        :param args:
        :param kwargs:

        :return:
        """
        from threading import Thread
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()

    return threaded_task
