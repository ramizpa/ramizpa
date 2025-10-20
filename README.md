# Hi there, I'm Ramiz 👋

-🧑‍💻 AI/ML Enthusiast

-🔐 AI/ML for InfoSec/CyberSecurity

-🧑‍💻 Solutions Consultant - RFID & Mobility Solutions at Technowave Group

-🎓 M.Tech In Artificial Intelligence & Machine Learning from BITS PILANI 

[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)](https://linkedin.com/in/ramizpa)
[![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?logo=github&logoColor=white)](https://github.com/ramizpa)
[![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?logo=twitter&logoColor=white)](https://twitter.com/ramizpa)
[![Kaggle](https://img.shields.io/badge/Kaggle-%2300C4B4.svg?logo=kaggle&logoColor=white)](https://kaggle.com/ramizpa)
[![Portfolio](https://img.shields.io/badge/Portfolio-%23FF5733.svg?logo=google-chrome&logoColor=white)](https://ramizpa.com)


![Ramiz's GitHub stats](https://github-readme-stats.vercel.app/api?username=ramizpa&show_icons=true&theme=radical)
![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username=ramizpa&show_icons=true&theme=radical)
![Top Libraries](https://github-readme-stats.vercel.app/api/top-langs/?username=ramizpa&hide=html,css,javascript&langs_count=10&theme=radical&layout=compact&custom_title=Library%20Usage)

import json
import urllib.parse

# Load your library JSON
url = "https://raw.githubusercontent.com/ramizpa/github-stats/main/data/libraries.json"
import requests
data = requests.get(url).json()

labels = list(data.keys())
values = list(data.values())
colors = ["#ff0080","#ff3cac","#ff79c6","#ffb6c1","#6a0dad","#38bdf8","#39ff14","#ffdd00","#ff7f50","#6affc1"]

chart_config = {
    "type": "bar",
    "data": {
        "labels": labels,
        "datasets": [{
            "data": values,
            "backgroundColor": colors,
            "borderRadius": 12
        }]
    },
    "options": {
        "indexAxis": "y",
        "plugins": {
            "legend": {"display": False},
            "datalabels": {
                "display": True,
                "color": "white",
                "align": "right",
                "anchor": "end",
                "font": {"weight": "600", "size": 12},
                "formatter": "function(value){return value+'%';}"
            },
            "title": {
                "display": True,
                "text": "Library Usage Stats",
                "color": "white",
                "font": {"size": 14, "weight": "600"}
            }
        },
        "scales": {"x": {"ticks": {"display": False}, "grid": {"display": False}},
                   "y": {"ticks": {"display": False}, "grid": {"display": False}}},
        "layout": {"padding": 4},
        "responsive": True,
        "maintainAspectRatio": False
    },
    "plugins": ["chartjs-plugin-datalabels"]
}

chart_url = "https://quickchart.io/chart?c=" + urllib.parse.quote(json.dumps(chart_config)) + "&width=500&height=130&bkg=0f1724"
print(chart_url)







