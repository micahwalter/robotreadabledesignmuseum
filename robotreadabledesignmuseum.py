#!/usr/bin/python
import pycurl
import urllib
import simplejson as json
import cStringIO
import sys
import logging, os
import urlparse
import oauth2 as oauth
from apscheduler.scheduler import Scheduler

tumblr_blog = os.environ['TUMBLR_BLOG']
api_token = os.environ['CH_API_KEY']

consumer_key = os.environ['TUMBLR_CONSUMER_KEY']
consumer_secret = os.environ['TUMBLR_CONSUMER_SECRET']
oauth_key = os.environ['TUMBLR_OAUTH_KEY']
oauth_secret = os.environ['TUMBLR_OAUTH_SECRET']

request_token_url = 'http://www.tumblr.com/oauth/request_token'
access_token_url = 'http://www.tumblr.com/oauth/access_token'
authorize_url = 'http://www.tumblr.com/oauth/authorize'

logging.basicConfig()
sched = Scheduler()
 
def create_post():
	buf = cStringIO.StringIO()
 
	c = pycurl.Curl()
	c.setopt(c.URL, 'https://api.collection.cooperhewitt.org/rest')
	d = {'method':'cooperhewitt.objects.getRandom','access_token':api_token}

	c.setopt(c.WRITEFUNCTION, buf.write)

	c.setopt(c.POSTFIELDS, urllib.urlencode(d) )
	c.perform()

	random = json.loads(buf.getvalue())

	buf.reset()
	buf.truncate()

	object_id = random.get('object', [])
	object_id = object_id.get('id', [])

	consumer = oauth.Consumer(consumer_key, consumer_secret)
	client = oauth.Client(consumer)

	resp, content = client.request(request_token_url, "GET")
	if resp['status'] != '200':
        	raise Exception("Invalid response %s." % resp['status'])

	request_token = dict(urlparse.parse_qsl(content))

	token = oauth.Token(oauth_key, oauth_secret)
	client = oauth.Client(consumer, token)

	object_link = 'http://collection.cooperhewitt.org/objects/'+object_id+'/qr/xxlg'

	params = {
        'type' : 'photo',
        'source' : object_link,
        'slug' : object_id,
		'state' : 'queue'
		}

	blog = 'http://api.tumblr.com/v2/blog/' + tumblr_blog + '/post'

	print client.request(blog, method="POST", body=urllib.urlencode(params))

    
@sched.cron_schedule(hour='*')
def scheduled_job():
	create_post()

def run_clock():
	sched.start()

	while True:
		pass

if __name__ == "__main__":
	
	import sys
		
	if len(sys.argv) > 1:
		if (sys.argv[1] == "timed"):
			run_clock()
	
	create_post()

