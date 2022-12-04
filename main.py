import csv
import math
import re
import os
import sys
import openpyxl as pxl
from openpyxl.styles import Font, Border, Side
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Environment, FileSystemLoader
import pdfkit
from prettytable import PrettyTable, ALL

<<<<<<< HEAD
#изменение для main
=======
#change for develop
>>>>>>> develop

currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}
dic_naming = {  'name': 'Название',
                'description': 'Описание',
                'key_skills': 'Навыки',
                'experience_id': 'Опыт работы',
                'premium': 'Премиум-вакансия',
                'employer_name': 'Компания',
                'salary_from': 'Оклад',
                'salary_to': 'Верхняя граница вилки оклада',
                'salary_gross': 'Оклад указан до вычета налогов',
                'salary_currency': 'Идентификатор валюты оклада',
                'area_name': 'Название региона',
                'published_at': 'Дата публикации вакансии',
                'salary': 'Оклад'}

dic_currency = {"AZN": "Манаты",
                "BYR": "Белорусские рубли",
                "EUR": "Евро",
                "GEL": "Грузинский лари",
                "KGS": "Киргизский сом",
                "KZT": "Тенге",
                "RUR": "Рубли",
                "UAH": "Гривны",
                "USD": "Доллары",
                "UZS": "Узбекский сум"}
dic_words = {   "noExperience": "Нет опыта",
                "between1And3": "От 1 года до 3 лет",
                "between3And6": "От 3 до 6 лет",
                "moreThan6": "Более 6 лет"}
dic_for_sort = {"noExperience": 1,
                "between1And3": 2,
                "between3And6": 3,
                "moreThan6": 4}
dic_gross = {"TRUE": "Без вычета налогов",
             "FALSE": "С вычетом налогов",
             "False": "С вычетом налогов",
             "True": "Без вычета налогов"}
                                            # Беда с FALSE и False
dic_bool = {"FALSE": "Нет", "TRUE": "Да", "False": "Нет", "True": "Да"}

dic_cort_key = {'Название': 'name',
                'Описание': 'description',
                'Навыки': 'key_skills',
                'Опыт работы': 'experience_id',
                'Премиум-вакансия': 'premium',
                'Компания': 'employer_name',
                'Нижняя граница вилки оклада': 'salary_from',
                'Верхняя граница вилки оклада': 'salary_to',
                'Оклад указан до вычета налогов': 'salary_gross',
                'Идентификатор валюты оклада': 'salary_currency',
                'Название региона': 'area_name',
                'Дата публикации вакансии': 'published_at',
                'Оклад': 'salary'}

l_titles = [
    '№',
    'Название',
    'Описание',
    'Навыки',
    'Опыт работы',
    'Премиум-вакансия',
    'Компания',
    'Оклад',
    'Название региона',
    'Дата публикации вакансии']

sort_dic = {
    'Навыки': lambda list, sort_rev: list.sort(key=lambda x: len(x.key_skills.split("\n")), reverse=sort_rev),
    'Оклад': lambda list, sort_rev: list.sort(key=lambda x: x.salary.salary_avg, reverse=sort_rev),
    'Опыт работы': lambda list, sort_rev: list.sort(key=lambda x: dic_for_sort[x.experience_id], reverse=sort_rev),
    'Дата публикации вакансии': lambda list, sort_rev: list.sort(key=lambda x: x.published_at, reverse=sort_rev),

    'Описание': lambda list, sort_rev: list.sort(key=lambda x: x.description, reverse=sort_rev),

    'Название': lambda list, sort_rev: list.sort(key=lambda x: x.name, reverse=sort_rev),
    'Премиум-вакансия': lambda list, sort_rev: list.sort(key=lambda x: x.premium, reverse=sort_rev),
    'Компания': lambda list, sort_rev: list.sort(key=lambda x: x.employer_name, reverse=sort_rev),

    'Название региона': lambda list, sort_rev: list.sort(key=lambda x: x.area_name, reverse=sort_rev),
}

