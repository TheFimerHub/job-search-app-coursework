from colorama import Fore, Style
from typing import List

from api.hh_api import HHJobSearchAPI
from api.superjob_api import SuperJobAPI
from implemented import api_key
from model.vacancies import VacancyFilter, Vacancy, VacancyOutput
from storage.json_handler import JSONHandler, Converter


class TextStyle:
    """
    Класс TextStyle предоставляет методы для вывода типизированного текста.
    """

    @staticmethod
    def print_error(message: str) -> None:
        """
        Функция выводит текстовые ошибки красным цветом.

        Parameters:
        - message (str): текст сообщения.
        """
        print(Fore.RED + Style.BRIGHT + f"Ошибка: {message}" + Style.RESET_ALL)

    @staticmethod
    def print_yellow_bold(message: str) -> None:
        """
        Функция выводит текстовое обращение пользователю желтым цветом.

        Parameters:
        - message (str): текст сообщения.
        """
        print(Fore.YELLOW + Style.BRIGHT + message + Style.RESET_ALL)

    @staticmethod
    def print_message(message: str) -> None:
        """
        Функция выводит текстовое обращение пользователю простым текстом.

        Parameters:
        - message (str): текст сообщения.
        """
        print(message)


class InputChecker:
    """
    Класс InputChecker предоставляет методы для проверок ввода.
    """

    def __init__(self) -> None:
        self.text_style = TextStyle()

    def check_int_digit(self, string: str) -> bool:
        """
        Функция проверяет является ли значение числом.

        Parameters:
        - string (str): введенное значение.

        Returns:
        - True (bool)
        - False (bool)
        """
        try:
            int(string)
        except ValueError:
            self.text_style.print_error("Введите корректное число.")
            return False
        return True

    def check_range_input(self, string: str, counts: List[int]) -> bool:
        """
        Функция проверяет находится ли значение в заданном диапазоне.

        Parameters:
        - string (str): введенное значение.
        - counts (List[int]): диапазон допустимых значений.

        Returns:
        - True (bool)
        - False (bool)
        """
        if not self.check_int_digit(string):
            return False

        if int(string) <= counts[-1] and int(string) >= counts[0]:
            return True
        self.text_style.print_error(f"Введите число в диапазоне от {counts[0]} до {counts[-1]}.")
        return False


