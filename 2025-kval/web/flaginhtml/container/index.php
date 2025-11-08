<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flag in HTML!</title>
    <style>
        body {
            background-color: #000;
            color: #fff;
            font-family: Arial, sans-serif;
            text-align: center;
        }

        h1 {
            font-size: 24px;
            margin-top: 50px;
        }

        #flagContainer {
            margin-top: 50px;
            font-size: 20px;
        }

        #firstHalf {
            color: #ff0000;
        }

        #secondHalf {
            color: #00ff00;
        }
    </style>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            document.getElementById("secondHalf").innerHTML = "";
        });
    </script>
</head>
<body>
    <h1>Här är flaggan!</h1>
    <div id="flagContainer">
        <span id="firstHalf">SSM{1nsp3kt3r4_0</span>
        <span id="secondHalf">ch_uppt4ck}</span>
    </div>
</body>
</html>