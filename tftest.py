import tensorflow as tf
import numpy as np

node1 = tf.constant(3.0, tf.float32)
node2 = tf.constant(4.0)

a = np.random.randn(3, 3)
b = np.random.randn(3, 1)
c = a*b

print c