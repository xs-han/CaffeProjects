#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 5/24/17 2:49 AM
# @Author  : Aries
# @Site    : http://nbviewer.jupyter.org/github/BVLC/caffe/blob/master/examples/00-classification.ipynb
# @File    : caffenet_eg.py
# @Software: PyCharm Community Edition

import numpy as np
import matplotlib.pyplot as plt
import caffe
import os

if __name__=='__main__':
    '''This is a website caffe net example'''
    plt.rcParams['figure.figsize'] = (10, 10)  # large images
    plt.rcParams['image.interpolation'] = 'nearest'  # don't interpolate: show square pixels
    plt.rcParams['image.cmap'] = 'gray'  # use grayscale output rather than a (potentially misleading) color heatmap

    caffe.set_mode_gpu()
    caffe_root = os.getenv('CAFFE_ROOT')+'/'
    model_def = caffe_root + 'models/bvlc_reference_caffenet/deploy.prototxt'
    model_weights = caffe_root + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'

    net = caffe.Net(model_def,  # defines the structure of the model
                    model_weights,  # contains the trained weights
                    caffe.TEST)  # use test mode (e.g., don't perform dropout)