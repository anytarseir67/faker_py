import random
import requests
import aiohttp
import typing
import re # oh no

base_url = "https://fakerapi.it/api/v1/"

locales = ["en_US", "en_EN", "fr_FR"] # don't seem to be documented, only locales show in the examples

date_regex = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")

class InvalidLocale(Exception):
    pass


class FakerResponse():
    def __init__(self, json: dict) -> None:
        self._json = json
        
        if 'address' in json.keys():
            addr = json.pop('address')
            self.address = AddressResponse(addr)

        if 'addresses' in json.keys():
            addrs = json.pop('addresses')
            self.addresses = [AddressResponse(addr) for addr in addrs]

        if 'images' in json.keys():
            imgs = json.pop('images')
            self.images = [ImageResponse(img) for img in imgs]

        if 'contact' in json.keys():
            cont = json.pop('contact')
            self.contact = PersonResponse(cont)

        self.__dict__.update(json)


    def __repr__(self) -> str:
        return str(self._json)


    def __len___(self) -> int:
        return len(self._json)


    def __eq__(self, o: object) -> bool:
        if isinstance(o, FakerResponse):
            return self._json == o._json
        return False
        

class AddressResponse(FakerResponse):
    id: int
    street: str
    streetName: str
    buildingNumber: str
    city: str
    zipcode: str
    country: str
    county_code: str
    latitude: float
    longitude: float


class BookResponse(FakerResponse):
    id: int
    title: str
    author: str
    genre: str
    description: str
    isbn: str
    image: str
    published: str
    publisher: str


class CreditCardResponse(FakerResponse):
    type: str
    number: str
    expiration: str
    owner: str


class ImageResponse(FakerResponse):
    title: str
    description: str
    url: str


class PersonResponse(FakerResponse):
    id: int
    firstname: str
    lastname: str
    email: str
    phone: str
    birthday: str
    gender: str
    address: AddressResponse
    website: str
    image: str


class PlaceResponse(FakerResponse):
    latitude: float
    longitude: float


class ProductResponse(FakerResponse):
    images: typing.List[ImageResponse]
    id: int
    name: str
    description: str
    ean: str
    upc: str
    image: str
    net_price: float
    taxes: int
    price: str
    categories: typing.List[str]
    tags: typing.List[str]


class TextResponse(FakerResponse):
    title: str
    author: str
    genre: str
    content: str


class UserResponse(FakerResponse):
    id: int
    uuid: str
    firstname: str
    lastname: str
    username: str
    password: str
    email: str
    ip: str
    macAddress: str
    website: str
    image: str


class CompanyResponse(FakerResponse):
    addresses: typing.List[AddressResponse]
    contact: PersonResponse
    id: int
    name: str
    email: str
    vat: str
    phone: str
    country: str
    website: str
    image: str


