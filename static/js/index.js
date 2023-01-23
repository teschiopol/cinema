/* eslint no-unused-vars: "error"*/
/* exported */
// show / hide campo pwd
function mostraPwd(){
    var pwd = document.getElementsByName('pwd');
    if (pwd[0].type === 'password'){
	    pwd[0].type = 'text' ;
		document.getElementById('mostra').value = 'Nascondi';
	}else{
		pwd[0].type = 'password';
		document.getElementById('mostra').value = 'Mostra';
	}
}

var c=0;

// Update count price
function countPrice(){
    c=0;
	var form = document.getElementById('posto');
	for (var i = 2; i < form.length ; i++) {
	    if (form[i].checked){
		    c++;
		}
	}
	c = c * 5;
	document.getElementById('priceTotale').innerHTML = 'Totale: '+c+',00 €' ;
}

// select ticket
function controllo(){
    var form = document.getElementById('posto');
	if (c!=0){
	    form.action = '/acquistaPosto';
	    form.submit();
	}else{
	    document.getElementById('warning').style.display = 'block';
	}
}

// back
function back(){
    var form = document.getElementById('posto');
	form.action = '/acquista';
	form.submit();
}

function modifica(){
		var form = document.getElementById('frm');
		form.action = '/pp';
		form.submit();
	}

function utenti(){
    document.getElementById('stats').style.display = 'none';
	document.getElementById('film').style.display = 'none';
    document.getElementById('utenti').style.display = 'block';
}

function film(){
    document.getElementById('utenti').style.display = 'none';
    document.getElementById('stats').style.display = 'none';
    document.getElementById('film').style.display = 'block';
}

function statis(){
    document.getElementById('utenti').style.display = 'none';
	document.getElementById('film').style.display = 'none';
	document.getElementById("stats").style.display = "block";
}

function addfilm(){
    document.getElementById('delfilm').style.display = 'none';
	document.getElementById("addfilm").style.display = "block";
	document.getElementById("rmvSpettacolo").style.display = "none";
    document.getElementById("addSpettacolo").style.display = "none";
}

function delfilm(){
    document.getElementById('addfilm').style.display = 'none';
	document.getElementById("delfilm").style.display = "block";
	document.getElementById("rmvSpettacolo").style.display = "none";
	document.getElementById("addSpettacolo").style.display = "none";
}

function addSpettacolo(){
    document.getElementById('addfilm').style.display = 'none';
	document.getElementById("delfilm").style.display = "none";
	document.getElementById("rmvSpettacolo").style.display = "none";
	document.getElementById("addSpettacolo").style.display = "block";
}

function rmvSpettacolo(){
    document.getElementById('addfilm').style.display = 'none';
	document.getElementById("delfilm").style.display = "none";
	document.getElementById("rmvSpettacolo").style.display = "block";
	document.getElementById("addSpettacolo").style.display = "none";
}

function admin(index){
    location.href="/promuoviAdmin/" + index;
}
