from middleware import JSONTranslator, SetHeaders

import pandas as pd
import falcon
import json
import numpy as np

from sklearn.neighbors import KDTree,BallTree
from scipy import spatial

class GetImageByCategory(object):
    def on_post(self, req, resp):
        try:
            print req
            category = req.context["category"]
        except KeyError:
            raise falcon.HTTPBadRequest(
                'Ombiko myre! Missing sample',
                'A sample must be submitted in the request body.')
        
        result = {'status':'success', 'imgList':'None'}
        
        result['imgList'] = get_image_by_category(category,"2071.png")
        #result['imgList'] = getSimilar("20187.png")

        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_201

api = falcon.API(middleware=[SetHeaders(), JSONTranslator()])

api.add_route('/get_image_by_category', GetImageByCategory())
# api.add_route('/get_image_by_similarity', GetImageBySimilarity())

import json
import pandas as pd
ui_details = pd.read_csv("ui_detailsCategory.csv")

catDict = {"entapp":'Entertainment',
           "bookapp":'Books & Reference',
           "socialapp":'Social',
           "travelapp":'Travel & Local',
           "shopapp":'Shopping'}

# def get_image_by_category(category):
#     res = ui_details["UI Number"][ui_details["category"]==catDict[category]]
#     return list(res.sample(n=40))

with open("data/ui_layout_vectors/ui_names.json") as json_data:
    ui_names = json.load(json_data)["ui_names"]
    json_data.close()

ui_vectors = np.load("data/ui_layout_vectors/ui_vectors.npy")

# def getSimilar(filename):
#     vec_index = ui_names.index(filename)
#     kdt = KDTree(ui_vectors, leaf_size=30, metric='euclidean')
#     return list(kdt.query(ui_vectors[vec_index,:], k=40, return_distance=False)[0])

def get_image_by_category(category, filename):
    categoryList = ui_details["UI Number"][ui_details["category"]==catDict[category]]

    arr = []
    vector = []
    for i in range(len(categoryList)):
        try:
            index = ui_names.index(str(categoryList[i])+".png")
        except:
            continue
        arr.append({"name":categoryList[i],"index":index, "vector":ui_vectors[index,:]})
        vector.append(ui_vectors[index,:])

    category_vectors = np.array(vector)

    vec_index = ui_names.index(filename)
    kdt = KDTree(category_vectors, leaf_size=30, metric='euclidean')
    data = kdt.query(ui_vectors[vec_index,:], k=100, return_distance=False)

    apidata = []
    for i in list(data[0]):
        apidata.append(arr[i]["name"])
    
    return apidata

        