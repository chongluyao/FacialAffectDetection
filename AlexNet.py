import math
import time
import tensorflow as tf
from datetime import datetime
import input_data

# input data
mnist = input_data.read_data_sets('data/', one_hot=True)
n_input = 784
n_output = 10
learning_rate = 0.001
dropout = 0.75
# function
def print_activations(t):
    print(t.op.name, '', t.get_shape().as_list())

# 定义卷积操作
def conv2d(input, w, b):
    return tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(input, w, strides=[1, 1, 1, 1], padding='SAME'), b)) # 参数分别指定了卷积核的尺寸、多少个channel、filter的个数即产生特征图的个数                                                                                       # 步长为1，即扫描全图像素,[1, 1, 1, 1]分别代表batch_size、h、w、c的stride
# 定义池化操作
def max_pool(input):
    return tf.nn.max_pool(input, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID') # padding有两种选择：'SAME'（窗口滑动时，像素不够会自动补0）或'VALID'（不够就跳过）两种选择
# 定义全连接操作
def fc(input, w, b):
    return tf.nn.relu(tf.add(tf.matmul(input, w), b)) # w*x+b，再通过非线性激活函数relu

# parameters
weights = {
    # 使用截断的正态分布（标准差0.1）初始化卷积核的参数kernel，卷积核大小为3*3，channel为1，个数64
    'wc1': tf.Variable(tf.truncated_normal([3, 3, 1, 64], dtype=tf.float32, stddev=0.1), name='weights1'),
    'wc2': tf.Variable(tf.truncated_normal([3, 3, 64, 128], dtype=tf.float32, stddev=0.1), name='weights2'),
    'wc3': tf.Variable(tf.truncated_normal([3, 3, 128, 256], dtype=tf.float32, stddev=0.1), name='weights3'),
    'wc4': tf.Variable(tf.truncated_normal([3, 3, 256, 256], dtype=tf.float32, stddev=0.1), name='weights4'),
    'wc5': tf.Variable(tf.truncated_normal([3, 3, 256, 128], dtype=tf.float32, stddev=0.1), name='weights5'),
    'wd1': tf.Variable(tf.truncated_normal([3*3*128, 1024], dtype=tf.float32, stddev=0.1), name='weights_fc1'),
    'wd2': tf.Variable(tf.random_normal([1024, 1024], dtype=tf.float32, stddev=0.1), name='weights_fc2'),
    'wd3': tf.Variable(tf.random_normal([1024, n_output], dtype=tf.float32, stddev=0.1), name='weights_output')
}
biases = {
    'bc1': tf.Variable(tf.constant(0.0, shape=[64], dtype=tf.float32), trainable=True, name='biases1'),
    'bc2': tf.Variable(tf.constant(0.0, shape=[128], dtype=tf.float32), trainable=True, name='biases2'),
    'bc3': tf.Variable(tf.constant(0.0, shape=[256], dtype=tf.float32), trainable=True, name='biases3'),
    'bc4': tf.Variable(tf.constant(0.0, shape=[256], dtype=tf.float32), trainable=True, name='biases4'),
    'bc5': tf.Variable(tf.constant(0.0, shape=[128], dtype=tf.float32), trainable=True, name='biases5'),
    'bd1': tf.Variable(tf.constant(0.0, shape=[1024], dtype=tf.float32), trainable=True, name='biases_fc1'),
    'bd2': tf.Variable(tf.constant(0.0, shape=[1024], dtype=tf.float32), trainable=True, name='biases_fc2'),
    'bd3': tf.Variable(tf.constant(0.0, shape=[n_output], dtype=tf.float32), trainable=True, name='biases_output')
}

# network structure
def alex_net(_input, _weights, _biases, _keep_prob):
    _input_r = tf.reshape(_input, [-1, 28, 28, 1])

    with tf.name_scope('conv1'):
        _conv1 = conv2d(_input_r, _weights['wc1'], _biases['bc1'])
        print_activations(_conv1)
    with tf.name_scope('pool1'):
        _pool1 = max_pool(_conv1)
        print_activations(_pool1)

    with tf.name_scope('conv2'):
        _conv2 = conv2d(_pool1, _weights['wc2'], _biases['bc2'])
        print_activations(_conv2)
    with tf.name_scope('pool2'):
        _pool2 = max_pool(_conv2)
        print_activations(_pool2)

    with tf.name_scope('conv3'):
        _conv3 = conv2d(_pool2, _weights['wc3'], _biases['bc3'])
        print_activations(_conv3)

    with tf.name_scope('conv4'):
        _conv4 = conv2d(_conv3, _weights['wc4'], _biases['bc4'])
        print_activations(_conv4)

    with tf.name_scope('conv5'):
        _conv5 = conv2d(_conv4, _weights['wc5'], _biases['bc5'])
        print_activations(_conv5)
    with tf.name_scope('pool3'):
        _pool3 = max_pool(_conv5)
        print_activations(_pool3)

    _densel = tf.reshape(_pool3, [-1, _weights['wd1'].get_shape().as_list()[0]])

    with tf.name_scope('fc1'):
        _fc1 = fc(_densel, _weights['wd1'], _biases['bd1'])
        _fc1_drop = tf.nn.dropout(_fc1, _keep_prob)
        print_activations(_fc1_drop)

    with tf.name_scope('fc2'):
        _fc2 = fc(_fc1_drop, _weights['wd2'], _biases['bd2'])
        _fc2_drop = tf.nn.dropout(_fc2, _keep_prob)
        print_activations(_fc2_drop)

    with tf.name_scope('out'):
        _out = tf.add(tf.matmul(_fc2_drop, _weights['wd3']), _biases['bd3'])
        print_activations(_out)

    return _out


x = tf.placeholder(tf.float32, [None, n_input])
y = tf.placeholder(tf.float32, [None, n_output])
keep_prob = tf.placeholder(tf.float32)

pred = alex_net(x, weights, biases, keep_prob)  # 前向传播的预测值
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=pred, labels=y))  # 交叉熵损失函数，reduce_mean为求平均loss
optm = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)  # 梯度下降优化器
corr = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))  # tf.equal()对比预测值的索引和实际label的索引是否一样，一样返回True，不一样返回False
accuracy = tf.reduce_mean(tf.cast(corr, tf.float32))  # 将pred即True或False转换为1或0,并对所有的判断结果求均值
# 初始化所有参数
init = tf.global_variables_initializer()
print("FUNCTIONS READY")

