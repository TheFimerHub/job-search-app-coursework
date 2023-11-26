from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AbstractJobSearchAPI(ABC):
    @abstractmethod
    def get_data(self, param: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Абстрактный метод для получения данных о вакансиях.

        Parameters:
            param (Optional[Dict[str, Any]]): Параметры запроса к API.

        Returns:
            Dict[str, Any]: Данные о вакансиях в формате, предоставляемом конкретным API.
        """
        pass
