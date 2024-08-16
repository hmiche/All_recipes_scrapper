import urllib.request

from bs4 import BeautifulSoup
import re
import requests
import random 
from PIL import Image
from io import BytesIO
import os
from datetime import datetime
from tqdm import tqdm



with open('keywords.txt', 'r') as file:
    keyord_list = [line.strip() for line in file if line.strip()]

with open('already_used_links.txt', 'r') as file:
    used_links = [line.strip() for line in file if line.strip()]

def main():
    stopper = input('how many post you want : ')
    stopper = int(stopper)
    
    links_list = get_links_from_keyword(keyord_list, stopper)
    print(links_list)
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    directory = f"{formatted_time}"
    
    os.makedirs(directory)
    
    for i, link in enumerate(tqdm(links_list)):
        
        if link in used_links:
            continue
        else:
            used_links.append(link)
            
        get_image_from_link(link, directory, i)
        if i == stopper -1 :
           break
    
    with open('already_used_links.txt', 'w') as file:
        for recipe in used_links:
            file.write(recipe + '\n')

def get_links_from_keyword(keyword_list, stopper):
    full_list = []
    for i, keyword in enumerate(keyword_list):
        search_url = convert_to_allrecipes_search_url(keyword)
        r = urllib.request.urlopen(search_url)
        soup = BeautifulSoup(r, 'html.parser')
        links = soup.find_all('a', class_="comp mntl-card-list-items mntl-document-card mntl-card card card--no-image")
        all_hrefs = [link['href'] for link in links]
        extracted_links = [link['href'] for link in links if link['href'].startswith('https://www.allrecipes.com/recipe/')]
        full_list += extracted_links
        
        if i == stopper :
            return full_list
    
    return full_list

def get_image_from_link(url, parent, index):
    
    r = urllib.request.urlopen(url)
    soup = BeautifulSoup(r, 'html.parser')

    script_tag = soup.findAll('script', type='text/javascript')
    script_tag = script_tag[1]
    docId = get_doc_id(script_tag)
    pic_urls_list = get_review_pic(docId)
    if pic_urls_list:
        
        for i, pic in enumerate(pic_urls_list):
            response = requests.get(pic)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                resized_image = image.resize((1200, 1200))
                clean_image = Image.new(resized_image.mode, resized_image.size)
                clean_image.paste(resized_image)
                if not os.path.exists(f"{parent}/{index}/"):
                    os.makedirs(f"{parent}/{index}/")
                    
                with open(f"{parent}/{index}/{index}.txt", "w") as file:
                    file.write(url)
                directory = f"{parent}/{index}/recipe__{i}_{index}.png"
                clean_image.save(directory, format="PNG")
            
def get_doc_id(script_tag):
    doc_id_match = re.search(r'docId:\s*\'(\d+)\',', script_tag.string)  # This will find `docId: '6663813',`
    if not doc_id_match:
        doc_id_match = re.search(r'documentId":\s*(\d+),', script_tag.string)

    if doc_id_match:
        doc_id = doc_id_match.group(1)
        return doc_id
    else:
        return ''
    
def get_review_pic(docId):
    pictures_list = []
    counter = 0
    if docId != "":
        try:
            url = f"https://www.allrecipes.com/servemodel/model.json?modelId=feedbacks&docId={docId}&sort=DATE_ASC&offset=0&limit=9&withPhoto=true"
            response = requests.get(url)
            json_data = response.json()
            for i in range(0, len(json_data['list'])):
                if counter == 3:
                    return pictures_list
                try:
                    picture = json_data['list'][i]['photos'][0]['url']
                    pictures_list.append(picture)
                    print(pictures_list)
                    counter += 1 
                except Exception as e:
                    print(e)
        except:
            pass
        
        return pictures_list
            
def convert_to_allrecipes_search_url(query):
    # Replace spaces with '+' and encode special characters like '&'
    encoded_query = query.replace(' ', '+').replace('&', '%26')
    # Construct the full search URL
    search_url = f"https://www.allrecipes.com/search?q={encoded_query}"
    return search_url

main()
    