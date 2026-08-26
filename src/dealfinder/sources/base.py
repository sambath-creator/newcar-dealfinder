from abc import ABC, abstractmethod
from ..models import VehicleListing

class ListingSource(ABC):
    name = "base"

    @abstractmethod
    def collect(self) -> list[VehicleListing]:
        """Return permitted/public vehicle listings."""
        raise NotImplementedError
