import math
import pandas
import multipledispatch
import random

# global variables
period = 0


# create a dataframe with the data created
def custom_df(data):
    df = pandas.DataFrame(data, columns=list(data.keys()))

    # print(df)

    # data = {"indice_tiempo": ["2020-12-01", "2021-01-01"],
    #         "tipo_cambio_bna_vendedor": [100, 110]}
    #
    # df = pandas.DataFrame(data, columns=["indice_tiempo", "tipo_cambio_bna_vendedor"])
    return df


# a behaviour for the consumption/saving decision
class BasicConsumptionSavingHeuristicBehaviour:

    percent_consumed = 1

    def __init__(self, percent_consumed):
        self.percent_consumed = percent_consumed

    def amount_to_consume(self, income):
        return income*self.percent_consumed


# a behaviour for the consumption/saving decision
class ConsumptionSavingDesiredWealthLevelBehaviour:
    pass


# a behaviour on how to spend the money set for consumption
class UtilityMaximizationConsumption:

    def consume(self, consumer, amount_to_consume):
        pass


# a behaviour on how to spend the money set for consumption
# requires agricultural sector
class MinFoodFixedProportionsConsumption:

    agriculture = None
    global industries

    def consume(self, consumer, amount_to_consume):

        # if the agriculture industry is not in the variable, get it
        if self.agriculture is None:
            self.agriculture = get_industry("Agriculture")

        # if no firm with stock is found, consume from non-agriculture industry (WRONG, CHANGE industries[1])
        if self.agriculture.get_cheapest_firm() is None:
            handle_consumer_transaction(consumer, industries[1],
                                        amount_to_consume)
            return

        # if the amount to spend is inferior to the min food to consume, spend all on food, CHANGE 30
        if self.agriculture.get_cheapest_firm().price*30 >= amount_to_consume:
            handle_consumer_transaction(consumer, self.agriculture, amount_to_consume)
        # if the amount to spend is superior to the min food to consume, spend the rest on other industries
        else:
            # this formula is wrong, it should spend the money necessary for 30 units, not assuming the 30 units
            # will have the cheapest price
            handle_consumer_transaction(consumer, self.agriculture, self.agriculture.get_cheapest_firm().price * 30)
            # this part should distribute the remaining consumption across industries instead of just one
            # WRONG should consume amount_to_consume - amount_already spent instead of subtracting a flat 30
            handle_consumer_transaction(consumer, industries[1],
                                        amount_to_consume - 30)


class Consumer:
    # identifier to keep track
    identifier = 0
    # how he decides how much to consume and save
    consumption_saving_behaviour = None
    # how he decides what to buy
    consumption_behaviour = None
    # skill, average = 1, to be set as a random distribution?
    skill = 1
    employed = False
    # keep a wealth and an income parameters?
    wealth = 100
    wage = 0
    other_income = 0
    # the minimum wage he will accept a job for
    reservation_wage = 40

    def __init__(self, identifier, consumption_saving_behaviour, consumption_behaviour, skill, employed):
        self.identifier = identifier
        self.consumption_saving_behaviour = consumption_saving_behaviour
        self.consumption_behaviour = consumption_behaviour
        self.skill = skill
        self.employed = employed

    def consume(self):
        amount_to_consume = self.consumption_saving_behaviour.amount_to_consume(self.wage + self.other_income)
        self.consumption_behaviour.consume(self, amount_to_consume)

    def update_reservation_wage(self):
        if not self.employed:
            # WRONG, check how this adjusts over time with reasonable values
            # wealth should be studied in relation to something else (ie the cost of food)
            # should also increase reservation wage if wealth increases
            self.reservation_wage = self.reservation_wage*(0.9**(1/self.wealth))

    def searching_job(self):
        return self.reservation_wage >= self.wage