class JobSearchApp:
    """
    Класс JobSearchApp предоставляет методы для взаимодействия с пользователем.

    Attributes:
    - api_list (List[dict]): перечисление api которые используются.
    """

    def __init__(self, api_list: List[dict]) -> None:
        self.api_list = api_list
        self.json_handler = JSONHandler()
        self.text_messages = self.json_handler.load_from_file('text_messages.json')
        self.text_style = TextStyle()
        self.input_checker = InputChecker()
        self.vacancy_filter = VacancyFilter()
        self.converter = Converter()
        self.save_filename = 'optimize_data.json'
        self.vacancy_output = VacancyOutput()

    def user_interaction(self) -> None:
        """
        Главная функция для взаимодействия с пользователем
        """
        while True:
            # Приветствие с пользователем
            self.text_style.print_yellow_bold(self.text_messages.get("greetings"))

            # Выбор площадки специализированной на поиске вакансий
            self.text_style.print_yellow_bold(self.text_messages.get("platform_selection"))
            data_platform = self.get_platform_input()

            for item in range(1, len(self.api_list) + 1):
                if int(data_platform) == item:
                    api = self.api_list[item - 1]
                    break

            # Выбор хочет ли пользователь искать по ключевому слову
            print('')
            self.text_style.print_yellow_bold(self.text_messages.get("keyword_selection"))
            data_keyword = self.get_keyword_input()

            if data_keyword == '1':
                print('')
                self.text_style.print_yellow_bold(self.text_messages.get("keyword_write"))

                keyword = input()

                # Добавление сортировки по ключевому слову
                self.vacancy_filter.sort_with_keyword(keyword, api)

            # Выбор сортировки которую хочет пользователь
            print('')
            self.text_style.print_yellow_bold(self.text_messages.get("sort_selection"))
            data_sort = self.get_sort_input()

            if data_sort == '1':
                self.vacancy_filter.sort_top_salary_vacancies(api)
                name_sort = 'вакансий по зарплате на данный момент'
            elif data_sort == '2':
                self.vacancy_filter.sort_top_last_published_vacancies(api)
                name_sort = 'последних опубликованных вакансий'

            # Выбор количества вакансий который захочет пользователь
            print('')
            self.text_style.print_yellow_bold(self.text_messages.get("top_selection"))
            data_top = self.get_top_input()

            # Получаем данные от api с примененными сортировками и конвертируем в короткий вид
            response_from_api = self.vacancy_filter.get_sort_data(api)
            response_after_convertation = self.converter.convert_vacancy_in_short_format(response_from_api, api)

            # Убираем ненужные вакансии
            response_after_clean = self.vacancy_filter.remove_bad_vacancies(response_after_convertation)

            # Сохраняем короткую информацию о вакансиях (в будущем можно сделать доп. функционал за счет JSON файла)
            self.json_handler.clear_json_file(self.save_filename)
            self.json_handler.save_to_file(response_after_clean, self.save_filename)

            # Получаем итоговый список вакансий
            vacancies_response = self.json_handler.load_from_file(self.save_filename)

            if vacancies_response == {}:
                self.text_style.print_error('По вашему запросу ничего не найдено.')
                continue

            while True:
                # Выводим итоговый список вакансий
                print('')
                self.text_style.print_yellow_bold(
                    f"Вот ваши Топ-{data_top} {name_sort} на платформе {api.get('name')}.")
                self.vacancy_output.data_short_output(vacancies_response, data_top)

                # Даем пользователю выбрать любую вакансию из предложенного списка
                print('')
                self.text_style.print_yellow_bold(self.text_messages.get('num_view_vacancy'))
                data_first_vacancy = self.get_view_vacancy(data_top)

                # Получаем данные первой выбранной вакансии пользователем
                vacancy_item = list(vacancies_response.items())[int(data_first_vacancy) - 1]
                vacancy_1 = Vacancy(vacancy_item[1])

                # Выводим выбранную вакансию
                print('')
                self.vacancy_output.data_vacancy_info_output(vacancy_1)

                # Вывод выбора интересующих пользователя функций
                print('')
                self.text_style.print_yellow_bold(self.text_messages.get('menu_selection'))
                data_first_menu = self.get_first_menu()

                # Выполняем запрос функции от пользователя
                while True:
                    rollback = False

                    # Пользователь выбирает сравнить 1 вакансию с другой
                    if data_first_menu == '1':
                        # Еще раз выводим список вакансий
                        print('')
                        self.text_style.print_yellow_bold(
                            f"Вот ваши Топ-{data_top} {name_sort} на платформе {api.get('name')}.")
                        self.vacancy_output.data_short_output(vacancies_response, data_top)

                        # Даем пользователю выбрать 2-ую вакансию из предложенного списка
                        print('')
                        self.text_style.print_yellow_bold(self.text_messages.get('num_second_view_vacancy'))
                        data_second_vacancy = self.get_view_vacancy_for_comparison(data_top, data_first_vacancy)

                        # Получаем данные второй выбранной вакансии пользователем
                        second_vacancy_item = list(vacancies_response.items())[int(data_second_vacancy) - 1]
                        vacancy_2 = Vacancy(second_vacancy_item[1])

                        # Выводим 2 выбранную вакансию
                        print('')
                        self.vacancy_output.data_vacancy_info_output(vacancy_2)

                        while True:
                            # Вывод выбора интересующих пользователя функций
                            print('')
                            self.text_style.print_yellow_bold(self.text_messages.get('menu_selection'))
                            data_second_menu = self.get_second_menu()

                            # Пользователь выбирает, чтобы вывести обе вакансии сразу
                            if data_second_menu == '1':
                                print('')
                                self.vacancy_output.data_2_vacancy_info_output(vacancy_1, vacancy_2)

                            # Пользователь выбирает, чтобы сравнить 2 вакансии по зарплате
                            if data_second_menu == '2':
                                print('')
                                print(vacancy_1.compare_salary(vacancy_2))
                                print('')

                                self.vacancy_output.continue_program_enter()

                            # Пользователь выбирает, чтобы выбрать другую 2 вакансию
                            if data_second_menu == '3':
                                break

                            # Пользователь выбирает, чтобы вернуться к вакансиям
                            if data_second_menu == '4':
                                rollback = True
                                break

                            # Пользователь выбирает выход из программы
                            if data_second_menu == '5':
                                exit()

                    # Пользователь выбирает, чтобы вернуться к вакансиям
                    if data_first_menu == '2':
                        break

                    # Пользователь выбирает выход из программы
                    if data_first_menu == '3':
                        exit()

                    if rollback == True:
                        break

    def get_platform_input(self) -> str:
        """
        Функция для выбора площадки специализированной на поиске вакансий.
        """
        for item, api, in enumerate(self.api_list, start=1):
            self.text_style.print_message(f'  {item}. {api.get("name")}')

        while True:
            data_platform = input()

            items = len(self.api_list)
            if not self.input_checker.check_range_input(data_platform, list(range(1, items + 1))):
                continue

            break

        return data_platform

    def get_keyword_input(self) -> str:
        """
        Функция для понимания, хочет ли пользователь искать по ключевому слову.
        """
        self.text_style.print_message('  1. Да')
        self.text_style.print_message('  2. Нет')

        while True:
            data_answer = input()

            if not self.input_checker.check_range_input(data_answer, [1, 2]):
                continue

            break

        return data_answer

    def get_sort_input(self) -> str:
        """
        Функция для выбора сортировки.
        """
        self.text_style.print_message('  1. Топ вакансии по зарплате на данный момент.')
        self.text_style.print_message('  2. Топ последних опубликованных вакансий.')

        while True:
            data_sort = input()

            if not self.input_checker.check_range_input(data_sort, [1, 2]):
                continue

            break

        return data_sort

    def get_top_input(self) -> str:
        """
        Функция для выбора числа топа.
        """
        while True:
            data_top = input()

            items = 30
            if not self.input_checker.check_range_input(data_top, list(range(2, items + 1))):
                continue

            break

        return data_top

    def get_view_vacancy(self, data_top: str) -> str:
        """
        Функция для опции выбора первой вакансии.

        Parameters:
        - data_top (str): количество вакансий в списке.
        """
        while True:
            num_vacancy = input()

            if not self.input_checker.check_range_input(num_vacancy, list(range(1, int(data_top) + 1))):
                continue

            break

        return num_vacancy

    def get_view_vacancy_for_comparison(self, data_top: str, selected_num: str) -> str:
        """
        Функция для опции выбора второй вакансии.

        Parameters:
        - data_top (str): количество вакансий в списке.
        - selected_num (str): номер уже выбранной вакансии.
        """
        while True:
            num_vacancy = input()

            if not self.input_checker.check_range_input(num_vacancy, list(range(1, int(data_top) + 1))):
                continue

            if num_vacancy == selected_num:
                self.text_style.print_error('Вы не можете сравнивать ту же вакасию.')
                continue

            break

        return num_vacancy

    def get_first_menu(self):
        """
        1 функция для выбора нужных опций пользователю.
        """
        self.text_style.print_message('  1. Сравнить эту вакансию с другой.')
        self.text_style.print_message('  2. Вернуться обратно к вакансиям.')
        self.text_style.print_message('  3. Выйти из программы.')

        while True:
            data_choice = input()

            if not self.input_checker.check_range_input(data_choice, [1, 2, 3]):
                continue

            break

        return data_choice

    def get_second_menu(self):
        """
        2 функция для выбора нужных опций пользователю.
        """
        self.text_style.print_message('  1. Просмотреть обе вакансии.')
        self.text_style.print_message('  2. Сравнить вакансии по зарплате.')
        self.text_style.print_message('  3. Выбрать другую 2 вакансию.')
        self.text_style.print_message('  4. Вернуться обратно к вакансиям.')
        self.text_style.print_message('  5. Выйти из программы.')

        while True:
            data_choice = input()

            if not self.input_checker.check_range_input(data_choice, [1, 2, 3, 4, 5]):
                continue

            break

        return data_choice


if __name__ == "__main__":
    hh_api = {"api_class": HHJobSearchAPI(), "name": "Head Hunter"}
    super_job_api = {"api_class": SuperJobAPI(api_key), "name": "Super Job"}
    job_search_app = JobSearchApp([hh_api, super_job_api])
    job_search_app.user_interaction()
