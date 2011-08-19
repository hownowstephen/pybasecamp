#!/usr/bin/python

from pybasecamp import Basecamp
import optparse

parser = optparse.OptionParser()
parser.add_option('-c', '--complete', help='complete at to-do item', dest='completed', action='store', default=False)

(opts, args) = parser.parse_args()

if __name__ == '__main__':

    wrapper = Basecamp()
    xml = wrapper.get_all_lists()

    todo = []
    for todolist in xml:
        for todoitem in todolist.find('todo-items'):
            todo.append({'_id': todoitem.find('id').text, 'text': todoitem.find('content').text})

    response = None
    if opts.completed != False:
        item = todo[int(opts.completed)]
        while response != 'y' and response != 'n':
            response = raw_input("Completed #%s: %s (y/n) " % (opts.completed,item['text']))
        if response == 'y': wrapper.complete_item(item['_id'])
        else:               print "no change"
    else:
        print "To-do list for %s" % wrapper.config.username
        count = 0
        for item in todo:
            print "[%i] %s" % (count,item['text'])
            count += 1