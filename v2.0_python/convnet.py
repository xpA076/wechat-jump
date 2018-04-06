import tensorflow as tf
import cv2
import numpy as np

import struct

batch = 1024


def read_imgdata(idx, frompath):
    path = 'E:\\Projects\\Coding\\wechat-jump\\v2.0_python\\__data\\' + frompath + '\\' \
           + str(idx // batch).zfill(2) + '\\' + str(idx % batch).zfill(4)
    image = cv2.imread(path + '.png')
    rd = open(path + '.dat', 'rb')
    data = struct.unpack('4i', rd.read(16))
    if data[0] == 0 and data[1] == 0 and data[2] == 0 and data[3] == 0:
        prob = 0
    else:
        prob = 1
    label_prob = np.array([[prob]])
    label_bbox = np.array([[data[0], data[1], data[2], data[3]]])
    rd.close()
    # upper-dimension label
    return np.array([image]), label_prob, label_bbox


def read_batch(idx, bsize, frompath):
    image = np.zeros((0, 687, 687, 3))
    label_prob = np.zeros((0, 1))
    label_bbox = np.zeros((0, 4))
    for i in range(idx, idx + bsize):
        img, prob, bbox = read_imgdata(i, frompath)
        image = np.concatenate((image, img), axis=0)
        label_prob = np.concatenate((label_prob, prob), axis=0)
        label_bbox = np.concatenate((label_bbox, bbox), axis=0)
    return image, label_prob, label_bbox


class MyConvNet(object):

    def __init__(self, batch=64):
        # hyperparameters
        self.t = 0.5
        self.m = 0.5
        # self.batch = 10

        self.input = tf.placeholder('float', [None, 687, 687, 3])
        self.label_prob = tf.placeholder('float', [None, 1])
        self.label_bbox = tf.placeholder('float', [None, 4])
        self.keep_prob = tf.placeholder('float')
        self.learn_rate=tf.placeholder('float')
        # 675 * 675 * 3
        self.kern1 = tf.Variable(tf.truncated_normal([9, 9, 3, 16], stddev=0.01),
            name='k1')
        self.bias1 = tf.Variable(tf.constant(0.1, shape=[16]), name='b1')
        self.conv1 = tf.nn.relu(tf.nn.conv2d(self.input, self.kern1, strides=[1, 3, 3, 1],
            padding='VALID') + self.bias1)
        # 223 * 223 * 16
        self.pool1 = tf.nn.max_pool(self.conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
            padding='VALID')
        # 111 * 111 * 16
        self.kern2 = tf.Variable(tf.truncated_normal([5, 5, 16, 32], stddev=0.01),
            name='k2')
        self.bias2 = tf.Variable(tf.constant(0.1, shape=[32]), name='b2')
        self.conv2 = tf.nn.relu(tf.nn.conv2d(self.pool1, self.kern2, strides=[1, 2, 2, 1],
            padding='VALID') + self.bias2)
        # 55 * 55 * 32
        self.pool2 = tf.nn.max_pool(self.conv2, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
            padding='VALID')
        # 27 * 27 * 32
        self.kern3 = tf.Variable(tf.truncated_normal([3, 3, 32, 64], stddev=0.01),
            name='k3')
        self.bias3 = tf.Variable(tf.constant(0.1, shape=[64]), name='b3')
        self.conv3 = tf.nn.relu(tf.nn.conv2d(self.pool2, self.kern3, strides=[1, 1, 1, 1],
            padding='SAME') + self.bias3)
        # 27 * 27 * 64
        self.pool3 = tf.nn.max_pool(self.conv3, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
            padding='VALID')
        # 13 * 13 * 64
        self.kern4 = tf.Variable(tf.truncated_normal([3, 3, 64, 64], stddev=0.01),
            name='k4')
        self.bias4 = tf.Variable(tf.constant(0.1, shape=[64]), name='b4')
        self.conv4 = tf.nn.relu(tf.nn.conv2d(self.pool3, self.kern4, strides=[1, 1, 1, 1],
            padding='SAME') + self.bias4)
        # 13 * 13 * 64
        self.pool4 = tf.nn.max_pool(self.conv4, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
            padding='VALID')
        # 6 * 6 * 64
        self.flat4 = tf.reshape(self.pool4, [-1, 6 * 6 * 64])
        self.drop4 = tf.nn.dropout(self.flat4, keep_prob=self.keep_prob)
        # 2304
        self.weig5 = tf.Variable(tf.truncated_normal([2304, 512], stddev=0.01), name='w5')
        self.bias5 = tf.Variable(tf.constant(0.1, shape=[1, 512]), name='b5')
        self.fcon5 = tf.nn.relu(
            tf.nn.dropout(tf.matmul(self.flat4, self.weig5) + self.bias5,
                keep_prob=self.keep_prob))
        # 512
        self.weig6 = tf.Variable(tf.truncated_normal([512, 128], stddev=0.01), name='w6')
        self.bias6 = tf.Variable(tf.constant(0.1, shape=[1, 128]), name='b6')
        self.fcon6 = tf.nn.relu(
            tf.nn.dropout(tf.matmul(self.fcon5, self.weig6) + self.bias6,
                keep_prob=self.keep_prob))
        # 128
        self.weig7 = tf.Variable(tf.truncated_normal([128, 32], stddev=0.01), name='w7')
        self.bias7 = tf.Variable(tf.constant(0.1, shape=[1, 32]), name='b7')
        self.fcon7 = tf.nn.relu(tf.matmul(self.fcon6, self.weig7) + self.bias7)
        # 32

        # output probability and bounding box label
        self.weig8_prob = tf.Variable(tf.truncated_normal([32, 1], stddev=0.01),
            name='w8')
        self.bias8_prob = tf.Variable(tf.constant(0.1, shape=[1, 1]), name='b8')
        self.z_out = tf.matmul(self.fcon7, self.weig8_prob) + self.bias8_prob
        self.output_prob = tf.nn.sigmoid(self.z_out)

        self.weig8_bbox = tf.Variable(tf.truncated_normal([32, 4], stddev=0.01))
        self.bias8_bbox = tf.Variable(tf.constant(0.1, shape=[1, 4]))
        self.output_bbox = tf.matmul(self.fcon7, self.weig8_bbox) + self.bias8_bbox

        # loss function , training methods , saver , etc.
        loss_prob = tf.reduce_sum(tf.nn.sigmoid_cross_entropy_with_logits(
            labels=self.label_prob, logits=self.z_out))
        delta = self.output_bbox - self.label_bbox
        dsqr = delta * delta
        zeros = tf.constant(0.0, shape=[batch, 1])
        ones = tf.constant(1.0, shape=[batch, 1])

        dsqr_xy = tf.reduce_sum(dsqr[0:batch, 0:2],
            reduction_indices=1, keepdims=True)
        dsqr_wh = tf.reduce_sum(dsqr[0:batch, 2:4],
            reduction_indices=1, keepdims=True)
        self.loss_dist = self.t * dsqr_xy + (1 - self.t) * dsqr_wh

        # loss_dist=tf.reduce_sum(dsqr,axis=1,keep_dims=True)
        self.loss = loss_prob + self.m * tf.reduce_sum(
            tf.where(tf.cast(self.label_prob, 'bool'), self.loss_dist, zeros))

        self.train = tf.train.AdamOptimizer(self.learn_rate).minimize(self.loss)

        self.saver = tf.train.Saver(
            [self.kern1, self.bias1, self.kern2, self.bias2, self.kern3, self.bias3,
             self.kern4, self.bias4, self.weig5, self.bias5, self.weig6, self.bias6,
             self.weig7, self.bias7, self.weig8_prob, self.bias8_prob, self.weig8_bbox,
             self.bias8_bbox])

        self.init_op = tf.global_variables_initializer()

        # for test
        self.classify_correct = tf.reduce_sum(
            tf.cast(tf.greater(self.output_prob, 0.5), 'float'))

        self.bbox_count = tf.reduce_sum(self.label_prob)
        self.bbox_delta = tf.reduce_sum(
            (self.output_bbox - self.label_bbox) * (self.output_bbox - self.label_bbox),
            reduction_indices=1, keepdims=True)
        ## correct threshold : 25.0
        self.bbox_correct = tf.reduce_sum(tf.where(tf.cast(self.label_prob, 'bool'),
            tf.where(tf.less(self.bbox_delta, 25.0), ones, zeros), zeros))
