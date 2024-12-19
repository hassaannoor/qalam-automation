import requests
import re
import json


session_id_cookie = "1ae8a5081986390ce8dd7816974e65518eee72a8"
headers = {
        "cookie": f"frontend_lang=en_US; session_id={session_id_cookie}",
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

def get_form_urls(headers):
    url = "https://qalam.nust.edu.pk/student/qa/feedback"

    res = requests.get(url, headers=headers)
    html = res.text

    with open("getFormUrls.html", "w", encoding="utf-8") as file:
        file.write(html)

    matches = re.findall(r'title="Title: (.*?)">\n\s*<a.*?href="(\/survey\/[a-z0-9-\/]*?)"', html)

    titles = [match[0] for match in matches]
    urls = [f"https://qalam.nust.edu.pk{match[1]}" for match in matches]
    
    return titles, urls


def begin_survey(token, access_token):
    # url = "https://qalam.nust.edu.pk/survey/begin/9d0f5a2c-b188-4319-bff2-1e007ca37bfa/b65d279f-8c32-48ff-9413-10bdefad31e4"

    begin_survey_headers = {
        "cookie": f"frontend_lang=en_US; session_id={session_id_cookie}; tz=Asia/Karachi; survey_{token}={access_token}" 
    }
    # print(begin_survey_headers["cookie"])
    
    url = f"https://qalam.nust.edu.pk/survey/begin/{token}/{access_token}"
    
    body = {"id": 0, "jsonrpc": "2.0", "method": "call", "params": {}}
    

    response = requests.post(url, headers=begin_survey_headers, json=body)

    if response.ok:
        return [response.json(), begin_survey_headers]
    else:
        response.raise_for_status()

def get_input_id_fragments(html):
    # match = re.search(r'id="([0-9]{6})_([0-9]{6})_([0-9]{7})', html)
    # return [int(match.group(1)), int(match.group(2)), int(match.group(3))] if match else None
    match = re.search(r'data-name="([0-9]{6})" data-question-type="matrix" data-sub-questions="(\[.+\])"', html)
    sliders_id = int(match.group(1)) if match else None
    slider_ids = match.group(2)[1:-1].split(',') if match else None
    return [sliders_id] + slider_ids if match else None

def get_textfield_name(html):
    match = re.search(r'name="([0-9]{6})" data-question-type="text_box"', html)
    return match.group(1) if match else None

def get_csrf(html):
    match = re.search(r'csrf_token: "(.+?)",', html)
    return match.group(1) if match else None

def get_excellent_value(html):
    match = re.search(r'class="o_survey_form_choice_item d-none" type="radio" name="[0-9_]+" value="(.+?)"', html)
    return match.group(1) if match else None

def main():
    titles, urls = get_form_urls(headers)

    # url = https://qalam.nust.edu.pk/student/evaluation/form/8a580f0e-47a9-4a41-9b92-0ced358fdc34/a1a5b2db-1fd0-409c-8951-45da49c768c0

    for idx, url in enumerate(urls):
        try:
            print("Submitting: " + titles[idx])

            segments = url.split('/')
            token = segments[-2]
            access_token = segments[-1]
            
            [begin_survey_response, begin_survey_headers] = begin_survey(token, access_token)
            if (begin_survey_response["result"]):
                print("Survey Begin Successful")

            # print(f"Begin Survey: {begin_survey_response}")
            response = requests.get(url, headers=begin_survey_headers)
            html = response.text
            print("Survey Form Fetching Successful")

            # log the response for debugging
            with open('survey.html', 'w', encoding='utf-8') as f:
                f.write(html)

            # skip if already submitted
            if (html.find("o_survey_review") != -1):
                print("Form already submitted")
                continue

            input_id_fragments = get_input_id_fragments(html)
            if input_id_fragments is None:
                raise Exception("Unable to extract input_id_fragments")
            
            sliders_id = input_id_fragments[0]
            slider_ids = input_id_fragments[1:]

            textfield_name = get_textfield_name(html)

            csrf = get_csrf(html)
            if csrf is None:
                raise Exception("Unable to extract CSRF token")

            EXCELLENT = get_excellent_value(html)
            if EXCELLENT is None:
                raise Exception("Unable to extract Excellent value")

            sliders_data = {}
            for slider_id in slider_ids:
                sliders_data[slider_id] = [str(EXCELLENT)]  # List of values as per format

            body = {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    str(sliders_id): sliders_data,
                    str(textfield_name): "This form was submitted through an automated system.\r\nDO ME A FAVOR PLEASE DONT FORCE THIS EVAL FORM ON ME.  THOUGH I APPRECIATE THE GESTURE FOR SURE",
                    "csrf_token": csrf,
                    "token": access_token
                }
            }

            response = requests.post(
                f"https://qalam.nust.edu.pk/survey/submit/{token}/{access_token}",
                headers=begin_survey_headers,
                data=json.dumps(body)
            )

            print(f"Submitted: {titles[idx]}")
            print(response.text)
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()