class LeontiefProductionFunction:
    # WRONG, should be set on init and be different per industry
    worker_productivity = 50
    capital_productivity = 50

    def produce(self, firm_workers, domestic_capital, foreign_capital):
        return min(self.worker_productivity*len(firm_workers),
                   self.capital_productivity*(domestic_capital + foreign_capital))

    def required_workers(self, desired_production, domestic_capital, foreign_capital):
        return max(desired_production/self.worker_productivity,
                   self.capital_productivity*(domestic_capital + foreign_capital))


class DesiredStockFirmBehaviour:
    desired_stock = 0
    prod_adj_parameter = 0
    price_adj_parameter = 0

    def __init__(self, desired_stock, prod_adj_parameter, price_adj_parameter):
        self.desired_stock = desired_stock
        self.prod_adj_parameter = prod_adj_parameter
        self.price_adj_parameter = price_adj_parameter

    def get_price(self, price, stock):
        if stock == 0:
            return price * (1 + self.price_adj_parameter * 2)

        # the new price is the old price plus the percent over/under the desired stock (min 0.5, max 2)
        # multiplied by a parameter
        return price*(1 + self.price_adj_parameter*
                      clamp((self.desired_stock - stock)/stock, -0.5, 2))

    def get_quantity(self, quantity_sold, stock):
        # the new quantity is equal to the last quantity sold plus the excess/shortage of stock
        # multiplied by a parameter
        return max(0, quantity_sold + self.prod_adj_parameter*(self.desired_stock - stock))


class Industry:
    name = ""
    industry_firms = []

    # maybe have a min, average and max price stored for use in functions
    price = 1

    def __init__(self, name):
        self.name = name

    def add_firms(self, industry_firms):
        self.industry_firms = industry_firms

    def get_cheapest_firm(self):
        random.shuffle(self.industry_firms)
        cheapest_firm = None
        for firm in self.industry_firms:
            if firm.stock == 0:
                continue
            if cheapest_firm is None:
                cheapest_firm = firm
            elif cheapest_firm.price > firm.price:
                cheapest_firm = firm
        return cheapest_firm

    def is_stock_zero(self):
        total_stock = 0
        for firm in self.industry_firms:
            total_stock += firm.stock
        return total_stock == 0

    # called after a month runs in order to log the state of each industry
    def log(self):
        stock = 0
        domestic_capital = 0
        foreign_capital = 0
        firm_workers = 0
        cash = 0
        for firm in self.industry_firms:
            stock += firm.stock
            domestic_capital += firm.domestic_capital
            foreign_capital += firm.foreign_capital
            firm_workers += len(firm.firm_workers)
            cash += firm.cash

        log({
            self.name: (len(self.industry_firms), stock, domestic_capital, foreign_capital, firm_workers, cash)
        })


def get_industry(name):
    for i in industries:
        if i.name == name:
            return i

    return None


