import mysql.connector
from datetime import datetime, timedelta
from config import *


class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Connection Error')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


@Singleton
class DBConnector(object):
    def __init__(self):
        self.create_connection()
        self.delete_old_items()

    def __str__(self):
        return 'Database connection object'

    def create_connection(self):
        self.conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            # database=DB_DATABASE
        )

        self.curr = self.conn.cursor()

        print('\n\n\nConnection success\n\n\n')

    def delete_old_items(self):
        # Deleting old vacancies
        curr_date = datetime.now() - timedelta(hours=336, minutes=0)
        self.curr.execute('delete from vacancies.indeed_job where created_at < %s', (curr_date,))
        self.conn.commit()

        # Deleting not verified vacancies
        # self.curr.execute('DELETE FROM vacancies.indeed_job AS t1 WHERE t1.company NOT IN (SELECT t2.Company FROM JOBS_FINDER.verified_companies AS t2);')
        # self.conn.commit()

    def store_db(self, item):
        self.curr.execute("select * from vacancies.indeed_job where source_id = %s", (item['source_id'],))
        result = self.curr.fetchone()

        if not result:
            self.curr.execute('INSERT INTO vacancies.indeed_job '\
                            ' (source_id, position, company, location, salary, schedule, short_description, full_description, link, website, logo, created_at)'\
                            ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',(
                                item['source_id'],
                                item['position'],
                                item['company'],
                                item['location'],
                                item['salary'],
                                item['schedule'],
                                # '' if item['shift'] is None else item['shift'],
                                item['short_description'][0:255],
                                item['full_description'][0:1000],
                                item['link'],
                                item['website'],
                                '' if item['logo_url'] is None else item['logo_url'],
                                datetime.now()))

            self.conn.commit()

        if item['website'] == 'seek':
            self.curr.execute("select * from vacancies.remote_job where source_id = %s", (item['source_id'],))
            result = self.curr.fetchone()
            if not result:
                self.curr.execute('INSERT INTO vacancies.remote_job '\
                            ' (source_id, position, company, location, salary, schedule, short_description, full_description, link, website, logo, created_at)'\
                            ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',(
                                item['source_id'],
                                item['position'],
                                item['company'],
                                item['location'],
                                item['salary'],
                                item['schedule'],
                                item['short_description'][0:255],
                                item['full_description'][0:1000],
                                item['link'],
                                item['website'],
                                '' if item['logo_url'] is None else item['logo_url'],
                                datetime.now()))

                self.conn.commit()
