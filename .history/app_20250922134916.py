from pathlib import Path
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import matplotlib.pyplot as plt
import fastf1
import fastf1.plotting as f1plt

app = Flask(__name__)
app.secret_key = "dev"  # needed for flash messages

# Ensure cache exists next to this app
BASE_DIR = Path(__file__).parent.resolve()
CACHE_DIR = BASE_DIR / ".fastf1"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

def generate_plot(year:int, event_str:str, session_code:str, drv1:str|None, drv2:str|None, outpath:Path) -> dict:
    """
    Generate a Speed vs Distance plot for one or two drivers.
    Returns a small dict with info to display.
    """
    # Determine event identifier: round number (int) or GP name (str)
    event_identifier: int|str
    if event_str.strip().isdigit():
        event_identifier = int(event_str.strip())
    else:
        event_identifier = event_str.strip()

    # Load session
    session = fastf1.get_session(year, event_identifier, session_code)
    session.load(laps=True, telemetry=True)

    # Prepare drivers
    drv1 = (drv1 or "").strip().upper()
    drv2 = (drv2 or "").strip().upper()

    # Collect laps and telemetry
    laps_info = []

    f1plt.setup_mpl()

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    if drv1:
        lap1 = session.laps.pick_driver(drv1).pick_fastest()
        tel1 = lap1.get_telemetry()
        ax.plot(tel1["Distance"], tel1["Speed"], label=f"{drv1} (fastest)")
        laps_info.append({"driver": drv1, "laptime": str(lap1['LapTime'])})
    if drv2:
        lap2 = session.laps.pick_driver(drv2).pick_fastest()
        tel2 = lap2.get_telemetry()
        ax.plot(tel2["Distance"], tel2["Speed"], label=f"{drv2} (fastest)")
        laps_info.append({"driver": drv2, "laptime": str(lap2['LapTime'])})

    # If no drivers provided, plot overall fastest
    if not laps_info:
        lap = session.laps.pick_fastest()
        tel = lap.get_telemetry()
        ax.plot(tel["Distance"], tel["Speed"], label=f"{lap['Driver']} (overall fastest)")
        laps_info.append({"driver": str(lap['Driver']), "laptime": str(lap['LapTime'])})

    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Speed [km/h]")
    ax.set_title(f"{session.event['EventName']} {session.event.year} — {session.name}")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)

    return {
        "event": str(session.event["EventName"]),
        "year": int(session.event.year),
        "session": session.name,
        "laps": laps_info
    }

@app.route("/", methods=["GET"])
def index():
    # Show form and, if present, last plot
    plot_url = None
    plot_path = BASE_DIR / "static" / "plot.png"
    if plot_path.exists():
        # cache-busting query param
        plot_url = url_for("static", filename="plot.png", v=int(time.time()))
    return render_template("index.html", plot_url=plot_url)

@app.route("/plot", methods=["POST"])
def plot():
    year = request.form.get("year", "2025").strip()
    event = request.form.get("event", "Baku").strip()
    session_code = request.form.get("session", "Q").strip()
    drv1 = request.form.get("driver1", "").strip()
    drv2 = request.form.get("driver2", "").strip()

    # Basic validation
    try:
        year_int = int(year)
    except ValueError:
        flash("Year must be a number.", "error")
        return redirect(url_for("index"))

    outpath = BASE_DIR / "static" / "plot.png"
    try:
        info = generate_plot(year_int, event, session_code, drv1, drv2, outpath)
        flash(f"Generated plot for {info['event']} {info['year']} — {info['session']}", "success")
        for li in info["laps"]:
            flash(f"{li['driver']}: {li['laptime']}", "info")
    except Exception as e:
        flash(f"Error: {e}", "error")

    return redirect(url_for("index"))

if __name__ == "__main__":
    # Run the dev server
    app.run(debug=True)  # http://127.0.0.1:5000/