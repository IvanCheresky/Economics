import math

import pandas
import multipledispatch

# create a dataframe with the data created
def custom_df():
    data = {"indice_tiempo": ["2020-12-01", "2021-01-01"],
            "tipo_cambio_bna_vendedor": [100, 110]}

    df = pandas.DataFrame(data, columns = ["indice_tiempo", "tipo_cambio_bna_vendedor"])
    return df


# a behaviour for the consumption/saving decision
class BasicConsumptionSavingHeuristicBehaviour:

    percent_consumed = 100

    def __init__(self, percent_consumed):
        self.percent_consumed = percent_consumed

    def amount_to_consume(self, income):
        return income*self.percent_consumed


# a behaviour on how to spend the money set for consumption
class UtilityMaximizationConsumption:

    def consume(self, consumer, amount_to_consume):
        pass


# a behaviour on how to spend the money set for consumption
# requires agricultural sector
class MinFoodFixedProportionsConsumption:

    agriculture = None

    def __init__(self):
        global industries

        for i in industries:
            if i.name == "agriculture":
                self.agriculture = i

    def consume(self, consumer, amount_to_consume):
        if self.agriculture.get_cheapest_firm.price*30 >= amount_to_consume:
            pass
        else:
            pass


class Consumer:
    # how he decides how much to consume and save
    consumption_saving_behaviour = None
    # how he decides what to buy
    consumption_behaviour = None
    # skill, average = 1, to be set as a random distribution?
    skill = 1;
    employed = False
    wealth = 100

    def __init__(self, consumption_saving_behaviour, consumption_behaviour, skill, employed):
        self.consumption_saving_behaviour = consumption_saving_behaviour
        self.consumption_behaviour = consumption_behaviour
        self.skill = skill
        self.employed = employed

    def consume(self):
        amount_to_consume = self.consumption_saving_behaviour.amount_to_consume()
        self.consumption_behaviour.consume(self, amount_to_consume)


class LeontiefProductionFunction:
    def produce(self, firm_workers, domestic_capital, foreign_capital):
        return min(firm_workers.count(), domestic_capital + foreign_capital)


class Industry:
    name = ""
    industry_firms = []

    # maybe have a min, average and max price stored for use in functions
    price = 1

    def __init__(self, name, industry_firms):
        self.name = name
        self.industry_firms = industry_firms

    def get_cheapest_firm(self):
        pass

    def is_stock_sero(self):
        pass


class Firm:
    # stock of the good it produces
    stock = 100
    # list of capital of which the firm disposes
    domestic_capital = 100
    foreign_capital = 100
    # list of workers of which the firm disposes
    firm_workers = []
    # amount of money
    cash = 100
    # type of production function
    production_function = None
    # price of the good it produces
    price = 1

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


# setup multidispatch for when there are multiple ways to set up the economy
@multipledispatch.dispatch()
def setup_economy():
    create_workers()
    create_industries()


# setup multidispatch for when there are multiple ways to set up the economy
@multipledispatch.dispatch(object)
def setup_economy():
    pass


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
    for industry in industries:
        for firm in industry.industry_firms:
            firm.produce()

    for consumer in workers:
        consumer.consume()


# function to log the results of each week
def log():
    pass


# UTLITY METHODS
def handle_transaction(consumer, industry, amount):

    if industry.is_stock_zero:
        return

    firm = industry.get_cheapest_firm()

    if firm.price > amount:
        return

    if math.floor(amount / firm.price) > firm.stock:
        consumer.wealth -= firm.stock*firm.price
        remaining_amount = amount - firm.stock*firm.price
        firm.stock = 0
        handle_transaction(consumer, industry, remaining_amount)
        return

    consumer.wealth -= amount
    firm.stock = firm.stock - amount/firm.price



