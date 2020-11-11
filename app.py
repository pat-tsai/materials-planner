from flask import Flask, render_template, make_response, send_from_directory, session, request
from flask_session import Session
import MRP
from werkzeug.utils import secure_filename
import io
import csv
import re
from backorder_log_script import aggregate_csv
import flask_excel as excel
import pyexcel as pe



UPLOAD_FOLDER = 'templates/outputs'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)


quote_num = ''

@app.route('/')
def index():
    return render_template('homepage.html')


@app.route("/system_sku_search")
def get_input():
    input = {}
    sku = request.args['product_sku']
    input[sku] = 1
    MRP.build_output(input, 1)
    return render_template('index.html')

'''
@app.route("/system_sku_search")
def get_input():
    return request.args['product_sku']
'''

@app.route('/search_quote_items')
def get_quote():
    input = {}
    quote_num = request.args['quote_num']
    session['quote_num'] = quote_num
    #quote_number.append(quote_num)
    input = MRP.get_quote_items(quote_num, 2)
    MRP.build_top_level_output(input,1, quote_num)

    return render_template('index.html', quote_num=quote_num)

'''
@app.route('/DownloadCSV')
def download_csv():
    return Flask.send_file('outputs/output.csv',
                     mimetype='text/csv',
                     attachment_Filename='downloadFile.csv',
                     as_attachment=True)


@app.route('/outputs/output.csv')
def download_file():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'output.csv',
                               as_attachment=True)
'''

# allows named file downloading, need to refresh to download additional searches
@app.route("/outputs/<csv>")
def download_file(csv):
    try:
        print(f"session variable is {session['quote_num']}")
        csv = str(session['quote_num']) + '_MRP.csv'
    except:
        print('Error obtaining quote number')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename=csv, as_attachment=True)

#@app.route("/form")
#def form():
#    return render_template('index.html')

@app.route("/form", methods = ['POST'])
def upload():
  #  if request.method == 'POST':
    f = request.files['file']
    print(f)
    f.save(secure_filename(f.filename))
    return "File saved successfully"



def transform(text_file_contents):
    return text_file_contents.replace("=", ",")


@app.route('/upload')
def form():
    return """
<html>  
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width", initial-scale=1>
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>myMRP</title>
    <link
      rel="stylesheet"
      href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"
      integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm"
      crossorigin="anonymous"
    />
    <link rel="stylesheet" type="text/css" href="../static/css/style.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="../static/js/script.js"></script>
</head>

<body class="bg-light">
    <div class="wrapper">
        <nav class="navbar navbar-light bg-light navbar-expand-lg">
            <a href="/" id="button1">Homepage</button>
            <a href="outputs/output.csv" id="button2" download>DownloadCSV</a>
            <a href="/upload" id="button3">BackorderLogAggregator</a>

        </nav>
    </div>
    <div class="jumbotron">Material Requirements Planner
    </div>
    <div class='col-md-8'>
                <h1>Backorder Report Aggregator</h1>
            <h3>Upload backorder sales report (do not change name of file), click submit to download csv with total material demand grouped by customer/order number</h3>
                <form action="/transform" method="post" enctype="multipart/form-data">
                    <input type="file" name="data_file" />
                    <input type="submit" />
                </form>
</div>
</html>
    """
'''
@app.route('/transform', methods=["POST"])
def transform_view():
    f = request.files['data_file']
    #data = pd.read_csv(f)
    output_dict = aggregate_csv(f)
    excel.init_excel(app)
#    response = make_response(csv)
#    response.headers["Content-Disposition"] = "attachment; filename=backorder_log_aggregated.csv"
    response = excel.make_response_from_dict(output_dict, file_type='csv', file_name="aggregated_backorder_log")
    return response
'''

@app.route('/transform', methods=["POST"])
def transform_view():
    f = request.files['data_file']
    f_name = f.filename
    date = f_name[-12:-4]
    print(date)
    if re.match(r'[1234567890]+', date):
        filename = date + '_backorder_log_aggregated.csv'
    #data = pd.read_csv(f)
    output_df = aggregate_csv(f)
    #excel.init_excel(app)
    response = make_response(output_df.to_csv())
    response.headers["Content-Disposition"] = (f"attachment; filename={filename}")
    response.headers["Content-Type"] = "text/csv"
    #response = excel.make_response_from_dict(output_dict, file_type='csv', file_name=f_name)
    return response


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000)
    app.run()
    #app.run(host='0.0.0.0', port=5000, debug=True)
    #print(MRP.build_output({'SYS-620P-TRT': 1}))