filt_dic = {
    'Название': lambda vacancy, sign, list: list.append(vacancy)
                                            if vacancy.name == sign else '',
    'Описание' : lambda vacancy, sign, list: list.append(vacancy)
                                            if vacancy.description == sign else '',
    'Навыки' : lambda vacancy, sign, list: list.append(vacancy)
                                            if all(x in vacancy.key_skills.split("\n") for x in sign.split(", ")) else '',
    'Опыт работы' : lambda vacancy, sign, list: list.append(vacancy)
                                                if dic_words[vacancy.experience_id] == sign else '',
    'Премиум-вакансия' : lambda vacancy, sign, list: list.append(vacancy)
                                                    if dic_bool[vacancy.premium] == sign else '',
    'Компания' : lambda vacancy, sign, list: list.append(vacancy)
                                            if vacancy.employer_name == sign else '',
    'Оклад' : lambda vacancy, sign, list: list.append(vacancy)
                                if ((int(sign) <= int(float(vacancy.salary.salary_to))) & (int(sign) >= int(float(vacancy.salary.salary_from)))) else '',
    'Название региона' : lambda vacancy, sign, list: list.append(vacancy)
                                                    if vacancy.area_name == sign else '',
    'Дата публикации вакансии' : lambda vacancy, sign, list: list.append(vacancy)
                                            if '.'.join(reversed(vacancy.published_at[0:10].split('-'))) == sign else '',
    'Идентификатор валюты оклада': lambda vacancy, sign, list: list.append(vacancy)
                                                    if dic_currency[vacancy.salary.salary_currency] == sign else '',
    'Оклад указан до вычета налогов': lambda vacancy, sign, list: list.append(vacancy)
                                                    if dic_bool[vacancy.salary.salary_gross] == sign else ''
}




class Salary(object):
    def __init__(self, salary_from: str, salary_to: str, salary_currency: str, salary_gross):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_currency = salary_currency
        self.salary_avg = currency_to_rub[salary_currency] * (float(salary_to) + float(salary_from)) / 2
        self.salary_gross = salary_gross


class Vacancy(object):

    def __init__(self, dic):
        self.name = dic['name']
        self.salary = Salary(dic['salary_from'], dic['salary_to'], dic['salary_currency'], dic['salary_gross'])
        self.key_skills = dic['key_skills']
        self.description = dic['description']
        self.area_name = dic['area_name']
        self.published_at = dic['published_at']
        self.experience_id = dic['experience_id']
        self.premium = dic['premium']
        self.employer_name = dic['employer_name']



    def request_by_str(self, title: str):
        if title == 'name': return self.name
        if title == 'salary': return self.salary
        if title == 'salary_currency': return dic_currency[self.salary.salary_currency]
        if title == 'area_name': return self.area_name
        if title == 'published_at': return int(self.published_at[0:4])

    def get_values(self):
        return [
            self.name,
            self.description,
            self.key_skills,
            self.experience_id,
            self.premium,
            self.employer_name,
            self.salary.salary_avg,
            self.area_name,
            self.published_at
            ]


