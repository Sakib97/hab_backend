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

role_list = [10,20,302]
target = 30
if target not in role_list:
    exists = "nott"
else:
    exists = "Yess"
print(exists)