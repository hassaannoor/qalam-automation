const fs = require("fs");
const { url } = require("inspector");
const cc = require("node-console-colors");
// let token = `6ce1a17c-d6ec-46a3-ad2b-9e86f5a53566s`
// let access_token = `6ce1a17c-d6ec-46a3-ad2b-9e86f5a53566s`

const headers = {
  accept: "application/json, text/javascript, */*; q=0.01",
  "accept-language": "en-US,en;q=0.9",
  "content-type":
    "multipart/form-data; boundary=----WebKitFormBoundary79B83XpSAqzZqBuB",
  "sec-ch-ua":
    '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": '"Windows"',
  "sec-fetch-dest": "empty",
  "sec-fetch-mode": "cors",
  "sec-fetch-site": "same-origin",
  "x-requested-with": "XMLHttpRequest",
  cookie:
    'frontend_lang=en_US; im_livechat_history=["/"]; session_id=18c340424f75c9311806d8a7f4efaf1d923a8cf3',
  "Referrer-Policy": "strict-origin-when-cross-origin",
};

async function getFormName(url) {
  let res = await fetch(
    url,
    // 'https://qalam.nust.edu.pk/student/evaluation/form/a316733b-01db-4cbb-9c67-8f35aef8393d/a1b8a706-33b4-43f8-b5a5-4a60f8201213'
    {
      headers: headers,
    }
  );
  let html = await res.text();

  fs.writeFileSync("getFormName.html", html, { encoding: "utf-8" });

  if (html.match(/Survey is submitted./)) {
    throw new Error("Survey Already Submitted. Can't find formname");
  }

  let form_name = parseInt(html.match(/id="custom_form" name="(.+?)"/)[1]);
  let form_name_sub = parseInt(
    html.match(
      new RegExp(
        `value="0" step="1" min="0" max="5" id="${form_name}_(.+?)_.*?"`
      )
    )[1]
  );
  let form_name_sub_sub = parseInt(
    html.match(
      new RegExp(
        `value="0" step="1" min="0" max="5" id="${form_name}_${form_name_sub}_(.+?)"`
      )
    )[1]
  );
  let csrf = html.match(
    /<input type="hidden" name="csrf_token" value="(.+?)"/
  )[1];
  return { form_name, form_name_sub, form_name_sub_sub, csrf };
}

main();
async function main() {
  const urls = await getFormUrls();
  if (urls.length === 0) {
    console.log(cc.set('bg_red', '[ERROR]: You might need to update the session_id. No form urls were found'));
    return;
  }
  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    console.log(cc.set("fg_blue", `[Filling Form]: ${url}`));
    // continue;
    await method1(url);
    continue;
    try {
      console.log(cc.set("bg_cyan", `[Fetching form_name]`));
      var { form_name, form_name_sub, form_name_sub_sub, csrf } =
        await getFormName(url);
    } catch (e) {
      console.log(cc.set("bg_red", `[ERROR]: Form already submitted`));
      continue;
    }
    console.log(
      cc.set("fg_green", "bg_default", `[Found form_name]: ${form_name}`)
    );

    // let url = `

    // https://qalam.nust.edu.pk/student/evaluation/form/a316733b-01db-4cbb-9c67-8f35aef8393d/a1b8a706-33b4-43f8-b5a5-4a60f8201213

    // `.trim();

    // Split the URL into segments
    let segments = url.split("/");

    let access_token = segments[segments.length - 2]; // 2nd last segment
    let token = segments[segments.length - 1]; // last segment

    const body = `------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"token\"

${token}
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"access_token\"

${access_token}
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"${form_name}_${form_name_sub}_${
      form_name_sub_sub + 0
    }\"

4456283
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"${form_name}_${form_name_sub}_${
      form_name_sub_sub + 1
    }\"

4456283
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"${form_name}_${form_name_sub}_${
      form_name_sub_sub + 2
    }\"

4456283
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"${form_name}_${form_name_sub}_${
      form_name_sub_sub + 3
    }\"

4456283
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"${form_name}_${form_name_sub}_${
      form_name_sub_sub + 4
    }\"

4456283
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"${form_name}_${form_name_sub}_${
      form_name_sub_sub + 5
    }\"

4456283
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"${form_name}_${form_name_sub}_${
      form_name_sub_sub + 6
    }\"

4456283
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"${form_name}_${form_name_sub}_${
      form_name_sub_sub + 7
    }\"

4456283
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"${form_name}_${form_name_sub + 1}\"

This form was submitted through an automated system.

DO ME A FAVOR PLEASE DONT FORCE THIS EVAL FORM ON ME. THOUGH I APPRECIATE THE GESTURE FOR SURE
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"csrf_token\"

${csrf}
------WebKitFormBoundary79B83XpSAqzZqBuB
Content-Disposition: form-data; name=\"button_submit\"

finish
------WebKitFormBoundary79B83XpSAqzZqBuB--
`;
    // console.log(body)

    const res = await fetch(
      `https://qalam.nust.edu.pk/student/evaluation/form/save/${access_token}/${token}`,
      {
        headers: headers,
        body: body,
        method: "POST",
      }
    );

    const html = await res.text();
    // console.log(html)
    fs.writeFileSync("main.html", html, { encoding: "utf-8" });
    try {
      const json = JSON.parse(html);
      if (json.status == "Success") {
        console.log(
          cc.set("bg_green", `[SUCCESS]: Form submitted successfully`)
        );
      } else {
        console.log(
          cc.set(
            "bg_red",
            `[ERROR]: JSON response doesn't indicate success`,
            "fg_white",
            json
          )
        );
      }
    } catch (e) {
      console.log(cc.set("bg_red", "[ERROR]: Operation wasn't successful"));
    }
    // return;
    // const json = await res.json();

    // console.log(json);
  }
}