class Firm:
    # identifier to keep track
    identifier = 0
    # the industry where the firm operates
    industry = None
    # stock of the good it produces
    stock = 0
    # list of capital of which the firm disposes
    domestic_capital = 100
    foreign_capital = 100
    # list of workers of which the firm disposes
    firm_workers = []
    # amount of money
    cash = 100
    # type of production function
    production_function = None
    # how the firm decides the quantity and price of the period
    production_behaviour = None
    # price of the good it produces
    price = 1
    # wage of workers in the firm
    wage = 40
    # the quantity sold the last period
    quantity_sold = 0
    # the quantity the firm wants to produce
    desired_production = 0

    def __init__(self, identifier, industry, stock, domestic_capital, foreign_capital, firm_workers, cash,
                 production_function, production_behaviour):
        self.identifier = identifier
        self.industry = industry
        self.stock = stock
        self.domestic_capital = domestic_capital
        self.foreign_capital = foreign_capital
        self.firm_workers = firm_workers
        for worker in self.firm_workers:
            worker.employed = True
            worker.wage = self.wage
        self.cash = cash
        self.production_function = production_function
        self.production_behaviour = production_behaviour
        # quantity sold in the previous period arbitrarily set at 10, change?
        self.quantity_sold = 10

    def production_objective(self):
        self.desired_production = self.production_behaviour.get_quantity(self.quantity_sold, self.stock)

    # if the firm cannot produce as much as it wants due to a labor limitation, it might want to hire workers
    def should_enter_labor_market(self):
        pass

    # if the firm cannot produce as much as it wants due to a capital limitation, it might want to buy capital
    def should_enter_capital_market(self):
        pass

    def produce(self):
        self.price = self.production_behaviour.get_price(self.price, self.stock)

        # print("PERIOD " + str(period) + ": firm in industry " + self.industry.name +
        #       " sold " + str(self.quantity_sold) + " last period and has a stock of " +
        #       str(self.stock) + " while it wants a stock of 100")

        self.stock += math.floor(min(
            self.desired_production,
            self.production_function.produce(self.firm_workers, self.domestic_capital, self.foreign_capital)))

        # print("therefore it produces: " + str(math.floor(min(
        #     self.desired_production,
        #     self.production_function.produce(self.firm_workers, self.domestic_capital, self.foreign_capital)))))

        self.quantity_sold = 0

    # keep in firms? if here cannot have different wages per worker
    def pay_wages(self):
        for worker in self.firm_workers:
            worker.wage = self.wage
            worker.wealth += self.wage
            self.cash -= self.wage

    def fire(self):
        objective_qty_workers = self.production_function.required_workers(self.desired_production,
                                                                          self.domestic_capital,
                                                                          self.foreign_capital)

        while objective_qty_workers < len(self.firm_workers):
            if len(self.firm_workers) == 0:
                return
            else:
                worker = self.firm_workers.pop(0)
                worker.wage = 0
                worker.employed = False


    # hiring or not hiring should be a short term calculation based on short term production necesities
    def hire(self, searching_workers):
        objective_qty_workers = self.production_function.required_workers(self.desired_production,
                                                                          self.domestic_capital,
                                                                          self.foreign_capital)

        while objective_qty_workers > len(self.firm_workers) and len(searching_workers) > 0:
            new_worker = searching_workers.pop(0)
            self.firm_workers.append(new_worker)
            # WRONG, should receive a wage equal to his reservation wage, needs individual wages inside a firm
            new_worker.wage = self.wage
            new_worker.employed = True



# variables that characterize the economy
# list of industries
industries = []
# list of workers
consumers = []


# setup multidispatch for when there are multiple ways to set up the economy
@multipledispatch.dispatch()
def setup_economy():
    create_consumers()
    create_industries()


# setup multidispatch for when there are multiple ways to set up the economy
@multipledispatch.dispatch(object)
def setup_economy(data):
    pass


consumer_identifier = 0


# initialize consumers
def create_consumers():
    global consumers
    global consumer_identifier
    for i in range(0, 1000):
        consumers.append(Consumer(consumer_identifier,BasicConsumptionSavingHeuristicBehaviour(0.9),
                                  MinFoodFixedProportionsConsumption(), 1, False))
        consumer_identifier += 1


# initialize industries
def create_industries():
    agriculture = Industry("Agriculture")
    agriculture.add_firms(create_firms(agriculture))
    industries.append(agriculture)

    food_industry = Industry("Food Industry")
    food_industry.add_firms(create_firms(food_industry))
    industries.append(food_industry)

    other_manufactures = Industry("Other Manufactures")
    other_manufactures.add_firms(create_firms(other_manufactures))
    industries.append(other_manufactures)

    commerce = Industry("Commerce")
    commerce.add_firms(create_firms(commerce))
    industries.append(commerce)

    transportation = Industry("Transportation")
    transportation.add_firms(create_firms(transportation))
    industries.append(transportation)

    construction = Industry("Construction")
    construction.add_firms(create_firms(construction))
    industries.append(construction)

    services = Industry("Services")
    services.add_firms(create_firms(services))
    industries.append(services)


def get_random_unemployed(quantity):
    workers = []
    i = 0
    for worker in consumers:
        if not worker.employed:
            workers.append(worker)
            i += 1
            if i >= quantity:
                return workers

    return workers


