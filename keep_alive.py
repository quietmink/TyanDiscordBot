from flask import Flask, request, render_template
import subprocess
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
  return "Alive"

@app.route('/github-webhook', methods = ['POST'])
def github_webhook():
    if request.headers.get('X-GitHub-Event') == 'push':
        subprocess.run(['git', 'pull'])
        return 'Webhook received successfully', 200
    else:
        return 'Invalid webhook event', 400

def run():
  app.run(host = '0.0.0.0', port = 8080)

def keep_alive():
  t = Thread(target = run)
  t.start()