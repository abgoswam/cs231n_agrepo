
# coding: utf-8

# # Image features exercise
# *Complete and hand in this completed worksheet (including its outputs and any supporting code outside of the worksheet) with your assignment submission. For more details see the [assignments page](http://vision.stanford.edu/teaching/cs231n/assignments.html) on the course website.*
# 
# We have seen that we can achieve reasonable performance on an image classification task by training a linear classifier on the pixels of the input image. In this exercise we will show that we can improve our classification performance by training linear classifiers not on raw pixels but on features that are computed from the raw pixels.
# 
# All of your work for this exercise will be done in this notebook.

# In[1]:

from __future__ import print_function
import random
import numpy as np
from cs231n.data_utils import load_CIFAR10
import matplotlib.pyplot as plt


get_ipython().magic('matplotlib inline')
plt.rcParams['figure.figsize'] = (10.0, 8.0) # set default size of plots
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'

# for auto-reloading extenrnal modules
# see http://stackoverflow.com/questions/1907993/autoreload-of-modules-in-ipython
get_ipython().magic('load_ext autoreload')
get_ipython().magic('autoreload 2')


# ## Load data
# Similar to previous exercises, we will load CIFAR-10 data from disk.

# In[ ]:

from cs231n.features import color_histogram_hsv, hog_feature

def get_CIFAR10_data(num_training=49000, num_validation=1000, num_test=1000):
    # Load the raw CIFAR-10 data
    cifar10_dir = 'cs231n/datasets/cifar-10-batches-py'
    X_train, y_train, X_test, y_test = load_CIFAR10(cifar10_dir)
    
    # Subsample the data
    mask = list(range(num_training, num_training + num_validation))
    X_val = X_train[mask]
    y_val = y_train[mask]
    mask = list(range(num_training))
    X_train = X_train[mask]
    y_train = y_train[mask]
    mask = list(range(num_test))
    X_test = X_test[mask]
    y_test = y_test[mask]
    
    return X_train, y_train, X_val, y_val, X_test, y_test

X_train, y_train, X_val, y_val, X_test, y_test = get_CIFAR10_data()


# ## Extract Features
# For each image we will compute a Histogram of Oriented
# Gradients (HOG) as well as a color histogram using the hue channel in HSV
# color space. We form our final feature vector for each image by concatenating
# the HOG and color histogram feature vectors.
# 
# Roughly speaking, HOG should capture the texture of the image while ignoring
# color information, and the color histogram represents the color of the input
# image while ignoring texture. As a result, we expect that using both together
# ought to work better than using either alone. Verifying this assumption would
# be a good thing to try for the bonus section.
# 
# The `hog_feature` and `color_histogram_hsv` functions both operate on a single
# image and return a feature vector for that image. The extract_features
# function takes a set of images and a list of feature functions and evaluates
# each feature function on each image, storing the results in a matrix where
# each column is the concatenation of all feature vectors for a single image.

# In[ ]:

from cs231n.features import *

num_color_bins = 10 # Number of bins in the color histogram
feature_fns = [hog_feature, lambda img: color_histogram_hsv(img, nbin=num_color_bins)]
X_train_feats = extract_features(X_train, feature_fns, verbose=True)
X_val_feats = extract_features(X_val, feature_fns)
X_test_feats = extract_features(X_test, feature_fns)

# Preprocessing: Subtract the mean feature
mean_feat = np.mean(X_train_feats, axis=0, keepdims=True)
X_train_feats -= mean_feat
X_val_feats -= mean_feat
X_test_feats -= mean_feat

# Preprocessing: Divide by standard deviation. This ensures that each feature
# has roughly the same scale.
std_feat = np.std(X_train_feats, axis=0, keepdims=True)
X_train_feats /= std_feat
X_val_feats /= std_feat
X_test_feats /= std_feat