firm_identifier = 0


def create_firms(industry):
    firms = []
    global firm_identifier
    for i in range(0, 10):
        # this is wrong: as it stands, each firm has all consumers as workers
        firms.append(Firm(firm_identifier, industry, 100, 100, 100, get_random_unemployed(10), 100,
                          LeontiefProductionFunction(), DesiredStockFirmBehaviour(100, 1, 0.1)))
        firm_identifier += 1
    return firms


def manage_economy(periods):

    dict_of_dataframes = {}
    seeking_workers = []

    for i in range(0, periods):
        global period
        global data

        seeking_workers.clear()

        # 1) industries estimate desired production
        # 2) industries fire excess workers
        for industry in industries:
            for firm in industry.industry_firms:
                firm.production_objective()
                firm.fire()

        # 3) consumers decide if they are looking for a job
        for consumer in consumers:
            if consumer.searching_job():
                seeking_workers.append(consumer)

        seeking_workers = sorted(seeking_workers, key=lambda x: x.reservation_wage)

        # 4) industries hire required workers
        random.shuffle(industries)
        for industry in industries:
            random.shuffle(industry.industry_firms)
            for firm in industry.industry_firms:
                firm.hire(seeking_workers)

        # 5) industries produce and pay wages
        random.shuffle(industries)
        for industry in industries:
            random.shuffle(industry.industry_firms)
            for firm in industry.industry_firms:
                firm.produce()
                firm.pay_wages()

        # 6) consumers consume
        random.shuffle(consumers)
        for consumer in consumers:
            # if consumer.employed:
            #     print("(before) In period: " + str(period) + " consumer " + str(consumer.identifier)
            #           + " has a wealth of " + str(consumer.wealth))
            consumer.consume()
            # if consumer.employed:
            #     print("(after) In period: " + str(period) + " consumer " + str(consumer.identifier)
            #           + " has a wealth of " + str(consumer.wealth))


        log({"Category": ["number of firms", "stock", "domestic_capital", "foreign_capital", "firm_workers", "cash"]})

        for industry in industries:
            industry.log()

        dict_of_dataframes[period] = custom_df(data)
        period += 1

    print_multiindex(dict_of_dataframes)


# hold the data to be logged
data = {}


# function to log the results of each month
def log(log_info):
    global data
    data = data | log_info


# UTLITY METHODS
# handle consumer to business
def handle_consumer_transaction(consumer, industry, amount):

    # print("consumer wants to spend " + str(amount) + " in industry " + industry.name)

    # if no firm in the industry has stock, return
    if industry.is_stock_zero():
        # print("case 1")
        return

    # get the firm with the cheapest price from the industry
    firm = industry.get_cheapest_firm()

    # if the amount of money is not enough to buy a single unit return
    if firm.price > amount:
        # print("case 2")
        return

    # if the number of units the consumer buys is higher than the stock from the firm,
    # buy the firm's stock and recurse for the remaining money
    if math.floor(amount / firm.price) > firm.stock:
        consumer.wealth -= firm.stock*firm.price
        firm.cash += firm.stock*firm.price
        remaining_amount = amount - firm.stock*firm.price
        # let a method in the firm class handle this? change?
        firm.quantity_sold += firm.stock
        firm.stock = 0
        handle_consumer_transaction(consumer, industry, remaining_amount)
        return

    # if none of the other options apply, buy goods for the amount the consumer wants to spend
    # start by making the amount spent a multiple of the price so that there are no partial goods
    actual_amount = math.floor(amount/firm.price)*firm.price
    consumer.wealth -= actual_amount
    firm.quantity_sold += actual_amount/firm.price
    firm.stock = firm.stock - actual_amount/firm.price


# handle business to business
def handle_business_transaction(consumer, industry, amount):
    pass


# fix so that it does not print the first column every time
def print_multiindex(list_of_dataframes):
    test = pandas.concat(list_of_dataframes, axis=1)
    test.to_csv("test.csv")


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))