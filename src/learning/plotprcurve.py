
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import auc, average_precision_score, precision_recall_curve


def prcurve_from_file(pr_filename, confusion_filename, y_real, y_proba, colorname):
    prcurve = pd.read_csv(pr_filename, sep='\t', index_col=None)
    precision = prcurve['precision']
    recall = prcurve['recall']
    confusion = pd.read_csv(confusion_filename, sep='\t', index_col=None)
     
    # Plotting each individual PR Curve
    plt.plot(recall, precision, lw=1, alpha=0.3, color=colorname,
             #label='PR fold %d (AUC = %0.2f)' % (i, average_precision_score(confusion['Significant'], confusion['y_prob']))
            )
    
    y_real.append(confusion['Significant'])
    y_proba.append(confusion['y_prob'])


def ABC_predict(inputfile, inputindex=None):
    ABC_pd = pd.read_csv(inputfile, sep="\t", index_col=0)
    if inputindex is not None:
      ABC_index = pd.read_csv(inputindex, sep="\t", index_col=0).index
      ABC_pd = ABC_pd.filter(items=ABC_index, axis=0)

    ABC_score = ABC_pd['ABC.Score'] 
    distance = 1/np.log(ABC_pd['distance'])
    y = ABC_pd['Significant'].astype(int)
    ABC_test = pd.concat([y, distance, ABC_score], axis=1)

    ABC_test['y_pred'] = ABC_test['ABC.Score'] > 0.022
    ABC_test['y_pred'] = ABC_test['y_pred'].astype(int)
    return ABC_test



