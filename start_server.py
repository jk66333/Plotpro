#!/usr/bin/env python3
import receipt_app
import os

if __name__ == "__main__":
    receipt_app.init_db()
    os.makedirs(receipt_app.app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join("static", "css"), exist_ok=True)
    receipt_app.app.run(debug=True, port=5002, host='127.0.0.1')
