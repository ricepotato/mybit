import json
import dotenv
import logging
from api.upbit import UPBitApi

dotenv.load_dotenv(verbose=False)
log = logging.getLogger(f"mybit.{__name__}")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

api = UPBitApi()

# 80000 원 K뱅크에서 인출 요청(카카오 인증)
response = api.deposits_krw(80000)
print(json.dumps(response, indent=4))
