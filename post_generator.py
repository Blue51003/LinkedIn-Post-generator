from llm_helper import llm
from few_shot import FewShotPost

few_shot = FewShotPost()

def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    elif length == "Medium":
        return "5 to 15 lines"
    else:
        return "15 to 40 lines"
    
def get_prompt(length, language, topic):
    length_str = get_length_str(length)

    prompt = f'''
    Generate a LinkedIn post using the below information. No preamble.

    1) Topic = {topic}
    2) Language = {language}
    3) Length = {length_str}
    4) If language selected is hindi or hinglish(hindi+ english), make sure the script of the words are in enlish.
    '''

    examples = few_shot.get_filtered_posts(length, language, topic)

    if len(examples)>0 :
        prompt+="5) Use the writing style as per the following examples. Since the topic can be vast, you dont need to get into the same sub-domain as the example goes. Try to go into various other sub-domains, but utilise the way these examples are written."
        for i, post in enumerate(examples):
            post_text=post['text']
            prompt+=f"\n\n Example {i+1}: \n\n {post_text}"

            if i==2:
                break

    return prompt

def generate_post(length, language, topic):
    prompt = get_prompt(length, language, topic)

    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    post = generate_post("Short", "English", "Investment")
    print(post)