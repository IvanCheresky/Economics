import pandas


def custom_df():
    data = {"indice_tiempo": ["2020-12-01", "2021-01-01"],
            "tipo_cambio_bna_vendedor": [100, 110]}

    df = pandas.DataFrame(data, columns = ["indice_tiempo", "tipo_cambio_bna_vendedor"])
    return df


class BasicConsumptionSavingHeuristicBehaviour:

    percent_consumed = 100

    def __init__(self, percent_consumed):
        self.percent_consumed = percent_consumed


class UtilityMaximizationConsumption:
    pass


class Consumer:
    # how he decides how much to consume and save
    consumption_saving_behaviour = None
    # how he decides what to buy
    consumption_behaviour = None
    # skill, average = 1, to be set as a random distribution?
    skill = 1;
    employed = False

    def __init__(self, consumption_saving_behaviour, consumption_behaviour, skill, employed):
        self.consumption_saving_behaviour = consumption_saving_behaviour
        self.consumption_behaviour = consumption_behaviour
        self.skill = skill
        self.employed = employed


class LeontiefProductionFunction:
    def produce(self, firm_workers, domestic_capital, foreign_capital):
        return min(firm_workers.count(), domestic_capital + foreign_capital)


class Industry:
    name = ""
    industry_firms = []

    def __init__(self, name, industry_firms):
        self.name = name
        self.industry_firms = industry_firms


class Firm:
    # stock of the good it produces
    stock = 0
    # list of capital of which the firm disposes
    domestic_capital = 0
    foreign_capital = 0
    # list of workers of which the firm disposes
    firm_workers = []
    # amount of money
    cash = 0
    # type of production function
    production_function = None

    def __init__(self, stock, capital, firm_workers, cash, production_function):
        self.stock = stock
        self.capital = capital
        self.firm_workers = firm_workers
        self.cash = cash
        self.production_function = production_function

    def produce(self):
        self.stock += self.production_function.produce(self.firm_workers, self.domestic_capital, self.foreign_capital)


# variables that characterize the economy
# list of industries
industries = []
# list of workers
workers = []


def setup_economy():
    create_workers()
    create_industries()


def create_workers():
    global workers
    workers.append(Consumer(BasicConsumptionSavingHeuristicBehaviour(90), UtilityMaximizationConsumption(), 1, True))


def create_industries():
    agriculture = Industry("Agriculture", create_firms())
    industries.append(agriculture)

    food_industry = Industry("Food Industry", create_firms())
    industries.append(food_industry)

    other_manufactures = Industry("Other Manufactures", create_firms())
    industries.append(other_manufactures)

    commerce = Industry("Commerce", create_firms())
    industries.append(commerce)

    transportation = Industry("Transportation", create_firms())
    industries.append(transportation)

    construction = Industry("Construction", create_firms())
    industries.append(construction)

    services = Industry("Services", create_firms())
    industries.append(services)


def create_firms():
    firms = []

    for i in range(0, 10):
        firms.append(Firm(0, 100, workers, 0, LeontiefProductionFunction()))

    return firms

def manage_economy():
    pass
