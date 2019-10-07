import json
import glob
import requests
import os
import sys
import shutil
import argparse
import multiprocessing as mp
import constants

path = os.getcwd()
folderReport = constants.REPORT_DIRECTORY
pathReport = "{}/{}".format(path,folderReport)


class Repository:
    def __init__(self, id, url, name):
        self.id = id
        self.url = url
        self.name = name

def github_repo_to_standar_repo(repository):
    repository = Repository(repository['id'], repository['html_url'], repository['name'])
    return repository

def azdev_repo_to_standar_repo(repository):
    repository = Repository(repository['id'], repository['webUrl'], repository['name'])
    return repository

def download_image():
    docker_pull = 'docker pull dpolania/gitleaks'
    os.system(docker_pull)

def request_url(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('GET / {}/ {}'.format(url, resp.status_code))

    result = resp.json()
    return result

def total_item(url, key):

    result = request_url(url)
    total_count = result[key]

    return total_count

def get_repositories_github(word_list):
    
    repositories = []

    if len(word_list) == 0:
        print("The list is empty")
        response = request_url(constants.GITHUB_URI_API_REPOSITORIES)
        repositories = map(github_repo_to_standar_repo, response) 

    else:
        print("The list is not empty")
        query = "+".join(word_list)
        url_base = constants.GITHUB_URI_API_SEACRH + query 
        total_count = total_item(url_base, constants.GITHUB_TOTAL_KEY)
        pages = int(total_count / 100) + (total_count % 100 > 0)
        for x in range(0, pages):
            response = request_url(url_base+'&page='+str(x+1)+'&per_page=100')
            repositories += map(github_repo_to_standar_repo, response['items']) 

    return repositories

def get_repositories_azdev(word_list):

    TOKEN = os.environ.get('TOKEN')
    ORGANIZATION = os.getenv('AZDEV_ORGANIZATION')
    PROJECT = os.getenv('AZDEV_PROJECT_ID')

    if len(word_list) == 0:
        print("The list is empty")
        response = request_url(constants.AZDEV_API_REPOSITORIES.format(TOKEN,ORGANIZATION,PROJECT))
        repositories = map(azdev_repo_to_standar_repo, response['value']) 

    else:
        print("The list is not empty")
        response = request_url(constants.AZDEV_API_REPOSITORIES.format(TOKEN,ORGANIZATION,PROJECT))
        result = map(azdev_repo_to_standar_repo, response['value']) 
        repositories = [x for x in result if any( s in x.name for s in word_list)]

    return repositories

def clean_and_create_report_directory():
    
    if not os.path.exists(folderReport):
        print('Create directory of report')
        os.makedirs(folderReport)
    else:
        print('Clean and create directoryof report')
        shutil.rmtree(folderReport)
        os.makedirs(folderReport)

def run_analysis(repository):

    print(repository.name)
    TOKEN = os.environ.get('TOKEN')

    if "AZDEV_ORGANIZATION" in os.environ:
        run_docker = 'docker run --rm -v {}:/data -e AZURE_DEVOPS_TOKEN={} dpolania/gitleaks --report=/data/report/{}.json --config=/data/rules.toml -r {} --threads=$(($(nproc --all) - 1))'.format(path, TOKEN, repository.id, repository.url)
    else:
        run_docker = 'docker run --rm -v {}:/data dpolania/gitleaks --report=/data/report/{}.json --config=/data/rules.toml -r {} --threads=$(($(nproc --all) - 1))'.format(path, repository.id, repository.url)

    os.system(run_docker)

def analysis(repositories):
    print("Number of processors: ", mp.cpu_count())
    pool = mp.Pool(mp.cpu_count())
    results = pool.map_async(run_analysis, [repository for repository in repositories]).get()
    pool.close()

def main():
    try:
        parser = argparse.ArgumentParser(description='Find secrets hidden in the depths of git.')
        parser.add_argument('--github', dest="do_github", action="store_true", help="Enable github analysis")
        parser.add_argument('--gitlab', dest="do_gitlab", action="store_true", help="Enable gitlab analysis")
        parser.add_argument('--azdev', dest="do_azdev", action="store_true", 
                           help='Enable azure devops code analysis'
                           'you must create the following environment variable'
                           'AZDEV_ORGANIZATION'
                           'AZDEV_PROJECT_ID')
        parser.add_argument('--bitbucket', dest="do_bitbucket", action="store_true", help="Enable bitbucket analysis")
        parser.add_argument("--words", dest="words", help="list of words to search to list the repositories that contain those words, if the list is empty it will analyze all the repositories, are longer than 256 characters")

        parser.set_defaults(words=os.path.join(path,constants.WORDS))
        args = parser.parse_args()
        clean_and_create_report_directory()
        download_image()
        word_list = [line.rstrip('\n') for line in open(args.words)]

        if args.do_github:
            repositories = get_repositories_github(word_list)
            print("Total repositories: " + str(len(repositories)) )
            analysis(repositories)
        elif args.do_azdev:
            repositories = get_repositories_azdev(word_list)
            print("Total repositories: " + str(len(repositories)) )
            analysis(repositories)
        elif args.do_gitlab:
            print("Pending contributions :), Sorry")
        elif args.do_bitbucket:
            print("Pending contributions :), Sorry")
        else:
            sys.exit(1)

    except Exception as e: print(e)
    else:
        pass
    finally:
        pass

try:

    if __name__== "__main__":
        main()

except Exception as e: print(e)

else:
    print ("Successfully")
    sys.exit(0)


