from flask import Flask, redirect, render_template, request
import json
import requests
from ratelimit import limits


api = Flask(__name__)


class KeySystems:

    def save(key, webhook):
        with open("webhooks.json", 'r') as f:
            data = json.loads(f.read())
            if key in data:
                return 
        data[key] = webhook
        with open("webhooks.json", 'r+') as f:
            f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

    def get(key):
        with open("webhooks.json", 'r') as f:
            data = json.loads(f.read())
            if key in data:
                return data[key]

@api.route('/')
def check():
	return render_template('home.html'), 201

@api.route('/api/sendhook', methods=['POST'])
@limits(calls=1, period=30) # ratelimit
def sendhook():
	data = request.get_json()
	key = data['key']
	payload = data['message']
	hook = KeySystems.get(key)
	r = requests.post(hook, json={"content": payload}, headers={"content-type": "application/json"})
	if r.status_code == 204 or 200:
		return "Sent Webhook"
	else:
		return "Error!"

@api.route('/api/addwebhook', methods=['POST'])
def addwebhook():
	data = request.get_json()
	webhook = data['webhook']
	key = data['key']
	KeySystems.save(key, webhook)
	return "Attempted to Save webhooks", 200

@api.errorhandler(404)
def page_not_found(e):
	return redirect("http://localhost:5000/")

@api.errorhandler(405)
def not_allowed(e):
	return redirect("http://localhost:5000/")

if __name__ == '__main__':
	api.run(debug=True)