import json

def analyze_comments(file):
    method_count = 0
    comments_count = 0
    commented_methods = 0

    with open(file) as f:
        src = json.load(f)
        for folder_key in src:
            for file_key in src[folder_key]:
                for method_key in src[folder_key][file_key]:
                    method_count += 1
                    comments_count += len(src[folder_key][file_key][method_key]['comments'])
                    if len(src[folder_key][file_key][method_key]['comments']) > 0:
                        commented_methods += 1
    
    return method_count, commented_methods, comments_count

if __name__ == "__main__":
    file_path = "/Users/facade/Documents/GitHub/CSCI8980_ASE_project07/CommentsParserJava/result.json"
    method_count, commented_methods, comments_count = analyze_comments(file_path)

    print("#method: "+str(method_count))
    print("#comments: "+str(comments_count))
    print("#commented_methods: "+str(commented_methods))
