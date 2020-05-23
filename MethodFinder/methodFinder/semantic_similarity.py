import en_vectors_web_lg

import pickle
import json
import csv

import numpy as np
from sklearn.preprocessing import MinMaxScaler

def calculate_similarity(src_docs, bug_reports):
    
    # Loading word vectors
    nlp = en_vectors_web_lg.load()
    
    min_max_scaler = MinMaxScaler()
    
    all_simis = []
    for report in bug_reports.values():
        report_nlp = nlp(' '.join(report))
        scores = []
        for src_doc in src_docs.values():
            src_nlp = nlp(' '.join(src_doc))
            simi = report_nlp.similarity(src_nlp)
            scores.append(simi)
        
        scores = np.array([float(count)
                            for count in scores]).reshape(-1, 1)
        normalized_scores = np.concatenate(
            min_max_scaler.fit_transform(scores)
        )
        
        all_simis.append(normalized_scores.tolist())
        
    return all_simis

def get_similar_methods(src_docs, report):
    # Loading word vectors
    nlp = en_vectors_web_lg.load()
    min_max_scaler = MinMaxScaler()
    methods = []

    if type(report[0]) == list:
        methods = [0]*len(report)
        for i in range(len(report)):
            max_similarity = -1
            report_nlp = nlp(' '.join(report[i]))
            for src_doc_key in src_docs.keys():
                src_nlp = nlp(' '.join(src_docs[src_doc_key]['doc']))
                if src_nlp and src_nlp.vector_norm:
                    simi = report_nlp.similarity(src_nlp)
                    if simi > max_similarity:
                        methods[i] = src_doc_key
                        max_similarity = simi
    else:
        methods = [0]
        max_similarity = -1
        report_nlp = nlp(' '.join(report))
        for src_doc_key in src_docs.keys():
            src_nlp = nlp(' '.join(src_docs[src_doc_key]['doc']))
            if src_nlp and src_nlp.vector_norm:
                simi = report_nlp.similarity(src_nlp)
                if simi > max_similarity:
                    methods[0] = src_doc_key
                    max_similarity = simi


    return methods
    
def main(userName, repoName):
    
    with open(userName + '/preprocessed_src.pickle', 'rb') as file:
        src_files = pickle.load(file)
    with open(userName + '/preprocessed_reports.pickle', 'rb') as file:
        bug_reports = pickle.load(file)


# write a .txt file for all the data.
# in VSM: just append to this doc.

    csv_file = open(userName + '/' + userName + '-' + repoName + '-issues.csv')
    csvReader = csv.reader(csv_file, delimiter=',', )

    next(csvReader)
    for row in csvReader:
        issue_number = row[0]
        print(issue_number)
        methods = get_similar_methods(src_files, bug_reports[issue_number])
        writeFile = open(userName + '/' + userName + '-' + issue_number + '.txt', 'a')

#        writeFile.write("Issue title: ")
#        writeFile.write(row[1])
#        writeFile.write("\n\nIssue detail: ")
#        writeFile.write(row[2])
        writeFile.write("\n\nSemantic similarity result for ONLY COMMENTS: \n")
        print(len(methods))
        for m in methods:
            writeFile.write(m)
            writeFile.write('\n')
        writeFile.close()

if __name__ == '__main__':
#    userName = "nextcloud"
#    repoName = "android"
#    main(userName, repoName)
#    
#    userName = "TeamAmaze"
#    repoName = "AmazeFileManager"
#    main(userName, repoName)
    
    userName = "pockethub"
    repoName = "PocketHub"
    main(userName, repoName)
    
    userName = "k9mail"
    repoName = "k-9"
    main(userName, repoName)
