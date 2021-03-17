import pandas


def custom_df():
    data = {"indice_tiempo": ["2020-12-01", "2021-01-01"],
            "tipo_cambio_bna_vendedor": [100, 110]}

    df = pandas.DataFrame(data, columns = ["indice_tiempo", "tipo_cambio_bna_vendedor"])
    return df