class Faker():

    def __init__(self, locale: str="en_US", seed: int=None, json: bool=False) -> None:
        if type(locale) != str:
            raise TypeError(f"'locale' must be str, not {type(locale)}")
        if locale not in locales:
            raise InvalidLocale(f"{locale} is not a valid locale")
        self.locale = locale

        if seed:
            if type(seed) != int:
                raise TypeError(f"'seed' must be int, not {type(seed)}")
        else:
            seed = int(random.random())
        self.seed = seed

        if type(json) != bool:
            raise TypeError(f"'json' must be bool, not {type(json)}")
        self.json = json


    def _expand(self, kwargs: dict) -> str:
        expanded = ""
        kwargs.pop('endpoint')
        if kwargs['seed'] == None:
            kwargs.pop('seed')
        for key in kwargs:
            if kwargs[key] == None:
                continue

            if expanded != "":
                expanded += "&"
            expanded += f"_{key}={kwargs[key]}"
        return expanded
        

    def _request(self, **kwargs) -> None:
        endpoint = kwargs.get('endpoint')
        expanded = self._expand(kwargs)
        print(f"{base_url}{endpoint}?{expanded}")
        return requests.get(f"{base_url}{endpoint}?{expanded}").json()


    def address(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False) -> typing.Union[dict, AddressResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json

        resp = self._request(endpoint="addresses", quantity=quantity, seed=seed, locale=locale)

        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(AddressResponse(response))
            return data
        return AddressResponse(resp['data'][0])


    def book(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False) -> typing.Union[dict, BookResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json

        resp = self._request(endpoint="books", quantity=quantity, seed=seed, locale=locale)
        
        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(BookResponse(response))
            return data
        return BookResponse(resp['data'][0])


    def company(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False) -> typing.Union[dict, CompanyResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json

        resp = self._request(endpoint="companies", quantity=quantity, seed=seed, locale=locale)
        
        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(CompanyResponse(response))
            return data
        return CompanyResponse(resp['data'][0])


    def creditcard(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False) -> typing.Union[dict, CreditCardResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json

        resp = self._request(endpoint="credit_cards", quantity=quantity, seed=seed, locale=locale)
        
        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(CreditCardResponse(response))
            return data
        return CreditCardResponse(resp['data'][0])

    
    def image(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False, type_: str="any", width: int=640, height: int=480) -> typing.Union[dict, ImageResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json
        types = ['any', 'animals', 'architecture', 'nature', 'people', 'tech', 'kittens', 'pokemon']
        if type_ not in types:
            raise ValueError(f"'type_' must be one of {str(types)}. not '{type_}'")

        resp = self._request(endpoint="images", quantity=quantity, seed=seed, locale=locale, type=type_, width=width, height=height)
        
        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(ImageResponse(response))
            return data
        return ImageResponse(resp['data'][0])

    
    def person(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False, gender: str='male', birthday_start: str='2000-00-00', birthday_end: str='2020-00-00', date_check: bool=True) -> typing.Union[dict, PersonResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json

        genders = ['male', 'female'] # api isn't very inclusive...
        if gender not in genders:
            raise ValueError(f"'gender' must be one of {str(genders)}. not '{gender}'. i do not agree with this, but those are the only 2 the api accepts :/")

        if date_check:
            if not bool(re.match(date_regex, birthday_start)):
                raise ValueError(f"'birthday_start' must match format '2000-01-13' (y/m/d)")
            if not bool(re.match(date_regex, birthday_end)):
                raise ValueError(f"'birthday_end' must match format '2000-01-13' (y/m/d)")

        resp = self._request(endpoint="persons", quantity=quantity, seed=seed, locale=locale, gender=gender, birthday_start=birthday_start, birthday_end=birthday_end)
        
        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(PersonResponse(response))
            return data
        return PersonResponse(resp['data'][0])


    def place(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False) -> typing.Union[dict, PlaceResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json

        resp = self._request(endpoint="places", quantity=quantity, seed=seed, locale=locale)

        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(PlaceResponse(response))
            return data
        return PlaceResponse(resp['data'][0])


    def product(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False, price_min: float=None, price_max: float=None, taxes: int=None, categories_type: str=None) -> typing.Union[dict, ProductResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json

        types = ['integer', 'string', 'uuid', None]
        if categories_type not in types:
            raise ValueError(f"'categories_type' must be one of {str(types)}, not {categories_type}")

        resp = self._request(endpoint="products", quantity=quantity, seed=seed, locale=locale, price_min=price_min, price_max=price_max, taxes=taxes, categories_type=categories_type)

        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(ProductResponse(response))
            return data
        return ProductResponse(resp['data'][0])
        

    def text(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False, characters: int=None) -> typing.Union[dict, TextResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json

        resp = self._request(endpoint="texts", quantity=quantity, seed=seed, locale=locale, characters=characters)

        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(TextResponse(response))
            return data
        return TextResponse(resp['data'][0])


    def user(self, quantity: int=1, seed: int=None, locale: str=None, json: bool=False, gender: str='male') -> typing.Union[dict, UserResponse]:
        seed = seed or self.seed
        locale = locale or self.locale
        json = json or self.json

        genders = ['male', 'female'] # api isn't very inclusive...
        if gender not in genders:
            raise ValueError(f"'gender' must be one of {str(genders)}. not '{gender}'. i do not agree with this, but those are the only 2 the api accepts :/")

        resp = self._request(endpoint="users", quantity=quantity, seed=seed, locale=locale, gender=gender)

        if json:
            return resp

        if quantity > 1:
            data = []
            for response in resp['data']:
                data.append(UserResponse(response))
            return data
        return UserResponse(resp['data'][0])

#yeah no, not rn
class AioFaker():
    ...