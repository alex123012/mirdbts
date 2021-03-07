"""
Python module for miRDB data parsing

Use this module for parse html to BeautifulSoup bs4 or
to pandas DataFrame from mirdb.org miRNA/targets predictions.
Requirements: pandas, requests, time, bs4.
"""

import pandas as pd
import requests
import time
from bs4 import BeautifulSoup as bs


class DefaultSearch:

    """
    Target search parser from mirdb.org.

    instance representing html text from site search responce
    default url for parse: http://mirdb.org/cgi-bin/search.cgi, attribute 'url'
    responce info is in atrribute 'responce'.

    Parametrs
    ---------
    searchBox : string
        Full miRNA name (if searchType is 'mirna')
        or gene symbol, GenBank, NCBI Gene Id (if searchType is 'gene').

    searchType : string, 'miRNA' or 'gene', default 'miRNA'
        Type of searchBox name string.
    species : string, 'Human', 'Mouse', 'Rat', 'Dog', 'Chicken', default Human
        Name of species for search in.
    geneChoice : string, 'symbol', 'geneID', 'accession', default 'symbol'
        Only valid if searchType is 'gene'.
        Type of gene name: Gene symbol ('symbol'),
                           GenBank Accession('accession'),
                           NCBI Gene Id('geneID').
    """

    url = 'http://mirdb.org/cgi-bin/search.cgi'

    def __init__(self, searchBox=None, searchType='miRNA',
                 species='Human', geneChoice='symbol'):
        self.searchBox = searchBox
        self.searchType = searchType
        self.species = species
        self.geneChoice = geneChoice
        self.__startsession()

    def __startsession(self):
        session = requests.Session()

        data = {'searchBox': self.searchBox,
                'searchType': self.searchType,
                'species': self.species,
                'submitButton': 'Go'}

        if self.searchType == 'gene':
            data['geneChoice'] = self.geneChoice
        self.__responce = session.post(self.url, data=data)

    def __repr__(self):
        return self.responce.text

    def __str__(self):
        return self.responce.text

    responce = property(doc="search responce (<class 'requests.models.Response'>)")
    searchType = property(doc='Type of searchBox string')
    species = property(doc='Name of species for search in')
    geneChoice = property(doc='Type of gene name')

    @responce.getter
    def responce(self):
        return self.__responce

    @searchType.getter
    def searchType(self):
        return self.__searchType

    @species.getter
    def species(self):
        return self.__species

    @geneChoice.getter
    def geneChoice(self):
        return self.__geneChoice

    @searchType.setter
    def searchType(self, x):
        if 'mirna' in x.lower():
            self.__searchType = 'miRNA'
        elif 'gene' in x.lower():
            self.__searchType = 'gene'
        else:
            raise KeyError("Choose between 'miRNA' or 'gene'\
 and enter it properly")

    @species.setter
    def species(self, x):
        x = x.lower().capitalize()
        if x in ['Human', 'Mouse', 'Rat', 'Dog', 'Chicken']:
            self.__species = x
        else:
            raise KeyError("Choose between 'Human', 'Mouse', 'Rat', 'Dog',\
 'Chicken' and enter it properly")

    @geneChoice.setter
    def geneChoice(self, x):
        if x in ['symbol', 'geneID', 'accession']:
            self.__geneChoice = x
        else:
            raise KeyError("Choose between 'symbol', 'geneID', 'accession'\
 and enter it properly")