class DataSet(object):
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.vacancies_objects = []
        self.filter_vac_obj = []
        self.list_titles = []

    def reader_filer(self):
        reader = []

        with open(self.file_name, encoding='utf-8-sig') as r_file:
            file_reader = csv.reader(r_file, delimiter=",")

            flag = True
            for row in file_reader:
                if flag:
                    self.list_titles = row
                    flag = False
                else:
                    reader.append(row)

        if len(reader) == 0:
            print('Нет данных')
            sys.exit(0)



        for row in reader:
            if ((len(row) == len(self.list_titles)) & (not ((None in row) | ("" in row)))):
                for e in range(0, len(row), 1):
                    row[e] = re.sub(re.compile('<.*?>'), '', row[e])

                    if not e == 2:
                        row[e] = ' '.join(row[e].split())

                self.vacancies_objects.append(Vacancy({k: v for k, v in zip(self.list_titles, row)}))

        if user_input.method == 'Статистика':

            for element in ['salary_to', 'salary_currency']:
                self.list_titles.remove(element)
            self.list_titles[2] = 'salary'
        else:
            for element in ['salary_to', 'salary_gross', 'salary_currency']:
                self.list_titles.remove(element)
            self.list_titles[6] = 'salary'

        for i in range(0, len(self.list_titles), 1):
            self.list_titles[i] = dic_naming[self.list_titles[i]]

    def filter(self, filter_data):

        if len(filter_data) != 0:
            ## Сама фильтрация
            for row in self.vacancies_objects:
                if filter_data in row.name:
                    self.filter_vac_obj.append(row)

    def filter_tb(self, filter_data_tb):
        filter_list = filter_data_tb.split(': ')

        if len(filter_list[0]) != 0:

            filtered_vac_obj = []

            ## Сама фильтрация

            for vacancy in self.vacancies_objects:
                filt_dic[filter_list[0]](vacancy, filter_list[1], filtered_vac_obj)

            if len(filtered_vac_obj) == 0:
                print("Ничего не найдено")
                sys.exit(0)

            self.vacancies_objects = filtered_vac_obj

    def sorter(self, sort_rev, sort_data):

        if sort_rev == 'Да':
            sort_rev = True
        else:
            sort_rev = False

        if len(sort_data) != 0:
            sort_dic[sort_data](self.vacancies_objects, sort_rev)

    def formated(self):
        for e in self.vacancies_objects:
            e.experience_id = dic_words[e.experience_id]
            e.premium = dic_bool[e.premium]
            e.published_at = '.'.join(reversed(e.published_at[0:10].split('-')))
            e.salary.salary_gross = dic_gross[e.salary.salary_gross]
            e.salary.salary_currency = dic_currency[e.salary.salary_currency]
            e.salary.salary_avg = f'{self.reNumber(e.salary.salary_from)} - {self.reNumber(e.salary.salary_to)} ({e.salary.salary_currency}) ({e.salary.salary_gross})'

    def reNumber(self, number: str):
        result: str = ''
        z = number.split(".")[0][::-1]
        count = len(z) // 3 * 3

        for i in range(0, count, 3):
            result += " " + z[i:i + 3]

        if not (len(z) % 3 == 0):
            result = result + " " + z[-(len(z) - count):]

        return result[::-1][:len(result) - 1]

    def clust(self, list_vac, value):
        dict = {}


        for vacancy in list_vac:
            key = vacancy.request_by_str(value)
            if key in dict:
                dict[key].append(vacancy)
            else:
                dict[key] = [vacancy]


        if value == 'area_name':
            new_dict = {}
            count = len(list_vac)
            for key in dict:
                if math.floor(len(dict[key])/count * 100) >= 1:
                    new_dict[key] = dict[key]
            return new_dict

        return dict

    def get_salary_level(self, list_vac, value):

        dict = self.clust(list_vac, value)
        result_dict = {}

        for year in dict:
            sum = 0
            set = dict[year]
            for vacancy in set:
                sum += vacancy.salary.salary_avg
            res = math.floor(sum / len(set))
            result_dict[year] = res

        return result_dict


    def num_vac(self, list_vac):

        dict_years = self.clust(list_vac, 'published_at')

        result_dict_years = {}

        for year in dict_years:
            result_dict_years[year] = len(dict_years[year])

        return result_dict_years

    def vac_rate(self, dict_input):

        dict = {}

        count = len(self.vacancies_objects)

        for key in dict_input:
            dict[key] = round(len(dict_input[key])/count, 4)

        return dict


class InputConnect(object):
    def __init__(self):
        self.method = ''
        self.file_name = ''
        self.filter_data = ''
        self.filter_data_tb = ''
        self.sort_data = ''
        self.sort_rev = ''
        self.numbers_row_inp = ''
        self.titles_table_inp = ''

    def input_processing(self):
        self.method = input("Введите способ отображения (Вакансии / Статистика): ")
        if self.method == 'Статистика':
            self.file_name = input("Введите название файла: ")
            self.filter_data = input("Введите название профессии: ")
        elif self.method == 'Вакансии':
            self.file_name = input("Введите название файла: ")
            self.filter_data_tb = input("Введите параметр фильтрации: ")
            self.sort_data = input("Введите параметр сортировки: ")
            self.sort_rev = input("Обратный порядок сортировки (Да / Нет): ")
            self.numbers_row_inp = input("Введите диапазон вывода: ")
            self.titles_table_inp = input("Введите требуемые столбцы: ")
        else:
            print('Ввод некорректен')
            sys.exit(0)



    def validate(self):
        if os.stat(self.file_name).st_size == 0:
            print('Пустой файл')
            sys.exit(0)

        if ( (len(self.filter_data) == 0) & (self.method == 'Статистика')):
            print('Формат ввода некорректен')
            sys.exit(0)

    def print(self, a, b, c, d, e, f):
        print(f'Динамика уровня зарплат по годам: {a}')
        print(f'Динамика количества вакансий по годам: {b}')
        print(f'Динамика уровня зарплат по годам для выбранной профессии: {c}')
        print(f'Динамика количества вакансий по годам для выбранной профессии: {d}')
        print(f'Уровень зарплат по городам (в порядке убывания): {e}')
        print(f'Доля вакансий по городам (в порядке убывания): {f}')

    def print_table(self, data_set: DataSet, numbers_row, titles_table):

        set = data_set.vacancies_objects
        list_titles = data_set.list_titles
        list_titles.insert(0, '№')


        cropped_set =[]
        for vacancy in set:

            if len(vacancy.key_skills) > 100:
                vacancy.key_skills = vacancy.key_skills[:100] + "..."
            if len(vacancy.description) > 100:
                vacancy.description = vacancy.description[:100] + "..."

            cropped_set.append(vacancy)


        vac_table = PrettyTable(list_titles)

        # Внешний вид таблицы
        for title in list_titles:
            vac_table._max_width[title] = 20
        vac_table.hrules = ALL
        vac_table.align = "l"
        #

        counter = 1
        for e_dict in cropped_set:
            row = [counter]
            row.extend(e_dict.get_values())
            vac_table.add_row(row)
            counter += 1

        print(vac_table.get_string(start=numbers_row[0] - 1, end=numbers_row[1] - 1, fields=titles_table))

    def parserData(self, count):
        if len(self.numbers_row_inp) == 0:
            return [1, count + 1]
        result = self.numbers_row_inp.split()
        if len(result) < 2:
            result.append(count + 1)
        for e in range(0, len(result), 1):
            result[e] = int(result[e])
        return result

    def parserTitles(self):
        if len(self.titles_table_inp) == 0:
            return l_titles
        result = self.titles_table_inp.split(", ")
        result.insert(0, "№")
        return result

