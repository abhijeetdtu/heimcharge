from math import sqrt
import glob
import os
import math
import json
from collections import defaultdict

from skimage import feature
from skimage.io import imread
from skimage.color import rgb2gray
from skimage import data
from skimage.feature import blob_dog, blob_log, blob_doh
from skimage.transform import rescale, resize, downscale_local_mean

from matplotlib import pyplot as plt


class Images:

    def __init__(self , path):
        print(path , os.path.isfile(path))
        image  = glob.glob(path)[0]
        self.im = imread(image , as_grey=True)

        self.arraySize = 100
        #self.array = defaultdict(lambda: defaultdict(int))
        self.array = [[0 for x in range(self.arraySize)] for x in range(self.arraySize) ]


    def EdgeDetection(self):
        image = self.im
        image_resized = rescale(image, 1.0/6.0 )
        edges = feature.canny(image_resized)
        xRange = edges.shape[0] / self.arraySize
        yRange = edges.shape[1] / self.arraySize

        for x in range(edges.shape[0]):
            for y in range(edges.shape[1]):
                i = math.floor( x / xRange)
                j = math.floor( y / yRange)
                self.array[i][j] += 1 if edges[x][y] else 0
                #print(self.array[i][j])

        circles = []
        for i in range(self.arraySize):
            for j in range(self.arraySize):
                if self.array[i][j] > 0:
                    circles.append({"x" : j , "y": i , "r": self.array[i][j]})

        json.dump(circles , open("test.json" , "w"))
        #print(len(circles) , flush=True)
        #image_downscaled = downscale_local_mean(edges1, (4, 3))
        #plt.imshow(edges)
        #plt.show()
        return circles


if __name__ == "__main__":

    Images(os.path.join("." , ".." , "PresentationLayer" , "static", "Images" , "7.jpg")).EdgeDetection()
