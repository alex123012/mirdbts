import pandas as pd
import requests
from bs4 import BeautifulSoup as bs


class CustomMiRDB:

    url = 'http://mirdb.org/cgi-bin/custom.cgi'

    def __init__(self, sequence=None, type_='miRNA', species='hsa'):

        if 'mirna' in type_.lower():
            self.type_ = 'miRNA'
            self.sequence = sequence.upper()

        elif 'mrna' in type_.lower():
            self.type_ = 'mRNATarget'
            self.sequence = sequence.upper() + 'a'

        self.species = species.lower()

        self.__startsession()

    def __filefind(self, temp):

        soup = bs(temp.text, "html.parser")
        table = soup.findAll("input")
        return table[0]['value']

    def __startsession(self):

        self.session = requests.Session()

        data = {'searchSpecies': self.species,
                'subChoice': self.type_,
                'customSub': self.sequence,
                '.submit': 'Go'}
        temp = self.session.post(self.url, data=data)

        self.filename = self.__filefind(temp)

        data = {'.submit': 'Retrieve Prediction Result',
                'fileName': self.filename}
        self.responce = self.session.post(self.url, data=data)

        data = {".submit": "Return to Custom Prediction"}
        self.session.post(self.url, data=data)

    def __repr__(self):
        return self.responce.text

    def __str__(self):
        return self.responce.text


class Mirdb(pd.DataFrame):
    def __init__(self, html, html_dict=None):

        __rows, __headers = self.__get_table_rows(html, html_dict)

        super().__init__(__rows, columns=__headers)
        try:
            self.set_index('Target Rank', inplace=True)
            self.drop(['Target Detail', 'miRNA Name', 'Gene Description'],
                      axis=1, inplace=True)
        except KeyError:
            pass

    def __get_table_rows(self, html, html_dict):

        """Given a url, returns all its table rows and headers"""

        if not html_dict:
            html_dict = {'border': "1", 'id': "table1",
                         'style': "border-collapse: collapse"}

        soup = bs(str(html), "html.parser")
        table = soup.findAll("table", html_dict)[0]

        rows = list(map(self.__get_row, table.find_all("tr")))

        rows, headers = rows[1:], rows[0]
        return rows, headers

    def __get_row(self, tr):
        return list(map(self.__get_cell, tr.find_all("td")))

    def __get_cell(self, td):

        res = td.text.strip()

        # Если в датафрем нужны ссылки на детали
        # по каждой микроРНК - можно раскомментить

        # x = td.select_one('a')
        # if x and x['href'].startswith('/'):
        #     return f'<a target="_blank" href="http://mirdb.org{x['href']}">{res}</a>'
        # elif x and x['href'].startswith('http'):
        #     return f'<a target="_blank" href="{x['href']}">{res}</a>'

        return res
