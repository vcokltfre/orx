from io import IOBase
from os import PathLike, path
from typing import Any, Optional


class File:
    __slots__ = (
        "fp",
        "_handle",
        "filename",
        "_original_close",
    )

    def __init__(
        self,
        fp: IOBase | PathLike[Any] | str,
        filename: Optional[str] = None,
        spoiler: bool = False,
    ) -> None:
        """A File object for use when sending messages.

        Args:
            fp (IOBase | PathLike[Any] | str): The file.
            filename (Optional[str], optional): The filename to use on Discord. Defaults to None.
            spoiler (bool, optional): Whether the file should be spoilered. Defaults to False.

        Raises:
            ValueError: An IOBase object was given but it was not seekable or readable.
            ValueError: An IOBase object was given but it had no name attribute to infer a file name.
        """

        if isinstance(fp, IOBase):
            if not (fp.seekable() and fp.readable()):
                raise ValueError(f"IOBase object {fp!r} must be seekable and readable.")

            self.fp = fp
            self._handle = True

        else:
            self.fp = open(fp, "rb")
            self._handle = False

        if filename is None:
            if isinstance(fp, str):
                self.filename: str = path.split(fp)[1]

            else:
                if not hasattr(fp, "name"):
                    if self._handle:
                        self.fp.close()

                    raise ValueError(f"Object given for fp parameter has no 'name' attribute.")

                self.filename: str = fp.name  # type: ignore[attr-defined]
        else:
            self.filename = filename

        if spoiler and not self.filename.startswith("SPOILER_"):
            self.filename = f"SPOILER_{self.filename}"

        self._original_close = (
            self.fp.close
        )  # see: https://github.com/Rapptz/discord.py/blob/master/discord/file.py#L92-L95
        self.fp.close = lambda: None

    def close(self) -> None:
        """Close the file."""

        self.fp.close = self._original_close
        if self._handle:
            self.fp.close()

    def reset(self, hard: bool | int = True) -> None:
        """Reset the file.

        Args:
            hard (bool | int, optional): Whether to seek to the start of the file. Defaults to True.
        """

        if hard:
            self.fp.seek(0)
