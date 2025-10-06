from pathlib import Path
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import matplotlib
matplotlib.use("Agg")   # headless backend for servers
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import fastf1
import fastf1.plotting as f1plt
import pandas as pd
from timple.timedelta import strftimedelta
from fastf1.core import Laps 

app = Flask(__name__)
app.secret_key = "dev"

BASE_DIR = Path(__file__).parent.resolve()
CACHE_DIR = BASE_DIR / ".fastf1"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

@app.get("/healthz")
def healthz():
    return "ok"

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/menu")
def menu():
    return render_template("menu.html")

@app.route("/result", methods=["GET"])
def result():
    p = BASE_DIR / "static" / "plot.png"
    if p.exists():
        plot_url = url_for("static", filename="plot.png", v=int(time.time()))
    return render_template("result.html", plot_url=plot_url)


@app.post("/plot")
def plot():
    year = int(request.form.get("year", "2025"))
    event = request.form.get("event", "...")
    session_code = request.form.get("session", "Q")
    drv1 = (request.form.get("driver1", "") or "").upper().strip()
    drv2 = (request.form.get("driver2", "") or "").upper().strip()

    sess = fastf1.get_session(year, int(event) if event.isdigit() else event, session_code)
    sess.load(laps=True, telemetry=True)

    f1plt.setup_mpl()
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    plotted = False
    if drv1:
        lap1 = sess.laps.pick_driver(drv1).pick_fastest()
        tel1 = lap1.get_telemetry()
        ax.plot(tel1["Distance"], tel1["Speed"], label=f"{drv1} fastest")
        plotted = True
    if drv2:
        lap2 = sess.laps.pick_driver(drv2).pick_fastest()
        tel2 = lap2.get_telemetry()
        ax.plot(tel2["Distance"], tel2["Speed"], label=f"{drv2} fastest")
        plotted = True
    if not plotted:
        lap = sess.laps.pick_fastest()
        tel = lap.get_telemetry()
        ax.plot(tel["Distance"], tel["Speed"], label=f"{lap['Driver']} (overall fastest)")

    ax.set_xlabel("Distance [m]"); ax.set_ylabel("Speed [km/h]")
    ax.set_title(f"{sess.event['EventName']} {sess.event.year} — {sess.name}")
    ax.grid(True); ax.legend(); fig.tight_layout()

    out = BASE_DIR / "static" / "plot.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    flash("Plot generated", "success")
    return redirect(url_for("result"))

@app.post("/quali")
def quali():
    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None)


    session = fastf1.get_session(2021, 'Spanish Grand Prix', 'Q')
session.load()

if __name__ == "__main__":
    app.run(debug=True)  # browse to http://127.0.0.1:5000/