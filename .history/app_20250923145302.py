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
from fastf1.utils import strftimedelta 

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
    f1plt.setup_mpl(mpl_timedelta_support=True, color_scheme=None)

    year = int(request.form.get("year", "2025"))
    event = (request.form.get("event", "") or "Baku").strip()
    session_code = request.form.get("session", "Q").strip()

    sess = fastf1.get_session(year, int(event) if event.isdigit() else event, session_code)
    sess.load(laps=True)

    drivers = pd.unique(sess.laps["Driver"])

    fastest = []
    for drv in drivers:
        # IMPORTANT: pass a list to pick_drivers
        lap = sess.laps.pick_drivers([drv]).pick_fastest()
        if lap is not None and pd.notna(lap["LapTime"]):
            fastest.append(lap)

    fastest_laps = (
        Laps(fastest)
        .sort_values(by="LapTime")
        .reset_index(drop=True)
    )

    pole_lap = fastest_laps.pick_fastest()
    fastest_laps["LapTimeDelta"] = fastest_laps["LapTime"] - pole_lap["LapTime"]

    # team colors per bar
    team_colors = [
        f1plt.get_team_color(lap["Team"], session=sess)
        for _, lap in fastest_laps.iterlaps()
    ]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    ax.barh(fastest_laps.index, fastest_laps["LapTimeDelta"],
            color=team_colors, edgecolor="grey")
    ax.set_yticks(fastest_laps.index, labels=fastest_laps["Driver"])
    ax.invert_yaxis()  # fastest on top
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which="major", linestyle="--", color="black", zorder=-1000)
    ax.set_xlabel("Δ to pole (mm:ss.ms)")

    lap_time_string = strftimedelta(pole_lap["LapTime"], "%m:%s.%ms")
    plt.suptitle(f"{sess.event['EventName']} {sess.event.year} {sess.name}\n"
                 f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")
    fig.tight_layout()

    out = STATIC_DIR / "quali.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

    flash("Qualifying delta chart generated.", "success")
    return redirect(url_for("result_quali"))

if __name__ == "__main__":
    app.run(debug=True)  # browse to http://127.0.0.1:5000/