# Preprocessing: Add a bias dimension
X_train_feats = np.hstack([X_train_feats, np.ones((X_train_feats.shape[0], 1))])
X_val_feats = np.hstack([X_val_feats, np.ones((X_val_feats.shape[0], 1))])
X_test_feats = np.hstack([X_test_feats, np.ones((X_test_feats.shape[0], 1))])


# ## Train SVM on features
# Using the multiclass SVM code developed earlier in the assignment, train SVMs on top of the features extracted above; this should achieve better results than training SVMs directly on top of raw pixels.

# In[ ]:

# Use the validation set to tune the learning rate and regularization strength

from cs231n.classifiers.linear_classifier import LinearSVM

learning_rates = [1e-4, 1e-3, 1e-2, 1e-1]
regularization_strengths = [1e0, 1e1, 1e2]

results = {}
best_val = -1
best_svm = None

pass
################################################################################
# TODO:                                                                        #
# Use the validation set to set the learning rate and regularization strength. #
# This should be identical to the validation that you did for the SVM; save    #
# the best trained classifer in best_svm. You might also want to play          #
# with different numbers of bins in the color histogram. If you are careful    #
# you should be able to get accuracy of near 0.44 on the validation set.       #
################################################################################
#pass
for _l in learning_rates:
    for _r in regularization_strengths:
        svm = LinearSVM()
        loss_hist = svm.train(X_train_feats, y_train, learning_rate=_l, reg=_r,
                      num_iters=1500, verbose=False)
                
        y_train_pred = svm.predict(X_train_feats)
        train_accuracy = np.mean(y_train == y_train_pred)
        print('training accuracy: {0}'.format(train_accuracy))
        
        y_val_pred = svm.predict(X_val_feats)
        val_accuracy = np.mean(y_val == y_val_pred)
        print('validation accuracy: {0}'.format(val_accuracy))

        results[(_l, _r)] = (train_accuracy, val_accuracy)
        if (val_accuracy > best_val):
            best_val = val_accuracy
            best_svm = svm

################################################################################
#                              END OF YOUR CODE                                #
################################################################################

# Print out results.
for lr, reg in sorted(results):
    train_accuracy, val_accuracy = results[(lr, reg)]
    print('lr %e reg %e train accuracy: %f val accuracy: %f' % (
                lr, reg, train_accuracy, val_accuracy))
    
print('best validation accuracy achieved during cross-validation: %f' % best_val)


# In[ ]:

# Evaluate your trained SVM on the test set
y_test_pred = best_svm.predict(X_test_feats)
test_accuracy = np.mean(y_test == y_test_pred)
print(test_accuracy)


# In[ ]:

# An important way to gain intuition about how an algorithm works is to
# visualize the mistakes that it makes. In this visualization, we show examples
# of images that are misclassified by our current system. The first column
# shows images that our system labeled as "plane" but whose true label is
# something other than "plane".

