from pymongo import MongoClient
from bson.objectid import ObjectId

class VacanciesRepository(object):
    """ Repository implementing CRUD operations on projects collection in MongoDB """

    def __init__(self):
        # initializing the MongoClient, this helps to
        # access the MongoDB databases and collections
        self.client = MongoClient(host='localhost', port=27017)
        self.database = self.client['vacancies']


    def create(self, vacancy):
        # Решение задания 3
        if vacancy is not None:
            if self.database.find({"url": vacancy.url}) is None:
                self.database.vacancies.insert(vacancy.get_as_json())
        else:
            raise Exception("Nothing to save, because project parameter is None")


    def read(self, vacancy_id=None):
        if vacancy_id is None:
            return self.database.vacancies.find({})
        else:
            return self.database.vacancies.find({"_id": vacancy_id})

    def update(self, vacancy):
        if vacancy is not None:
            self.database.vacancies.save(vacancy.get_as_json())
        else:
            raise Exception("Nothing to update, because project parameter is None")

    def delete(self, vacancy):
        if vacancy is not None:
            self.database.vacanciess.remove(vacancy.get_as_json())
        else:
            raise Exception("Nothing to delete, because project parameter is None")

    def find_salary_by_limit(self, m):
        print(list(self.database.vacancies.find({ "salary_min":  {"$gte": m}})))