class CustomSearch:

    """
    Custom search parser from mirdb.org.

    instance representing html text from site search responce
    default url for parse: http://mirdb.org/cgi-bin/custom.cgi, attribute 'url'
    responce info is in atrribute 'responce'.

    Parametrs
    ---------
    customSub : string
        Full miRNA sequence (if subChoice is 'miRNA')
        or target gene sequence (if subChoice is 'mRNATarget').

    subChoice : string, 'miRNA' or 'mRNATarget', default 'miRNA'
        Type of customSub sequence string.
    species : string, 'hsa', 'mmu', 'rno', 'cfa', 'gga', default 'hsa'
        Name of species for search in.
    """

    url = 'http://mirdb.org/cgi-bin/custom.cgi'

    def __init__(self, customSub=None, subChoice='miRNA', species='hsa'):

        self.customSub = customSub.upper()
        self.subChoice = subChoice
        self.species = species

        self.__startsession()

    def __filefind(self, temp):

        soup = bs(temp.text, "html.parser")
        return soup.findAll("input", {'name': 'fileName'})[0]['value']

    def __startsession(self):

        self.session = requests.Session()

        data = {'searchSpecies': self.species,
                'subChoice': self.subChoice,
                'customSub': self.customSub,
                '.submit': 'Go'}
        temp = self.session.post(self.url, data=data)

        self.filename = self.__filefind(temp)

        data = {'.submit': 'Retrieve Prediction Result',
                'fileName': self.filename}
        self.__responce = self.session.post(self.url, data=data)

        data = {".submit": "Return to Custom Prediction"}
        self.session.post('http://mirdb.org/custom.html', data=data)

    def __repr__(self):
        return self.responce.text

    def __str__(self):
        return self.responce.text

    responce = property(doc="search responce (<class 'requests.models.Response'>)")
    subChoice = property(doc='Type of customSub sequence string')
    species = property(doc='Name of species for search in')

    @responce.getter
    def responce(self):
        return self.__responce

    @subChoice.getter
    def subChoice(self):
        return self.__subChoice

    @species.getter
    def species(self):
        return self.__species

    @subChoice.setter
    def subChoice(self, x):
        x = x.lower()
        if 'mirna' in x:
            self.__subChoice = 'miRNA'
        elif 'mrna' in x:
            self.__subChoice = 'mRNATarget'
        else:
            raise KeyError("Enter something that contains 'mirna' or 'mrna'")

    @species.setter
    def species(self, x):
        x = x.lower()
        if x in ['hsa', 'mmu', 'rno', 'cfa', 'gga']:
            self.__species = x
        else:
            raise KeyError("""Choose between 'hsa', 'mmu', 'rno', 'cfa', 'gga'
('Human', 'Mouse', 'Rat', 'Dog', 'Chicken') and enter it properly""")


class Mirdb(pd.DataFrame):

    """
    Data structure (pandas.DataFrame) created from mirdb.org
    prediction pages html text. Use like pandas.DataFrame.

    Parametrs
    ---------
    input : string created from html text
        html text from mirdb.org prediction pages received
        with CustomSearch, DefaultSearch or another tool.

    mirna_search : bool, defaul True
        if searching miRNA enter True (default) to drop not valid columns
        if searching gene targets enter False to
        not drop valid columns.
    detail_link : bool, default False
        If True, create html links to details from mirdb.org.
    html_style_dict : dict-like object, default None
        if searching another tables (not predictions)
        give valid css style in dict format for
        html table block to more accurate search.

    See Also
    --------
    pandas.DataFrame - Two-dimensional, size-mutable,
    potentially heterogeneous tabular data.
    """

    def __init__(self, html, mirna_search=True, detail_link=False,
                 html_style_dict=None, *args, **kwargs):

        __rows, __headers = self.__get_table_rows(html, html_style_dict,
                                                  detail_link)

        super().__init__(__rows, columns=__headers, *args, **kwargs)
        try:
            self.set_index('Target Rank', inplace=True)
            if mirna_search:
                self.drop(['Target Detail', 'miRNA Name', 'Gene Description'],
                          axis=1, inplace=True)
        except KeyError:
            pass

    def __get_table_rows(self, html, html_style_dict, detail_link,):

        """Given a url, returns all its table rows and headers"""

        if not html_style_dict:
            html_style_dict = {'border': "1", 'id': "table1",
                               'style': "border-collapse: collapse"}

        soup = bs(str(html), "html.parser")
        table = soup.findAll("table", html_style_dict)[0]

        rows = list(map(lambda x: self.__get_row(x, detail_link),
                        table.find_all("tr")))

        rows, headers = rows[1:], rows[0]
        return rows, headers

    def __get_row(self, tr, detail_link):
        return list(map(lambda x: self.__get_cell(x, detail_link),
                        tr.find_all("td"),))

    def __get_cell(self, td, detail_link):

        res = td.text.strip()

        # Если в датафрем нужны ссылки на детали
        if detail_link:
            x = td.select_one('a')
            if x and x['href'].startswith('/'):
                return f'<a target="_blank" href="http://mirdb.org{x["href"]}">{res}</a>'
            elif x and x['href'].startswith('http'):
                return f'<a target="_blank" href="{x["href"]}">{res}</a>'

        return res
