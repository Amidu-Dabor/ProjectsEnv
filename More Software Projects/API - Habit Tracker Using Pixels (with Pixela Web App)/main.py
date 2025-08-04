import requests
from datetime import datetime


USERNAME ="amidu"
GRAPH_ID = "graph1"
TOKEN = "1b4cee1f27c4c13cb07d51f96993160a"

# Get current date, remove dashes
unformatted_date = datetime.now()
current_date = unformatted_date.strftime("%Y%m%d")


# CREATE A NEW PIXELA USER ACCOUNT
user_endpoint = "https://pixe.la/v1/users"

user_params = {
    "token": TOKEN,
    "username": USERNAME,
    "agreeTermsOfService": "yes",
    "notMinor": "yes",
}

user_response = requests.post(url=user_endpoint, json=user_params)
# print(user_response.text)


# CREATE A GRAPH DEFINITION
graph_endpoint = f"{user_endpoint}/{USERNAME}/graphs"

graph_config = {
    "id": GRAPH_ID,
    "name": "Study Graph",
    "unit": "commit",
    "type": "int",
    "color": "ajisai",
}

headers = {
    "X-USER-TOKEN": TOKEN,
}

# graph_response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)


# POST A PIXEL TO THE GRAPH (Pixel Creation)
graph_post_endpoint = f"{user_endpoint}/{USERNAME}/graphs/{GRAPH_ID}"

graph_data_to_post = {
    "date": current_date,
    "quantity": "17",
}

# graph_data_post = requests.post(url=graph_post_endpoint, json=graph_data_to_post, headers=headers)


# UPDATE THE GRAPH
graph_update = {
    "name": "Study Graph",
    "color": "shibafu",
}

# graph_update_res = requests.put(url=graph_post_endpoint, json=graph_update, headers=headers)


# UPDATE A PIXEL
pixel_update_endpoint = f"{user_endpoint}/{USERNAME}/graphs/{GRAPH_ID}/{current_date}"

pixel_update_data = {
    "quantity": "25",
}

# pixel_update_res = requests.put(url=pixel_update_endpoint, json=pixel_update_data, headers=headers)


# DELETE A PIXEL
pixel_delete_endpoint = f"{user_endpoint}/{USERNAME}/graphs/{GRAPH_ID}/{current_date}"

data_delete_res = requests.delete(url=pixel_delete_endpoint, headers=headers)
print(data_delete_res.text)

