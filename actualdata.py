# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import pandas
import urllib
import matplotlib
import futuredata


def get_api_call(ids, frequency="month", **kwargs):
    # the base of the url
    API_BASE_URL = "https://apis.datos.gob.ar/series/api/"
    # create a single string with all the identifiers
    kwargs["ids"] = ",".join(ids)
    # return the url
    return "{}{}?{}&{}".format(API_BASE_URL, "series", urllib.parse.urlencode(kwargs), "collapse=" + frequency)


def actual_data_test():
    # read_csv returns a dataframe object (a table with comma separated values)
    df = pandas.read_csv(get_api_call(
        ["168.1_T_CAMBIOR_D_0_0_26"],
        format="csv", start_date=2018
    ))

    print(df)

    df.plot(x='indice_tiempo', y='tipo_cambio_bna_vendedor', kind='line')
    matplotlib.pyplot.show()

    del df


def test():
    test = Test()
    return test

class Test:
    a = 10

if __name__ == '__main__':
    # actual_data_test()
    futuredata.setup_economy()
    futuredata.manage_economy()

