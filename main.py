from flask import request, redirect, Flask
import cgi
import services
import configs
from app import app

app = Flask(__name__)
app.config['DEBUG'] = configs.debug     # displays runtime errors in the browser, too

#test route 
@app.route("/", methods=['GET'])
def test_thing():
    key = services.GetFile(configs.test_file_path)
    #temp for testing file, ptstype,ptscolor,ptsx,ptsy
    ar = key + '--pt--[255,0,0]--40--60'
    services.TrackVideo(ar)
    #services.TrackVideo(services.ParseArguments(request)) correct for later
    services.UploadFile('Tracked-' + key)
    print(key)
    return 'Data'

#@app.route("/vidtrack", methods=['GET', 'POST'])
#def register():


# Create a new route called rate_movie which handles a POST request on /rating-confirmation
#@app.route("/rating-confirmation", methods=['POST'])
#def rate_movie():
 #   movie_id = request.form['movie_id']


# In a real application, this should be kept secret (i.e. not on github)
# As a consequence of this secret being public, I think connection snoopers or
# rival movie sites' javascript could hijack our session and act as us,
# perhaps giving movies bad ratings - the HORROR.
#app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == "__main__":
    app.run()
