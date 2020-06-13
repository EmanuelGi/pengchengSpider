# -*- coding: utf-8 -*-

import Queue
import json

def get_content_from_txt(txt_file_name):
    with open(txt_file_name) as f:
        f.readline()
        while True:
            line = f.readline()
            if not line:
                break
            text = line.split(" | ")
            yield text


def save_queue(queue, filename):
    with open(filename, 'w+') as f:
        while not queue.empty():
            value = queue.get()
            map = {
                u"value": value
            }
            f.write(json.dumps(map))
            f.write(u'\n')


def load_queue(filename, value_type):
    queue = Queue.Queue()
    with open(filename) as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            map = json.loads(line)
            queue.put(value_type(map[u"value"]))
    return queue

