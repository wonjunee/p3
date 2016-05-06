#!/usr/bin/env python
# Run this after "finalProject_dbinsert.py"

import pprint

def get_db(db_name):
    """ Import Database """
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def fix_source(db):
    """ Fix sources """
    fix_sources = {"Bing"  : ['Bing; knowledge; logic','bing imagery,_data, field papers,on-site','bing imagery,_data,field papers,on-site',"binng", "BING", "bing", "bing imagery", "Bing imagery", "bing imagery, _data,firld papers,on-site", 'bing imagery, _data, field papers, on-site', "biung", "Bing, site visit"],
                   "Yahoo" : ["Yahoo imagery", "yahoo"],
                   "site visit" : ["Site visit", "imagery", "site survey", "GPS, site visit"],
                   "ground truth" : ["ground truthing"],
                   "fairfaxtrails.org" : ['http://www.fairfaxtrails.org', 'http://www.fairfaxtrails.org/pimmit/110707Legal_brochures_updown.pdf'],
                   "Fairfax County GIS" : ['http://www.fairfaxcounty.gov/library/branches/dm/','Fairfax County Free GIS data','www.fairfaxcounty.gov > Tax Records property map 0602010037','Fairfax County GIS (http://www.fairfaxcounty.gov/maps/metadata.htm)','county_import_v0.1_20080508235459'],
                   "knowledge" : ['from walking it','ground truth','I work there','local knowledge','In-person Source, ate there'],
                   "survey" : ["ground survey"],
                   "Tiger" : ['TIGER/Line 2008 Place Shapefiles (http://www.census.gov/geo/www/tiger/)', "Tiger2008 by DaleP 2009-02-28"],
                   "DCGIS" : ['DCGIS; NPS','DCGIS; NPS; Park Service Map; USGS NM',"dcgis"]
                }

    for key in fix_sources.keys():
        for word in fix_sources[key]:
            db.map.update(
                        { "created.source" : word},
                        { "$set": {
                            "created.source" : key
                            }
                        },
                        multi = True
                    )
    unique_sources = db.map.distinct("created.source")
    print "After processing"
    print "Total Number of Unique Sources:", len(unique_sources)
    pprint.pprint(unique_sources)
    return unique_sources

if __name__ == '__main__':
    db = get_db('finalproject')

    """ Total Count """
    print "Total Number of Records:", db.map.count()

    """ Total node numbers """
    print "Total Number of Nodes:", db.map.find({"type":"node"}).count()

    """ Total way numbers """
    print "Total Number of Ways:", db.map.find({"type":"way"}).count()

    """ Total number of unique users """
    print "Total Number of Unique Users:", len(db.map.distinct("created.user"))

    """ Total number of unique sources """
    unique_sources = db.map.distinct("created.source")
    print "Total Number of Unique Sources:", len(unique_sources)
    pprint.pprint(unique_sources)


    """ Fix Sources """
    # unique_sources = fix_source(db)

    """ Top contributing users """
    top_user = db.map.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, {"$sort":{"count":-1}}, {"$limit":5}])
    print "Top 5 Contributing Users"
    for doc in top_user:
        print doc

    """ Top source """
    top_source = db.map.aggregate([{"$group":{"_id":"$created.source", "count":{"$sum":1}}}, {"$sort":{"count":-1}}, {"$limit":5}])
    print "Top 5 Sources"
    for doc in top_source:
        print doc

    """ Number of users appearing only once """
    one_time_users = db.map.aggregate([ {
                                        "$group": {
                                            "_id": "$created.user",
                                            "count": { "$sum" : 1}
                                            }
                                        },
                                        {
                                        "$match": {
                                            "count" : 1
                                            }
                                        }
                                    ])
    count = 0
    one_time_users_list = []
    for user in one_time_users:
        one_time_users_list.append(user)
        count += 1

    print "\nNumber of One Time Users:", count

    """ Top user for each source """
    for source in unique_sources:
        source_top_user = db.map.aggregate([ {
                "$match": { "created.source" : source },
                },
                {
                "$group": {
                    "_id": "$created.user",
                    "count": { "$sum" : 1}
                    }
                },
                {
                "$sort": {"count": -1}
                },
                {
                "$limit": 1
                }
            ])
        top_user = [doc for doc in source_top_user]
        print "Top User of", source,":", top_user[0]['_id'], "-", top_user[0]["count"]
    
    """ Number of buildings """
    num_metros = db.map.aggregate([{
            "$match": {"building": {"$ne" : None}}
            },
            {
            "$group": {"_id": None, "count": {"$sum": 1}}
            }
        ])
    for doc in num_metros:
        print "\nTotal Number of Buildings:", doc["count"]

    """ Number of Metros """
    num_metros = db.map.aggregate([
            {
            "$match": {"railway": "station"}
            },
            {
            "$project": {"railway": "$railway",
                         "name" : "$name",
                         "type" : "$type"}
            }
        ])
    print "\nNumber of Metros"
    for i in num_metros:
        pprint.pprint(i["name"])
    # Actually there are more than 3 but looks like the data is not up-to-date.

    """ Number of Amenities """
    num_metros = db.map.aggregate([
            {
            "$match": {"amenity": {"$ne": None}}
            },
            {
            "$group": {"_id": "$amenity"}
            },
            {
            "$group": {"_id": None, "count": {"$sum": 1}}
            }
        ])
    for i in num_metros:
        print "\nNumber of Amenities:", i["count"]

    """ Number of Schools """
    num_metros = db.map.aggregate([
            {
            "$match": {"amenity": "school"}
            },
            {
            "$group": {"_id": None, "count":{"$sum":1}}
            }
        ])
    for i in num_metros:
        print "\nNumber of Schools:", i["count"]

    """ Number of Buildings """
    num_metros = db.map.aggregate([
            {
            "$match": {"building": {"$ne": None}}
            },
            {
            "$group": {"_id": None, "count":{"$sum": 1}}
            }
        ])
    for i in num_metros:
        print "\nNumber of Buildings:", i["count"]

    """ ADDITIONAL STATISTICS """
    # 1. Percentage of top source
    # 2. Percentage of top user
    # 3. Percentage of top amenity
    # 4. Percentage of top building

    """ Percentage of top source """
    top_source_percentage = 394065.0/398663.0*100
    second_source_percentage = 3385.0/398663.0*100
    print "Percentage of top source (None):", top_source_percentage, "%"
    print "Percentage of 2nd top source (Bing)", second_source_percentage, "%"

    """ Percentage of top user """
    print
    print "Percentage of top user (ingalls):", (133558.0/398663.0*100), "%"

    """ Percentage of top amenity """
    print
    print "Percentage of top amenity ()"

    """ ADDITIONAL IDEAS """
    # 1. which metro station has the most number of houses nearby
    # 2. which metro station has the most number of amenities
    # 3. which school has the most number of housese nearby
