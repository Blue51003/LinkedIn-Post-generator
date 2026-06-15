import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm_helper import llm

def process_posts(raw_file_path, processed_file_path="data/processed_posts.json"):
    enriched_posts = []
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)
        for post in posts:
            metadata = extract_metadata(post['text'])
            post_with_metadata = post | metadata
            enriched_posts.append(post_with_metadata)

    unified_tags = get_unified_tags(enriched_posts)

    for post in enriched_posts:
        current_tag = post['tags']
        new_tags = {unified_tags[tag] for tag in current_tag}
        post['tags'] = list(new_tags)

    with open(processed_file_path, encoding='utf-8', mode="w") as outfile:
        json.dump(enriched_posts, outfile, indent=4)


    
def get_unified_tags(post_with_metadata):
    unique_tags = set()
    for posts in post_with_metadata:
        unique_tags.update(posts['tags'])

    unique_tags_list = ', '.join(unique_tags)

    template = '''
    I will give you a list of tags. You need to unify the tags with the following requirements.
    1. tags are unified and merged to create s shorter list.
       Example 1: "investment", "Investments", "investing", "portfolio" can all be merged into a single tag "Investment"
       Example 2: "finance", "money management", "wealth" can be mapped to "Finance"
       Example 3. "K-shaped economy", "Economic Policies" can be mapped to "Economy"
       Example 4. "stock market", "market", "market sentiments" can be mapped to "Stock Market"
    2. each tags should follow title case convention: "Motivation", "Job Search"
    3. output should be a JSON object. Not a preamble
    4. output should have mapping of the original tag and e unified tag.
       for example: {{"investing": "Investment", "stock market": "Stock Market"}}

    Here is the list of tags:
    {tags}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={'tags':str(unique_tags_list)})
    
    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs")
    return res

def extract_metadata(post):
    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
    1. Return a valid JSON. No preamble
    2. JSON object should have exactly 3 keys: line_count, language and tags.
    3. tags is an array of text tags. Extract maximum two tags.
    4. Language should be English or Hinglish. Hinglish means English + Hindi
    
    Here is the actual post on which you need to perform this task:
    {post}
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={'post':post})
    
    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs")
    return res

if __name__ == "__main__":
    process_posts("data/raw_posts.json", "data/processed_posts.json")