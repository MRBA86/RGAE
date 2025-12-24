from kavenegar import *
from django.utils.text import slugify
import re

def send_otp_code(phone_number, code):
    try:
        api = KavenegarAPI('6A64347672633735455344446E416A71387563476F79596A696D53383242427975573035475A58425738553D')
        params = { 'sender' : '2000660110',
                  'receptor': phone_number,
                  'message' : f'کد ورود شما {code} می باشد.' }
        response = api.sms_send(params)
        print(response)
    except APIException as e: 
        print(e)
    except HTTPException as e: 
        print(e)
        
        
def slugify_farsi(text):
    # جایگزین فاصله با خط تیره (بدون تبدیل کاراکترهای فارسی)
    slug = re.sub(r'\s+', '-', text.strip())
    return slug