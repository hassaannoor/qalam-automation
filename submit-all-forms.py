import requests
import re
import json

# Read session_id_cookie from file
with open("session_id_cookie.txt", "r") as file:
    session_id_cookie = file.read().strip()

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
        "content-type": "application/json",
        "cookie": f"frontend_lang=en_US; session_id={session_id_cookie}; tz=Asia/Karachi; survey_{token}={access_token}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "origin": "https://qalam.nust.edu.pk",
        "priority": "u=1, i",
        "referer": f"https://qalam.nust.edu.pk/survey/{token}/{access_token}"
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
    pattern = r'data-name="([0-9]{6})" data-question-type="matrix" data-sub-questions="(\[.+?\])"'
    matches = list(re.finditer(pattern, html))

    slider_id1 = None
    slider_ids1 = None
    slider_id2 = None
    slider_ids2 = None

    if len(matches) >= 1:
        match1 = matches[0]
        slider_id1 = int(match1.group(1))
        try:
            slider_ids1 = [int(x.strip().strip('"')) for x in match1.group(2)[1:-1].split(',')]
        except (ValueError, AttributeError):
            slider_ids1 = None

    if len(matches) >= 2:
        match2 = matches[1]
        slider_id2 = int(match2.group(1))
        try:
            slider_ids2 = [int(x.strip().strip('"')) for x in match2.group(2)[1:-1].split(',')]
        except (ValueError, AttributeError):
            slider_ids2 = None

    return (slider_id1, slider_ids1), (slider_id2, slider_ids2)

def get_textfield_name(html):
    match = re.search(r'name="([0-9]{6})" data-question-type="text_box"', html)
    return match.group(1) if match else None

def get_csrf(html):
    match = re.search(r'csrf_token: "(.+?)",', html)
    return match.group(1) if match else None

def get_vgood_value(html):
    pattern = r'class="o_survey_form_choice_item d-none" type="radio" name="[0-9_]+" value="(.+?)"'
    matches = list(re.finditer(pattern, html))
    rating = 1 # 0 => excellent, 1 => very good, 2 => good, 3 => average, 4 => poor
    return matches[rating].group(1) if matches[rating] else None

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

            (slider_id1, slider_ids1), (slider_id2, slider_ids2) = get_input_id_fragments(html)

            if slider_id1 is None and slider_id2 is None:
                raise Exception("Unable to extract any slider ID fragments")

            textfield_name = get_textfield_name(html)

            csrf = get_csrf(html)
            if csrf is None:
                raise Exception("Unable to extract CSRF token")

            EXCELLENT = get_vgood_value(html)
            if EXCELLENT is None:
                raise Exception("Unable to extract Excellent value")

            params = {}

            if slider_ids1 is not None:
                sliders_data1 = {}
                for slider_id in slider_ids1:
                    sliders_data1[slider_id] = [str(EXCELLENT)]
                if slider_id1 is not None:
                    params[str(slider_id1)] = sliders_data1

            if slider_ids2 is not None:
                sliders_data2 = {}
                for slider_id in slider_ids2:
                    sliders_data2[slider_id] = [str(EXCELLENT)]
                if slider_id2 is not None:
                    params[str(slider_id2)] = sliders_data2

            params[str(textfield_name)] = "This form was submitted through an automated system.\r\nDO ME A FAVOR PLEASE DONT FORCE THIS EVAL FORM ON ME.  THOUGH I APPRECIATE THE GESTURE FOR SURE"
            params["csrf_token"] = csrf
            params["token"] = access_token

            body = {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "call",
                "params": params
            }

            response = requests.post(
                f"https://qalam.nust.edu.pk/survey/submit/{token}/{access_token}",
                headers=begin_survey_headers,
                data=json.dumps(body)
            )

            if response.status_code != 200:
                print("Error: " + str(response.status_code))
            else: 
                print(f"Submitted: {titles[idx]}")
                
            with open(f"temp/submission-response-{idx}.html", 'w', encoding='utf-8') as f:
                f.write(f"{titles[idx]}\n\n" + response.text)
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()
