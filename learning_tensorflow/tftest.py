
import pandas as pd              # A beautiful library to help us work with data as tables
import numpy as np               # So we can use number matrices. Both pandas and TensorFlow need it.
import matplotlib.pyplot as plt  # Visualize the things
import tensorflow as tf          # Fire from the gods

#id; state; player; ones; lib_b4; score; lib_after; zeroes; win_or_lose;
# win, player, lib_b4, score, lib_after, player_is_nn, piece_id, piece_x, piece_y, rotation, flip, move_id
UNUSED_COLUMNS = ["piece_id","piece_x","piece_y","rotation","flip","move_id"] # use column name
NUM_SAMPLES = 10
CSV_FILENAME = "logs/training-complete.csv"
COLUMN_NAMES = ["y","player","lib_b4","score","lib_after","player_is_nn"]

dataframe = pd.read_csv(CSV_FILENAME) # Let's have Pandas load our dataset as a dataframe
dataframe = dataframe.drop(UNUSED_COLUMNS, axis=1) # Remove columns we don't care about
dataframe = dataframe[0:NUM_SAMPLES] # We'll only use the first 10 rows of the dataset in this example

dataframe.loc[:, ("y2")] = dataframe["y"] == 0           # y2 is the negation of y1
dataframe.loc[:, ("y2")] = dataframe["y2"].astype(int)    # Turn TRUE/FALSE values into 1/0

inputX = dataframe.loc[:, COLUMN_NAMES].as_matrix()
inputY = dataframe.loc[:, ["y", "y2"]].as_matrix()

K = 152                       # depth of convolutional layers
LEARNING_RATE = .003          # initial learning rate
DECAY = 8.664339379294006e-08 # rate of exponential learning_rate decay

n_samples = inputY.size

x = tf.placeholder(tf.float32, [None, 2])  # Okay TensorFlow, we'll feed you an array of examples. Each example will
# be an array of two float values (area, and number of bathrooms).
# "None" means we can feed you any number of examples
# Notice we haven't fed it the values yet

W = tf.Variable(tf.zeros([2, 2]))  # Maintain a 2 x 2 float matrix for the weights that we'll keep updating
# through the training process (make them all zero to begin with)

b = tf.Variable(tf.zeros([2]))  # Also maintain two bias values

y_values = tf.add(tf.matmul(x, W), b)  # The first step in calculating the prediction would be to multiply
# the inputs matrix by the weights matrix then add the biases

# SOFTMAX:
# takes an array of values, returns an array of the same length of the probability of it being each value
# outputs are all positive and add up to 1
y = tf.nn.softmax(y_values)  # Then we use softmax as an "activation function" that translates the
# numbers outputted by the previous layer into probability form

y_ = tf.placeholder(tf.float32, [None, 2])  # For training purposes, we'll also feed you a matrix of labels

cost = tf.reduce_sum(tf.pow(y_ - y, 2))/(2*n_samples)
# Gradient descent
optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)


for i in range(training_epochs):
    sess.run(optimizer, feed_dict={x: inputX, y_: inputY}) # Take a gradient descent step using our inputs and labels

    # That's all! The rest of the cell just outputs debug messages.
    # Display logs per epoch step
    if (i) % display_step == 0:
        cc = sess.run(cost, feed_dict={x: inputX, y_:inputY})
        print "Training step:", '%04d' % (i), "cost=", "{:.9f}".format(cc) #, \"W=", sess.run(W), "b=", sess.run(b)

print "Optimization Finished!"
training_cost = sess.run(cost, feed_dict={x: inputX, y_: inputY})
print "Training cost=", training_cost, "W=", sess.run(W), "b=", sess.run(b), '\n'


print sess.run(y, feed_dict={x: inputX })

def softmax(E, temp):
    #print "E =\n", E
    expE = np.exp(temp * (E - max(E))) # subtract max to avoid overflow
    return expE / np.sum(expE)