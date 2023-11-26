from typing import Type

from colorama import Fore, Style


class Vacancy:
    def __init__(self, data_vacancy: dict):
        """
        Инициализирует объект Vacancy.

        Аргументы:
            data_vacancy (dict): Данные о вакансии.
        """
        self.data_vacancy = data_vacancy
        self.title = data_vacancy.get('title', 'Нет информации')
        self.url = data_vacancy.get('url', 'Нет информации')
        self.currency = data_vacancy.get('currency', 'Нет информации')
        self.salary = data_vacancy.get('salary', 'Нет информации')
        self.description = data_vacancy.get('description', 'Нет информации')
        self.city = data_vacancy.get('city', 'Нет информации')
        self.published_at = data_vacancy.get('published_at', 'Нет информации')
        self.employer = data_vacancy['employer'].get('name', 'Нет информации')
        self.employer_url = data_vacancy['employer'].get('url', 'Нет информации')

    def __str__(self):
        """
        Аргументы строковое представление объекта Vacancy.

        Возвращает:
            str: Строковое представление объекта.
        """
        print('__________________________________________________________________________________')
        print(Fore.BLUE + Style.BRIGHT + "Название: " + Fore.CYAN + self.title + Style.RESET_ALL)
        print(Fore.BLUE + Style.BRIGHT + "Оплата: " + Fore.GREEN + str(
            self.salary) + Fore.BLUE + ' ' + self.currency + Style.RESET_ALL)
        print(Fore.BLUE + Style.BRIGHT + "Дата публикации: " + Style.RESET_ALL + self.published_at)
        if self.description is not None:
            truncated_description = self.description[:100] if len(self.description) > 100 else self.description
            print(
                Fore.BLUE + Style.BRIGHT + "Описание: " + Style.RESET_ALL + truncated_description + '...' + Style.RESET_ALL + Fore.RED + '\n(Читать подробнее по ссылке на вакансию)' + Style.RESET_ALL)
        else:
            print(Fore.BLUE + Style.BRIGHT + "Описание отсутствует" + Style.RESET_ALL)
        print(Fore.BLUE + Style.BRIGHT + "Ссылка на вакансию: " + Style.RESET_ALL + self.url)
        print('__________________________________________________________________________________')
        print(Fore.YELLOW + Style.BRIGHT + "Дополнительная информация: " + Style.RESET_ALL)
        print(Fore.BLUE + Style.BRIGHT + "Город: " + self.city + Style.RESET_ALL)
        print(Fore.BLUE + Style.BRIGHT + "Работодатель: " + Fore.MAGENTA + self.employer + Style.RESET_ALL)
        print(Fore.BLUE + Style.BRIGHT + "Ссылка на работодателя: " + Style.RESET_ALL + self.employer_url)
        print('__________________________________________________________________________________')
        print('')

    def compare_salary(self, other):
        """
        Сравнивает зарплату текущей вакансии с другой вакансией.

        Аргументы:
            other (Vacancy): Другая вакансия для сравнения.

        Возвращает:
            str: Результат сравнения зарплат.
        """
        self_salary = int(self.salary)
        other_salary = int(other.salary)

        if self_salary > other_salary:
            difference = self_salary - other_salary
            return f"Зарплата вакансии {Fore.CYAN}'{self.title}'{Style.RESET_ALL} выше на {Fore.GREEN}{difference}{Style.RESET_ALL}{Fore.BLUE} {self.currency}{Style.RESET_ALL}."
        elif self_salary < other_salary:
            difference = other_salary - self_salary
            return f"Зарплата вакансии {Fore.CYAN}'{other.title}'{Style.RESET_ALL} выше на {Fore.GREEN}{difference}{Style.RESET_ALL}{Fore.BLUE} {self.currency}{Style.RESET_ALL}."
        else:
            return Fore.GREEN + "Зарплаты для обеих вакансий одинаковы." + Style.RESET_ALL


