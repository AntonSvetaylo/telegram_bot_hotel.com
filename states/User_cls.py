class User:
    users = dict()

    def __init__(self, user_id):
        self.__id = user_id
        self.__query = Query()
        User.add_user(user_id, self)

    @classmethod
    def add_user(cls, user_id, user):
        cls.users[user_id] = user

    def get_query(self):
        return self.__query


class Query:
    __command = ''
    __destinationId = ''
    __check_in = ''
    __check_out = ''
    __currency = ''
    __adults = ''
    __children = ''
    __minprice = 0
    __maxprice = 1000000
    __sortorder = 'PRICE'
    __photo = 0
    __max_distance = ''
    __result = None

    def status(self):
        return 'command = {}\n' \
               'destinationId = {}\n' \
               'check_in = {}\n' \
               'check_out = {}\n' \
               'adults = {}\n' \
               'children = {}\n' \
               'minprice = {}\n' \
               'maxprice = {}\n' \
               'currency = {}\n' \
               'sortorder = {}\n' \
               'photo = {}'.format(
                                      self.__command,
                                      self.__destinationId,
                                      self.__check_in,
                                      self.__check_out,
                                      self.__adults,
                                      self.__children,
                                      self.__minprice,
                                      self.__maxprice,
                                      self.__currency,
                                      self.__sortorder,
                                      self.__photo
                                )

    @property
    def destinationid(self) -> str:
        return self.__destinationId

    @destinationid.setter
    def destinationid(self, value: str) -> None:
        self.__destinationId = value

    @property
    def check_in(self) -> str:
        return self.__check_in

    @check_in.setter
    def check_in(self, value: str) -> None:
        self.__check_in = value

    @property
    def check_out(self) -> str:
        return self.__check_out

    @check_out.setter
    def check_out(self, value: str) -> None:
        self.__check_out = value

    @property
    def currency(self) -> str:
        return self.__currency

    @currency.setter
    def currency(self, value: str) -> None:
        self.__currency = value

    @property
    def adults(self) -> str:
        return self.__adults

    @adults.setter
    def adults(self, value: str) -> None:
        self.__adults = value

    @property
    def children(self) -> str:
        return self.__children

    @children.setter
    def children(self, value: str) -> None:
        self.__children = value

    @property
    def sortorder(self) -> str:
        return self.__sortorder

    @sortorder.setter
    def sortorder(self, value: str) -> None:
        self.__sortorder = value

    @property
    def command(self) -> str:
        return self.__command

    @command.setter
    def command(self, value: str) -> None:
        self.__command = value

    @property
    def photo(self) -> int:
        return self.__photo

    @photo.setter
    def photo(self, value: int) -> None:
        self.__photo = value

    @property
    def minprice(self) -> int:
        return self.__minprice

    @minprice.setter
    def minprice(self, value: int) -> None:
        self.__minprice = value

    @property
    def maxprice(self) -> int:
        return self.__maxprice

    @maxprice.setter
    def maxprice(self, value: int) -> None:
        self.__maxprice = value

    @property
    def max_distance(self) -> str:
        return self.__max_distance

    @max_distance.setter
    def max_distance(self, value: str) -> None:
        self.__max_distance = value

    @property
    def result(self) -> list:
        return self.__result

    @result.setter
    def result(self, value: list) -> None:
        self.__result = value
