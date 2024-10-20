#!/usr/bin/python 
from configparser import ConfigParser
import json
  
  
def config(filename='database.ini', section='postgresql'): 
    # create a parser 
    parser = ConfigParser() 
    # read config file 
    parser.read(filename) 
  
    # get section, default to postgresql 
    db = {} 
    if parser.has_section(section): 
        params = parser.items(section) 
        for param in params: 
            db[param[0]] = param[1] 
    else: 
        raise Exception('Section {0} not found in the {1} file'.format(section, filename)) 
  
    return db

def sites_config(filename='database.ini', section='manage'): 
    # create a parser 
    parser = ConfigParser() 
    # read config file 
    parser.read(filename) 
  
    # get section, default to postgresql 
    sites = {} 
    if parser.has_section(section): 
        params = parser.items(section) 
        for param in params: 
            sites[param[0]] = param[1].split(',')
    else: 
        raise Exception('Section {0} not found in the {1} file'.format(section, filename)) 
    
    return sites


def write_new_site(site_name):

    old_value = sites_config()['sites']
    print(old_value)

    old_value.append(site_name)
    old_value = set(old_value)

    config = ConfigParser()
    config.read('database.ini')
    config.set('manage', 'sites', ','.join(old_value))

    with open('database.ini', 'w') as configFile:
        config.write(configFile)

def delete_site(site_name):
    old_value = sites_config()['sites']
    old_value.remove(site_name)

    config = ConfigParser()
    config.read('database.ini')
    config.set('manage', 'sites', ','.join(old_value))

    with open('database.ini', 'w') as configFile:
        config.write(configFile)

