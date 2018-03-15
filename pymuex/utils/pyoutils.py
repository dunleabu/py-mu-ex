import pyo

class PyoServer(object):

    __server = None

    def __new__(cls):
        if PyoServer.__server is None:
            PyoServer.__server = pyo.Server()
            PyoServer.__server.setOutputDevice(0)
            PyoServer.__server.boot()
        return PyoServer.__server


