from colorama import Fore, Style

from api.hh_api import HHJobSearchAPI
from api.superjob_api import SuperJobAPI
from implemented import api_key
from model.vacancies import VacancyFilter, Vacancy, VacancyOutput
from storage.json_handler import JSONJobDataHandler


class TextStyle:
    @staticmethod
    def print_error(message):
        print(Fore.RED + Style.BRIGHT + f"Ошибка: {message}" + Style.RESET_ALL)

    @staticmethod
    def print_yellow_bold(message):
        print(Fore.YELLOW + Style.BRIGHT + message + Style.RESET_ALL)

    @staticmethod
    def print_message(message):

        print(message)


class JobSearchApp:
    def __init__(self):
        self.hh_api = HHJobSearchAPI()
        self.superjob_api = SuperJobAPI(api_token=api_key)
        self.vacancy_actions = VacancyFilter()
        self.json_handler = JSONJobDataHandler("optimize_data.json")
        self.text_style = TextStyle()
        self.vacancy_output = VacancyOutput()

    def check_digit(self, string):
        try:
            int(string)
        except ValueError:
            self.text_style.print_error("Введите корректное число.")
            return False
        return True

    def check_number(self, data):
        try:
            number = float(data)

            if 0 < number <= 30:
                return True
            else:
                self.text_style.print_error("Введите число от 1 до 30.")
                return False
        except ValueError:
            self.text_style.print_error("Введите корректное число.")
            return False

    def check_input(self, inp, counts):
        if not self.check_digit(inp):
            return False

        if int(inp) <= counts[-1] and int(inp) >= counts[0]:
            return True
        self.text_style.print_error(f"Введите число в диапазоне от {counts[0]} до {counts[-1]}.")
        return False

    def user_interaction(self):
        while True:
            self.text_style.print_yellow_bold('Приветствую, ты находишься в программе "Поиск вакансий"!')

            data_platform = self.get_platform_input()

            if data_platform == '1':
                name_platform = 'Head Hunter'
                api = self.hh_api
            elif data_platform == '2':
                name_platform = 'Super Job'
                api = self.superjob_api

            data_sort = self.get_sort_input()

            data_top = self.get_top_input()

            if data_sort == '1':
                self.vacancy_actions.sort_top_salary_vacancies(name_platform)
                data_name_sort = 'вакансий по зарплате на данный момент'
            elif data_sort == '2':
                self.vacancy_actions.sort_top_last_published_vacancies(name_platform)
                data_name_sort = 'последних опубликованных вакансий'

            data_answer = self.get_keyword_input()

            if data_answer == '1':
                self.text_style.print_yellow_bold('Введите ключевое слово: ')
                keyword = input()
                self.vacancy_actions.sort_with_keyword(keyword, name_platform)

            vacancies_data = self.vacancy_actions.get_sort_data(api)
            self.json_handler.clear_json_file()
            self.json_handler.convert_list_to_custom_format(vacancies_data, name_platform)
            self.json_handler.load_from_file()
            self.vacancy_actions.remove_bad_vacancies(self.json_handler.data)
            self.json_handler.clear_json_file()
            self.json_handler.data = self.vacancy_actions.data
            self.json_handler.save_to_file()

            if self.json_handler.data == {}:
                self.text_style.print_error(f"Вакансий по вашему запросу не найдено :(")
                continue


            while True:
                self.text_style.print_yellow_bold(
                    f"Вот ваши Топ-{data_top} {data_name_sort} на платформе {name_platform}.")
                self.vacancy_output.data_short_output(self.json_handler.data, data_top)

                data_check_vacansy = self.get_vacansy_for_check(data_top)

                vacancy_list = list(self.json_handler.data.items())
                vacansy_items = vacancy_list[int(data_check_vacansy) - 1]
                vacancy = Vacancy(vacansy_items[1])

                print('')
                print(Fore.YELLOW + Style.BRIGHT + "Вот вакансия которую вы выбрали:" + Style.RESET_ALL)
                vacancy.__str__()

                print('Нажмите' + Fore.YELLOW + Style.BRIGHT + ' ENTER ' + Style.RESET_ALL + 'что бы продолжить.')
                input()

                data_choice_option = self.get_menu()

                while True:
                    if data_choice_option == '1':
                        self.text_style.print_yellow_bold(
                            f"Вот ваши Топ-{data_top} {data_name_sort}")
                        self.vacancy_actions.data_short_output(self.json_handler.data, data_top)

                        data_check_second_vacansy = self.get_vacancy_for_comparison(data_top, data_check_vacansy)
                        second_vacansy_items = vacancy_list[int(data_check_second_vacansy) - 1]
                        second_vacansy = Vacancy(second_vacansy_items[1])

                        while True:
                            data_choice_option_2 = self.get_settings_from_comparison()

                            if data_choice_option_2 == '1':
                                print('')
                                print(Fore.YELLOW + Style.BRIGHT + "Вот 2 вакансии которую вы выбрали:" + Style.RESET_ALL)
                                print(Fore.BLUE + "Первая вакансия" + Style.RESET_ALL)
                                vacancy.__str__()
                                print(Fore.BLUE + "Вторая вакансия" + Style.RESET_ALL)
                                second_vacansy.__str__()

                                print('Нажмите' + Fore.YELLOW + Style.BRIGHT + ' ENTER ' + Style.RESET_ALL + 'что бы продолжить.')
                                input()

                            if data_choice_option_2 == '2':
                                print('')
                                print(vacancy.compare_salary(second_vacansy))
                                print('')
                                print(
                                    'Нажмите' + Fore.YELLOW + Style.BRIGHT + ' ENTER ' + Style.RESET_ALL + 'что бы продолжить.')
                                input()
                                continue

                            if data_choice_option_2 == '3':
                                break

                            if data_choice_option_2 == '4':
                                exit()


                    if data_choice_option == '2':
                        break

                    if data_choice_option == '3':
                        exit()

                    break

    def get_platform_input(self):
        while True:
            self.text_style.print_yellow_bold(
                'Выберете цифру соответствено той на какой площадке \nвы хотите найти вакансии?')
            self.text_style.print_message('  1. HeadHunter')
            self.text_style.print_message('  2. SuperJob')
            data_platform = input()
            if not self.check_input(data_platform, [1, 2]):
                continue
            break
        return data_platform

    def get_sort_input(self):
        while True:
            self.text_style.print_yellow_bold(
                'Выберете цифру соответствено той, какую сортировку \nвы хотите получить?')
            self.text_style.print_message('  1. Топ вакансии по зарплате на данный момент.')
            self.text_style.print_message('  2. Топ последних опубликованных вакансий.')
            data_sort = input()
            if not self.check_digit(data_sort):
                continue
            break
        return data_sort

    def get_top_input(self):
        while True:
            self.text_style.print_yellow_bold('Сколько вакансий вы хотите увидеть? (от 1 до 30)')
            data_top = input()

            if not self.check_digit(data_top) or not self.check_number(data_top):
                continue

            break
        return data_top

    def get_keyword_input(self):
        while True:
            self.text_style.print_yellow_bold('Нужно ли искать по ключевому слову?')
            self.text_style.print_message('  1. Да')
            self.text_style.print_message('  2. Нет')

            data_answer = input()

            if not self.check_input(data_answer, [1, 2]):
                continue
            break
        return data_answer

    def get_vacansy_for_check(self, data_top):
        while True:
            self.text_style.print_yellow_bold('Введите номер интересующей вас вакансии:')
            num_vacansy = input()
            if not self.check_input(num_vacansy, list(range(1, int(data_top) + 1))):
                continue
            break
        return num_vacansy

    def get_vacancy_for_comparison(self, data_top, selected_num):
        while True:
            self.text_style.print_yellow_bold('Введите номер вакансии c которой ты хочешь сравнить эту вакансию:')
            num_vacansy = input()
            if not self.check_input(num_vacansy, list(range(1, int(data_top) + 1))):
                continue
            if num_vacansy == selected_num:
                self.text_style.print_error('Вы не можете сравнивать ту же вакасию.')
                continue
            break
        return num_vacansy

    def get_settings_from_comparison(self):
        while True:
            self.text_style.print_yellow_bold('Выберите опцию:')
            print('  1. Просмотреть обе вакансии.')
            print('  2. Сравнить вакансии по зарплате.')
            print('  3. Вернуться обратно к вакансиям.')
            print('  4. Выйти из программы.')
            data_choice = input()
            if not self.check_input(data_choice, [1, 2, 3, 4]):
                continue
            break
        return data_choice

    def get_menu(self):
        while True:
            self.text_style.print_yellow_bold('Выберите опцию.')
            print('  1. Сравнить эту вакансию с другой.')
            print('  2. Вернуться обратно к вакансиям.')
            print('  3. Выйти из программы.')
            data_choice = input()
            if not self.check_input(data_choice, [1, 2, 3]):
                continue
            break
        return data_choice


if __name__ == "__main__":
    job_search_app = JobSearchApp()
    job_search_app.user_interaction()
