from bson.objectid import ObjectId


class Vacancy(object):
    """A class for storing Project related information"""

    def __init__(self,  hh_id=None, vacancy_name=None, url=None, salary_min=0.0,
                 salary_max=0.0, currency=None):
        # if vacancy_id is None:
        #     self._id = ObjectId()
        # else:
        #     self._id = vacancy_id
        self.hh_id = hh_id
        self.vacancy_name = vacancy_name
        self.url = url
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.currency = currency

    def get_as_json(self):
        """ Method returns the JSON representation of the Project object, which can be saved to MongoDB """
        return self.__dict__

    @staticmethod
    def build_from_json(json_data):
        """ Method used to build Project objects from JSON data returned from MongoDB """
        if json_data is not None:
            try:
                return Vacancy(
                    # json_data.get('_id', None),
                               json_data['hh_id'],
                               json_data['vacancy_name'],
                               json_data['url'],
                               json_data['salary_min'],
                               json_data['salary_max'],
                               json_data['currency'])
            except KeyError as e:
                raise Exception("Key not found in json_data: {}".format(e.message))
        else:
            raise Exception("No data to create Project from!")