if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--traindir', required=True, help="directory containing pr_curve and confusion from training")
  parser.add_argument('--testdir', required=True, help="directory containing  pr_curve and confusion from test")
  parser.add_argument('--studyname', required=True, help="studyname used as prefix for filenames")
  parser.add_argument('--testname', required=True, help="test data label")
  args=parser.parse_args()

  train_dir = args.traindir
  test_dir = args.testdir
  studyname = args.studyname
  testname = args.testname

  pr_cv = [
          train_dir+"/"+studyname+".2pass.pr_curve.xgb.0.txt",
          train_dir+"/"+studyname+".2pass.pr_curve.xgb.1.txt",
          train_dir+"/"+studyname+".2pass.pr_curve.xgb.2.txt",
          train_dir+"/"+studyname+".2pass.pr_curve.xgb.3.txt", 
          ]
  confusion_cv = [
      train_dir+"/"+studyname+".2pass.confusion.xgb.0.txt",
      train_dir+"/"+studyname+".2pass.confusion.xgb.1.txt",
      train_dir+"/"+studyname+".2pass.confusion.xgb.2.txt",
      train_dir+"/"+studyname+".2pass.confusion.xgb.3.txt",
      ]
  pr_test = [
          test_dir+"/pr_curve."+studyname+".2pass.save.0.txt",
          test_dir+"/pr_curve."+studyname+".2pass.save.1.txt",
          test_dir+"/pr_curve."+studyname+".2pass.save.2.txt",
          test_dir+"/pr_curve."+studyname+".2pass.save.3.txt", 
          ]
  confusion_test = [
      test_dir+"/confusion."+studyname+".2pass.save.0.txt",
      test_dir+"/confusion."+studyname+".2pass.save.1.txt",
      test_dir+"/confusion."+studyname+".2pass.save.2.txt",
      test_dir+"/confusion."+studyname+".2pass.save.3.txt",
      ]

  train_inputfile  = train_dir+"/"+studyname+".learninginput.txt"
  test_inputfile  = test_dir+"/applyinput.txt"
  Xfeatures_cv = [
      train_dir+"/"+studyname+".2pass.Xtest.0.txt",
      train_dir+"/"+studyname+".2pass.Xtest.1.txt",
      train_dir+"/"+studyname+".2pass.Xtest.2.txt",
      train_dir+"/"+studyname+".2pass.Xtest.3.txt",
  ]
  Xfeatures_test = test_dir+"/Xfeatures."+studyname+".2pass.save.0.txt",
  

  i = 0
  y_real_cv = []
  y_proba_cv = []

  fig, axis = plt.subplots(nrows=1, ncols=1, figsize=(6, 6))
  for i in range(4):
      prcurve_from_file(pr_cv[i], confusion_cv[i], y_real_cv, y_proba_cv, 'blue')
      i += 1

  y_real_cv = np.concatenate(y_real_cv)
  y_proba_cv = np.concatenate(y_proba_cv)
  precision, recall, _ = precision_recall_curve(y_real_cv, y_proba_cv)
  AUCPR=auc(recall, precision)
  plt.plot(recall, precision, color='blue',
           label=r'Test(outer fold CV) (AUC = %0.2f)' % (average_precision_score(y_real_cv, y_proba_cv)),
           #label=r'Test(outer fold CV) (AUC = %0.2f)' % (AUCPR),
           lw=2, alpha=.8)

  ABC_cv = pd.DataFrame()
  for i in range(4):
      ABC_fold = ABC_predict(train_inputfile, Xfeatures_cv[i])
      ABC_cv = pd.concat([ABC_cv, ABC_fold]) 

  ABC_cv = ABC_cv[['Significant','y_pred', 'ABC.Score', 'distance']]
  ABC_cv.to_csv('ABC.gasperini.outerCV.confusion.txt', sep='\t')

  ABC_cv = ABC_cv.dropna()
  precision, recall, thresholds = precision_recall_curve(ABC_cv['Significant'], ABC_cv['ABC.Score'])
  AUCPR=auc(recall, precision)
  plt.plot(recall, precision, color='green',
           label=r'ABC_score(outer fold data) (AUC = %0.2f)' % (average_precision_score(ABC_cv['Significant'], ABC_cv['ABC.Score'])),
           #label=r'ABC_score (AUC = %0.2f)' % (AUCPR),
           lw=2, alpha=.8)

  precision, recall, thresholds = precision_recall_curve(ABC_cv['Significant'], ABC_cv['distance'])
  AUCPR=auc(recall, precision)
  plt.plot(recall, precision, color='black',
           label=r'distance(outer fold data) (AUC = %0.2f)' % (average_precision_score(ABC_cv['Significant'], ABC_cv['distance'])),
           #label=r'distance (AUC = %0.2f)' % (AUCPR),
           lw=2, alpha=.8)

  plt.xlim([-0.05, 1.05])
  plt.ylim([-0.05, 1.05])
  plt.xlabel('Recall')
  plt.ylabel('Precision')
  plt.title('PR curve')
  plt.legend(loc="upper right")
  plt.show()

  plt.savefig('prcurve.outerCV.pdf')
  plt.close()





  # now let's plot the test set performance 

  y_real_test = []
  y_proba_test = []

  fig, axis = plt.subplots(nrows=1, ncols=1, figsize=(6, 6))
  for i in range(4):
      prcurve_from_file(pr_test[i], confusion_test[i], y_real_test, y_proba_test, 'red')
      i += 1

  y_real_test = np.concatenate(y_real_test)
  y_proba_test = np.concatenate(y_proba_test)

  precision, recall, _ = precision_recall_curve(y_real_test, y_proba_test)
  AUCPR=auc(recall, precision)
  avgPrecision = average_precision_score(y_real_test, y_proba_test)
  plt.plot(recall, precision, color='red',
           label=r'Test: %s (AUC = %0.2f)' % (testname, avgPrecision),
           #label=r'Test: %s (AUC = %0.2f)' % (AUCPR),
           lw=2, alpha=.8)


  ABC_test = ABC_predict(test_inputfile)
  ABC_test = ABC_test[['Significant','y_pred', 'ABC.Score', 'distance']]
  ABC_test.to_csv('ABC.test.'+testname+'.confusion.txt', sep='\t')

  ABC_test = ABC_test.dropna()
  precision, recall, thresholds = precision_recall_curve(ABC_test['Significant'], ABC_test['ABC.Score'])
  AUCPR=auc(recall, precision)
  avgPrecision = average_precision_score(ABC_test['Significant'], ABC_test['ABC.Score'])
  plt.plot(recall, precision, color='green',
           label=r'ABC_score: %s (AUC = %0.2f)' % (testname, avgPrecision),
           #label=r'ABC_score (AUC = %0.2f)' % (AUCPR),
           lw=2, alpha=.8)

  precision, recall, thresholds = precision_recall_curve(ABC_test['Significant'], ABC_test['distance'])
  AUCPR=auc(recall, precision)
  avgPrecision = average_precision_score(ABC_test['Significant'], ABC_test['distance'])
  plt.plot(recall, precision, color='black',
           label=r'distance: %s (AUC = %0.2f)' % (testname, avgPrecision),
           #label=r'distance (AUC = %0.2f)' % (AUCPR),
           lw=2, alpha=.8)


  plt.xlim([-0.05, 1.05])
  plt.ylim([-0.05, 1.05])
  plt.xlabel('Recall')
  plt.ylabel('Precision')
  plt.title('PR curve')
  plt.legend(loc="upper right")
  plt.show()

  plt.savefig('prcurve.test.'+testname+'.pdf')
  plt.close()