examples_per_class = 8
classes = ['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
for cls, cls_name in enumerate(classes):
    idxs = np.where((y_test != cls) & (y_test_pred == cls))[0]
    idxs = np.random.choice(idxs, examples_per_class, replace=False)
    for i, idx in enumerate(idxs):
        plt.subplot(examples_per_class, len(classes), i * len(classes) + cls + 1)
        plt.imshow(X_test[idx].astype('uint8'))
        plt.axis('off')
        if i == 0:
            plt.title(cls_name)
plt.show()


# ### Inline question 1:
# Describe the misclassification results that you see. Do they make sense?

# ## Neural Network on image features
# Earlier in this assigment we saw that training a two-layer neural network on raw pixels achieved better classification performance than linear classifiers on raw pixels. In this notebook we have seen that linear classifiers on image features outperform linear classifiers on raw pixels. 
# 
# For completeness, we should also try training a neural network on image features. This approach should outperform all previous approaches: you should easily be able to achieve over 55% classification accuracy on the test set; our best model achieves about 60% classification accuracy.

# In[ ]:

print(X_train_feats.shape)


# In[ ]:

from cs231n.classifiers.neural_net import TwoLayerNet

input_dim = X_train_feats.shape[1]
hidden_dim = 500
num_classes = 10

best_net = None

################################################################################
# TODO: Train a two-layer neural network on image features. You may want to    #
# cross-validate various parameters as in previous sections. Store your best   #
# model in the best_net variable.                                              #
################################################################################
#pass

learning_rates = [1]
regularization_strengths = [0,0.25,0.5,1]
learning_rate_decay = [1, 0.95, 0.8]

for _l in learning_rates:
  for _r in regularization_strengths:
    for _d in learning_rate_decay:  
        net = TwoLayerNet(input_dim, hidden_dim, num_classes)
        # Train the network
        stats = net.train(X_train_feats, y_train, X_val_feats, y_val,
            num_iters=1000, batch_size=200,
            learning_rate=_l, learning_rate_decay=_d,
            reg=_r, verbose=True)

        # Predict on the validation set
        val_accuracy = (net.predict(X_val_feats) == y_val).mean()
        print('Validation accuracy: {0}. learning rate : {1}. regularization strength : {2}. decay : {3} '.format(val_accuracy, _l, _r, _d))
        
        if (val_accuracy > best_val):
            best_val = val_accuracy
            best_net = net
            best_stats = stats

# Plot the loss function and train / validation accuracies
plt.subplot(2, 1, 1)
plt.plot(best_stats['loss_history'])
plt.title('Loss history')
plt.xlabel('Iteration')
plt.ylabel('Loss')

plt.subplot(2, 1, 2)
plt.plot(best_stats['train_acc_history'], label='train')
plt.plot(best_stats['val_acc_history'], label='val')
plt.title('Classification accuracy history')
plt.xlabel('Epoch')
plt.ylabel('Clasification accuracy')
plt.grid(True)
plt.legend(loc=0)
plt.show()

################################################################################
#                              END OF YOUR CODE                                #
################################################################################


# In[ ]:

# Run your neural net classifier on the test set. You should be able to
# get more than 55% accuracy.

test_acc = (best_net.predict(X_test_feats) == y_test).mean()
print(test_acc)


# # Bonus: Design your own features!
# 
# You have seen that simple image features can improve classification performance. So far we have tried HOG and color histograms, but other types of features may be able to achieve even better classification performance.
# 
# For bonus points, design and implement a new type of feature and use it for image classification on CIFAR-10. Explain how your feature works and why you expect it to be useful for image classification. Implement it in this notebook, cross-validate any hyperparameters, and compare its performance to the HOG + Color histogram baseline.

from cs231n.classifiers import Softmax

X2_train_feats = np.dot(X_train_feats, best_net.params['W1']) + best_net.params['b1']
X2_val_feats = np.dot(X_val_feats, best_net.params['W1']) + best_net.params['b1']
X2_test_feats = np.dot(X_test_feats, best_net.params['W1']) + best_net.params['b1']

learning_rates = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0]
regularization_strengths = [0, 1e1]

results = {}
best_val = -1
best_softmax = None

################################################################################
# Softmax
################################################################################
for _l in learning_rates:
    for _r in regularization_strengths:
        softmax = Softmax()
        loss_hist = softmax.train(X2_train_feats, y_train, learning_rate=_l, reg=_r,
                      num_iters=1500, verbose=False)
                
        y_train_pred = softmax.predict(X2_train_feats)
        train_accuracy = np.mean(y_train == y_train_pred)
        
        y_val_pred = softmax.predict(X2_val_feats)
        val_accuracy = np.mean(y_val == y_val_pred)
        print("train accuracy:{0}, val accuracy : {1}".format(train_accuracy, val_accuracy))

        results[(_l, _r)] = (train_accuracy, val_accuracy)
        if (val_accuracy > best_val):
            best_val = val_accuracy
            best_softmax = softmax
    
# Print out results.
for lr, reg in sorted(results):
    train_accuracy, val_accuracy = results[(lr, reg)]
    print('lr %e reg %e train accuracy: %f val accuracy: %f' % (lr, reg, train_accuracy, val_accuracy))
    
