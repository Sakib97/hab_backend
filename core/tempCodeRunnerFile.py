# from decouple import config
# import time
# from datetime import datetime
# import os
# from dotenv import load_dotenv
# from email.message import EmailMessage

# # Load environment variables from .env file
# load_dotenv()

# # ACCESS_TOKEN_EXPIRE_MINUTES = config("access_token_exp_min")
# # REFRESH_TOKEN_EXPIRE_DAYS = config("refresh_token_exp_days")
# ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("access_token_exp_min")
# REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("refresh_token_exp_days")

# # access_exp_sec = int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60
# # refresh_exp_sec = int(REFRESH_TOKEN_EXPIRE_DAYS) * 24 * 60 * 60

# # print(datetime.fromtimestamp(time.time()))

# # print(ACCESS_TOKEN_EXPIRE_MINUTES)
# # print(REFRESH_TOKEN_EXPIRE_DAYS)

# email = str(os.getenv("EMAIL_USER2"))
# password = str(os.getenv("EMAIL_PASSWORD4"))

# print("email:: ", email)
# print("password:: ", password)

# msg = EmailMessage()
# msg.set_content("body")
# msg['Subject'] = "This is subject"
# msg['From'] = "sakib"
# msg['To'] = "John doe"

# print("msg:: ", msg)

# # MAIL_USERNAME = os.getenv('MAIL_USERNAME')
# # MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
# # MAIL_FROM = os.getenv('MAIL_FROM')
# # MAIL_PORT = int(os.getenv('MAIL_PORT'))
# # MAIL_SERVER = os.getenv('MAIL_SERVER')
# # MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME')

# # print(MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM,MAIL_PORT, MAIL_SERVER, MAIL_FROM_NAME)

# list_1 = [1453, 1260, 1444]
# list_2 = [2024, 1203]

# # Convert to sets and check for intersection
# if set(list_1) & set(list_2):
#     print(True)
# else:
#     print(False)

import ast
list1 = "[1,2,3]"
list2 = "['bd', 'me', 'eu']"

list1 = ast.literal_eval(list1)
list2 = ast.literal_eval(list2)

# for i in range(len(list1)):
#     print(list1[i], list2[i] )

