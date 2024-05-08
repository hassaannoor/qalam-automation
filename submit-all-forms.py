import requests
import re



def get_form_urls(headers):
    url = "https://qalam.nust.edu.pk/student/qa/feedback"

    res = requests.get(url, headers=headers)
    html = res.text

    with open("getFormUrls.html", "w", encoding="utf-8") as file:
        file.write(html)

    matches = re.findall(r'title="Title: (.*?)">\n\s*<a.*href="(\/student\/evaluation\/form.*?)"', html)

    titles = [match[0] for match in matches]
    urls = [f"https://qalam.nust.edu.pk{match[1]}" for match in matches]
    
    return titles, urls

def get_input_id_fragments(html):
    match = re.search(r'id="([0-9]{6})_([0-9]{6})_([0-9]{7})', html)
    return [int(match.group(1)), int(match.group(2)), int(match.group(3))] if match else None

def get_textfield_name(html):
    match = re.search(r'name="([0-9]{6}_[0-9]{6})"', html)
    return match.group(1) if match else None

def get_csrf(html):
    match = re.search(r'csrf_token: "([a-z0-9]{41})",', html)
    return match.group(1) if match else None

def get_excellent_value(html):
    match = re.search('value="([0-9]{7})" label="Excellent"', html)
    return match.group(1) if match else None

def get_total_sliders(html):
    matches = re.finditer('class="slider"', html)
    return sum(1 for _ in matches) if matches else 0

session_id_cookie = "47fa9f5bc1d0e93581198310c9c154ae2c918243"
headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundary79B83XpSAqzZqBuB",
        "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "cookie": f"frontend_lang=en_US; im_livechat_history=[\"/\"]; session_id={session_id_cookie}",
        "Referer": f"https://qalam.nust.edu.pk/student/evaluation/form",
        "Referrer-Policy": "strict-origin-when-cross-origin"
}

def main():
    titles, urls = get_form_urls(headers)

    # url = https://qalam.nust.edu.pk/student/evaluation/form/8a580f0e-47a9-4a41-9b92-0ced358fdc34/a1a5b2db-1fd0-409c-8951-45da49c768c0

    for idx, url in enumerate(urls):
        # if re.search("Course", titles[idx]) is None:
        #     continue
        print("Submitting: " + titles[idx])

        segments = url.split('/')
        token = segments[-2]
        access_token = segments[-1]
        
        response = requests.get(url, headers=headers)
        html = response.text

        # log the response for debugging
        with open('survey.html', 'w', encoding='utf-8') as f:
            f.write(html)

        # skip if already submitted
        if (html.find("Survey is submitted.") != -1):
            print("Form already submitted")
            continue

        input_id_fragments = get_input_id_fragments(html)
        if (input_id_fragments is None):
            raise "Unable to extract input_id_fragments"
        
        [form_id, sliders_id, first_slider_id] = input_id_fragments 
        textfield_name = get_textfield_name(html)

        csrf = get_csrf(html)
        if (csrf is None):
            raise "Unable to extract CSRF token"
        
        # EXCELLENT = 4853812
        # EXCELLENT = 4875781
        EXCELLENT = get_excellent_value(html)

        total_sliders = get_total_sliders(html)

        sliders_body = ""
        for i in range(total_sliders):
            sliders_body += (
                f"------WebKitFormBoundary79B83XpSAqzZqBuB\r\n"
                f"Content-Disposition: form-data; name=\"{form_id}_{sliders_id}_{first_slider_id+(i+1)}\"\r\n\r\n{EXCELLENT}\r\n"
            )

        body = (
            f"------WebKitFormBoundary79B83XpSAqzZqBuB\r\n"
            f"Content-Disposition: form-data; name=\"token\"\r\n\r\n{token}\r\n"
            f"------WebKitFormBoundary79B83XpSAqzZqBuB\r\n"
            f"Content-Disposition: form-data; name=\"access_token\"\r\n\r\n{access_token}\r\n"
            +
            sliders_body
            + 
            f"------WebKitFormBoundary79B83XpSAqzZqBuB\r\n"
            f"Content-Disposition: form-data; name=\"{textfield_name}\"\r\n\r\n"
            "This form was submitted through an automated system.\r\n"
            "DO ME A FAVOR PLEASE DONT FORCE THIS EVAL FORM ON ME.  THOUGH I APPRECIATE THE GESTURE FOR SURE\r\n"
            f"------WebKitFormBoundary79B83XpSAqzZqBuB\r\n"
            f"Content-Disposition: form-data; name=\"csrf_token\"\r\n\r\n{csrf}\r\n"
            f"------WebKitFormBoundary79B83XpSAqzZqBuB\r\n"
            f"Content-Disposition: form-data; name=\"button_submit\"\r\n\r\nfinish\r\n"
            f"------WebKitFormBoundary79B83XpSAqzZqBuB--\r\n"
        )

        # print(body)

        response = requests.post(f"https://qalam.nust.edu.pk/student/evaluation/form/save/{token}/{access_token}",
                                headers=headers, data=body)
        print(response.text)

if __name__ == "__main__":
    main()
