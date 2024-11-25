import requests
from requests.structures import CaseInsensitiveDict
import json

# headers for authentication
headers = CaseInsensitiveDict()
headers["Authorization"] = "Token token=\"redacted\""
# get max results
parameters = {'per_page': 500}

# this is a function that loops through the subcollections in a collection
# and returns a list of their uuids
def getSubcollectionUUIDs(collectionURL):

    subcollectionUUIDs = []
    # send request - remember to use authentication token
    r = requests.get(collectionURL, headers=headers, params=parameters)
    subcollectionsAsJSON = r.json()

    # validation check for how many subcollections found
    print("there are", subcollectionsAsJSON['nyplAPI']['response']['numSubCollections'], "subcollections")

    listJSONSubcollections = subcollectionsAsJSON['nyplAPI']['response']['collection']

    # loop through subcollections
    for subcollection in listJSONSubcollections:
        # look at uuid and append to list
        subcollectionUUIDs.append(subcollection['uuid'])

    return subcollectionUUIDs

# this is a function that returns a list of item uuids
# within a list of subcollections
def getItemUUIDs(subcollectionUUIDs):

    itemUUIDs = []
    base_url = "https://api.repo.nypl.org/api/v2/collections/"
   
    # counter for how many items could not be captured
    couldntGet = 0

    # loop through subcollections
    for uuid in subcollectionUUIDS:
        # for each subcollection, look at json
        r = requests.get(base_url + uuid, headers=headers, params=parameters)
        itemsAsJSON = r.json()

        # look at items and append to list, if possible
        listJSONItems = itemsAsJSON['nyplAPI']['response']['item']

        for item in listJSONItems:
            try:
                itemUUIDs.append(item['uuid'])
                print(item['uuid'])
            except:
                couldntGet += 1
                next
    
    # validation check
    print("got", str(len(itemUUIDs)), "items in total")
    print("couldn't capture", str(couldntGet), "items")
    
    return itemUUIDs

# this is a function that loops through a list of item uuids
# and downloads its image and metadata
def getItemInfo(itemUUIDs):

    item_base_url = "https://api.repo.nypl.org/api/v2/items/"

    counter = 0

    for item in itemUUIDs:
        counter += 1
        try:
            r = requests.get(item_base_url + item, headers=headers, params={'fo': 'json'})

            # validation check    
            print(counter, r.status_code, r.url)

            string_as_json = json.loads(r.text)

            # get id number for name of files
            item_id = string_as_json['nyplAPI']['request']['uuid']
            print('item id:', item_id)
            
            # download and save image (grab highest quality)
            image_container = string_as_json['nyplAPI']['response']['capture']
            # note: image_container is a list, not a dict...therefore convert to dict
            image_dict = dict(enumerate(image_container))
            image_url = image_dict[0]['imageLinks']['imageLink'][0]
            print('downloading:', image_url)
            image = requests.get(image_url).content
            image_file = open('nypl-item-files/' + item_id + '.jpg', 'wb')
            image_file.write(image)
            image_file.close()

            # write rest of metadata to json file
            mods_base_url = "https://api.repo.nypl.org/api/v2/items/mods/"
            mods_r = requests.get(mods_base_url + item, headers=headers, params={'fo': 'json'})
            file = open('nypl-item-metadata/' + item_id + '.json', 'w')
            file.write(mods_r.text)
            file.close()
        except:
            print('could not get item', counter)
            


# for the collection, get subcollection UUIDs
collectionURL = "https://api.repo.nypl.org/api/v2/collections/07430830-c5d1-012f-bd22-58d385a7bc34/subcollections"
subcollectionUUIDS = getSubcollectionUUIDs(collectionURL)

# for each subcollection, get item UUIDs
itemUUIDs = getItemUUIDs(subcollectionUUIDS)

# request and download image and metadata for each item
getItemInfo(itemUUIDs)