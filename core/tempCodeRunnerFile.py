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

# list1 = [2024, 1260, 1453, 1203]
# list2 = [1260, 1453, 124]

# # Check if all elements of list2 are in list1
# is_present =any(item in list1 for item in list2)

# print(is_present)  # Output: True (if all values are present)

# import ast
# # list1 = "[1,2,3]"
# list2 = "['bd', 'me', 'eu']"
# # str1 = "Hello "

# # list1 = ast.literal_eval(list1)
# list2 = ast.literal_eval(list2)

# # list2 = list1.copy()
# list1 = list2.copy()
# print(list1[:-1])
# print(list2)

# str2 = str1.lower().replace(" ", "-")
# print(str2)

# import random

# list1 = [
# 			{
# 				"user_id": 19,
# 				"user_email": "dr@gmail.com",
# 				"assigned_cat_name_list": "['Bangladesh', 'Middle East', 'Europe', 'Early Islamic Age', 'Islamic States', 'Americas', 'China & Far East', 'Opinions', 'Malaysia', 'Russia']",
# 				"assigned_cat_id_list": "[1, 2, 4, 5, 6, 7, 8, 3, 10, 9]",
# 				"editor_id": 11
# 			},
#             {
# 				"user_id": 20,
# 				"user_email": "ab@gmail.com",
# 				"assigned_cat_name_list": "['Bangladesh', 'Middle East']",
# 				"assigned_cat_id_list": "[1, 2 ]",
# 				"editor_id": 12
# 			}
# 		]
# random_number = random.choice(list1)

# print(random_number["user_id"])

# string1 = ""
# string2 = "  " \
# "   "
# string3 = "hello"
# string4 = " hello   dfd   "

# if len(string4) == 0 or string4.isspace(): 
#     print(" is empty")
# else: 
#     print(" is not empty")
from datetime import datetime
now1 = datetime.now()
now_list = []
now_list.append(str(now1))

now2 = datetime.now()
now_list.append(str(now2))
print(now_list)



