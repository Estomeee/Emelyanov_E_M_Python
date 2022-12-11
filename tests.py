import unittest
import main
from test_for_test import calc1

dic_vacancy = {
                'name': 'Название',
                'description': 'Описание',
                'key_skills': 'Навыки',
                'experience_id': 'between3And6',
                'premium': 'False',
                'employer_name': 'Компания',
                'salary_from': '100',
                'salary_to': '200',
                'salary_gross': 'False',
                'salary_currency': 'RUR',
                'area_name': 'Название региона',
                'published_at': '2022-07-05T18:21:28+0300'}

vacancy = main.Vacancy(dic_vacancy)

vacancy_values = ['Название', 'Описание', 'Навыки', 'between3And6', 'False', 'Компания', 150, 'Название региона', '2022-07-05T18:21:28+0300']

dataset = main.DataSet('test_vac.csv', "Вакансии")
dataset.reader_filer()


class MyTestCase(unittest.TestCase):

    def test_salary_avg(self):
        self.assertEqual(main.Salary("100", "200", "RUR", "False").salary_avg, 150)
        self.assertEqual(main.Salary("100.0", "200.0", "RUR", "False").salary_avg, 150)
        self.assertEqual(main.Salary("100", "200", "EUR", "False").salary_avg, 8985)
    def test_salary_from(self):
        self.assertEqual(main.Salary("100", "200", "RUR", "False").salary_from, "100")
    def test_salary_to(self):
        self.assertEqual(main.Salary("100", "200", "RUR", "False").salary_to, "200")
    def test_salary_gross(self):
        self.assertEqual(main.Salary("100", "200", "RUR", "False").salary_gross, "False")
    def test_salary_cur(self):
        self.assertEqual(main.Salary("100", "200", "RUR", "False").salary_currency, "RUR")

    def test_vacancy_get_valuse(self):
        self.assertEqual(main.Vacancy(dic_vacancy).get_values(), vacancy_values)
    def test_vacancy_request(self):
        self.assertEqual(main.Vacancy(dic_vacancy).request_by_str('name'), "Название")
        self.assertEqual(main.Vacancy(dic_vacancy).request_by_str('salary').salary_avg, 150)
        self.assertEqual(main.Vacancy(dic_vacancy).request_by_str('published_at'), 2022)
        self.assertEqual(main.Vacancy(dic_vacancy).request_by_str('salary_currency'), "Рубли")

    def test_data_set(self):
        self.assertEqual(main.DataSet('test_vac.csv', "Вакансии").file_name, "test_vac.csv")

    def test_data_set_filer_reader(self):
        self.assertEqual(len(main.DataSet("test_vac.csv", "Вакансии").reader_filer()), 5)
        self.assertEqual(main.DataSet("test_vac.csv", "Вакансии").reader_filer()[0].request_by_str('name'), 'Название1')

    def test_data_set_filter(self):

        test_value = ["Название: Название1", "Оклад: 150"]
        test_len = ["Название: Название1",
                    "Оклад указан до вычета налогов: Нет",
                    "Идентификатор валюты оклада: Рубли",
                    "Название региона: Новосибирск",
                    "Компания: Компания1",
                    "Премиум-вакансия: Нет",
                    "Опыт работы: От 3 до 6 лет",
                    "Навыки: Навык2",
                    "Оклад: 150"
                    ]

        dataset = main.DataSet('test_vac.csv', "Вакансии")
        dataset.reader_filer()
        self.assertEqual(dataset.filter("Оклад: 150")[0].request_by_str('salary').salary_avg, 150)

        for e in test_value:
            dataset = main.DataSet('test_vac.csv', "Вакансии")
            dataset.reader_filer()
            self.assertEqual(dataset.filter(e)[0].request_by_str('name'), 'Название1')

        for el in test_len:
            dataset = main.DataSet('test_vac.csv', "Вакансии")
            dataset.reader_filer()
            self.assertEqual(len(dataset.filter(el)), 4)

    def test_data_set_sorter(self):

        test_value = ["Название",
                      "Название региона",
                      "Компания",
                      "Премиум-вакансия",
                      "Опыт работы",
                      "Навыки",
                      "Оклад"
                      ]

        dataset = main.DataSet('test_vac_sort.csv', "Вакансии")
        dataset.reader_filer()
        self.assertEqual(dataset.sorter("Да", "Название")[0].request_by_str('name'), 'Название5')

        for e in test_value:
            dataset = main.DataSet('test_vac_sort.csv', "Вакансии")
            dataset.reader_filer()
            self.assertEqual(dataset.sorter("Да", e)[0].request_by_str('name'), 'Название5')


if __name__ == '__main__':
    unittest.main()
