from players import Player
import numpy as np
import tensorflow as tf
import os
import time
import random
from datetime import *
import features

class NNPlayer(Player):
    def __init__(self, ps, index, model):
        super(NNPlayer, self).__init__(ps, index)

        self.model = model
        self.last_move_probs = np.zeros(self.model.N)

        with tf.Graph().as_default():
            with tf.device('/cpu:0'):
                self.feature_planes = tf.placeholder(tf.float32, shape=[None, self.model.N, self.model.Nfeat],
                                                     name='feature_planes')
                self.logits = model.inference(self.feature_planes, self.model.Nfeat)

                saver = tf.train.Saver(tf.trainable_variables())
                init = tf.initialize_all_variables()
                self.sess = tf.Session(config=tf.ConfigProto(log_device_placement=False))
                self.sess.run(init)

                checkpoint_dir = os.path.join(model.train_dir, 'checkpoints')
                restore_from_checkpoint(self.sess, saver, checkpoint_dir)

    def get_move(self, board, players):

        # build the feature planes
        board_feature_planes = features.make_feature_planes(board, self.id)

        Normalization.apply_featurewise_normalization_B(board_feature_planes)

        feature_batch = make_symmetry_batch(board_feature_planes)

        feed_dict = {self.feature_planes: feature_batch}

        logit_batch = self.sess.run(self.logits, feed_dict)

        # !! returns NxN image, used to create move probabilities
        move_logits = average_plane_over_symmetries(logit_batch, self.model.N)
        softmax_temp = 1.0
        move_probs = softmax(move_logits, softmax_temp)

        # zero out illegal moves
        # for every possible move,

        # for x in xrange(self.model.N):
        #     for y in xrange(self.model.N):
        #         ind = self.model.N * x + y
        #         if not board.play_is_legal(x, y, index):
        #             move_probs[ind] = 0



        sum_probs = np.sum(move_probs)
        if sum_probs == 0: return None # no legal moves, pass
        move_probs /= sum_probs # re-normalize probabilities

        pick_best = True
        if pick_best:
            move_ind = np.argmax(move_probs)
        else:
            move_ind = sample_from(move_probs)
        move_x = move_ind / self.model.N
        move_y = move_ind % self.model.N

        self.last_move_probs = move_probs.reshape((board.N, board.N))

       # return Move(move_x, move_y)


        return None

    def get_type(self):
        return "NN"

    def get_last_move_probs(self):
        return self.last_move_probs


def restore_from_checkpoint(sess, saver, ckpt_dir):
    print "Trying to restore from checkpoint in dir", ckpt_dir
    ckpt = tf.train.get_checkpoint_state(ckpt_dir)
    if ckpt and ckpt.model_checkpoint_path:
        print "Checkpoint file is ", ckpt.model_checkpoint_path
        saver.restore(sess, ckpt.model_checkpoint_path)
        global_step = int(ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1])
        print "Restored from checkpoint %s" % global_step
        return global_step
    else:
        print "No checkpoint file found"
        assert False

def optionally_restore_from_checkpoint(sess, saver, train_dir):
    while True:
        response = raw_input("Restore from checkpoint [y/n]? ").lower()
        if response == 'y':
            return restore_from_checkpoint(sess, saver, train_dir)
        if response == 'n':
            return 0

def make_symmetry_batch(features):
    assert len(features.shape) == 3
    N = features.shape[0]
    Nfeat = features.shape[2]
    feature_batch = np.empty((8, N, N, Nfeat), dtype=features.dtype)
    for s in xrange(8):
        feature_batch[s,:,:,:] = features
        apply_symmetry_planes(feature_batch[s,:,:,:], s)
    return feature_batch

def apply_symmetry_planes(planes, s):
    assert len(planes.shape) == 3
    if (s & 1) != 0: # flip x
        np.copyto(planes, planes[::-1,:,:])
    if (s & 2) != 0: # flip y
        np.copyto(planes, planes[:,::-1,:])
    if (s & 4) != 0: # swap x and y
        np.copyto(planes, np.transpose(planes[:,:,:], (1,0,2)))

def average_plane_over_symmetries(planes, N):
    assert planes.shape == (8, N*N)
    planes = planes.reshape((8, N, N))
    for s in xrange(8):
        invert_symmetry_plane(planes[s,:,:], s)
    mean_plane = planes.mean(axis=0)
    mean_plane = mean_plane.reshape((N*N,))
    return mean_plane

def invert_symmetry_plane(plane, s):
    assert len(plane.shape) == 2
    # note reverse order of 4,2,1
    if (s & 4) != 0: # swap x and y
        np.copyto(plane, np.transpose(plane[:,:], (1,0)))
    if (s & 2) != 0: # flip y
        np.copyto(plane, plane[:,::-1])
    if (s & 1) != 0: # flip x
        np.copyto(plane, plane[::-1,:])


