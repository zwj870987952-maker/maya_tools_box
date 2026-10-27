"""Compatibility for data-only mGear binary skin dictionaries; no code objects."""
import builtins
import io
import pickle


class DataUnpickler(pickle.Unpickler):
    def find_class(self,module,name):
        if module in ('builtins','__builtin__') and name in ('set','frozenset'):
            return getattr(builtins,name)
        raise ValueError('mGear skin pickle refers to an executable/custom object; export basic JSON in a trusted original environment')


def load_basic_pickle(stream):
    data=stream.read(512*1024*1024+1)
    if not isinstance(data,bytes) or len(data)>512*1024*1024:
        raise ValueError('mGear binary skin data must be bytes <=512 MiB')
    value=DataUnpickler(io.BytesIO(data),encoding='latin1').load()
    if not isinstance(value,dict):
        raise ValueError('Expected a mGear skin data dictionary')
    return value
