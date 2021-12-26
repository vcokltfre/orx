from typing import Sequence


class SmartReprMixin:
    """
    A mixin class for objects that want to have a smart repr.
    """

    def __repr__(self):
        """
        Return a string representation of the object.
        """

        if not (sri := getattr(self, "__smart_repr__")):
            return super().__repr__()

        sri: Sequence[str]
        items = []

        for item in sri:
            val = getattr(self, item).__repr__()
            items.append(f"{item}={val}")

        return f"<{self.__class__.__name__} {' '.join(items)}>"
