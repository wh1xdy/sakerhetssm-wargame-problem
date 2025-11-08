let pizzatype = "";

function setOrder(pizzaname)
{
	if(pizzatype != "") 
	{ 
		document.getElementById("pizza_" + pizzatype).classList.remove("selected"); 
	}
	else
	{
		document.getElementById("delivery_details").classList.remove("hidden");
		document.getElementById("delivery_details").classList.add("animated");

	}
	document.getElementById("pizza_" + pizzaname).classList.add("selected");
	pizzatype = pizzaname;
	
}

function sendOrder(e)
{
	let address = document.getElementById("address").value;
	const data = {
		type: pizzatype,
		address: address
	};
	const orderParams = new URLSearchParams(data);

	location.href = `order?${orderParams.toString()}`
}

function finishOrder()
{
	setTimeout(() => {
		location.href = "/pizza_order";
	}, 5000);
}
