'''from prettytable import PrettyTable

csv_file = open('outputs/output.csv', 'r')
csv_file = csv_file.readlines()

line1 = csv_file[0]
line1 = line1.split(',')

line2 = csv_file[1]
line2 = line2.split(',')

x = PrettyTable([line1[0], line2[0]], border=True)

for i in range(1,len(line1)):
    x.add_row([line1[i], line2[i]])

html_code = x.get_html_string()
html_file = open('webpage/table.html', 'w')
html_file = html_file.write(html_code)'''

import pandas as pd
import pandas.io.formats.style

def write_to_html_file(df, filename='templates/index.html', title=''):
    '''
    Write an entire dataframe to an HTML file with nice formatting.
    '''

    result = '''
<!DOCTYPE html>
<html lang="en">
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
    <link rel="stylesheet" type="text/css" href="{{url_for('static',filename='css/style.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="../static/js/script.js"></script>
</head>

<body class="bg-light">
    <div class="wrapper">
        <nav class="navbar navbar-light bg-light navbar-expand-lg">
            <a href="/" id="button1">Homepage</button>
            <a href="/outputs/output.csv" id="button2" download>DownloadCSV</a>
            <a href="output.csv" id="button3">UserGuide</a>

        </nav>
    </div>
    <div class="jumbotron">Material Requirements Planner
    </div>
    <div class="container-fluid">
    <div class="row">
      <div class="col-md-2">
        <h4>Search by SMC Product ID<br></h4>
        <h5>format: SKU, quantity</h5>
      </div>
      <div class="col-md-5">
          <form action="/system_sku_search" method="POST" class="bg-light">
            <ul class="list-group bg-light">
                <li class="list-group-item bg-light">
                    <label for="sku">Enter SKU</label>
                    <input style="width:400px" type="text" name="product_sku" placeholder="(ie. SYS-620P-TRT --> material requirements for 1 unit)" id="product_sku" value={{request.form.product_sku}} >
                </li>
            </ul>
          </form>
      </div>
      <p>or</p>
        <div class="col-md-4">
                    <form action="/search_quote_items" class="bg-light">
            <ul class="list-group bg-light">
                <li class="list-group-item bg-light">
                    <label for="quote">Enter Quote(86-)</label>
                    <input type="text" name = "quote_num" placeholder="(ie. 8612345678)" id="sap_quote" />
                </li>
              </ul>
            </form>
        </div>
      </div>
      <div class="space">
                <!-- Choose/upload csv input -->
        <form action="/action_page.php">
          <input type="file" id="myFile" name="filename">
          <input type="submit">
        </form>
      </div>
        <div class="row"><br></div>
      <div class="row">
            <div class="container1"  style="padding-left: 10px;" >
              <button class="add_form_field">Add New Field &nbsp;
              <span style="font-size:16px; font-weight:bold;">+ </span>
              </button>
              <div>
                <input type="text" name="mytext[]" placeholder="SKU, quantity">
              </div>
            </div>
          <div class="col-md-9">
              '''
    result += '<h2> %s </h2>\n' % title
    if type(df) == pd.io.formats.style.Styler:
        result += df.render()
    else:
        result += df.to_html(classes='wide', escape=False)
    result += '''
<input type="button" value="select table" onclick="copyTable();">

        </div>
      </div>
          <script src="../static/js/script.js"></script>

<div class="row"><br></div>
</body>
</html>
'''
    with open(filename, 'w') as f:
        f.write(result)