class VacancyFilter:
    def __init__(self):
        self.sort_params = {}

    def sort_top_salary_vacancies(self, api: dict):
        """
        Добавляет сортировку вакансий по максимальной зарплате.

        Аргументы:
            api (dict): Информация об API.
        """
        if api.get('name') == 'Head Hunter':
            param = {'order_by': 'salary_desc'}
        if api.get('name') == 'Super Job':
            param = {'order_field': 'payment',
                     'order_direction': 'desc'}

        self._update_sort_params(param)

    def sort_top_last_published_vacancies(self, api: dict):
        """
        Добавляет сортировку вакансий по последней дате публикации.

        Аргументы:
            api (dict): Информация об API.
        """
        if api.get('name') == 'Head Hunter':
            param = {'order_by': 'publication_time'}
            self._update_sort_params(param)

    def sort_with_keyword(self, keyword: str, api: dict):
        """
        Добавляет сортировку вакансий по ключевому слову.

        Аргументы:
            keyword (str): Ключевое слово для фильтрации.
            api (dict): Информация об API.
        """
        if api.get('name') == 'Head Hunter':
            param = {'text': keyword}
        if api.get('name') == 'Super Job':
            param = {'keyword': keyword}
        self._update_sort_params(param)

    def _update_sort_params(self, param: dict):
        """
        Обновляет параметры сортировки вакансий.

        Аргументы:
            param (dict): Параметры сортировки.

        """
        self.sort_params.update(param)

    def get_sort_data(self, api: dict):
        """
        Получает отсортированные данные вакансий с учетом параметров сортировки.

        Аргументы:
            api (dict): Информация об API.

        Возвращает:
            dict: Отсортированные данные вакансий.
        """
        return api.get('api_class').get_data(self.sort_params)

    def remove_bad_vacancies(self, vacancies: dict):
        """
        Удаляет дублирующиеся вакансии и те, у которых отсутствует зарплата.

        Аргументы:
            vacancies (dict): Информация о вакансиях.

        Возвращает:
            dict: Уникальные данные вакансий.
        """
        unique_vacancies = {}
        seen_titles = set()

        for vacancy_key, vacancy in vacancies.items():
            title = vacancy["title"]
            salary = vacancy.get("salary")
            employer_name = vacancy["employer"]["name"]
            key = (title, salary, employer_name)

            if salary is not None and salary != 0 and key not in seen_titles:
                seen_titles.add(key)
                unique_vacancies[vacancy_key] = vacancy

        return unique_vacancies

class VacancyOutput:
    def data_short_output(self, sorted_data: dict, data_top: str):
        """
        Выводит короткую информацию о вакансиях.

        Аргументы:
            sorted_data (dict): Отсортированные данные вакансий.
            data_top (str): Количество вакансий для вывода.
        """
        for id, vacancy in enumerate(sorted_data.values(), start=1):
            print(Fore.YELLOW + f'{id}.' + Style.RESET_ALL + ' ' + vacancy[
                'title'] + ' — ' + Fore.GREEN + Style.BRIGHT + str(vacancy['salary']) + ' ' + Fore.BLUE + vacancy[
                      'currency'] + Style.RESET_ALL)

            if id == int(data_top):
                break

    def data_vacancy_info_output(self, vacancy: Type[Vacancy]):
        """
        Выводит подробную информацию о выбранной вакансии.

        Аргументы:
            vacancy (Type[Vacancy]): Выбранная вакансия.
        """
        print(Fore.YELLOW + Style.BRIGHT + "Вот вакансия которую вы выбрали:" + Style.RESET_ALL)
        vacancy.__str__()

        self.continue_program_enter()

    def data_2_vacancy_info_output(self, vacancy_1: Type[Vacancy], vacancy_2: Type[Vacancy]):
        """
        Выводит подробную информацию о двух выбранных вакансиях.

        Аргументы:
            vacancy_1 (Type[Vacancy]): Первая выбранная вакансия.
            vacancy_2 (Type[Vacancy]): Вторая выбранная вакансия.
        """
        print(Fore.YELLOW + Style.BRIGHT + "Вот 2 вакансии которую вы выбрали:" + Style.RESET_ALL)
        print(Fore.BLUE + "Первая вакансия" + Style.RESET_ALL)
        vacancy_1.__str__()
        print(Fore.BLUE + "Вторая вакансия" + Style.RESET_ALL)
        vacancy_2.__str__()

        self.continue_program_enter()

    def continue_program_enter(self):
        """
        Останавливает выполнение программы до нажатия ENTER.
        """
        while True:
            print('Нажмите' + Fore.YELLOW + Style.BRIGHT + ' ENTER ' + Style.RESET_ALL + 'что бы продолжить.')
            response = input()

            if response == '':
                break
