import numpy as np
import sklearn
import sklearn.datasets
import sklearn.linear_model
import logging_util


class DataReader(object):

    def __init__(self, source, num_samples):
        self.N = num_samples
        self.source = source

    def _read(self):
        X = []
        Y = []
        with open(self.source, 'r') as f:
            for line in f:
                data = line.split(":")
                array = data[4]
                component = array.split("]")
                for i in range(component.__len__()):
                    if len(Y) == self.N:
                        self.add_indexes(X)
                        return X, Y
                    component[i] = component[i].replace("[","")
                    component[i] = component[i][1:]
                    component[i] = component[i].split(",")

                    if len(component[i]) >8:

                        #last value of list goes in as the y value
                        Y.append(component[i][len(component[i])-1])

                        #save the rest as the features
                        X.append(component[i][:len(component[i])-1])

        self.add_indexes(X)
        return X, Y

    def add_indexes(self, X):
        row = 0
        column = 0
        for x in X:
            x.append(column)
            x.append(row)

            if column == 19:
                column = 0
                row +=1
            else: column +=1

    def test_read_sizes(self):
        X, Y = self._read()
        print "%d" % len(Y)
        print "%d" % len(X)

    def get_matrices(self):
        X, Y = self._read()
        X = np.array(X).astype(np.int).transpose()
        Y = np.array(Y).astype(np.int)

        shape_X = X.shape
        shape_Y = Y.shape
        m = shape_X[1]

        if self.N is not -1:
            assert not self.N < m, "Error configuring the number of samples desired (n < m)"
        assert m == shape_X[1], "X has bad shape: incorrect number of samples %d" % shape_X[1]
        assert m == shape_Y[0], "X has bad shape: incorrect number of samples %d" % shape_Y[0]
        #assert self.n_f == shape_X[0], "X has bad shape: incorrect number of features %d" % shape_X[0]

        if self.N > m:
            print "I don't have that many samples available, giving you what I have which is %d samples..." % m

        return X, Y

class logistic_regression_test(object):

    def __init__(self, source, samples = -1):
        data = DataReader(source, samples)
        self.X, self.Y = data.get_matrices()

    def check(self):
        print "Computing logistic regression with %d features and %d samples..." % (self.X.shape[0],self.X.shape[1])
        clf = sklearn.linear_model.LogisticRegressionCV()
        clf.fit(self.X.T, self.Y.T)
        LR_predictions = clf.predict(self.X.T)
        print ('Accuracy of logistic regression: %d ' % float(
            (np.dot(self.Y, LR_predictions) + np.dot(1 - self.Y, 1 - LR_predictions)) / float(self.Y.size) * 100) +
               '% ' + "(percentage of correctly labelled datapoints)")



if __name__ == "__main__":
    #test = logistic_regression_test("logs/ai-training-more.txt")
    #test.check()
    with open("logs/ai-training-more2.txt", 'r') as f:
        for line in f:
            print line