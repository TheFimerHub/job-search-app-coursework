import requests
from typing import Optional, Dict, Any

from api.abs_api import AbstractJobSearchAPI

class SuperJobAPI(AbstractJobSearchAPI):
    def __init__(self, api_token: str):
        """
        Инициализирует объект SuperJobAPI.

        Parameters:
            api_token (str): Токен для доступа к API Super Job.
        """
        self.api_token: str = api_token

    def get_data(self, param: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Получает данные о вакансиях с использованием API Super Job.

        Parameters:
            param (Optional[Dict[str, Any]]): Параметры запроса к API.

        Returns:
            Dict[str, Any]: Данные о вакансиях в формате, предоставляемом API.
        """
        headers: Dict[str, str] = {'X-Api-App-Id': self.api_token}
        pages: int = 600
        params: Dict[str, Any] = {'count': pages,
                                  'no_agreement': 1}

        if param:
            params.update(param)

        data: Dict[str, Any] = requests.get('https://api.superjob.ru/2.0/vacancies/', headers=headers, params=params).json()

        return data