def softmax(E, temp):
    expE = np.exp(temp * (E - max(E))) # subtract max to avoid overflow
    return expE / np.sum(expE)

def sample_from(probs):
    cumsum = np.cumsum(probs)
    r = random.random()
    for i in xrange(len(probs)):
        if r <= cumsum[i]:
            return i
    assert False, "problem with sample_from"


def train_model(model, N, Nfeat, build_feed_dict, normalization, loss_func, train_data_dir, val_data_dir, lr_base,
                lr_half_life, max_steps, just_validate=False):
    with tf.Graph().as_default():
        # build the graph
        learning_rate_ph = tf.placeholder(tf.float32)
        momentum_ph = tf.placeholder(tf.float32)
        feature_planes = tf.placeholder(tf.float32, shape=[None, N, N, Nfeat])

        model_outputs = model.inference(feature_planes, N, Nfeat)
        outputs_ph, total_loss, accuracy = loss_func(model_outputs)
        train_op = train_step(total_loss, learning_rate_ph, momentum_ph)

        saver = tf.train.Saver(tf.trainable_variables(), max_to_keep=5, keep_checkpoint_every_n_hours=2.0)

        init = tf.initialize_all_variables()
        sess = tf.Session(config=tf.ConfigProto(log_device_placement=False))
        sess.run(init)

        summary_writer = tf.train.SummaryWriter(
            os.path.join(model.train_dir, 'summaries', datetime.now().strftime('%Y%m%d-%H%M%S')), graph=sess.graph,
            flush_secs=5)
        accuracy_avg = MovingAverage('accuracy', time_constant=1000)
        total_loss_avg = MovingAverage('total_loss', time_constant=1000)

        def run_validation():  # run the validation set
            val_loader = NPZ.Loader(val_data_dir)
            mean_loss = 0.0
            mean_accuracy = 0.0
            mb_num = 0
            print "Starting validation..."
            while val_loader.has_more():
                if mb_num % 100 == 0: print "validation minibatch #%d" % mb_num
                feed_dict = build_feed_dict(val_loader, normalization, feature_planes, outputs_ph)
                loss_value, accuracy_value = sess.run([total_loss, accuracy], feed_dict=feed_dict)
                mean_loss += loss_value
                mean_accuracy += accuracy_value
                mb_num += 1
            mean_loss /= mb_num
            mean_accuracy /= mb_num
            print "Validation: mean loss = %.3f, mean accuracy = %.2f%%" % (mean_loss, 100 * mean_accuracy)
            summary_writer.add_summary(make_summary('validation_loss', mean_loss), step)
            summary_writer.add_summary(make_summary('validation_accuracy_percent', 100 * mean_accuracy), step)

        last_training_loss = None

        if just_validate:  # Just run the validation set once
            Checkpoint.restore_from_checkpoint(sess, saver, model.train_dir)
            run_validation()
        else:  # Run the training loop
            # step = 0
            step = Checkpoint.optionally_restore_from_checkpoint(sess, saver,
                                                                 os.path.join(model.train_dir, 'checkpoints'))
            # step = optionally_restore_from_checkpoint(sess, saver, model.train_dir)
            # print "WARNING: CHECKPOINTS TURNED OFF!!"
            print "WARNING: WILL STOP AFTER %d STEPS" % max_steps
            print "WARNING: IGNORING lr.txt and momentum.txt"
            print "lr_base = %f, lr_half_life = %f" % (lr_base, lr_half_life)
            # loader = NPZ.AsyncRandomizingLoader(train_data_dir, minibatch_size=128)
            minibatch_size = 128
            batch_queue = EvalTraining.AsyncRandomBatchQueue(feature_planes, outputs_ph, train_data_dir, minibatch_size,
                                                             normalization)
            # loader = NPZ.RandomizingLoader(train_data_dir, minibatch_size=128)
            # loader = NPZ.GroupingRandomizingLoader(train_data_dir, Ngroup=1)
            # loader = NPZ.SplittingRandomizingLoader(train_data_dir, Nsplit=2)
            last_step_ref_time = 0
            while True:
                if step % 10000 == 0 and step != 0:
                    run_validation()

                start_time = time.time()
                # feed_dict = build_feed_dict(loader, normalization, feature_planes, outputs_ph)
                feed_dict = batch_queue.next_feed_dict()
                load_time = time.time() - start_time

                if step % 1 == 0:
                    # learning_rate = read_float_from_file('../work/lr.txt', default=0.1)
                    # momentum = read_float_from_file('../work/momentum.txt', default=0.9)
                    if step < 100:
                        learning_rate = 0.0003  # to stabilize initially
                    else:
                        learning_rate = lr_base * 0.5 ** (float(step - 100) / lr_half_life)
                    momentum = 0.9
                    summary_writer.add_summary(make_summary('learningrate', learning_rate), step)
                    summary_writer.add_summary(make_summary('momentum', momentum), step)
                feed_dict[learning_rate_ph] = learning_rate
                feed_dict[momentum_ph] = momentum

                start_time = time.time()
                _, loss_value, accuracy_value, outputs_value = sess.run([train_op, total_loss, accuracy, model_outputs],
                                                                        feed_dict=feed_dict)
                train_time = time.time() - start_time

                total_loss_avg.add(loss_value)
                accuracy_avg.add(100 * accuracy_value)
                # print "outputs_value ="
                # print outputs_value.flatten()
                # print "feed_dict[outputs_ph] ="
                # print feed_dict[outputs_ph].flatten()

                if np.isnan(loss_value):
                    print "Model diverged with loss = Nan"
                    return
                # assert not np.isnan(loss_value), 'Model diverged with loss = NaN'

                if step >= max_steps:
                    return

                if step % 10 == 0:
                    total_loss_avg.write(summary_writer, step)
                    accuracy_avg.write(summary_writer, step)

                full_step_time = time.time() - last_step_ref_time
                last_step_ref_time = time.time()

                if step % 1 == 0:
                    minibatch_size = feed_dict[feature_planes].shape[0]
                    examples_per_sec = minibatch_size / full_step_time
                    print "%s: step %d, lr=%.6f, mom=%.2f, loss = %.4f, accuracy = %.2f%% (mb_size=%d, %.1f examples/sec), (load=%.3f train=%.3f total=%0.3f sec/step)" % \
                          (datetime.now(), step, learning_rate, momentum, loss_value, 100 * accuracy_value,
                           minibatch_size, examples_per_sec, load_time, train_time, full_step_time)
                    if step % 10 == 0:
                        summary_writer.add_summary(make_summary('examples/sec', examples_per_sec), step)
                        summary_writer.add_summary(make_summary('step', step), step)

                if step % 1000 == 0 and step != 0:
                    # print "WARNING: CHECKPOINTS TURNED OFF!!"
                    saver.save(sess, os.path.join(model.train_dir, "checkpoints", "model.ckpt"), global_step=step)

                step += 1

