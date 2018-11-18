import logging
import sqlite3
import toolkit_file

import json
import csv

import pandas as pd


class SqliteDB():
    """docstring for _sqlitedb"""

    def __init__(self, DB_FILE):
        self.DB_FILE = DB_FILE
        if self.DB_FILE == ':memory:' or toolkit_file.check_file_exists(self.DB_FILE):
            self.conn = sqlite3.connect(self.DB_FILE)

    def __enter__(self):
        return self

    def __exit__(self, Type, value, traceback):
        '''
        Executed after "with"
        '''
        if hasattr(self, 'self.cursor'):
            print('Close the DB')
            self.cursor.close()

    def create_database(self, SQLFile):
        '''Create a new database using deploy SQLFile'''
        if not toolkit_file.check_file_exists(self.DB_FILE):
            print('Deploy {} to {}'.format(SQLFile, self.DB_FILE))
            self.conn = sqlite3.connect(self.DB_FILE)
            self.cursor = self.conn.cursor()
            with open(SQLFile) as f:
                self.cursor.executescript(f.read())
        else:
            print('{} exists'.format(self.DB_FILE))

    def query(self, sql):
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            logging.error("sqlite query error: %s", e)
            return None
        finally:
            self.cursor.close()
        return result

    def execute(self, sql):
        self.cursor = self.conn.cursor()
        affected_row = -1
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            affected_row = self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logging.error("sqlite execute error: %s", e)
            return 0
        finally:
            print('affected_rows: ' + str(affected_row))
            self.cursor.close()
        return affected_row

    def executescript(self, sql):
        self.cursor = self.conn.cursor()
        self.cursor.executescript(sql)

    def executemany(self, sql, params=None):
        self.cursor = self.conn.cursor()
        affected_rows = 0
        try:
            self.cursor.executemany(sql, params)
            self.conn.commit()
            affected_rows = self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logging.error("sqlite executemany error: %s", e)
            return 0
        finally:
            self.cursor.close()
            print('affected_rows: ' + str(affected_rows))
        return affected_rows

    def load_json(self, JSON_FILE, tableName=None):
        '''
        Load file into sqlite
        '''
        if not tableName:
            tableName = toolkit_file.get_basename(JSON_FILE)

        with open(JSON_FILE, 'r') as f:
            dicSet = json.load(f)

        print('Load json {} to table {}'.format(JSON_FILE, tableName))
        tupleList = []
        columnNames = list(dicSet[0].keys())
        columnNamesSqlJoined = ', '.join(
            map(lambda x: '`' + x + '`', columnNames))

        for dic in dicSet:
            tupleList.append(tuple(dic.values()))

        insertSql = "INSERT INTO {} ({}) VALUES(?{});".format(
            tableName, columnNamesSqlJoined, ',?' * (len(tupleList[0]) - 1))

        self.executemany(insertSql, tupleList)

    def load_csv(self, csvFile, tableName=None, delimiter=','):
        '''
        Load file into sqlite
        '''
        if not tableName:
            tableName = toolkit_file.get_basename(csvFile)

        with open(csvFile, 'r') as f:
            reader = csv.reader(f, delimiter=delimiter)
            header = next(reader)
        header = list(map(lambda x: x.strip().replace(' ', '_'), header))
        # print(header)
        drop_SQL = '''DROP TABLE IF EXISTS {}'''.format(tableName)
        self.execute(drop_SQL)
        chunks = pd.read_csv(csvFile, chunksize=100000, sep=delimiter,
                             dtype=str, names=header, header=0)
        for chunk in chunks:
            chunk.to_sql(name=tableName, if_exists='append',
                         con=self.conn, index=False)

    def dump_database(self):
        print('Dump database to {}'.format(self.DB_FILE + '.sql'))
        with open(self.DB_FILE + '.sql', 'w', encoding='utf-8') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)


if __name__ == '__main__':
    PATH = r'C:\Users\chdu\Desktop\Portal\Other\python_toolkit'
    DB_FILE = 'test.db'
    # DB_FILE = ':memory:'
    JSON_FILE = PATH + '\\' + 'ctl_rs_process_sql_test.json'
    csvFile = 'SMGE_20170320.txt'

    create_view = '''CREATE TABLE IF NOT EXISTS `work_todo11` as select * from Status_sheet '''
    truncate_table = '''DELETE FROM `test` '''
    drop_table = '''DROP TABLE `work_todo11` '''
    # sqlitedb = _sqlitedb(DB_FILE)

    with SqliteDB(DB_FILE) as sqlitedb:
        # print(sqlitedb.query('select * from Status_sheet'))
        # sqlitedb.execute(create_view)
        sqlitedb.load_csv(csvFile, tableName=None, delimiter='\t')
        # sqlitedb.executemany(batch_insert, tupleList)
        # sqlitedb.execute(drop_table)
