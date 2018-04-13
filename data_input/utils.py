import os
import scipy
import numpy as np
import tensorflow as tf


def create_dataset(dataset, is_shuffle=True, n_repeates=0):
    trX, trY, valX, valY = load_data(dataset, is_training=True)
    tf.data.Dataset.from_tensor_slices((trX, trY))


def extract_cifar(files):
    # 验证文件是否存在
    for f in files:
        if not tf.gfile.Exists(f):
            raise ValueError('Failed to find file: ' + f)
    # 读取数据
    labels = None
    images = None

    for f in files:
        bytestream = open(f, 'rb')
        # 读取数据
        buf = bytestream.read(10000 * (32 * 32 * 3 + 1))
        # 把数据流转化为np的数组
        data = np.frombuffer(buf, dtype=np.uint8)
        # 改变数据格式
        data = data.reshape(10000, 1 + 32 * 32 * 3)
        # 分割数组
        labels_images = np.hsplit(data, [1])

        label = labels_images[0].reshape(10000)
        image = labels_images[1].reshape(10000, 32, 32, 3)

        if labels is None:
            labels = label
            images = image
        else:
            # 合并数组，不能用加法
            labels = np.concatenate((labels, label))
            images = np.concatenate((images, image))

    return labels, images


def load_cifar10(is_training=True, valid_size=0.1):
    if is_training:
        files = [os.path.join('data/cifar10/cifar-10-batches-bin', 'data_batch_%d.bin' % i) for i in range(1, 6)]
        labels, images = extract_cifar(files)

        indices = np.random.permutation(50000)
        valid_idx, train_idx = indices[:50000 * valid_size], indices[50000 * valid_size:]

        return images[train_idx], labels[train_idx], images[valid_idx], labels[valid_idx]
    else:
        files = [os.path.join('data/cifar10/cifar-10-batches-bin', 'test_batch.bin'), ]
        return extract_cifar(files)


def load_mnist(is_training=True):
    path = os.path.join('data', 'mnist')
    if is_training:
        fd = open(os.path.join(path, 'train-images-idx3-ubyte'))
        loaded = np.fromfile(file=fd, dtype=np.uint8)
        trainX = loaded[16:].reshape((60000, 784)).astype(np.float32)

        fd = open(os.path.join(path, 'train-labels-idx1-ubyte'))
        loaded = np.fromfile(file=fd, dtype=np.uint8)
        trainY = loaded[8:].reshape((60000)).astype(np.int32)

        trX = trainX[:55000] / 255.
        trY = trainY[:55000]

        valX = trainX[55000:, ] / 255.
        valY = trainY[55000:]

        return trX, trY, valX, valY
    else:
        fd = open(os.path.join(path, 't10k-images-idx3-ubyte'))
        loaded = np.fromfile(file=fd, dtype=np.uint8)
        teX = loaded[16:].reshape((10000, 784)).astype(np.float)

        fd = open(os.path.join(path, 't10k-labels-idx1-ubyte'))
        loaded = np.fromfile(file=fd, dtype=np.uint8)
        teY = loaded[8:].reshape((10000)).astype(np.int32)

        return teX / 255., teY


def load_fashion_mnist(is_training=True):
    path = os.path.join('data', 'fashion-mnist')
    if is_training:
        fd = open(os.path.join(path, 'train-images-idx3-ubyte'))
        loaded = np.fromfile(file=fd, dtype=np.uint8)
        trainX = loaded[16:].reshape((60000, 784)).astype(np.float32)

        fd = open(os.path.join(path, 'train-labels-idx1-ubyte'))
        loaded = np.fromfile(file=fd, dtype=np.uint8)
        trainY = loaded[8:].reshape((60000)).astype(np.int32)

        trX = trainX[:55000] / 255.
        trY = trainY[:55000]

        valX = trainX[55000:, ] / 255.
        valY = trainY[55000:]

        return trX, trY, valX, valY
    else:
        fd = open(os.path.join(path, 't10k-images-idx3-ubyte'))
        loaded = np.fromfile(file=fd, dtype=np.uint8)
        teX = loaded[16:].reshape((10000, 784)).astype(np.float)

        fd = open(os.path.join(path, 't10k-labels-idx1-ubyte'))
        loaded = np.fromfile(file=fd, dtype=np.uint8)
        teY = loaded[8:].reshape((10000)).astype(np.int32)

        return teX / 255., teY


def load_smallNORB(is_training=True):
    pass


def load_data(dataset, is_training=True):
    if dataset == 'mnist':
        return load_mnist(is_training)
    elif dataset == 'fashion-mnist':
        return load_fashion_mnist(is_training)
    elif dataset == 'smallNORB':
        return load_smallNORB(is_training)
    elif dataset == 'cifar10':
        return load_cifar10(is_training)
    else:
        raise Exception('Invalid dataset, please check the name of dataset:', dataset)


def get_batch_data(dataset, batch_size, num_threads):
    if dataset == 'mnist':
        trX, trY, num_tr_batch, valX, valY, num_val_batch = load_mnist(batch_size, is_training=True)
    elif dataset == 'fashion-mnist':
        trX, trY, num_tr_batch, valX, valY, num_val_batch = load_fashion_mnist(batch_size, is_training=True)
    elif dataset == 'smallNORB':
        trX, trY, num_tr_batch, valX, valY, num_val_batch = load_smallNORB(batch_size, is_training=True)
    data_queues = tf.train.slice_input_producer([trX, trY])
    X, Y = tf.train.shuffle_batch(data_queues, num_threads=num_threads,
                                  batch_size=batch_size,
                                  capacity=batch_size * 64,
                                  min_after_dequeue=batch_size * 32,
                                  allow_smaller_final_batch=False)

    return (X, Y)


def save_images(imgs, size, path):
    """
    Args:
        imgs: [batch_size, image_height, image_width]
        size: a list with tow int elements, [image_height, image_width]
        path: the path to save images
    """
    imgs = (imgs + 1.) / 2  # inverse_transform
    return scipy.misc.imsave(path, mergeImgs(imgs, size))


def mergeImgs(images, size):
    h, w = images.shape[1], images.shape[2]
    imgs = np.zeros((h * size[0], w * size[1], 3))
    for idx, image in enumerate(images):
        i = idx % size[1]
        j = idx // size[1]
        imgs[j * h:j * h + h, i * w:i * w + w, :] = image

    return imgs


def get_transformation_matrix_shape(in_pose_shape, out_pose_shape):
    return [out_pose_shape[0], in_pose_shape[0]]
