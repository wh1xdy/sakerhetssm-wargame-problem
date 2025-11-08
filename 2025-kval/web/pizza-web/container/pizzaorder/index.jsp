<html>
<head>
<title>Pizza Web</title>
<script src="index.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Gemunu+Libre:wght@300&display=swap" rel="stylesheet">
</head>
<body>
<style>
html {
  font-family: "Gemunu Libre", serif;	
}

.column {
  float: left;
  width: 20%;
  padding: 0 10px;
}

.card {
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); 
  padding: 16px;
  text-align: center;
  background-color: #f1f1f1;
  aspect-ratio : 1 / 1;
  border-radius: 25px;
}

.card:hover {
  background-color: #c2c2c2;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.8);
}

.img {
  width: 100%;
  height: 90%;
  border-radius: 25px;
  margin-top: 5%;
}

.bottom {
  position: fixed;
  bottom: 0;
  right: 0;
  border: 3px solid #AA1111;
  background-color:CC9999;
  font-size: 1.5em;
}

.selected {
  background-color: #a0c0a0 !important;
}

.hidden {
  display: none;
}

@keyframes slide-bottom {
  0% {
	opacity: 0;
    transform: translateY(-100px);
  }
  100% {
	opacity: 1;
    transform: translateY(0px);
  }
}
 
.animated {
  animation: slide-bottom 0.5s ease-in-out 1 alternate both;
}

.placeholder {
  visibility: hidden;
  aspect-ratio : 5 / 1;
  width: 100%;
}

.input {
  width: 50%;
  font-size: 2em;
  border: 5px solid #AA8888;
  border-radius: 10px;
  background-color: #CCDDBB;
  font-family: "Gemunu Libre", serif;
  margin: 10px;
}

.button {
  border: 5px solid #448866;
  background-color: #88AABB;
}
</style>

<h1>Welcome to Pizza Web</h2>
<p>Select the pizza you want to order</p>
<div>
<div class="column"><div onclick="setOrder('pepperoni')" id="pizza_pepperoni" class="card">Pepperoni</br><img src="img/pizza_pepperoni.webp" class="img"></div></div>
<div class="column"><div onclick="setOrder('pineapple')" id="pizza_pineapple" class="card">Pineapple</br><img src="img/pizza_pineapple_meat.jpg" class="img"></div></div>
<div class="column"><div onclick="setOrder('funghi')" id="pizza_funghi" class="card">Funghi</br><img src="img/pizza_funghi.webp" class="img"></div></div>
<div class="column"><div onclick="setOrder('cheese')" id="pizza_cheese" class="card">Cheese</br><img src="img/pizza_cheese.jfif" class="img"></div></div>
<div class="placeholder"></div>
</div>
<div id="delivery_details" class="hidden">
<h2>Delivery<h2>
<form onsubmit="sendOrder(); return false;">
<input type="text" id="address" placeholder="Enter your address (No { no })" class="input"></input>
<br>
<button type="submit" class="input button">Send Order</button>
</form>
</div>

<a href="src.html" class="bottom">Source Code</a>
</body>
</html>