class Report(object):
    def __init__(self, vacancy_name: str):
        self.vacancy_name = vacancy_name

    def generate_excel(self, a, b, c, d, e, f):

        file = pxl.Workbook()
        list_t = file.active
        list_t.title = 'Статистика по годам'

        self.fillColumn(list_t, list(a.keys()), 'Год', 'A1')
        self.fillColumn(list_t, list(a.values()), 'Средняя зарплата', 'B1')
        self.fillColumn(list_t, list(c.values()), 'Средняя зарплата - ' + self.vacancy_name, 'C1')
        self.fillColumn(list_t, list(b.values()), 'Количество вакансий', 'D1')
        self.fillColumn(list_t, list(d.values()), 'Количество вакансий - ' + self.vacancy_name, 'E1')

        list_t2 = file.create_sheet('Статистика по городам')

        self.fillColumn(list_t2, list(e.keys()), 'Город', 'A1')
        self.fillColumn(list_t2, list(e.values()), 'Уровень зарпалт', 'B1')

        self.fillColumn(list_t2, list(e.keys()), 'Город', 'D1')
        self.fillColumn(list_t2, list(f.values()), 'Доля вакансий', 'E1')

        file.save('result_file.xlsx')

    def fillColumn(self, list_t, values, title: str, cell: str):

        list_t[cell] = title

        list_t[cell].font = Font(bold = True)

        brd = Side(border_style='thin', color='000000')

        list_t[cell].border = Border(top=brd, bottom=brd, right=brd, left=brd)

        letter = cell[0:1]
        number = int(cell[1:])


        max_len = len(title)
        for i in range(0, len(values), 1):
            if len(str(values[i])) > max_len:
                max_len = len(str(values[i]))
            list_t[letter + str(number + 1 + i)] = values[i]
            list_t[letter + str(number + 1 + i)].border = Border(top=brd, bottom=brd, right=brd, left=brd)

        list_t.column_dimensions[letter].width = max_len * 1.3

    def generate_image(self, a, b, c, d, e, f, name):
        fig = plt.figure(figsize=(18, 10))
        plt.rcParams['font.size'] = '8'

        width = 0.4
        offset = width / 2
        dots_year = np.arange(len(a.keys()))

        ax1 = fig.add_subplot(221)

        ax1.bar(dots_year - offset, a.values(), width, label='средняя з/п')
        ax1.bar(dots_year + offset, c.values(), width, label=f'з/п {name}')

        ax1.set_title('Уровень зарплат по годам')
        ax1.set_xticks(dots_year)
        ax1.set_xticklabels(list(c.keys()))
        ax1.legend()

        ax2 = fig.add_subplot(222)

        ax2.bar(dots_year - offset, list(b.values()), width, label='Количество вакансий')
        ax2.bar(dots_year + offset, list(d.values()), width, label=f'Количество вакансий\n{name}')

        ax2.set_title('Количество вакансий по годам')
        ax2.set_xticks(dots_year)
        ax2.set_xticklabels(list(c.keys()))
        ax2.legend()
        ax2.grid(axis='y')

        dots_area = np.arange(len(e.keys()))

        ax3 = fig.add_subplot(223)

        values = list(e.values())
        values.reverse()
        keys = list(e.keys())
        keys.reverse()

        ax3.barh(dots_area - offset, values, width + offset)
        ax3.set_title('Уровень зарплат по годам')
        ax3.set_yticks(dots_area)
        ax3.set_yticklabels(keys)
        ax3.grid(axis='x')

        ax4 = fig.add_subplot(224)

        values = list(f.values())
        keys = list(f.keys())

        ax4.pie(values, labels=keys)
        ax4.set_title('Доля вакансий по городам')
        ax4.axis("equal")

        fig.savefig('graph.png')

    def generate_pdf(self, year_salary, year_salary_vac, year_count, year_count_vac, area_salary_cut, area_peace_cut):
        name = user_input.filter_data
        stat_years = []
        for i in range(0, len(year_salary), 1):
            an_item = dict(date=list(year_salary.keys())[i],
                           salary=list(year_salary.values())[i],
                           salary_name=list(year_salary_vac.values())[i],
                           count=list(year_count.values())[i],
                           count_name=list(year_count_vac.values())[i])
            stat_years.append(an_item)

        stat_area_salary = []
        for i in range(0, len(area_salary_cut), 1):
            an_item = dict(area=list(area_salary_cut.keys())[i],
                           salary=list(area_salary_cut.values())[i])
            stat_area_salary.append(an_item)

        stat_area_peace = []
        for i in range(0, len(area_peace_cut), 1):
            an_item = dict(area=list(area_peace_cut.keys())[i],
                           peace=list(area_peace_cut.values())[i])
            stat_area_peace.append(an_item)

        titles = []

        titles.append(['Год', 'Средняя зарплата', f'Средняя зарплата - {name}', 'Количество вакансий',
                       f'Количество вакансий - {name}'])
        titles.append(['Город', 'Уровень зарплат'])
        titles.append(['Город', 'Доля вакансий'])

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("pdf_template.html")

        pdf_template = template.render({'name': name,
                                        'stat_years': stat_years,
                                        'titles': titles,
                                        'stat_area_salary': stat_area_salary,
                                        'stat_area_peace': stat_area_peace})

        config = pdfkit.configuration(
            wkhtmltopdf=r'C:\Users\Пользователь\PycharmProjects\3\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options={'enable-local-file-access': None})

def cut_sort_dict(dic, num1, num2):
    new_dic = list(dic.items())
    new_dic.sort(key=lambda x: x[1], reverse=True)
    if num2 == 0:
        new_dic = new_dic[num1:]
    else:
        new_dic = new_dic[num1:num2]
    return dict(new_dic)

def get_other_peace(dic):

    other = dict((list(dic.items()))[10:])
    sum = 0
    for e in other:
        sum += other[e]
    other = dict((list(dic.items()))[:9])
    other['Другие'] = sum
    return other



# Основной код

# Ввод и обработка некорректных данных
user_input = InputConnect()
user_input.input_processing()
user_input.validate()

# Делаем

data_set = DataSet(user_input.file_name)
data_set.reader_filer()


if user_input.method == 'Статистика':

    data_set.filter(user_input.filter_data)


    year_salary = data_set.get_salary_level(data_set.vacancies_objects, 'published_at')
    year_count = data_set.num_vac(data_set.vacancies_objects)
    if len(data_set.filter_vac_obj) == 0:
        year_salary_vac = {}
        for key in year_count:
            year_salary_vac[key] = 0
        year_count_vac = year_salary_vac
    else:
        year_salary_vac = data_set.get_salary_level(data_set.filter_vac_obj, 'published_at')
        year_count_vac = data_set.num_vac(data_set.filter_vac_obj)


    area_salary = data_set.get_salary_level(data_set.vacancies_objects, "area_name")
    area_salary_cut = cut_sort_dict(area_salary, 0, 10)


    area_peace = data_set.vac_rate(data_set.clust(data_set.vacancies_objects, "area_name"))
    area_peace_cut = cut_sort_dict(area_peace, 0, 10)

    area_peace_oth = cut_sort_dict(area_peace, 0, 0)
    area_peace_oth = get_other_peace(area_peace_oth)


    report = Report(user_input.filter_data)
    '''report.generate_excel(year_salary, year_count, year_salary_vac, year_count_vac, area_salary_cut, area_peace_cut)'''

    '''report.generate_image(year_salary, year_count, year_salary_vac, year_count_vac, area_salary_cut, area_peace_oth, user_input.filter_data)'''
    report.generate_pdf(year_salary, year_salary_vac, year_count, year_count_vac, area_salary_cut, area_peace_cut)

    user_input.print(year_salary, year_count, year_salary_vac, year_count_vac, area_salary_cut, area_peace_cut)

else:
    data_set.filter_tb(user_input.filter_data_tb)
    data_set.sorter(user_input.sort_rev, user_input.sort_data)
    data_set.formated()

    titles_table = user_input.parserTitles()

    numbers_row = user_input.parserData(len(data_set.vacancies_objects))  # обрезка

    user_input.print_table(data_set, numbers_row, titles_table)









