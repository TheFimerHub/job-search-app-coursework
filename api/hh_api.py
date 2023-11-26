import requests
from typing import Optional, Dict, Any

from api.abs_api import AbstractJobSearchAPI


class HHJobSearchAPI(AbstractJobSearchAPI):
    def get_data(self, param: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Получает данные о вакансиях с использованием API Head Hunter.

        Parameters:
            param (Optional[Dict[str, Any]]): Параметры запроса к API.

        Returns:
            Dict[str, Any]: Данные о вакансиях в формате, предоставляемом API.
        """
        pages: int = 100
        params: Dict[str, Any] = {'only_with_salary': 'true',
                                  'per_page': pages,
                                  'search_field': 'name'}

        if param:
            params.update(param)

        data: Dict[str, Any] = requests.get('https://api.hh.ru/vacancies', params=params).json()

        return data
