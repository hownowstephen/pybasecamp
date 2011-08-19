#!/usr/bin/python

from pybasecamp import Basecamp
import optparse

parser = optparse.OptionParser()
parser.add_option('-c', '--complete', help='complete at to-do item', dest='completed', action='store', default=False)
parser.add_option('-a', '--add', help='add a new to-do item', dest='new', action='store', default=False)
parser.add_option('-l', '--list', help='select which list to use', dest='list', action='store', default=None)

(opts, args) = parser.parse_args()

if __name__ == '__main__':

    wrapper = Basecamp()
    xml = wrapper.get_all_lists()

    my_id = None

    todo = []
    for todolist in xml:
        for todoitem in todolist.find('todo-items'):
            todo.append({'_id': todoitem.find('id').text, 'text': todoitem.find('content').text})
            if not my_id:   my_id = todoitem.find('responsible-party-id').text

    response = None
    if opts.completed != False:
        item = todo[int(opts.completed)]
        while response != 'y' and response != 'n':
            response = raw_input("Completed #%s: %s (y/n) " % (opts.completed,item['text']))
        if response == 'y': 
            wrapper.complete_item(item['_id'])
            del todo[int(opts.completed)]
        else:               
            pass
        
    if opts.new != False:
        wrapper.create_item(opts.list, content=opts.new, responsible_party=my_id)
        todo.append({'text': opts.new})

    print "To-do list for %s" % wrapper.config.username
    count = 0
    for item in todo:
        print "[%i] %s" % (count,item['text'])
        count += 1