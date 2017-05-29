from pylab import *
import sys
import os
import caffe
import pylab
from caffe import layers as L, params as P

caffe_root = os.getenv('CAFFE_ROOT')+'/'  # this file should be run from {caffe_root}/examples (otherwise change this line)
os.chdir(caffe_root+'examples/')


def lenet(lmdb, batch_size):
    # our version of LeNet: a series of linear and simple nonlinear transformations
    n = caffe.NetSpec()

    n.data, n.label = L.Data(batch_size=batch_size, backend=P.Data.LMDB, source=lmdb,
                             transform_param=dict(scale=1. / 255), ntop=2)
    n.conv1 = L.Convolution(n.data, kernel_size=5, num_output=20, weight_filler=dict(type='xavier'))
    n.pool1 = L.Pooling(n.conv1, kernel_size=2, stride=2, pool=P.Pooling.MAX)
    n.conv2 = L.Convolution(n.pool1, kernel_size=5, num_output=50, weight_filler=dict(type='xavier'))
    n.pool2 = L.Pooling(n.conv2, kernel_size=2, stride=2, pool=P.Pooling.MAX)
    n.fc1 = L.InnerProduct(n.pool2, num_output=500, weight_filler=dict(type='xavier'))
    n.relu1 = L.ReLU(n.fc1, in_place=True)
    n.score = L.InnerProduct(n.relu1, num_output=10, weight_filler=dict(type='xavier'))
    n.loss = L.SoftmaxWithLoss(n.score, n.label)
    return n.to_proto()

if __name__ == '__main__':
    with open('mnist/lenet_auto_train.prototxt', 'w') as f:
        f.write(str(lenet('mnist/mnist_train_lmdb', 64)))

    with open('mnist/lenet_auto_test.prototxt', 'w') as f:
        f.write(str(lenet('mnist/mnist_test_lmdb', 100)))

    caffe.set_device(7)
    caffe.set_mode_gpu()

    ### load the solver and create train and test nets
    solver = None  # ignore this workaround for lmdb data (can't instantiate two solvers on the same data)
    solver = caffe.SGDSolver('mnist/lenet_auto_solver.prototxt')
    print [(k, v.data.shape) for k, v in solver.net.blobs.items()]
    print [(k, v[0].data.shape) for k, v in solver.net.params.items()]

    solver.net.forward()  # train net
    solver.test_nets[0].forward()  # test net (there can be more than one)

    # we use a little trick to tile the first eight images
    # imshow(solver.net.blobs['data'].data[:8, 0].transpose(1, 0, 2).reshape(28, 8*28), cmap='gray'); axis('off')
    # print 'train labels:', solver.net.blobs['label'].data[:8]
    # pylab.show()
    # imshow(solver.test_nets[0].blobs['data'].data[:8, 0].transpose(1, 0, 2).reshape(28, 8*28), cmap='gray'); axis('off')
    # print 'test labels:', solver.test_nets[0].blobs['label'].data[:8]
    # pylab.show()

    # solver.step(1)
    # imshow(solver.net.params['conv1'][0].diff[:, 0].reshape(4, 5, 5, 5)\
    #        .transpose(0, 2, 1, 3).reshape(4 * 5, 5 * 5), cmap='gray')
    # axis('off')
    # pylab.show()

    # training
    niter = 20000
    test_interval = 500
    # losses will also be stored in the log
    train_loss = zeros(niter)
    test_acc = zeros(int(np.ceil(niter / test_interval)))
    output = zeros((niter, 8, 10))

    # the main solver loop
    for it in range(niter):
        solver.step(1)  # SGD by Caffe

        # store the train loss
        train_loss[it] = solver.net.blobs['loss'].data

        # run a full test every so often
        # (Caffe can also do this for us and write to a log, but we show here
        #  how to do it directly in Python, where more complicated things are easier.)
        if it % test_interval == 0:
            print 'Iteration', it, 'testing...'
            correct = 0
            for test_it in range(100):
                solver.test_nets[0].forward()
                correct += sum(solver.test_nets[0].blobs['score'].data.argmax(1) == solver.test_nets[0].blobs['label'].data)
            test_acc[it // test_interval] = correct / 1e4

    _, ax1 = subplots()
    ax2 = ax1.twinx()
    ax1.plot(arange(niter), train_loss)
    ax2.plot(test_interval * arange(len(test_acc)), test_acc, 'r')
    ax1.set_xlabel('iteration')
    ax1.set_ylabel('train loss')
    ax2.set_ylabel('test accuracy')
    ax2.set_title('Test Accuracy: {:.2f}'.format(test_acc[-1]))
    pylab.show()
