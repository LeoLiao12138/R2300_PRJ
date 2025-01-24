import requests

url='http://10.0.10.76/cmd/request_handle_udp?address=10.0.10.110&port=10000'
response = requests.get(url)

if response.status_code ==200:
    print(response.text)
    json_data = response.json()
    handle = json_data.get('handle')
    print(handle)
    url_start_scanoutput='http://10.0.10.76/cmd/start_scanoutput'
    params = {'handle':handle}
    response_start_scanoutput = requests.get(url_start_scanoutput, params=params)
    if response_start_scanoutput.status_code ==200:
        print("start success")
    else:
        print("start fail")
else:
    print("error")