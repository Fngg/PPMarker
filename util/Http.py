import requests
import traceback
from util.Logger import logger


class HTTPPlatform():
    _session = requests.session()
    host = "http://127.0.0.1:8000/"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def get_data(self,url_path,data):
        url = self.host+url_path
        try:
            res = self._session.get(
                url=url,
                params=data
            )
            return res.json()
        except Exception as e:
            logger.error(traceback.format_exc())

    def get_data_post(self,url_path,data):
        url = self.host+url_path
        try:
            res = self._session.post(
                url=url,
                data=data
            )
            return res.json()
        except Exception as e:
            logger.error(traceback.format_exc())

    def download_file(self,url_path,data,out_path):
        url = self.host+url_path
        try:
            res = self._session.get(
                url=url,
                params=data,
                stream=True
            )
            if res!=None and res.status_code==200:
                with open(out_path, "wb") as f:
                    for chunk in res.iter_content(chunk_size=512):
                        f.write(chunk)
        except Exception as e:
            logger.error(traceback.format_exc())