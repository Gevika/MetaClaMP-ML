import argparse
import pandas as pd
from sklearn.model_selection import LeaveOneOut
from sklearn.svm import LinearSVC
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import roc_auc_score
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import ExtraTreesClassifier

parser = argparse.ArgumentParser()
parser.add_argument("input", help='input sample .tsv file for ML script', type=str)
args = parser.parse_args()

humann2=pd.read_csv(args.input, index_col=0, sep='\t')
X = humann2[humann2.columns[2:]]
y=humann2['flag']
yy=y
#binarize the labels
from sklearn.preprocessing import Binarizer
############Feature selection ############################3
rf_clf = RandomForestClassifier(n_estimators=100)
rf_clf = rf_clf.fit(X, y)
model = SelectFromModel(rf_clf, prefit=True)
X_new = model.transform(X)
print(X_new.shape)
idxs_selected = model.get_support(indices=True)
f = X.columns[idxs_selected]
features_dataframe_new=X[f]
print(features_dataframe_new.shape)
f = open("actual_pred",'w')
#############################
from sklearn.model_selection import LeaveOneOut
loo = LeaveOneOut()
loo.get_n_splits(features_dataframe_new)
final_pred_discrete=[]
final_pred=[];
final_actual=[];
for train_index, test_index in loo.split(features_dataframe_new):
	print("TRAIN:", train_index, "TEST:", test_index)
	X_train, X_test = features_dataframe_new.iloc[train_index], features_dataframe_new.iloc[test_index]
	y_train, y_test = yy[train_index], yy[test_index]
	#print(X_train, X_test, y_train, y_test)
	#clf=SVC(kernel='linear',probability=True,class_weight="balanced")
	clf = RandomForestClassifier(n_estimators=100, max_depth=2,random_state=0)
	clf.fit(X_train, y_train.ravel())
	y_pred11 = clf.predict(X_test)
	y_p_d=y_pred11.tolist()
	final_pred_discrete.extend(y_p_d)
	y_p_score=clf.predict_proba(X_test) ##### getting prob scores (coressponding to SVM score)
	y_t=y_test.tolist() # converting np array to list
	y_predicted=y_p_score.tolist()
	y_p_s1=[i[1] for i in y_predicted] # feteching 2nd element of 2 d array
	final_pred.extend(y_p_s1)
	final_actual.extend(y_t)
res = "\n".join("{} {}".format(x, y) for x, y in zip(final_actual, final_pred))
print(res,file=f)
print(classification_report(final_actual, final_pred_discrete))
print("AUROC")
print(roc_auc_score(final_actual, final_pred))
