import tensorflow as tf

from convnet import MyConvNet, read_batch


cnn = MyConvNet(batch=32)
print('initialization finished')
sess = tf.Session()
sess.run(cnn.init_op)
# cnn.saver.restore(sess,'__cnn/train01/model_01')

for i in range(1000):
    print('training times: ' + str(i).zfill(3))
    loss = 0
    for idx in range(0, 1024, 32):
        img, prob, bbox = read_batch(idx, 32, 'origin')
        temp = sess.run([cnn.loss, cnn.train],
            feed_dict={cnn.input: img, cnn.label_prob: prob, cnn.label_bbox: bbox,
                       cnn.keep_prob: 0.5, cnn.learn_rate: 1e-3})
        loss += temp[0]
        print('', end='.', flush=True)
    print('\nloss: ' + str(loss))

    if (i + 1) % 5 == 0:
        print('saving model...')
        cnn.saver(sess, '__cnn/train01/model_' + str(i + 1).zfill(3))

sess.close()
