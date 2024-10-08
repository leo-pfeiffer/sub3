import re

TIMER_HTML = """
<html lang="en">
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: Arial, sans-serif;
        }
        .timer {
            font-size: 4rem;
            font-weight: bold;
            font-family: "Share Tech Mono", monospace;
            color: black;
        }
        @media (prefers-color-scheme: dark) {
            .timer {
                color: white; /* Color in dark mode */
            
    </style>
</head>
<body>
    <div class="timer" id="timer">00:00:00</div>

    <script>
        let hours = 0;
        let minutes = 0;
        let seconds = 0;
        let delay = 100;
        let speedFactor = 1;
        let totalSeconds = 0;

        function updateTimer() {
            totalSeconds += Math.round(speedFactor ** 2, 0);
            speedFactor++;

            if (totalSeconds > 3 * 60 * 60) {
                hours = 2;
                minutes = 59;
                seconds = 59;
            } else {
                hours = Math.floor(totalSeconds / 3600);
                minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
                seconds = totalSeconds - (hours * 3600) - (minutes * 60);
            }

            // Update the displayed time
            document.getElementById('timer').textContent = 
                String(hours).padStart(2, '0') + ':' + 
                String(minutes).padStart(2, '0') + ':' + 
                String(seconds).padStart(2, '0');

            if (hours === 2 && minutes === 59 && seconds === 59) {
                clearInterval(timerInterval);
                return;
            }

            clearInterval(timerInterval);
            timerInterval = setInterval(updateTimer, delay);
        }

        let timerInterval = setInterval(updateTimer, delay);
    </script>
</body>
</html>               
"""

STRAVA_EMBED_HTML = """
<!DOCTYPE html>
<html lang="en">
<div style="display: flex; justify-content: center; align-items: center; height: 100%;">
<div class="strava-embed-placeholder" data-embed-type="activity" data-embed-id="12532420236" data-style="standard"></div>
</div>
<script src="https://strava-embeds.com/embed.js"></script>
</html>
"""

_PACE_FORMATTER = """function (params) {
    console.log();
    var value = params[0].value;
    var minutes = Math.floor(value);
    var seconds = Math.round((value - minutes) * 60);
    if (seconds < 10) {
        seconds = '0' + seconds;
    }
    var formattedValue = minutes + ':' + seconds;
    return `${params[0].name} : ${formattedValue}`;
}""".replace("\n", " ")
PACE_FORMATTER = re.sub(r'\s+', " ", _PACE_FORMATTER)

_SHOE_FORMATTER = """function (params) {
    let lowerCaseName = params[0].name.toLowerCase();
    if (lowerCaseName.includes("speed")) {
        return `<img src="https://i.imghippo.com/files/1oPtm1728072579.png" width="60" height="30">`;
    }
    if (lowerCaseName.includes("pro")) {
        return `<img src="https://i.imghippo.com/files/HQFmB1728072623.png" width="60" height="30">`;
    }
    if (lowerCaseName.includes("glycerin")) {
        return `<img src="https://i.imghippo.com/files/DYdAj1728072607.png" width="60" height="30">`;
    }
    if (lowerCaseName.includes("hyperion")) {
        return `<img src="https://i.imghippo.com/files/Ki7TO1728072531.png" width="60" height="30">`;
    }
    return null;
}""".replace("\n", " ")
SHOE_FORMATTER = re.sub(r'\s+', " ", _SHOE_FORMATTER)
