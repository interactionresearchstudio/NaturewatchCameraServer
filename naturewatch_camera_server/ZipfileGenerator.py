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
    def __init__(self,
                 paths = [], # { 'filename':'', 'arcname':'' }
                 chunk_size = 0x8000):

        self.paths      = paths
        self.chunk_size = chunk_size

    # Generator
    def get(self):

        output = ZipfileGenerator.UnseekableStream()

        with ZipFile(output, mode='w') as zf:

            for path in self.paths:

                try:
                    if len(path['arcname']) == 0:
                        path['arcname'] = path['filename']

                    z_info = ZipInfo.from_file(path['filename'], path['arcname'])

                    # it's not worth the resources, achieves max 0.1% on JPEGs...
                    #z_info.compress_type = ZIP_DEFLATED

                    # should we try to fix the disk timestamps?
                    # or should it be solved by setting the system time with the browser time?
                    
                    with open(path['filename'], 'rb') as entry, zf.open(z_info, mode='w') as dest:

                        for chunk in iter(lambda: entry.read(self.chunk_size), b''):
                            dest.write(chunk)
                            # yield chunk of the zip file stream in bytes.
                            yield output.get()

                except FileNotFoundError:
                    # this should probably be logged, but how?
                    pass

        # ZipFile was closed: get the final bytes
        yield output.get()

