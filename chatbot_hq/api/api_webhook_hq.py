# -*- coding: utf-8 -*-

import sys
from api.hq_module import *
from flask import Flask

sys.path.append('../')

app = Flask(__name__, static_url_path='')
app.static_folder = ''

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    app.register_blueprint(hq_sema_etl)
    app.run(debug=False, host='0.0.0.0', port=10011, threaded=True)
