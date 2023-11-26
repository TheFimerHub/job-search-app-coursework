import json
from datetime import datetime
from typing import Dict, Optional

from dateutil import parser

class Converter:
    def convert_vacancy_in_short_format(self, vacancy_data: Dict, api: Dict) -> Dict:
        """
        Конвертирует данные вакансий в краткий формат для отображения.

        Parameters:
            vacancy_data (Dict): Данные вакансий от API.
            api (Dict): Информация об API, из которого получены данные.

        Returns:
            Dict: Словарь с адаптированными данными вакансий.
        """
        if api.get('name') == 'Head Hunter':
            return self._adapt_headhunter_vacancy(vacancy_data)
        elif api.get('name') == 'Super Job':
            return self._adapt_superjob_vacancy(vacancy_data)

    def _adapt_headhunter_vacancy(self, vacancy_data: Dict) -> Dict:
        """
        Адаптирует данные вакансий от Head Hunter в краткий формат.

        Parameters:
            vacancy_data (Dict): Данные вакансий от Head Hunter API.

        Returns:
            Dict: Словарь с адаптированными данными вакансий.
        """
        result_vacancies = {}
        for id, data in enumerate(vacancy_data['items'], start=1):
            try:
                # Обработка данных о зарплате
                currency: str = 'RUB'
                active_salary: float = 0
                if data['salary']['to'] is not None:
                    active_salary = data['salary']['to']
                elif data['salary']['from'] is not None:
                    active_salary = data['salary']['from']

                # Конвертация зарплаты в рубли, если в другой валюте
                if data['salary']['currency'] in ['AZN', 'BYR', 'EUR', 'GEL', 'KGS', 'KZT', 'USD', 'UAH', 'UZS']:
                    salary_value: float = active_salary
                    salary_in_rubles: int = self.convert_to_rubles(salary_value, data['salary']['currency'])
                else:
                    salary_in_rubles = active_salary

                # Формирование данных вакансии
                date: str = parser.parse(data['published_at']).strftime("%Y-%m-%d %H:%M:%S")
                vacancy: Dict = {
                    "title": data['name'],
                    "url": data['alternate_url'],
                    "currency": currency,
                    "salary": salary_in_rubles,
                    "description": data['snippet']['requirement'],
                    "city": data['area']['name'],
                    "published_at": date,
                    "employer": {
                        "name": data['employer']['name'],
                        "url": data['employer']['alternate_url']
                    }
                }
            except Exception:
                continue

            result_vacancies.update({f"vacancy {id}": vacancy})

        return result_vacancies

    def _adapt_superjob_vacancy(self, vacancy_data: Dict) -> Dict:
        """
        Адаптирует данные вакансий от Super Job в краткий формат.

        Parameters:
            vacancy_data (Dict): Данные вакансий от Super Job API.

        Returns:
            Dict: Словарь с адаптированными данными вакансий.
        """
        result_vacancies = {}
        for id, data in enumerate(vacancy_data['objects'], start=1):
            try:
                # Обработка данных о зарплате
                currency: str = 'RUB'
                date: str = datetime.utcfromtimestamp(data['date_published']).strftime('%Y-%m-%d %H:%M:%S')
                active_salary: float = 0
                if data['payment_to'] is not None:
                    active_salary = data['payment_to']
                elif data['payment_from'] is not None:
                    active_salary = data['payment_from']

                # Конвертация зарплаты в рубли, если в другой валюте
                if data['currency'].upper() in ['UAH', 'UZS']:
                    salary_value: float = active_salary
                    salary_in_rubles: int = self.convert_to_rubles(salary_value, data['currency'].upper())
                else:
                    salary_in_rubles = active_salary

                # Формирование данных вакансии
                vacancy: Dict = {
                    "title": data['profession'],
                    "url": data['link'],
                    "currency": currency,
                    "salary": salary_in_rubles,
                    "description": data['candidat'],
                    "city": data['town']['title'],
                    "published_at": date,
                    "employer": {
                        "name": data['client']['title'],
                        "url": data['client']['link']
                    }
                }
            except Exception:
                continue

            result_vacancies.update({f"vacancy {id}": vacancy})

        return result_vacancies

    def convert_to_rubles(self, amount: float, currency: str) -> Optional[int]:
        """
        Конвертирует заданную сумму в заданной валюте в рубли.

        Parameters:
            amount (float): Сумма денег.
            currency (str): Код валюты.

        Returns:
            Optional[int]: Сумма в рублях или None, если валюта не поддерживается.
        """
        exchange_rates: Dict[str, float] = {
            'AZN': 52.25,
            'BYR': 26.98,
            'EUR': 97.16,
            'GEL': 32.84,
            'KGS': 0.99,
            'KZT': 0.19,
            'USD': 88.8,
            'UZS': 0.0072,
            'UAH': 2.44
        }

        if currency in exchange_rates:
            rate: float = exchange_rates[currency]
            rubles: int = amount * rate

            return int(rubles)
        else:
            return None

class JSONHandler:
    def save_to_file(self, data, filename: str) -> None:
        """
        Сохраняет данные в файл в формате JSON.

        Parameters:
            data: Данные для сохранения.
            filename (str): Имя файла.
        """
        with open(filename, 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def clear_json_file(self, filename: str) -> None:
        """
        Очищает содержимое JSON-файла.

        Parameters:
            filename (str): Имя файла.
        """
        with open(filename, 'w') as file:
            file.truncate(0)

    def load_from_file(self, filename: str) -> Dict:
        """
        Загружает данные из файла в формате JSON.

        Parameters:
            filename (str): Имя файла.

        Returns:
            Dict: Данные, загруженные из файла.
        """
        with open(filename, 'r') as file:
            return json.load(file)
