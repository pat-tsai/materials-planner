$(document).ready(function() {
    var max_fields = 20;
    var wrapper = $(".container1");
    var add_button = $(".add_form_field");

    var x = 1;
    $(add_button).click(function(e) {
        e.preventDefault();
        if (x < max_fields) {
            x++;
            $(wrapper).append('<div><input type="text" name="mytext[]"/><a href="#" class="delete">Delete</a></div>'); //add input box
        } else {
            alert('You Reached the limits')
        }
    });

    $(wrapper).on("click", ".delete", function(e) {
        e.preventDefault();
        $(this).parent('div').remove();
        x--;
    })
});

// allows user to quickly copy table results
/*
function selectElementContents(el) {
	var body = document.body, range, sel;
	if (document.createRange && window.getSelection) {
		range = document.createRange();
		sel = window.getSelection();
		sel.removeAllRanges();
		try {
			range.selectNodeContents(el);
			sel.addRange(range);
		} catch (e) {
			range.selectNode(el);
			sel.addRange(range);
		}
	} else if (body.createTextRange) {
		range = body.createTextRange();
		range.moveToElementText(el);
		range.select();
	}
}
*/


var non_material = ['EWCSC','MC0037','OS4HR3','OSDMR3', 'OSNBD3','SFT-DCMS-SINGLE','SFT-DCMS-SVC-KEY','SFT-OOB-LIC','SMMSG3'];
//var rows = [...document.getElementsByTagName('th')].filter(function(elem,i,rep) {
//    return i == rep.indexOf(elem);
//});

// shades table cells based on demand/OH quantity
var cells = document.getElementsByTagName('td');
for (var i=0, len=cells.length; i<len; i++){
        if (non_material.indexOf(cells[i].parentElement.cells[0].innerText) !== -1) {
            console.log(cells[i].parentElement.cells[0].innerText)
            cells[i].style.backgroundColor = 'LightGrey';
            continue
        }
        if (i % 4 == 0){
            if (parseInt(cells[i].innerHTML,10) > parseInt(cells[i+1].innerHTML,10)){
                cells[i].style.backgroundColor = 'indianred';
            }
            else if (parseInt(cells[i].innerHTML,10) < parseInt(cells[i+1].innerHTML,10)){
                cells[i].style.backgroundColor = 'LightGreen';
            }
        }
        if (i % 4 == 0 && parseInt(cells[i+1].innerHTML,10) !== 0){
            if (parseInt(cells[i+1].innerHTML,10) <= Math.round(1.2 * parseInt(cells[i].innerHTML,10) + parseInt(cells[i].innerHTML,10))){
                cells[i].style.backgroundColor = 'gold';
            }
            if (parseInt(cells[i].innerHTML,10) > parseInt(cells[i+1].innerHTML,10)){
                cells[i].style.backgroundColor = 'indianred';
            }
        }
}

/*
$("td").each(function(){
  if($(this).text() > 5)$(this).css('background-color','red');
});

function refreshPage(){
    window.location.load();
}
*/

/*
var downloadLink = document.getElementById('button2');
var inputQuote = document.getElementsByTagName('h2');
inputQuote.onchange=inputQuote.onload= function(downloadLink) {
    downloadLink.href = 'outputs/'
    var pathToCsv = downloadLink.href + (inputQuote[0].innerText) + '_MRP.csv';
    downloadLink.href = pathToCsv;
    return downloadLink;
};
*/


/*  ---functional---
document.addEventListener('DOMContentLoaded', function() {
document.getElementById("button2").addEventListener("click",window.onload=function() {
    document.getElementById("button2").href = "/outputs/" + parseInt(document.getElementsByTagName("h2")[0].innerText) + "_MRP.csv"
});
});
*/

/*
function getCsv() {
    return document.getElementById("button2") + document.getElementsByTagName("h2")[0].innerText + "_MRP.csv";
}
function download () {
    document.getElementById("button2").href = getCsv(downloadLink);
}
*/

