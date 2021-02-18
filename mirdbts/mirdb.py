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
        dictir = {'searchSpecies': self.species,
                  'subChoice': self.type_,
                  'customSub': self.sequence,
                  '.submit': 'Go'}
        temp = self.session.post(self.url, data=dictir)

        self.filename = self.__filefind(temp)

        dictir = {'.submit': 'Retrieve Prediction Result',
                  'fileName': self.filename}
        self.responce = self.session.post(self.url, data=dictir)
        self.session.post(self.url,
                          data={".submit": "Return to Custom Prediction"})

    def __repr__(self):
        return self.responce.text

    def __str__(self):
        return self.responce.text


class Mirdb(pd.DataFrame):
    def __init__(self, html, dictir=None):
        __rows, __headers = self.__get_table_rows(html, dictir)
        super().__init__(__rows, columns=__headers)
        try:
            self.set_index('Target Rank', inplace=True)
            self.drop(['Target Detail', 'miRNA Name', 'Gene Description'],
                      axis=1, inplace=True)
        except KeyError:
            print('lol')

    def __get_table_rows(self, html, dictir):

        """Given a url, returns all its table rows and headers"""

        if not dictir:
            dictir = {'border': "1", 'id': "table1",
                      'style': "border-collapse: collapse"}

        # использовать, если по url, а не по html
#         reques = requests.get(url)
#         print(reques)
#         html = url.text

        soup = bs(str(html), "html.parser")
        table = soup.findAll("table", dictir)[0]

        rows = list(map(self.__get_row, table.find_all("tr")))

        rows, headers = rows[1:], rows[0]
        return rows, headers

    def __get_row(self, tr):
        return list(map(self.__get_cell, tr.find_all("td")))

    def __get_cell(self, td):

        res = td.text.strip()
        # x = td.select_one('a')

        # Если в датафрем нужны ссылки на детали
        # по каждой микроРНК - можно раскомментить
        # if x and x['href'].startswith('/'):
        #     return f'<a target="_blank" href="http://mirdb.org{x['href']}">{res}</a>'
        # elif x and x['href'].startswith('http'):
        #     return f'<a target="_blank" href="{x['href']}">{res}</a>'

        return res
