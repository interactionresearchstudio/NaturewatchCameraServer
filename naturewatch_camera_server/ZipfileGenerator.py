from io import RawIOBase
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import os

class ZipfileGenerator():

    class UnseekableStream(RawIOBase):
        def __init__(self):
            self._buffer = b''

        def writable(self):
            return True

        def write(self, b):
            if self.closed:
                raise ValueError('Stream was closed!')
            self._buffer += b
            return len(b)

        def get(self):
            chunk = self._buffer
            self._buffer = b''
            return chunk

    # Constructor
    def __init__(self, paths):
        self.paths   = paths

    # Generator
    def get(self):

        output = ZipfileGenerator.UnseekableStream()

        with ZipFile(output, mode='w') as zf:

            for path in self.paths:

                z_info = ZipInfo.from_file(path,os.path.join('photos',os.path.basename(path)))
                # it's not worth the resources, achieves max 0.1% on JPEGs...
                #z_info.compress_type = ZIP_DEFLATED

                with open(path, 'rb') as entry, zf.open(z_info, mode='w') as dest:

                    for chunk in iter(lambda: entry.read(16384), b''):
                        dest.write(chunk)
                        # Yield chunk of the zip file stream in bytes.
                        yield output.get()

        # ZipFile was closed.
        yield output.get()

