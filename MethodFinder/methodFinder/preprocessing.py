import string
import pickle
import re
import json
import csv

import inflection
import nltk
from nltk.stem.porter import PorterStemmer

from assets import stop_words, java_keywords

class SrcPreprocessor:
    def __init__(self, file):
        super().__init__()
        self.src_doc = {}

        with open(file) as f:
            src = json.load(f)
            for folder_key in src:
                for file_key in src[folder_key]:
                    for method_key in src[folder_key][file_key]:
                        all_content = ""
                        for key in ['comments']:
                            if isinstance(src[folder_key][file_key][method_key][key], list):
                                all_content =  all_content + " " + " ".join(src[folder_key][file_key][method_key][key])
                            else:
                                all_content =  all_content + " " + src[folder_key][file_key][method_key][key]

                        self.src_doc[folder_key+'.'+file_key+'.'+method_key] = src[folder_key][file_key][method_key]
                        self.src_doc[folder_key+'.'+file_key+'.'+method_key]["doc"] = all_content

    def _split_camelcase(self, tokens):
    
        # Copy tokens
        returning_tokens = tokens[:]
        
        for token in tokens:
            split_tokens = re.split(fr'[{string.punctuation}]+', token)
            
            # If token is split into some other tokens
            if len(split_tokens) > 1:
                returning_tokens.remove(token)
                # Camel case detection for new tokens
                for st in split_tokens:
                    camel_split = inflection.underscore(st).split('_')
                    if len(camel_split) > 1:
                        returning_tokens.append(st)
                        returning_tokens += camel_split
                    else:
                        returning_tokens.append(st)
            else:
                camel_split = inflection.underscore(token).split('_')
                if len(camel_split) > 1:
                    returning_tokens += camel_split
    
        return returning_tokens

    def preprocess(self):
        stemmer = PorterStemmer()
        punctnum_table = str.maketrans({c : None for c in string.punctuation + string.digits})

        for key in self.src_doc:
            # print(self.src_doc[key]['doc'])
            self.src_doc[key]['doc'] = self.src_doc[key]['doc'].strip()
            self.src_doc[key]['doc'] = self.src_doc[key]['doc'].replace("\n","")
            self.src_doc[key]['doc'] = self.src_doc[key]['doc'].replace("\r","")
            self.src_doc[key]['doc'] = nltk.wordpunct_tokenize(self.src_doc[key]['doc'])
            self.src_doc[key]['doc'] = [token.translate(punctnum_table)
                                    for token in self.src_doc[key]['doc']]
            self.src_doc[key]['doc'] = [token for token in self.src_doc[key]['doc']
                                    if token not in stop_words]
            self.src_doc[key]['doc'] = [token for token in self.src_doc[key]['doc']
                                    if token not in java_keywords]
            self.src_doc[key]['doc'] = [token for token in self.src_doc[key]['doc']
                                    if len(token) > 0]
            self.src_doc[key]['doc'] = self._split_camelcase(self.src_doc[key]['doc'])
            # self.src_doc[key]['doc'] = [stemmer.stem(token) for token in self.src_doc[key]['doc']]

        return self.src_doc









class ReportPreprocessor:
    def extract_steps(self, description):
        # pattern = re.compile('[0-9].[.)} ]*[a-zA-Z ]*')
        pattern = re.compile('''[0-9]+[.)} ]+[a-zA-Z '"0-9.,;:/?]+''')
        steps = re.findall(pattern, description)
        punctnum_table = str.maketrans({c : None for c in string.punctuation + string.digits})
        for i in range(len(steps)):
            steps[i] = ' '.join([token.translate(punctnum_table)
                                        for token in steps[i].split()])

        return steps
        
    def _split_camelcase(self, tokens):
    
        # Copy tokens
        returning_tokens = tokens[:]
        
        for token in tokens:
            split_tokens = re.split(fr'[{string.punctuation}]+', token)
            
            # If token is split into some other tokens
            if len(split_tokens) > 1:
                returning_tokens.remove(token)
                # Camel case detection for new tokens
                for st in split_tokens:
                    camel_split = inflection.underscore(st).split('_')
                    if len(camel_split) > 1:
                        returning_tokens.append(st)
                        returning_tokens += camel_split
                    else:
                        returning_tokens.append(st)
            else:
                camel_split = inflection.underscore(token).split('_')
                if len(camel_split) > 1:
                    returning_tokens += camel_split
    
        return returning_tokens

    def preprocess(self, file):
        reports_doc = {}
        stemmer = PorterStemmer()
        punctnum_table = str.maketrans({c : None for c in string.punctuation + string.digits})

        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', )
            next(csv_reader)

            for row in csv_reader:
                key = row[0]
                body = row[2]
                steps = self.extract_steps(body)
                steps = [s for s in steps if len(s)>1]
                if len(steps) > 2:
                    reports_doc[key] = steps
                    reports_doc[key] = [step.strip() for step in reports_doc[key]]
                    reports_doc[key] = [nltk.wordpunct_tokenize(step) for step in reports_doc[key]]
                    for i in range(len(reports_doc[key])):
                        reports_doc[key][i] = [token.translate(punctnum_table)
                                                for token in reports_doc[key][i]]
                        reports_doc[key][i] = [token for token in reports_doc[key][i]
                                                if token not in stop_words]
                        reports_doc[key][i] = [token for token in reports_doc[key][i]
                                                if token not in java_keywords]
                        reports_doc[key][i] = [token for token in reports_doc[key][i]
                                                if len(token) > 0]
                else:
                    reports_doc[key] = body
                    reports_doc[key] = reports_doc[key].strip()
                    reports_doc[key] = nltk.wordpunct_tokenize(reports_doc[key])
                    reports_doc[key] = [token.translate(punctnum_table)
                                            for token in reports_doc[key]]
                    reports_doc[key] = [token for token in reports_doc[key]
                                            if token not in stop_words]
                    reports_doc[key] = [token for token in reports_doc[key]
                                            if token not in java_keywords]
                    reports_doc[key] = [token for token in reports_doc[key]
                                            if len(token) > 0]
        
        return reports_doc

def main(userName, repoName):
    
    scp = SrcPreprocessor("/Users/facade/Documents/GitHub/CSCI8980_ASE_project07/MethodFinder/methodFinder/" + userName + "/result.json")
    src_doc = scp.preprocess()
    with open(userName + '/preprocessed_src.pickle', 'wb') as file:
        pickle.dump(src_doc, file, protocol=pickle.HIGHEST_PROTOCOL)


    # Steps to reproduce
    # 1. Go to a site with text.
    # 2. Tap on the app\'s menu.
    # 3. Choose "Find in page" option.
    ### Expected behavior
    # The search bar is displayed.
    # Actual behavior
    # The search bar is being overlapped by the virtual keyboard.\r\n###

    # print(d)
    # s=srp.extract_steps(d)
    # print(s)
#    reports_doc = srp.preprocess("C:\\Users\\PranayDev\\Documents\\UMN\\ASE\\bugLocalizer\\bug-localization\\data\\issues-extracted\\mozilla-mobile-focus-android-issues.csv")

    srp = ReportPreprocessor()
    reports_doc = srp.preprocess("/Users/facade/Documents/GitHub/CSCI8980_ASE_project07/MethodFinder/methodFinder/" + userName + "/" + userName + "-" + repoName + "-issues.csv")
    with open(userName + '/preprocessed_reports.pickle', 'wb') as file:
        pickle.dump(reports_doc, file, protocol=pickle.HIGHEST_PROTOCOL)
    
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