print('best validation accuracy achieved during cross-validation: %f' % best_val)

y_test_pred_softmax2 = best_softmax.predict(X2_test_feats)
test_acc_softmax2 = (y_test_pred_softmax2 == y_test).mean()
print("Prediction accuracy Softmax (with new features): {0}".format(test_acc_softmax2))


# # Bonus: Do something extra!
# Use the material and code we have presented in this assignment to do something interesting. Was there another question we should have asked? Did any cool ideas pop into your head as you were working on the assignment? This is your chance to show off!

#learning_rates = [1e-7, 5e-7]
#regularization_strengths = [2.5e4, 5e4]
learning_rates = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0]
regularization_strengths = [0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6]

results = {}
best_val = -1
best_softmax = None

################################################################################
# Softmax
################################################################################
for _l in learning_rates:
    for _r in regularization_strengths:
        softmax = Softmax()
        loss_hist = softmax.train(X_train_feats, y_train, learning_rate=_l, reg=_r,
                      num_iters=1500, verbose=False)
                
        y_train_pred = softmax.predict(X_train_feats)
        train_accuracy = np.mean(y_train == y_train_pred)
        
        y_val_pred = softmax.predict(X_val_feats)
        val_accuracy = np.mean(y_val == y_val_pred)
        print("train accuracy:{0}, val accuracy : {1}".format(train_accuracy, val_accuracy))

        results[(_l, _r)] = (train_accuracy, val_accuracy)
        if (val_accuracy > best_val):
            best_val = val_accuracy
            best_softmax = softmax
    
# Print out results.
for lr, reg in sorted(results):
    train_accuracy, val_accuracy = results[(lr, reg)]
    print('lr %e reg %e train accuracy: %f val accuracy: %f' % (
                lr, reg, train_accuracy, val_accuracy))
    
print('best validation accuracy achieved during cross-validation: %f' % best_val)

#####################################################

y_test_pred_svm = best_svm.predict(X_test_feats)
y_test_pred_softmax = best_softmax.predict(X_test_feats)
y_test_pred_net = best_net.predict(X_test_feats)

test_acc_svm = (y_test_pred_svm == y_test).mean()
print("Prediction accuracy SVM : {0}".format(test_acc_svm))

test_acc_softmax = (y_test_pred_softmax == y_test).mean()
print("Prediction accuracy Softmax : {0}".format(test_acc_softmax))

test_acc_net = (y_test_pred_net == y_test).mean()
print("Prediction accuracy neural net : {0}".format(test_acc_net))

plt.subplot(2,2,1)
plt.hist(y_test)
plt.title("Histogram of correct labels")

plt.subplot(2,2,2)
plt.hist(y_test_pred_svm)
plt.title("Histogram of predicted labels (SVM)")

plt.subplot(2,2,3)
plt.hist(y_test_pred_softmax)
plt.title("Histogram of predicted labels (Softmax)")

plt.subplot(2,2,4)
plt.hist(y_test_pred_net)
plt.title("Histogram of predicted labels (Neural Net)")
plt.show()

from collections import Counter 

y_test_pred_ensemble = []
for i in range(len(y_test)):
    predicted_classes = [y_test_pred_svm[i], y_test_pred_softmax[i], y_test_pred_net[i]]
    predicted_counter = Counter(predicted_classes)
    
    predicted_counter_mostcommon = predicted_counter.most_common(1)
    
    if predicted_counter_mostcommon[0][1] > 1:
#        if majority exists, use that an prediction
        y_test_pred_ensemble.append(predicted_counter_mostcommon[0][0])
    else:
#        take the NN prediction
        y_test_pred_ensemble.append(y_test_pred_net[i])
        
test_acc_ensemble = (y_test_pred_ensemble == y_test).mean()
print("Prediction accuracy using ensemble : {0}".format(test_acc_ensemble))    





