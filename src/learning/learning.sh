python src/learning/learning.py --dir data/Gasperini/ --outdir run.all --port 17203 --studyname all --init --infile Gasperini2019.at_scale.ABC.TF.erole.grouped.train.txt
bash src/learning/opt.all.sh
bash src/learning/featureselection.sh
python src/learning/learning.py --dir data/Gasperini/ --outdir run.all --port 17203 --studyname all --dropfeatures
python src/learning/learning.py --dir data/Gasperini/ --outdir run.all --port 17203 --studyname all --init2pass
bash src/learning/opt2pass.sh
python src/learning/learning.py --dir data/Gasperini/ --outdir run.all --port 17203 --studyname all.2pass --test
bash src/learning/apply_model.sh

python src/learning/runshap.py --modeldir run.all/ --studyname all.2pass --outdir apply.all/shap

python src/learning/plotprcurve.py --traindir run.all --testdir apply.all/Fulco/ --studyname all --testname Fulco
python src/learning/plotprcurve.py --traindir run.all --testdir apply.all/Gasperini/ --studyname all --testname chr5,10,15,20

