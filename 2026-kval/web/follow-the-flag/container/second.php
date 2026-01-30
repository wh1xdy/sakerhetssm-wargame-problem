<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Follow The Flag</title>

    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: "Courier New", monospace;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        color: #00ff41;
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        position: relative;
      }

      body::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
          0deg,
          rgba(0, 255, 65, 0.03) 0px,
          transparent 1px,
          transparent 2px,
          rgba(0, 255, 65, 0.03) 3px
        );
        pointer-events: none;
        animation: scan 8s linear infinite;
      }

      @keyframes scan {
        0% {
          transform: translateY(0);
        }
        100% {
          transform: translateY(20px);
        }
      }

      .container {
        text-align: center;
        padding: 40px;
        background: rgba(10, 10, 10, 0.8);
        border: 2px solid #00ff41;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3),
          inset 0 0 20px rgba(0, 255, 65, 0.05);
        max-width: 600px;
        position: relative;
        z-index: 1;
        animation: fadeIn 1s ease-in;
      }

      @keyframes fadeIn {
        from {
          opacity: 0;
          transform: translateY(-20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      h1 {
        font-size: 2.5em;
        margin-bottom: 30px;
        text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41;
        animation: glow 2s ease-in-out infinite alternate;
      }

      @keyframes glow {
        from {
          text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41;
        }
        to {
          text-shadow: 0 0 20px #00ff41, 0 0 30px #00ff41, 0 0 40px #00ff41,
            0 0 50px #00ff41;
        }
      }

      .flag {
        font-size: 1.8em;
        padding: 25px;
        background: rgba(0, 255, 65, 0.1);
        border: 2px solid #00ff41;
        border-radius: 5px;
        margin: 20px 0;
        animation: pulse 3s ease-in-out infinite;
        font-weight: bold;
      }

      @keyframes pulse {
        0%,
        100% {
          box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
        }
        50% {
          box-shadow: 0 0 20px rgba(0, 255, 65, 0.6);
        }
      }

      .info {
        font-size: 1.1em;
        padding: 15px;
        margin-top: 20px;
        color: #ffdc00;
      }

      a {
        color: #00ff41;
        text-decoration: none;
        padding: 8px 16px;
        border: 1px solid #00ff41;
        border-radius: 5px;
        display: inline-block;
        margin-top: 10px;
        transition: all 0.3s ease;
        text-shadow: 0 0 10px #00ff41;
      }

      a:hover {
        background: rgba(0, 255, 85, 0.2);
        box-shadow: 0 0 15px rgba(0, 255, 85, 0.5);
        transform: translateY(-2px);
      }

      .redirecting {
        color: #ffdc00;
        font-size: 1em;
        margin-top: 15px;
        animation: blink 1s step-start infinite;
      }

      @keyframes blink {
        50% {
          opacity: 0;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Here's the second flag part!</h1>
      <div class="flag">_fr0m_r3direc7ing!}</div>
      <div class="info">
        If you missed the first part, go back <a href="/">here</a>
      </div>
    </div>
  </body>
</html>
