
import requests
import csv

def search_github_repositories(token, min_stars, max_stars, languages, output_file, max_results):
    url = 'https://api.github.com/search/repositories'
    headers = {
        'Authorization': f'token {token}'
    }

    results = []
    page = 1
    total_count = 0

    while len(results) < max_results:
        query = f'stars:{min_stars}..{max_stars}'
        if languages:
            query += ' ' + ' '.join(f'language:{lang}' for lang in languages)

        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': 100, 
            'page': page
        }

        response = requests.get(url, headers=headers, params=params)
        print(response)
        data = response.json()

        if response.status_code == 200:
            print("status_code:"+str(200))
            repositories = data.get('items', [])
            total_count = data.get('total_count', 0)

            if not repositories:
                break

            results.extend(repositories)
            page += 1

            if len(results) >= max_results or len(results) >= total_count:
                break
        else:
            print(f'Failed to fetch data: {data["message"] if "message" in data else "Unknown error"}')
            break

    results = results[:max_results] 

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Repository Name', 'Repository URL', 'Languages', 'Stars','suitLangNum']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for repo in results:
            repo_name = repo['name']
            repo_url = repo['html_url']
            repo_stars = repo['stargazers_count']
            languages_url = repo['languages_url']


            languages_response = requests.get(languages_url, headers=headers)
            languages_data = languages_response.json()

            pct_all = 0
            if languages_response.status_code == 200:
                repo_languages =""

                for lang, pct in languages_data.items():
                    pct_all += pct

                for lang, pct in languages_data.items():
                    percent = pct/pct_all 
                    if percent < 0.05:
                        continue
                    else:
                        repo_languages = repo_languages + ', '+str(lang)+"("+str(round(percent * 100, 3))+"%)"

                repo_languages = repo_languages[1:]
                print(repo_languages)

            else:
                repo_languages = ''

            langList = []


            for lang, pct in languages_data.items():
                percent = pct / pct_all
                if percent < 0.05:
                    continue
                else:
                    langList.append(str(lang).lower())

            sum = 0
            for l in languages:
                if l in langList:
                    sum += 1

            if sum == len(languages):
                writer.writerow({
                    'Repository Name': repo_name,
                    'Repository URL': repo_url,
                    'Languages': repo_languages,
                    'Stars': repo_stars,
                    'suitLangNum': sum
                })

    print(f'Search results (up to {max_results} repositories) have been saved to {output_file}')


if __name__ == "__main__":
    github_token = ''
    min_stars = 1000
    max_stars = 1000000
    languages = [['c', 'java'],['c','python'],['c++','java'],['c++','python'],['java','python']]
    max_results = 300 

    for langs in languages:
        output_file = 'repo_'+langs[0]+'_'+langs[1]+'.csv'

        search_github_repositories(github_token, min_stars, max_stars, langs, output_file, max_results)
