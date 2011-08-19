'''
PyBasecamp
@author: @stephenyoungdev
'''

import sys, json, urllib, urllib2
from lxml import etree

default_config = '/etc/pybasecamp/config.json'

class Basecamp():
    '''Wrapper for accessing basecamp API data using the current basecamp api'''

    def __init__(self,profile='default',config=default_config):
        '''Loads the local pybasecamp configuration file and generates an authenticated url opener'''
        self.config = BasecampConfig(profile,config)
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.config.domain, self.config.username, self.config.password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        self.opener = urllib2.build_opener(authhandler)

    def _load(self,method,endpoint,**kwargs):
        '''Abstraction for the load action, performs a load of the xml tree'''
        url = "%s/%s" % (self.config.domain,endpoint.lstrip('/'))
        if not url.startswith("http://"): url = "https://%s" % url

        # Generate a request
        request = urllib2.Request(url, data=urllib.urlencode(kwargs))
        request.add_header('Content-Type', 'application/xml')
        request.get_method = lambda: method

        try:
            req = self.opener.open(request)
            data = req.read()
            xml = etree.fromstring(data)
            return xml
        except:
            return None

    ''' To-do List actions: http://developer.37signals.com/basecamp/to-do-lists.shtml '''

    def get_all_lists(self,**kwargs):
        '''Loads all lists from the current configuration'''
        return self._load("GET","todo_lists.xml",**kwargs)
    
    def get_project_lists(self,project,**kwargs):
        '''Loads all lists for a supplied project from the current configuration'''
        return self._load("GET","/projects/%s/todo_lists.xml" % project,**kwargs)
    
    def get_list(self,list_id,**kwargs):
        '''Loads a single list by id'''
        return self._load("GET","/todo_lists/%s.xml" % list_id,**kwargs)

    ''' Unimplemented / Incomplete '''
    def update_list(self,list_id,**kwargs): 
        '''Loads a list template, updates it with new values, and pushes the update to basecamp'''
        template = self._load("GET","/todo_lists/%s/edit.xml" % list_id,**kwargs)
        self._load("PUT","/todo_lists/%s.xml" % list_id)

    def create_list(self,project_id,**kwargs):
        '''Loads a new list template, updates it with our values and pushes it to basecamp'''
        template = self._load("GET","/projects/%s/todo_lists/new.xml" % project_id,**kwargs)
        self._load("POST","/projects/%s/todo_lists.xml" % project_id)

    ''' To-do List item actions: http://developer.37signals.com/basecamp/to-do-list-items.shtml '''

    def get_all_items(self,list_id,**kwargs): 
        '''Loads all items in a given to-do list'''
        return self._load("GET","/todo_lists/%s/todo_items.xml" % list_id,**kwargs)

    def get_item(self,item_id,**kwargs): 
        '''Loads details for a single to-do list item'''
        return self._load("GET","/todo_items/%s.xml" % item_id,**kwargs)

    def complete_item(self,item_id,**kwargs): 
        '''Flags a to-do list item as completed'''
        print "/todo_items/%s/complete.xml" % item_id
        return self._load("PUT","/todo_items/%s/complete.xml" % item_id,**kwargs)

    def uncomplete_item(self,item_id,**kwargs):
        '''Flags a to-do list item as incomplete'''
        return self._load("PUT","/todo_items/%s/uncomplete.xml" % item_id,**kwargs)
        
    def create_item(self,**kwargs): pass
        #  /todo_lists/#{todo_list_id}/todo_items/new.xml
        # POST /todo_lists/#{todo_list_id}/todo_items.xml
    def update_item(self,**kwargs): pass
        #  /todo_items/#{id}/edit.xml
        #  PUT /todo_items/#{id}.xml
        


class BasecampConfig():
    '''Wrapper for pybasecamp configuration file to allow for easier attribute access'''
    def __init__(self,profile=None,config=None,create=False):
        # Load the configuration file and parse it into a local dict
        try:    
            self.config = self.load(config)
        except: 
            if create:  self.config = {}
            else:       raise PyBasecampException('No configuration file exists at %s, or not readable' % config)
        # If a profile is selected
        try:    
            if profile: self.profile = self.config[profile]
            else:       self.profile = None
        except: 
            raise PyBasecampException('Profile does not exist %s' % profile)

    def add(self,config_name):
        '''Add a new configuration to the config file'''
        self.config[config_name] = {'domain': '', 'username': '', 'password': ''}
    
    def remove(self,config_name):
        del self.config[config_name]

    def load(self,config):
        '''Load a configuration file'''
        self.config_path = config
        f = open(config,'r')
        data = json.loads(f.read())
        f.close()
        return data

    def save(self):
        '''Save a configuration file'''
        f = open(self.config_path,'w')
        f.write(json.dumps(self.config))
        f.close()

    def iteritems(self):
        return self.config.iteritems()

    def __nonzero__(self):
        if len(self.config) > 0: return True
        return False
    
    def __iter__(self):
        return self.config.__iter__()

    def __getitem__(self,key):
        return self.config[key]

    def __getattr__(self,key):
        try:
            return self.profile[key]
        except:
            return self.config[key]

    
    @classmethod
    def Configure(self,config=default_config):
        '''Allows easy configuration of pybasecamp'''
        print "Loading config: %s" % config
        config = BasecampConfig(None,config,True)
        if not config:
            print "Configuration file is currently empty"
        else:
            print "Available Configurations:"
            for key,value in config.iteritems():
                print "\t%s" % key
        while True:
            cfg = raw_input("? ")
            if cfg == '\list' or cfg == '\l':
                print "Available Configurations:"
                for key,value in config.iteritems():
                    print key,
                print ''
            # Catch the save command
            elif cfg == '' or cfg == '\save' or cfg == '\s':
                print "Saving and exiting"
                try:    
                    config.save()
                except:
                    raise PyBasecampException("Configuration file is not writeable %s" % config.config_path)
                sys.exit(0)
            # Handle the selection of a configuration line
            elif cfg in config or cfg.startswith('+'):
                if cfg.startswith('+'):
                    # Catch an addition
                    cfg = cfg.strip('+')
                    if not cfg in config:
                        config.add(cfg)
                    else:
                        raise PyBasecampException("Configuration %s already exists!" % cfg)
                line = config[cfg]
                for key,value in line.iteritems():
                    data = raw_input("%s [%s]: " % (key,value))
                    if data: line[key] = data
                print "saving updated configuration"
                config.save()
            elif cfg.startswith('-'):
                cfg = cfg.strip('-')
                if not cfg in config:
                    raise PyBasecampException("Configuration %s does not exist!" % cfg)
                else:
                    config.remove(cfg)
            # Catch a does not exist error
            elif cfg and not cfg in config:
                print "Configuration does not exist"
                pass

class PyBasecampException(Exception):
    '''Default exception handler for pybasecamp'''


if __name__ == '__main__':
    #BasecampConfig.Configure()
    b = Basecamp()
    b.todo_lists(responsible_party=7779036)