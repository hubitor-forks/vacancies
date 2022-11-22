from connection.connection import DBConnector


class MultyPipeline:
    def __init__(self):
        self.conn = DBConnector.Instance()

    def process_item(self, item, spider):
        self.conn.store_db(item)
        return item
