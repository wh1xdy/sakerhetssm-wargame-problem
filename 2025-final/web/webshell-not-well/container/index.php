<?php
    // Define site title
    $site_title = "Staketmyndigheten - Vi håller koll på alla staket!";
?>
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $site_title; ?></title>
    <link rel="stylesheet" href="styles.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #006aa7;
            color: white;
            padding: 15px;
            text-align: center;
        }
        nav ul {
            list-style: none;
            padding: 0;
        }
        nav ul li {
            display: inline;
            margin-right: 20px;
        }
        nav ul li a {
            color: white;
            text-decoration: none;
            font-weight: bold;
        }
        main {
            padding: 20px;
            text-align: center;
        }
        footer {
            background-color: #006aa7;
            color: white;
            text-align: center;
            padding: 10px;
            position: fixed;
            bottom: 0;
            width: 100%;
        }
    </style>
</head>
<body>
    <header>
        <h1><?php echo $site_title; ?></h1>
        <nav>
            <ul>
                <li><a href="index.php">Hem</a></li>
                <li><a href="about.php">Om Staket</a></li>
                <li><a href="contact.php">Kontakta Staketmyndigheten</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section>
            <h2>Välkommen till Staketmyndigheten</h2>
            <p>Vi ser till att Sveriges staket är i toppskick. Inga lutande plankor på vår vakt!</p>
        </section>
    </main>

    <center>
        <img style="align-items: center;" src="image.png" alt="Staket" >
    </center>
    
    <footer>
        <p>&copy; <?php echo date("Y"); ?> Staketmyndigheten. Alla rättigheter förbehållna. Håll dig innanför staketet!</p>
    </footer>
</body>
</html>
