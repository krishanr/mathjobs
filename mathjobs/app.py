from flask import Flask, render_template, request, redirect
import json

from mathjob_ovtime import find_trends

#from rq import Queue
#from rq.job import Job
#from worker import conn

#q = Queue(connection=conn)

app = Flask(__name__)

@app.route('/start')
def start():
    keyword = request.args.get("keyword", None)
    position = request.args.get("position", None) 
    job = request.args.get("result", None)
    
    if position != None and keyword != None:
        key_words = [[r"(?i)(?=.*" + keyword + ")(?=.*" + position + ").*", 0]]
        searchs = [keyword]
    elif position != None:
        key_words = [[r"(?i)" + position , 0]]
        searchs = [position]
    elif keyword != None:
        key_words = [[r"(?i)" + keyword , 0]]
        searchs = [keyword]
    else:
        return json.dumps(repr(request.args))
    
    return json.dumps("hello world")

    if job == "trends":
        # prepare some data
        dates = range(2010, 2012) #range(2010, 2019)
        
        #job = q.enqueue_call(
        #    func=find_trends, args=(dates, key_words,), result_ttl=5000
        #)
    else:        
        raise Exception()
        #job = q.enqueue_call(
        #    func=find_locs, args=(searchs,), result_ttl=5000
        #)
    
    return json.dumps("keyword") #keyword)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507)