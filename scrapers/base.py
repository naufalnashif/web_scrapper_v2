from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def get_data(self, identifier: str):
        """Method utama untuk mengambil data"""
        pass