class Linear:
    def __init__(self, N, Nfeat):
        self.train_dir = "/Users/Savanna/Documents/School/Fall\ 2017/COMP4905/blokus-AI/tf/train_dirs/linear_N%d_fe%d" % (N, Nfeat)
        self.N = N
        self.Nfeat = Nfeat
    def inference(self, feature_planes, N, Nfeat):
        features_flat = tf.reshape(feature_planes, [-1, N*N*Nfeat])
        weights = tf.Variable(tf.constant(0.0, shape=[N*N*Nfeat, 1]), name='weights')
        #weights = tf.constant(0.0, shape=[N*N*Nfeat, 1])
        bias = tf.Variable(tf.constant(0.0, shape=[1]))
        out = tf.matmul(features_flat, weights) + bias
        #out = tf.matmul(features_flat, weights)
        score = tf.tanh(out)
        return score

class Evaluator:
    def __init__(self):
        self.model = Linear(20, 7)

        # build the graph
        with tf.Graph().as_default():
            with tf.device('/cpu:0'):
                self.feature_planes = tf.placeholder(tf.float32, shape=[None, self.model.N, self.model.N, self.model.Nfeat], name='feature_planes')
                self.score_op = self.model.inference(self.feature_planes, self.model.N, self.model.Nfeat)
                saver = tf.train.Saver(tf.trainable_variables())
                init = tf.initialize_all_variables()
                self.sess = tf.Session(config=tf.ConfigProto(log_device_placement=False))
                self.sess.run(init)
                checkpoint_dir = os.path.join(self.model.train_dir, 'checkpoints')
                restore_from_checkpoint(self.sess, saver, checkpoint_dir)

    def evaluate(self, board):
        board_feature_planes = Features.make_feature_planes_stones_4liberties_4history_ko_4captures(board, board.color_to_play).astype(np.float32)
        Normalization.apply_featurewise_normalization_C(board_feature_planes)
        feed_dict = {self.feature_planes: board_feature_planes.reshape(1,self.model.N,self.model.N,self.model.Nfeat)}
        score = np.asscalar(self.sess.run(self.score_op, feed_dict))
        return score