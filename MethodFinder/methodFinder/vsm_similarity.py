import pickle
import json
import csv

from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Similarity:
    def __init__(self, src_files):
        self.src_files = src_files
        self.src_strings = [' '.join(src['doc'])
                            for src in self.src_files.values()]
    
    def calculate_similarity(self, src_tfidf, reports_tfidf):
        """Calculatnig cosine similarity between source files and bug reports"""

        # Normalizing the length of source files
        src_lenghts = np.array([float(len(src_str.split()))
                                for src_str in self.src_strings]).reshape(-1, 1)
        min_max_scaler = preprocessing.MinMaxScaler()
        normalized_src_len = min_max_scaler.fit_transform(src_lenghts)
         
        # Applying logistic length function
        src_len_score = 1 / (1 + np.exp(-12 * normalized_src_len))
        
        simis = []
        for report in reports_tfidf:
            s = cosine_similarity(src_tfidf, report)
            
            # revised VSM score calculation
            rvsm_score = s
            
            normalized_score = np.concatenate(
                min_max_scaler.fit_transform(rvsm_score)
            )
            
            simis.append(normalized_score.tolist())
            
        return simis
    
    def find_similars(self, report):
        """Calculating tf-idf vectors for source and report sets
        to find similar source files for each bug report.
        """
        tfidf = TfidfVectorizer(sublinear_tf=True, smooth_idf=False)
        src_tfidf = tfidf.fit_transform(self.src_strings)

        if type(report[0]) == list:
            simis = []
            for i in range(len(report)):
                reports_tfidf = tfidf.transform([' '.join(report[i])])
                simis.append(self.calculate_similarity(src_tfidf, reports_tfidf))
        else:
            reports_tfidf = tfidf.transform([' '.join(report)])
            simis = self.calculate_similarity(src_tfidf, reports_tfidf)

        return simis

def main(userName, repoName):
    
    # Unpickle preprocessed data
    with open(userName + '/preprocessed_src.pickle', 'rb') as file:
        src_files = pickle.load(file)
    with open(userName + '/preprocessed_reports.pickle', 'rb') as file:
        bug_reports = pickle.load(file)


    csv_file = open(userName + '/' + userName + '-' + repoName + '-issues.csv')
    csvReader = csv.reader(csv_file, delimiter=',', )

    next(csvReader)
    for row in csvReader:
        issue_number = row[0]
        print(issue_number + " for vsm similarity")
        
        writeFile = open(userName + '/' + userName + '-' + issue_number + '.txt', 'a')

        writeFile.write("\n\n\nVSM similarity result: \n")



        sm = Similarity(src_files)
        simis = sm.find_similars(bug_reports[issue_number])

        method_names = [src['methodName'] for src in src_files.values()]

        # print(simis)
        method = []
        if type(simis[0]) == list:
            for i in range(len(simis)):
                n = -3
                method_indices = np.argsort(simis[i][0])[n:]
                method.append([method_names[j] for j in method_indices[::-1]])
        else:
            n = -3
            method_indices = np.argsort(simis[0])[n:]
            method.append([method_names[j] for j in method_indices[::-1]])

        for i in range(len(bug_reports[issue_number])):
#            print(len(bug_reports[issue_number]))
#            print(len(method))
#            print (i)

            for j in range(len(bug_reports[issue_number][i])):
                writeFile.write(bug_reports[issue_number][i][j] + ';\t')

            writeFile.write('\n')

            if len(method) > i:
                for k in range(len(method[i])):
                    writeFile.write(method[i][k] + ';\t')

            writeFile.write('\n~~~~~~~~~~~~~~~~~~~~~~\n')

        writeFile.close()







if __name__ == '__main__':
    userName = "nextcloud"
    repoName = "android"
    main(userName, repoName)
    
    userName = "TeamAmaze"
    repoName = "AmazeFileManager"
    main(userName, repoName)
    
    userName = "pockethub"
    repoName = "PocketHub"
    main(userName, repoName)
    
    userName = "k9mail"
    repoName = "k-9"
    main(userName, repoName)
