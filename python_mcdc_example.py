#!/usr/bin/env python
import environ
from opinion.opinion_core.models import *
import numpy as np
from opinion.includes.queryutils import *
import scipy.io
import itertools
import scipy.linalg


#returns a list of tuples
def commonRatingsList(commentTuple):
	ratingPreList1 = CommentAgreement.objects.filter(is_current = True, comment = commentTuple[0])
	ratingUserSet1 = ratingPreList1.values_list('rater', flat=True)
	ratingList2 = CommentAgreement.objects.filter(is_current = True, comment = commentTuple[1], rater__in=ratingUserSet1).order_by('id')
	ratingUserSet2 = ratingList2.values_list('rater', flat=True)
	ratingList1 = ratingPreList1.filter(rater__in = ratingUserSet2).order_by('id')
	commonRatings = zip(ratingList1.values_list('agreement',flat=True), ratingList2.values_list('agreement',flat=True))
	return np.transpose(np.array(commonRatings))

#calculates the correlation cofficient r and returns (1- r^2)
def correlationFromMattrix(npCommentRatingArray):
	R = np.corrcoef(npCommentRatingArray)

	size = np.shape(R)
	if size[0] == 0:
		r = 1.0
	else:
		r = 1-sqrt(max(R[0,1],0))#*R[0,1]
		r=  r*(np.sum(np.mean(npCommentRatingArray, axis=1)))
		if np.isnan(r):
			r = 1.0

	return r
	


#comments above k ratings
comments = []
id2Index = {}
index = 0
for c in DiscussionComment.objects.filter(id__gte = 15):
	if CommentAgreement.objects.filter(comment = c, is_current=True).count() > 10:
		comments.append(c)
		id2Index[c.id] = index
		index = index + 1

adjacency_matrix = np.zeros((len(comments),len(comments)))

#theta join of the comments with itself
theta_join = itertools.ifilter(lambda x: x[0].id > x[1].id, itertools.product(comments, comments))

#fill adjacency matrix
for c in theta_join:
	adjacency_matrix[id2Index[c[0].id], id2Index[c[1].id]] = correlationFromMattrix(commonRatingsList(c))

W = np.mat(adjacency_matrix + np.transpose(adjacency_matrix))
Sums = np.sum(adjacency_matrix, axis=0)
"""
for i in range(0,np.shape(Sums)[0]):
	if Sums[i] != 0:
		Sums[i] = 1.0 / np.sqrt(Sums[i])
"""

D = np.mat(np.diag(Sums))
L = D-W

print L

w, v = scipy.linalg.eig(L,D)
idx = w.argsort()[-2]
ranks_list = zip(v[:,idx]-np.mean(v[:,idx]), comments)
ranks_list.sort(reverse=True)
print ranks_list