async function getFormUrls() {
  let url = "https://qalam.nust.edu.pk/student/qa/feedback";
  const res = await fetch(url, {
    headers: headers,
  });
  const html = await res.text();

  fs.writeFileSync("getFormUrls.html", html, { encoding: "utf-8" });

  const urls = Array.from(
    html.matchAll(/href="(\/student\/evaluation\/form.*?)"/g)
  ).map((a) => `https://qalam.nust.edu.pk${a[1]}`);
  return urls;
}

async function method1(url) {
  const res = await fetch(url, {
    headers,
  });

  const html = await res.text();
  await submitForm(html, url);

  // const formHtml = html.match(/(<form.*<\/form>)/s,)[1]

}
async function submitForm(html, url) {
  const cheerio = require("cheerio");
  const FormData = require("form-data");

  const $ = cheerio.load(html);
  const form = $("form");
  if (form.length === 0) {
    console.log(cc.set("bg_red", `[ERROR]: Form already submitted`));
    return;
  }
  const actionUrl = form.attr("action");
  const method = form.attr("method") || "get";

  form.find('[type=range]').remove()
  form.find('[type=radio]:not(:nth-child(3))').remove(); // remove all radio inputs except for the third one in each slider
  // the remaining radio btns can be submitted as is
  // because they already have the values set

  // fill the textarea
  form.find('textarea').value = `This form was submitted through an automated system.

    DO ME A FAVOR PLEASE DONT FORCE THIS EVAL FORM ON ME. THOUGH I APPRECIATE THE GESTURE FOR SURE`
  // Prepare form data
  const formData = new FormData();
  form.find("input, textarea").each((i, elem) => {
    const name = $(elem).attr("name");
    const value = $(elem).attr("value");
    if (name && value) {
      formData.append(name, value);
    }
  });

  // Perform the fetch request
  try {
    const response = await fetch(url, {
      method: method,
      body: method.toLowerCase() === "post" ? formData : null,
      headers: {
        ...headers,
        ...formData.getHeaders(),
        // ...{"content-type": "multipart/form-data; boundary=----WebKitFormBoundary3WCUxaENYxpl6a7g"}
    },
    });

    const responseText = await response.text();
    const urlLast10Chars = url.substr(-10, 100);
    fs.writeFileSync(`submitForm-${urlLast10Chars}.html`, responseText, { encoding: "utf-8" });
    // console.log(responseText);
  } catch (error) {
    console.error("Error submitting form:", error);
  }
}