# 上面神经网络结构定义好之后，下面定义一些超参数
training_epochs = 1000  # 所有样本迭代1000次
batch_size = 1  # 每进行一次迭代选择50个样本
display_step = 10

sess = tf.Session()  # 定义一个Session
sess.run(init)  # 在sess里run一下初始化操作
for epoch in range(training_epochs):
    avg_cost = 0.
    total_batch = int(mnist.train.num_examples/batch_size)
    start_time = time.time()
    for i in range(total_batch):
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)  # 逐个batch的去取数据
        # 获取批数据
        sess.run(optm, feed_dict={x: batch_xs, y: batch_ys, keep_prob: dropout})
        avg_cost += sess.run(cost, feed_dict={x: batch_xs, y: batch_ys, keep_prob: 1.0})/total_batch
    if epoch % display_step == 0:
        train_accuracy = sess.run(accuracy, feed_dict={x: batch_xs, y: batch_ys, keep_prob: 1.0})
        test_accuracy = sess.run(accuracy, feed_dict={x: mnist.test.images, y: mnist.test.labels, keep_prob: 1.0})
        print("Epoch: %03d/%03d cost: %.9f TRAIN ACCURACY: %.3f TEST ACCURACY: %.3f"
              % (epoch, training_epochs, avg_cost, train_accuracy, test_accuracy))
    # 计算每轮迭代的平均耗时mn和标准差sd，并显示
    duration = time.time() - start_time
    print('%s: step %d, duration = %.3f' % (datetime.now(), epoch, duration))

print("DONE")
