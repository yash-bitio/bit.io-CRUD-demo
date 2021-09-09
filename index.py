# coding: utf-8
from logging import log
import eel
import sys
import bitdotio
import datetime
from datetime import timezone
import uuid

b = bitdotio.bitdotio("YOUR_API_KEY")
username = "YOUR_USERNAME"
repo_name = "to_do_view"

@eel.expose
def create_repo():
    try:
        r = bitdotio.model.repo.Repo(name=repo_name)
        r.description = "Our to-do application"
        r.is_private = True
        b.create_repo(repo=r)
    except:
        pass

    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute(f'CREATE TABLE IF NOT EXISTS "{username}/{repo_name}"."lists" \
    (list_name TEXT, key TEXT, archived BOOLEAN, created DATE, updated DATE)')

    cur.execute(f'CREATE TABLE IF NOT EXISTS "{username}/{repo_name}"."messages" \
    (message TEXT, key TEXT, id TEXT, completed BOOLEAN, created DATE, updated DATE)')

@eel.expose
def createNewList(list_name):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute(f'INSERT INTO "{username}/{repo_name}"."lists" \
    VALUES (\'{list_name}\', \'{uuid.uuid4()}\', false, \'{datetime.datetime.now(timezone.utc)}\', \'{datetime.datetime.now(timezone.utc)}\')')

@eel.expose
def createNewItem(item_name, key):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute(f'INSERT INTO "{username}/{repo_name}"."messages" \
    VALUES (\'{item_name}\', \'{key}\', \'{uuid.uuid4()}\', false, \'{datetime.datetime.now(timezone.utc)}\', \'{datetime.datetime.now(timezone.utc)}\')')

@eel.expose
def updateItem(id, status):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute(f'UPDATE "{username}/{repo_name}"."messages" \
    SET completed = {status} WHERE id = \'{id}\'')

@eel.expose
def archiveList(key):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute(f'UPDATE "{username}/{repo_name}"."lists" \
    SET archived = true WHERE key = \'{key}\'')

@eel.expose
def delete_item(id):
    conn = b.get_connection()
    cur = conn.cursor()
    cur.execute(f'DELETE FROM "{username}/{repo_name}"."messages" \
    WHERE id = \'{id}\'')

@eel.expose
def getLists():
    conn = b.get_connection()
    cur = conn.cursor()

    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = '{}' AND table_schema = '{}/{}'".format('lists', username, repo_name))
    columns = cur.fetchall()
    list_columns_unzipped = [item for t in columns for item in t]

    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = '{}' AND table_schema = '{}/{}'".format('messages', username, repo_name))
    columns = cur.fetchall()
    messages_columns_unzipped = [item for t in columns for item in t]

    cur.execute(f'SELECT * FROM "{username}/{repo_name}"."lists" \
    WHERE archived = false')
    data = cur.fetchall()

    all_to_do_lists = []

    for list_item in data:
        zip_iterator = zip(list_columns_unzipped, list(list_item))
        to_do_list = dict(zip_iterator)

        to_do_list['list_items'] = []

        key = to_do_list['key']
        cur.execute(f'SELECT * FROM "{username}/{repo_name}"."messages" WHERE key = \'{key}\'')
        message_data = cur.fetchall()

        for message in message_data:
            zip_iterator = zip(messages_columns_unzipped, list(message))
            message = dict(zip_iterator)
            to_do_list['list_items'].append(message)

        all_to_do_lists.append(to_do_list)

    return all_to_do_lists

if __name__ == '__main__':
    if sys.argv[1] == '--develop':
        eel.init('client')
        eel.start({
            'port': 3000
        }, options={
            'port': 8888,
            'host': 'localhost',
        }, suppress_error=True)
    else:
        eel.init('build')
        eel.start('index.html')
