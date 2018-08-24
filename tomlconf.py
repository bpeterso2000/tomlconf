class File:
    """File context manager

    The file contents are read into `self.text` when entering the
    context manager; if `read` is permitted.

    The `self.text` string is written to the file when exiting the
    context manager; if `write` is permitted.  If `self.text` can
    not be converted to a string it will raise a `TypeError`.

    In write-only mode `self.text` = ''

    filename (str):
        file path/name
    mode:
        'r':  read-only (default)
        'r+': read & wite`
        'w':  write-only
    encoding:
        See the codecs module for the list of supported encodings.
        The default is 'utf-8'.
    errors:
        See the documentation for codecs.register for a list of the
        permitted encoding error strings. The default is 'strict'.
    """

    def __init__(self, filename, mode='r', encoding='utf-8', errors='strict'):
        if mode not in ('r', 'r+', 'w'):
            raise ValueError(
              "File context manager mode must be 'r', 'r+' or 'w'."
            )
        self.__openfile = None
        self._mode = mode
        self.filename = filename
        self.encoding = encoding
        self.errors = errors
        self.text = ''

    @property
    def mode(self):
        return self._mode

    def __enter__(self):
        self.__openfile = open(
            self.filename,
            mode=self.mode,
            encoding=self.encoding,
            errors=self.errors,
            newline=''
        )
        if 'r' in self.mode:
            self.text = self.__openfile.read()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__openfile:
            if self.mode in ('r+', 'w'):
                self.__openfile.seek(0)
                self.__openfile.write(str(self.text))
                self.__openfile.truncate()
            self.__openfile.close()
